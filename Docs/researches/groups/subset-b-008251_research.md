# subset-b-008251 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/client.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rpc/client.rs

Purpose: This file is the small shared gRPC client factory and interceptor layer for RustFS ecstore internode control-plane RPCs. It builds `NodeServiceClient<InterceptedService<Channel, TonicInterceptor>>` instances from cached or freshly-created tonic channels, attaches HMAC authentication for signed calls, and provides a no-auth variant for callers that intentionally skip signing.

Important APIs/types/functions: `node_service_time_out_client` looks up `GLOBAL_CONN_MAP` by address and falls back to `rustfs_protos::create_new_channel` when no cached `Channel` exists. `node_service_time_out_client_no_auth` wraps the same factory with `TonicInterceptor::NoOp`. `is_network_like_disk_error` centralizes disk/RPC error classification for timeout, connection refusal/reset, broken pipe, EOF, tonic transport, unavailable, deadline, and similar network strings. `TonicSignatureInterceptor` signs tonic calls with `gen_signature_headers(TONIC_RPC_PREFIX, GET)`, then injects W3C trace context and `x-request-id` metadata. `NoOpInterceptor` is a pass-through, and `TonicInterceptor` is an enum wrapper that lets call sites pass either behavior through the same tonic generic type.

Control flow: Callers pass an address and interceptor. The factory takes a read lock on `GLOBAL_CONN_MAP`, clones a cached channel if present, or awaits `create_new_channel`. It then constructs the protobuf-generated `NodeServiceClient` with the selected interceptor. During each signed RPC, tonic invokes `TonicSignatureInterceptor::call`; the interceptor generates signature/timestamp metadata, maps auth setup failures to `tonic::Status::unauthenticated`, extends request metadata, and propagates tracing/request identifiers before the RPC leaves the process.

State and persistence behavior: The file persists no data itself. Its only shared state interaction is the global async connection cache. It does not insert newly-created channels into the cache directly; that is delegated to `create_new_channel`/connection infrastructure. Interceptor state is stateless apart from temporary request metadata mutation.

Dependencies and integration points: The module depends on `crate::rpc::http_auth` for signing, `context_propagation` for observability metadata, `rustfs_common::GLOBAL_CONN_MAP`, `rustfs_protos` channel/client generation, tonic interceptors, and ecstore disk errors. It is consumed by `peer_rest_client.rs`, `peer_s3_client.rs`, and other RPC modules via `rpc/mod.rs`.

Risks: `node_service_time_out_client` trusts the cached channel even when the remote peer was recently marked unhealthy; higher layers must evict or fast-fail appropriately. gRPC signatures use a fixed canonical prefix and `GET`, so server verification must match that convention for all tonic methods. `is_network_like_disk_error` includes string matching, which is pragmatic but can over/under-classify new transport messages.

Test signals: Inline tests verify signed interceptor metadata includes signature/timestamp, may inject `x-request-id`, and propagates `traceparent` metadata from an OpenTelemetry parent context. There are no direct tests for connection-cache behavior or failed `create_new_channel` paths in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/context_propagation.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rpc/context_propagation.rs

Purpose: This file provides the observability propagation glue used by HTTP and tonic internode RPCs. It injects OpenTelemetry trace context and a stable request id into outbound HTTP headers or tonic metadata so downstream peers can correlate logs and spans.

Important APIs/types/functions: `HttpHeaderInjector` and `MetadataInjector` implement OpenTelemetry `Injector` for `http::HeaderMap` and `tonic::metadata::MetadataMap`. `current_trace_id` reads the current tracing span's OpenTelemetry context and returns a valid trace id when available. `fallback_request_id` creates a short `req-<uuid-prefix>` identifier. `propagated_request_id` prefers `trace-<trace_id>` and falls back to the generated request id. Public crate functions are `inject_trace_context_into_http_headers`, `inject_request_id_into_http_headers`, `inject_trace_context_into_metadata`, and `inject_request_id_into_metadata`; `REQUEST_ID_HEADER` is re-exported from `rustfs_utils`.

Control flow: Trace injection obtains `Span::current().context()` and calls the global text-map propagator with the appropriate injector. Each injector validates header/metadata keys and values before insertion and silently skips invalid output from the propagator. Request-id injection first checks whether the destination already contains `x-request-id`; if it does, the upstream value is preserved. Otherwise it derives a trace-backed or fallback id and inserts it if the value is valid for the destination map.

State and persistence behavior: The module has no persistent state. Its runtime behavior depends on the process-global OpenTelemetry propagator and current tracing subscriber/span. Request ids generated without a valid trace id are random UUID-derived values and are not stored.

Dependencies and integration points: It is called by `http_auth::build_auth_headers` for HTTP data-plane requests and by `client::TonicSignatureInterceptor` for gRPC control-plane requests. It depends on `http`, `tonic`, `opentelemetry`, `tracing`, `tracing-opentelemetry`, `uuid`, and `rustfs_utils` header constants.

Risks: Injection failures are intentionally ignored, so malformed propagator output can silently drop trace context. Fallback request ids use only the first eight UUID characters, which is compact for logs but has less uniqueness than a full UUID. The module only injects outbound context; extraction/continuation for inbound peer handlers must be implemented elsewhere for full distributed tracing.

Test signals: Inline tests cover preserving existing request ids, deriving request ids from a supplied trace id for both HTTP and tonic metadata, and fallback `req-` ids when no trace context is active. Tests construct OpenTelemetry SDK subscribers and parent span contexts but do not verify full cross-process extraction.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/context_propagation.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/http_auth.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rpc/http_auth.rs

Purpose: This file implements shared-secret HMAC authentication for RustFS internode RPCs, including HTTP data-plane requests and tonic control-plane metadata generation. It signs the canonical path/query, method, and timestamp, verifies inbound signatures within a replay window, and appends trace/request-id headers to outbound HTTP requests.

Important APIs/types/functions: Constants are `x-rustfs-signature`, `x-rustfs-timestamp`, a 300-second validity window, and `TONIC_RPC_PREFIX`. `get_shared_secret` resolves the RPC token through `rustfs_credentials::try_get_rpc_token` and logs secret-resolution failures once. Test-only `resolve_shared_secret` documents the rejection of empty/default fallback secrets. `signature_payload` canonicalizes a URI to `path_and_query|method|timestamp`. `generate_signature` uses HMAC-SHA256 and base64 output; `verify_signature` decodes base64 and uses `Mac::verify_slice` for constant-time verification. Public APIs are `build_auth_headers`, `gen_signature_headers`, and `verify_rpc_signature`.

Control flow: Signing resolves the secret, reads the current UTC Unix timestamp, builds the HMAC over path/query, method, and timestamp, and returns headers. `build_auth_headers` extends an existing header map with signature headers, then injects trace context and request id. Verification extracts both headers, parses the timestamp, rejects timestamps more than five minutes old or in the future, resolves the secret, and verifies the HMAC against the URL/method supplied by the caller.

State and persistence behavior: No persistent state is written. The only process state is `RPC_SECRET_RESOLUTION_LOG_ONCE`, which suppresses repeated secret-resolution error logs. Authentication correctness depends on both peers using the same runtime secret and sufficiently synchronized clocks.

Dependencies and integration points: It is re-exported by `rpc/mod.rs`, used by `internode_data_transport.rs` for streaming HTTP readers/writers and by `client.rs` for tonic metadata. It integrates with `rustfs_credentials`, `hmac`, `sha2`, `base64`, `time`, `http`, tracing, and context propagation.

Risks: `signature_payload` uses `url.parse().expect("Invalid URL")` and `path_and_query().unwrap()`, so invalid caller input can panic instead of returning an error. The signature covers path/query rather than scheme/host, which allows the same signed request to verify across hosts if path/query/method/timestamp match; that appears intentional for proxy/path canonicalization but is a security boundary to understand. The 300-second window requires clock discipline. Error logs include URL, method, timestamp, and signature length, but intentionally avoid logging secrets or raw signatures.

Test signals: Tests cover secret fallback rejection, deterministic and input-sensitive signatures, building headers, preserving or injecting request ids, successful verification, invalid signatures, constant-time HMAC verification, log redaction, expired and future timestamps, missing/invalid headers, URL/method mismatch, validity-window boundary behavior, and round-trip auth for multiple methods/URLs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/http_auth.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/internode_data_transport.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rpc/internode_data_transport.rs

Purpose: This file defines the ecstore internode data-plane transport abstraction for remote disk streams. It keeps large read/write/walk-dir payload movement on HTTP streaming while control-plane metadata, lock, and admin calls remain on gRPC.

Important APIs/types/functions: `InternodeDataTransportCapabilities` advertises streaming read/write/walk-dir support, ordered delivery, optional maximum transfer size, and fallback support. Request structs are `ReadStreamRequest`, `WriteStreamRequest`, and `WalkDirStreamRequest`. The `InternodeDataTransport` trait exposes `open_read`, `open_write`, `open_walk_dir`, `name`, and `capabilities`. `TcpHttpInternodeDataTransport` is the current implementation. URL builders create `/rustfs/rpc/read_file_stream`, `/rustfs/rpc/put_file_stream`, and `/rustfs/rpc/walk_dir` URLs with encoded query fields. `build_internode_data_transport` and `build_internode_data_transport_from_env` choose the backend.

Control flow: A read request builds a signed GET URL with disk, volume, path, offset, and length, then returns a boxed `HttpReader`. A write request builds a signed PUT URL with disk, volume, path, append, and size, then returns a boxed `HttpWriter`. A walk-dir request signs a GET URL containing the disk reference and passes the serialized body plus optional stall timeout into `HttpReader::new_with_stall_timeout`. Backend selection trims the configured value, defaults blanks to `tcp-http`, accepts the configured default and `tcp` alias case-insensitively, and rejects unknown values with a message listing known backends.

State and persistence behavior: The module writes no persistent data. In non-test builds, `build_internode_data_transport_from_env` caches the first resolved transport or configuration error in a `OnceLock`, so environment changes after first use do not affect the selected data transport. In tests, the cache is bypassed to allow per-test configuration.

Dependencies and integration points: This module is re-exported by `rpc/mod.rs` and is used by remote disk code to open stream readers/writers. It depends on `rustfs_rio::HttpReader/HttpWriter`, `crate::disk::{FileReader, FileWriter}`, `crate::rpc::build_auth_headers`, `rustfs_config` transport constants, `http`, `urlencoding`, `async_trait`, and ecstore disk errors.

Risks: Only the TCP/HTTP implementation is currently available, so the abstraction is future-facing but not yet multi-backend. URLs encode query values but trust `endpoint` as a complete base URL. The cached error behavior means a bad environment value at first access persists until process restart. Authentication uses the full URL for signing, while verification in tests demonstrates path/query canonicalization compatibility.

Test signals: Tests verify capability flags, URL query encoding for disk/volume/path fields, default and blank transport behavior, accepted aliases, known-backend list expectations, rejection of unsupported backends, and raw cached error message shape. There are no live network streaming tests in this file.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/internode_data_transport.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rpc/mod.rs

Purpose: This file is the public module boundary for ecstore RPC support. It declares private RPC implementation modules and re-exports the types/functions that other ecstore components use for gRPC clients, HTTP auth, internode data transport, peer administration, peer S3 bucket operations, remote disk access, and remote locking.

Important APIs/types/functions: Private modules declared here are `client`, `context_propagation`, `http_auth`, `internode_data_transport`, `peer_rest_client`, `peer_s3_client`, `remote_disk`, and `remote_locker`. Re-exports include `TonicInterceptor`, signed/no-auth node-service client constructors, auth helpers and `TONIC_RPC_PREFIX`, `InternodeDataTransport` plus request/capability structs and builders, peer REST constants and `PeerRestClient`, `PeerS3Client`/`LocalPeerS3Client`/`RemotePeerS3Client`/`S3PeerSys`, `RemoteDisk`, and `RemoteClient`.

Control flow: There is no runtime control flow beyond Rust module initialization. Its compile-time role is to keep implementation modules private while exposing a curated API surface.

State and persistence behavior: The file owns no state and performs no persistence. Stateful behavior lives in the re-exported modules, notably connection caches, transport `OnceLock`, peer health trackers, and remote disk/locker implementations.

Dependencies and integration points: This is the integration point consumed by the rest of `ecstore`. It makes RPC internals available to storage pools, remote disks, admin/peer coordination, and bucket operations without requiring callers to know individual file paths. It also ensures auth and data-transport APIs are accessible to sibling modules through `crate::rpc`.

Risks: Because this module re-exports a broad set of internode primitives, API changes here can ripple through much of ecstore. `context_propagation` remains private, which is good for encapsulation but means new outbound transports must either use existing auth/client helpers or add new re-exports.

Test signals: No inline tests are present. Coverage comes indirectly from the re-exported modules' unit tests and any compile failures in downstream callers when the public RPC surface changes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/peer_rest_client.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rpc/peer_rest_client.rs

Purpose: This file implements the peer administrative/control client used to call NodeService RPCs on other RustFS nodes. Despite the name, the implementation is tonic/gRPC based and covers storage/server info, realtime metrics, live events, profiling, IAM/config metadata reloads, service signals, pool/rebalance reloads, and transition-tier reloads.

Important APIs/types/functions: `PeerRestClient` stores the peer `XHost`, `grid_host`, and two atomic flags for offline state and recovery-loop ownership. `PeerLiveEventsBatch` wraps live-event bytes and sequence metadata. `new_clients` builds remote/all peer lists from `EndpointServerPools` only in distributed erasure mode. `get_client`, `evict_connection`, `is_network_like_error`, `mark_offline_and_spawn_recovery`, `perform_connectivity_check`, and `finalize_result` implement connection acquisition and health recovery. Public RPC wrappers include `local_storage_info`, `server_info`, `get_cpus`, `get_net_info`, `get_partitions`, `get_os_info`, `get_se_linux_info`, `get_sys_config`, `get_sys_errors`, `get_mem_info`, `get_metrics`, `get_live_events`, `get_proc_info`, `start_profiling`, bucket metadata loads/deletes, policy/user/group/service-account loads/deletes, `reload_site_replication_config`, `signal_service`, `reload_pool_meta`, `stop_rebalance`, `load_rebalance_meta`, and `load_transition_tier_config`.

Control flow: Most wrapper methods call `get_client`, build a protobuf request, await a NodeService method, check the `success` flag, convert optional `error_info` to `Error::other`, and deserialize MessagePack payloads where needed. `get_metrics` serializes `MetricType` and `CollectMetricsOpts` with MessagePack before sending. `signal_service` builds the request variable map from the signal constants. Every implemented public RPC runs through `finalize_result`, which marks the peer offline and evicts the cached connection when the error text looks network-like. Once offline, `get_client` fast-fails and starts a recovery monitor; the monitor performs TCP connectivity checks with exponential backoff up to 60 attempts, clears offline on success, and otherwise waits for a future request to restart recovery.

State and persistence behavior: No durable state is written. Runtime state is in atomic booleans and the global connection cache evicted through `rustfs_protos::evict_failed_connection`. Recovery tasks are spawned Tokio tasks; `recovery_running` prevents duplicate recovery loops for the same `PeerRestClient` clone set.

Dependencies and integration points: The file depends on `node_service_time_out_client` with signed tonic interceptors, generated NodeService request types, `rustfs_madmin` admin/health/metric models, `rmp_serde`, endpoint discovery, distributed-erasure global state, drive active check intervals/timeouts, tracing, and TCP connectivity checks. It is re-exported by `rpc/mod.rs` for higher-level peer admin flows.

Risks: Network-like classification is string based, so error text changes can affect recovery behavior. Many wrappers repeat the same success/error handling, increasing drift risk. Several methods are explicit `NotImplemented` stubs (`download_profile_data`, bucket stats, site-replication metrics, metacache listing/update), so callers must tolerate that. `new_clients` warns if remote/all counts do not match the assumed local-node relationship but still returns its computed lists. Recovery validates only TCP connectivity, not successful authenticated RPC execution.

Test signals: Inline tests cover network-like classification, offline fast-fail, `finalize_result` marking network errors offline while preserving business errors, and tracing span inheritance for recovery monitor logs. Serialization/deserialization and each individual NodeService wrapper rely on broader integration or generated-service tests.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/peer_rest_client.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/peer_s3_client.rs -->
# sources/object-store/rustfs/crates/ecstore/src/rpc/peer_s3_client.rs

Purpose: This file implements distributed peer S3 bucket operations across local and remote nodes. It provides a trait abstraction for peer bucket APIs, a system-level fan-out coordinator with per-pool quorum reduction, local disk implementations, remote NodeService implementations with health tracking, and local bucket-heal helpers.

Important APIs/types/functions: `PeerS3Client` defines `heal_bucket`, `make_bucket`, `list_bucket`, `delete_bucket`, `get_bucket_info`, and `get_pools`. `S3PeerSys` owns peer clients and `pools_count`. Helper functions `pool_participant_errors`, `pool_write_quorum`, and `reduce_pool_write_quorum_errs` reduce errors only among clients participating in a given pool. `LocalPeerS3Client` filters `all_local_disk()` by pool and performs disk-level volume operations. `RemotePeerS3Client` wraps signed NodeService calls and tracks health with `DiskHealthTracker`, a cancellation token, periodic TCP probes, `execute_with_timeout`, and recovery monitors. `heal_bucket_local`/`heal_bucket_local_on_disks` inspect and optionally repair bucket volume presence across drives.

Control flow: `S3PeerSys::new` converts endpoint nodes into local or remote peer clients. `make_bucket`, `heal_bucket`, `list_bucket`, and `get_bucket_info` fan out with `join_all`, collect per-client results, and enforce write/visibility quorum per pool. `heal_bucket` first probes bucket info to decide remove versus recreate when `opts.recreate` is false, then runs peer heal and returns the first successful `HealResultItem`. `delete_bucket` fans out deletes and, on quorum failure, attempts to recreate the bucket unless it was not found or `no_recreate` is set. Local list/stat/make/delete operate directly on local disks and use majority quorum across filtered disks. Remote methods serialize options to JSON, call generated NodeService methods, convert protobuf errors back into disk errors, and run inside `execute_with_timeout`.

State and persistence behavior: S3PeerSys itself has no persistence. Local operations mutate bucket volumes on local disks through `make_volume`, `delete_volume`, and `stat_volume`; `get_bucket_info` reads bucket metadata via `metadata_sys` to report versioning. Remote health state is in `DiskHealthTracker`, including faulty/ok status, waiting counts, and last-start time; recovery tasks are runtime-only and cancellable. `clone_drives` reads `GLOBAL_LOCAL_DISK_MAP`.

Dependencies and integration points: The file integrates with endpoint topology, local disk stores, bucket metadata, error quorum reducers, heal command types, NodeService protobufs, signed gRPC client creation, global local-disk maps, bucket option types, tracing, Tokio, and TCP connectivity checks. It is re-exported by `rpc/mod.rs` and is a core dependency for distributed bucket create/list/delete/info/heal paths.

Risks: `LocalPeerS3Client::delete_bucket` has a TODO for quorum reduction and currently returns success after best-effort deletes unless `VolumeNotEmpty` triggers recreation, so partial delete failures may be underreported. `heal_bucket_local_on_disks` appears to append after-state drive entries into `res.before.drives` rather than `res.after.drives`, which can confuse heal result consumers. Remote peer health checks use TCP reachability and string/network-like disk error classification, not full RPC health. `execute_with_timeout` uses `unwrap()` on system time duration since Unix epoch, which is practically safe but still a panic site. The fan-out logic assumes each client's `get_pools` membership is accurate; empty participants produce write quorum errors.

Test signals: Tests cover remote timeout/network error fault marking versus business errors, local bucket info after prior walk timeout, local write quorum for partial buckets, local disk filtering by pool, bucket heal recreation, per-pool quorum reduction, make-bucket quorum behavior by participants, and list-bucket visibility for single-participant pools. Remaining high-value gaps include remote NodeService success/error integration, delete-bucket partial failure semantics, and heal result before/after structure.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/rpc/peer_s3_client.rs -->
