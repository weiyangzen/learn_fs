# subset-b-000414 research

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/mod.rs

Purpose: this module is the common gRPC support layer for the io-engine. It publishes `MayastorGrpcServer`, declares the v0/v1 service modules, maps common internal errors to `tonic::Status`, defines the standard `GrpcResult<T>`, and provides reactor submission and request serialization primitives used by almost every gRPC service.

Important APIs/types/functions: `GrpcClientContext` captures method id, debug args, and timeout from `grpc-timeout`; `Serializer`, `RWSerializer`, and `RWLock` standardize service locking; `spdk_submit!` wraps `rpc_submit_ext2` and converts reactor results into `tonic::Response`; `rpc_submit`, `rpc_submit_ext`, and `rpc_submit_ext2` schedule futures on the primary SPDK reactor; `acquire_subsystem_lock` bridges gRPC operations to `ResourceSubsystem` locks; `endpoint_from_str`, `node_name`, `get_request_timeout`, and `lvm_enabled` provide service setup helpers.

Control flow: service handlers generally build `GrpcClientContext`, lock through the service trait, submit SPDK work with `rpc_submit`/`spdk_submit!`, await the oneshot receiver, map cancellation to `Status::cancelled`, and map domain errors via `From` impls. Timeout parsing follows gRPC timeout units and falls back to `DEFAULT_GRPC_TIMEOUT_SEC`.

State and persistence: the module does not persist business data. It controls in-memory operation context and lock acquisition, and it may expose stale timed-out context warnings when a previous cancelled top-level future left a marker behind.

Dependencies and integration points: depends on `tonic`, `tokio`, `futures::oneshot`, `nix::Errno`, `Reactor`, `ResourceSubsystem`, `MayastorFeatures`, and domain errors from bdev/core. It is the integration point between generated protobuf services and SPDK reactor-affine code.

Risks: incorrect error mapping can change control-plane retry behavior; `endpoint_from_str` panics on invalid endpoints; malformed or overflowing timeout values silently fall back or may multiply seconds without explicit saturation; all reactor submissions report spawn failure as resource exhaustion. Test signals should cover timeout parsing, status mapping, lock contention, LVM feature gating, and cancellation of submitted futures.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/server.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/server.rs

Purpose: this file owns process-local startup and shutdown of the tonic gRPC server. It builds a single `MayastorGrpcServer` instance, binds the TCP endpoint, and conditionally registers v0 and v1 service implementations based on the advertised `ApiVersion` list.

Important APIs/types/functions: `MayastorGrpcServer` stores an async-channel receiver/sender pair used as a termination signal. `get_or_init` initializes the global `OnceCell`, `fini` closes the sender, and `run` constructs service instances, binds `TcpIncoming`, wires generated `*Server` wrappers, and races server completion against the shutdown channel.

Control flow: `run` creates shared v1 `PoolService` and `ReplicaService` so stats, snapshot, snapshot-rebuild, and test services operate over the same lock contexts. Optional v1 services include bdev, json, pool, replica, test, snapshot, snapshot rebuild, host, nexus, and stats. Optional v0 services include mayastor, json, and bdev. `futures::select!` returns success on graceful shutdown, logs and returns an error on tonic server failure, or exits when the termination channel closes.

State and persistence: server state is in-memory only. Business persistence is delegated to service implementations. The static `OnceCell` means there is one server control channel per process, and closing `fini_chan` is a one-way shutdown signal.

Dependencies and integration points: integrates generated `io_engine_api` servers, `registration_grpc::ApiVersion`, tonic transport, and all gRPC service modules. It receives node identity, node NQN, endpoint, JSON-RPC address, and API-version selection from upper startup code.

Risks: service availability is controlled only by `api_versions.contains`; a misconfigured list silently omits an API generation. Binding errors are normalized to `AddrInUse`, which may hide other socket setup details. Shutdown closes the channel rather than using tonic graceful shutdown with per-request draining. Test signals should instantiate with v0-only, v1-only, and both versions, assert binding failure messages, and verify that shared services are cloned consistently.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/server.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v0/bdev_grpc.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v0/bdev_grpc.rs

Purpose: this v0 compatibility service exposes raw SPDK bdev lifecycle and NVMf sharing RPCs. It converts internal `UntypedBdev` objects into v0 protobuf `Bdev` records and forwards create/destroy/share/unshare work to the primary reactor.

Important APIs/types/functions: `impl From<UntypedBdev> for RpcBdev` maps name, UUID, size, block size, claim state, aliases, product, share URI, and parsed URI. `BdevSvc::new/default` constructs the stateless service. The `BdevRpc` implementation provides `list`, `create`, `destroy`, `share`, and `unshare`.

Control flow: `list` iterates `UntypedBdev::bdev_first()` and returns all current bdevs. `create` and `destroy` move a URI into `bdev_create` or `bdev_destroy`. `share` accepts only string protocol `"nvmf"`, looks up the bdev, builds `NvmfShareProps` with allowed hosts, shares it, then re-reads the bdev to return the effective URI. `unshare` is idempotent for missing names.

State and persistence: this file mutates SPDK bdev state and NVMf exports but persists nothing itself. Share state is reflected through core bdev metadata and any lower-level NVMf/PTPL behavior.

Dependencies and integration points: depends on `io_engine_api::v0`, `bdev_api`, `core::{UntypedBdev, Share, NvmfShareProps}`, `url::Url`, and `grpc::rpc_submit`. It is registered only when v0 API support is enabled in `server.rs`.

Risks: protocol validation is string-based and rejects anything except lowercase `"nvmf"`; `create` returns only a name, so clients must call list to inspect details; `unshare` silently succeeds when the bdev is absent; aliases are comma-joined and lose structure. Test signals should cover URI error mapping, NVMf allowed-host propagation, missing bdev share/unshare behavior, and list conversion for claimed/orphaned bdevs.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v0/bdev_grpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v0/json_grpc.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v0/json_grpc.rs

Purpose: this small v0 service proxies gRPC requests to the local SPDK JSON-RPC endpoint. It preserves old clients that invoke arbitrary SPDK methods through the gRPC API.

Important APIs/types/functions: `JsonRpcSvc` stores a `Cow<'static, str>` JSON-RPC address. `json_rpc_call` implements generated `JsonRpc` by extracting method and params. `empty_as_none` converts an empty params string into `None`. `spdk_jsonrpc_call` parses params into `serde_json::Value`, calls `jsonrpc::call`, and pretty-serializes the JSON result.

Control flow: the service does not use the SPDK reactor submission helpers. It runs async JSON-RPC client I/O directly from the tonic handler, propagating parse/call/serialization failures through `jsonrpc::error::Error` into tonic via existing conversions.

State and persistence: no persistent state; only the configured RPC address is stored. The proxied method may mutate SPDK state outside this module’s type system.

Dependencies and integration points: depends on `io_engine_api::v0`, the `jsonrpc` helper crate, `serde_json`, and the address supplied by `server.rs`. It bypasses typed service validation and can reach SPDK methods not modeled by protobuf.

Risks: params are accepted as a raw JSON string, so malformed JSON fails at runtime; pretty serialization changes formatting but not semantic content; arbitrary method access can bypass higher-level locks and validation; the static lifetime comment indicates address ownership is a workaround. Test signals should exercise empty params, invalid JSON params, JSON-RPC failure propagation, and a harmless read-only SPDK method.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v0/json_grpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v0/mayastor_grpc.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v0/mayastor_grpc.rs

Purpose: this is the large v0 Mayastor service implementation for legacy provisioning, nexus, replica, snapshot, host, resource, and NVMe-controller RPCs. It maps older protobuf contracts onto current lvs, nexus, bdev, rebuild, and host modules.

Important APIs/types/functions: `MayastorSvc` owns a service lock and timeout-aware `serialized` helper for per-nexus/global resource locking. Conversion impls map `LvsError`, `Protocol`, `Lvs`, `Lvol`, space usage, rebuild stats, features, block devices, resource usage, NVMe controllers, and reservation options into v0 types. RPC methods cover pool create/destroy/list, replica create/list/share/destroy/stats, nexus create/destroy/shutdown/list/child operations/publish/ANA/rebuild/history, snapshot creation, block-device listing, resource usage, controller list/stats, and version/features.

Control flow: simple pool/replica paths use `self.locked` plus `rpc_submit`; nexus paths use `serialized`, which spawns a Tokio task, optionally grabs the global lock, then grabs the protected nexus resource lock before submitting reactor work. Pool creation is idempotent for existing LVS pools and exports captured `PoolConfig`; pool destruction removes config before destroying. Replica create handles idempotent existing bdevs, validates share protocol, creates lvols, and destroys newly-created lvols if sharing fails.

State and persistence: mutates LVS pools/lvols, NVMf exports, nexus structures, rebuild jobs, snapshots, and SPDK controllers. It persists pool config on create/destroy and creates PTPL files for shared replicas. Snapshot requests generate timestamps and UUIDs.

Dependencies and integration points: integrates `io_engine_api::v0`, `Lvs/Lvol`, `PoolConfig`, `nexus_grpc` helpers, `ResourceLockManager`, `controller_grpc`, host block-device/resource modules, rebuild state, and version info.

Risks: legacy idempotency is uneven; some list/stat paths unwrap lvol conversion; v0 names sometimes strip or add `nexus-`; share failures trigger best-effort cleanup; config export before destroy can diverge if destroy fails. Test signals should include pool config persistence, replica share rollback, per-nexus lock contention, invalid reservation/preemption inputs, PTPL cleanup, and v0/v2 nexus naming compatibility.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v0/mayastor_grpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v0/nexus_grpc.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v0/nexus_grpc.rs

Purpose: this helper module contains v0 nexus conversion and lookup utilities shared by `mayastor_grpc.rs`. It bridges internal nexus/child state and legacy v0 protobuf shapes, including the historical `nexus-{uuid}` naming convention.

Important APIs/types/functions: `map_fault_reason` and `map_child_state` map internal `FaultReason` and `ChildStateClient` into v0 child state/reason enums. `NexusChild::to_grpc`, `Nexus::to_grpc`, and `Nexus::to_grpc_v2` build v0 nexus responses. `name_to_uuid`, `uuid_to_name`, `nexus_lookup`, `nexus_add_child`, and `nexus_destroy` implement compatibility lookup and child/destruction behavior.

Control flow: lookups first try exact name, then UUID lookup, then `nexus-<uuid>` name conversion. `to_grpc_v2` reads ANA state only for NVMf-published nexuses. `nexus_add_child` looks up the nexus, adds a child with the request’s `norebuild` flag, then returns the child by URI. `nexus_destroy` is idempotent: if no nexus exists but the input is a UUID, it best-effort destroys the PTPL file.

State and persistence: conversions are read-only except for rebuild progress/ANA queries. `nexus_add_child` mutates nexus children. `nexus_destroy` mutates nexus state and may remove PTPL persistence.

Dependencies and integration points: depends on internal `nexus` types, `NexusPtpl`, `Share`, rebuild job count, UUID parsing, and `io_engine_api::v0`. It is used by the v0 Mayastor service and is intentionally separate because some macros cannot use `?` inline.

Risks: v0 maps `HotRemove` to `None`, unlike v1’s explicit hot-removed reason; `nexus_add_child` has a TODO for idempotency and may duplicate a child if URI parameters differ; lookup fallback accepts unconventional names; PTPL deletion on missing nexus can mask not-found cases. Test signals should verify state mapping, name/UUID compatibility, ANA visibility only when shared, child duplicate behavior, and idempotent destroy.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v0/nexus_grpc.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/bdev.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/bdev.rs

Purpose: this v1 service exposes typed bdev list/create/destroy/share/unshare RPCs. Compared with v0 it returns richer protobuf responses, supports optional name filtering in `list`, and returns the resulting `Bdev` after create/share.

Important APIs/types/functions: `impl<T> From<core::Bdev<T>> for Bdev` maps core bdev metadata to protobuf. `BdevService::new/default` constructs the stateless service. `BdevRpc` methods are `list`, `create`, `destroy`, `share`, and `unshare`.

Control flow: all SPDK-affine work is submitted through `rpc_submit`. `list` either returns a named bdev or all bdevs. `create` calls `bdev_create`, then looks up the created bdev by name before returning it. `destroy` delegates to `bdev_destroy`. `share` accepts protobuf `Protocol`, only permits `Nvmf`, applies allowed hosts, and returns a fresh bdev snapshot. `unshare` succeeds for missing bdevs and unshares only if present.

State and persistence: this mutates SPDK bdev state and NVMf shares, but does not write persistence directly. It reflects share URI and claim state from core bdevs.

Dependencies and integration points: integrates `io_engine_api::v1::bdev`, `bdev_api`, `core::{UntypedBdev, Bdev, Share, NvmfShareProps, Protocol}`, `url::Url`, and common gRPC status mapping. Registered by `server.rs` for v1.

Risks: create fails if the bdev cannot be found immediately after creation; `unshare` remains idempotent and may hide absent resources; share rejects all protocols except NVMf; URI conversion failures produce an empty string, which may be ambiguous. Test signals should cover filtered list, create lookup failure, allowed-host update, invalid protocol status, and destroy error mapping.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/bdev.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/host.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/host.rs

Purpose: this v1 service reports host/io-engine identity, supported features/bugfixes, block devices, process resource usage, and NVMe controller information. It is the typed replacement for v0 host/resource/controller methods.

Important APIs/types/functions: `HostService` stores node name, optional NQN, gRPC socket, enabled API versions, and a mutex-protected `GrpcClientContext`. It implements `Serializer` for panic/cancellation logging. Conversion impls map features, bugfixes, block-device structures, resource usage, controller info, controller state, and I/O stats into v1 protobuf types. `HostRpc` methods include `get_mayastor_info`, `list_block_devices`, `get_mayastor_resource_usage`, `list_nvme_controllers`, and `stat_nvme_controller`.

Control flow: information-only calls directly build responses except controller list/stat, which lock through `self.locked` and use `rpc_submit` for reactor-affine controller access. `get_mayastor_info` embeds registration payload including node id, endpoint, instance UUID, API versions, host NQN, features, bugfixes, and version.

State and persistence: no mutations or persistence. It reads registration state, process resource usage, udev/mount data, and controller stats.

Dependencies and integration points: depends on `host::blk_device`, `host::resource`, `controller_grpc`, `Registration`, `MayastorFeatures`, `MayastorBugFixes`, version info, and v1 registration protobufs. It is created by `server.rs` with node/server configuration.

Risks: block-device availability depends on udev and mount table freshness; feature/bugfix reporting can affect control-plane scheduling; controller stat errors are propagated for a single named controller; context storage uses a mutex, serializing controller calls. Test signals should verify registration info fields, API version conversion, block-device conversion including connection/rotational fields, and controller not-found/error behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/host.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/json.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/json.rs

Purpose: this v1 service proxies typed gRPC JSON-RPC requests to the local SPDK JSON-RPC endpoint, equivalent to the v0 proxy but using v1 protobuf messages.

Important APIs/types/functions: `JsonService` stores the JSON-RPC address as `Cow<'static, str>`. `json_rpc_call` extracts the method and raw parameter string. `empty_as_none` treats empty params as absent. `spdk_jsonrpc_call` parses params into `serde_json::Value`, calls `jsonrpc::call`, and pretty-prints the returned JSON value.

Control flow: the handler performs JSON parsing and network/client I/O directly in the tonic async context. There is no resource locking, request serialization, or reactor submission, because it delegates to the SPDK JSON-RPC service rather than directly touching reactor-bound Rust objects.

State and persistence: no local state beyond the configured address. Proxied methods may mutate SPDK state externally to the typed gRPC locking model.

Dependencies and integration points: depends on `io_engine_api::v1::json`, `jsonrpc`, `serde_json`, and the RPC address passed by `server.rs`.

Risks: arbitrary method proxying can bypass typed validation and locks; invalid params fail dynamically; pretty JSON response formatting may not match clients expecting compact JSON; address lifetime is acknowledged as a workaround. Test signals should include empty params, malformed params, JSON-RPC transport failures, and read-only SPDK calls.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/json.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/lvm/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/lvm/mod.rs

Purpose: this module centralizes conversion from the internal LVM backend error type into tonic statuses for v1 gRPC callers.

Important APIs/types/functions: the sole public behavior is `impl From<LvmError> for tonic::Status`. It maps invalid pool type, VG UUID mismatch, and disk mismatch to `invalid_argument`; missing VG/LV to `not_found`; no space to `resource_exhausted`; unsupported snapshots to `failed_precondition`; and all remaining errors to `internal`.

Control flow: conversion is a direct match on `LvmError`, preserving the error’s string representation as the status message. There is no asynchronous behavior and no service implementation in this file.

State and persistence: none. It only translates errors raised by the LVM backend elsewhere.

Dependencies and integration points: depends on `crate::lvm::Error` and `tonic::Status`. It is pulled into the v1 gRPC module tree and is also indirectly gated by `grpc::lvm_enabled` and pool backend selection.

Risks: broad fallback to `internal` may obscure actionable client errors; adding new `LvmError` variants without updating this match changes client-visible semantics; messages may include backend details. Test signals should pin mappings for each explicit variant and include a representative fallback variant.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/lvm/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/lvs/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/lvs/mod.rs

Purpose: this compatibility shim converts legacy `Lvol` values into the v1 `Replica` protobuf through the generic replica backend abstraction.

Important APIs/types/functions: `impl From<Lvol> for Replica` casts `&Lvol` to `&dyn ReplicaOps` and delegates to the `From<&dyn ReplicaOps> for Replica` implementation defined in `grpc/v1/replica.rs`.

Control flow: conversion is synchronous and intentionally tiny. It avoids duplicating field mapping for LVS replicas by reusing the trait-object conversion path shared by all replica backends.

State and persistence: none. It reads `Lvol` metadata through `ReplicaOps` only.

Dependencies and integration points: depends on `crate::lvs::Lvol`, `crate::replica_backend::ReplicaOps`, and `io_engine_api::v1::replica::Replica`. It links older LVS-specific code with the backend-neutral v1 replica API.

Risks: correctness depends entirely on the `ReplicaOps` implementation for `Lvol` and on the central mapping in `replica.rs`; any backend-specific data not exposed through `ReplicaOps` is lost. Test signals should verify an `Lvol` converts identically through direct trait-object mapping and through this shim, including snapshots/clones/encryption fields.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/lvs/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/nexus.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/nexus.rs

Purpose: this v1 service implements typed nexus lifecycle, publication, child management, ANA, rebuild control, and rebuild history APIs. It is the main control-plane surface for Mayastor target devices.

Important APIs/types/functions: `NexusService` provides timeout-aware `serialized` locking. Conversion helpers map nexus status, child state/reason, rebuild state/stats/history, NVMe reservation and preemption options, and internal nexus objects to protobuf. Public helpers include `nexus_lookup` and `nexus_destroy`; private `nexus_add_child` validates duplicate URI/device names. RPC methods cover create/destroy/resize/shutdown/list, add/remove/fault child, publish/unpublish, ANA get/set, child operation, rebuild start/stop/pause/resume/state/stats/history/list-history.

Control flow: mutating calls build a `GrpcClientContext`, then `serialized` spawns a Tokio task, optionally takes the global lock, and takes a protected per-nexus lock before reactor submission. `create_nexus` validates name and UUID uniqueness, converts NVMe reservation parameters, stores optional nexus-info key, creates the nexus, generates an event, and returns the converted nexus. List paths can filter by name or UUID. Publish validates 16-byte keys and protocol, then calls `share_ext`.

State and persistence: mutates nexus in-memory/SPDK state, NVMf publication, children, rebuild jobs, ANA state, and rebuild history. `nexus_destroy` removes PTPL files when UUID parsing succeeds but lookup fails.

Dependencies and integration points: integrates internal `nexus`, `ResourceLockManager`, `rpc_submit`, rebuild records, eventing, device-name parsing, `NexusPtpl`, and v1 protobufs.

Risks: repeated lookups after mutation can race if invariants change despite locks; not-found destroy has PTPL side effects; action codes are numeric and invalid actions map to `InvalidKey`; list-history computes a default end time even with empty histories. Test signals should cover duplicate name/UUID rejection, child duplicate detection by URI and device name, publish protocol/key validation, event generation, lock timeout, rebuild history filters, and PTPL cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/nexus.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/pool.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/pool.rs

Purpose: this v1 service implements backend-neutral pool creation, import, listing, export, destroy, grow, error clearing, and disk probing. It abstracts LVS and optional LVM backends behind `PoolFactory`/`PoolOps`.

Important APIs/types/functions: `PoolService` implements `RWSerializer`/`RWLock`; `PoolEncryptionParams` and `util_fetch_secret_params` handle inline or secret-backed encryption keys; `PoolGrpc` wraps a `PoolOps` with a held resource lock; `PoolErrorsNt` builds alert status from bdev error stats and IO-stall state; `pool_to_proto` and `AsyncFrom` map pools to protobuf; `GrpcPoolFactory` selects/list/finds backend factories. `PoolRpc` methods include create/destroy/export/import/list/grow_v2/clear_errors/probe.

Control flow: create/import fetch encryption data before taking the service lock, validate pool type and UUID, take subsystem/resource locks by pool name, ensure no backend already owns the requested pool, then call backend create/import via `spdk_submit!`. Finder locates a pool and locks its name. Listing iterates factories and logs per-backend list failures. Probe parses disk URIs and invokes per-URI probe with import options, collecting structured errors.

State and persistence: mutates pool backend state, may create encrypted crypto vbdev metadata, exports/destroys/imports pools, grows pools, clears error counters, and reads cached `pool_information` state for alert generation.

Dependencies and integration points: integrates `pool_backend`, `secret_provider`, `ResourceLockManager`, encryption types, bdev URI probing, `MayastorEnvironment`, and v1 pool/common protobufs.

Risks: secret retrieval happens outside the service lock and may expose latency; pool locks are by name with TODOs for UUID/disk-content collision; list suppresses backend errors; alert state depends on cached pool info; deprecated `grow_pool` always returns unimplemented. Test signals should cover encryption validation/secret keys, backend feature gating, cross-backend duplicate detection, lock contention, pool alert thresholds, probe error aggregation, and LVM disabled behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/pool.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/replica.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/replica.rs

Purpose: this v1 service implements backend-neutral replica create/destroy/list/share/unshare/resize/entity-id APIs and provides common replica wrappers used by snapshot and test services.

Important APIs/types/functions: `ReplicaService` implements `RWSerializer`/`RWLock`. `GrpcReplicaFactory` lists/finds replicas across backends and maps missing pools to `failed_precondition`. `ReplicaGrpc` wraps `ReplicaOps` and provides `wiper`, `destroy`, `share`, `unshare`, `resize`, `set_entity_id`, and `verify_pool`. Conversion impls map `ReplicaOps` and `LvolSpaceUsage` into v1 protobufs. `filter_replicas_by_replica_type` filters regular replicas, snapshots, and clones.

Control flow: `create_replica` validates protocol, finds the target pool by UUID/name, then delegates to `PoolGrpc::create_replica`. Destroy optionally validates the supplied pool before deleting and tags not-found with `gtm-602` metadata. List builds backend filters from requested pool types and suppresses per-backend list errors. Share/unshare take the pool resource lock, update allowed hosts if already shared, and require NVMf for new shares.

State and persistence: mutates replica lvol/backend state, NVMf sharing, PTPL files via `create_ptpl`, size, and entity id. Wiper setup opens bdev descriptors for destructive test operations but actual wiping is in test service.

Dependencies and integration points: integrates `replica_backend`, `pool_backend`, `GrpcPoolFactory`, `ResourceLockManager`, core bdev/wiper/share traits, and v1 pool/replica protobufs.

Risks: list ignores backend errors; resize has a TODO about missing pool lock; share rejects `Off` while unshare is separate; pool verification uses both name and UUID and returns `aborted` for compatibility. Test signals should cover backend filtering, pool mismatch, NVMf idempotent share property updates, PTPL creation failure, resize semantics, not-found metadata, and snapshot/clone query filtering.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/replica.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/snapshot.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/snapshot.rs

Purpose: this v1 service implements nexus snapshots, replica snapshots, snapshot listing/deletion, clone creation, and clone listing. It reuses `ReplicaService` locks for replica-backed operations and nexus resource locks for nexus-wide snapshots.

Important APIs/types/functions: `SnapshotService` delegates `RWSerializer` to `replica_svc` and has its own `serialized` helper for protected nexus locks. Conversions map nexus snapshot descriptors/statuses, `SnapshotDescriptor` to `SnapshotInfo`, list requests to backend args, and clone requests to list args. `ReplicaGrpc::create_snapshot` prepares replica snapshot config, checks UUID collision, creates the snapshot, and returns descriptor info. `SnapshotGrpc` finds snapshots across factories and verifies pool ownership.

Control flow: `create_nexus_snapshot` locks the nexus, builds `SnapshotParams`, converts requested replica descriptors, calls `nexus.create_snapshot`, and returns done/skipped statuses plus timestamp. Replica snapshot and list/destroy/clone paths run through `spdk_submit!` under replica shared/exclusive locks. Clone creation rejects duplicate clone UUIDs and discarded snapshots before preparing clone config.

State and persistence: creates snapshot lvol metadata, snapshot xattrs/config, clone lvols, and nexus snapshot coordination state. `SNAPSHOT_READY_AS_SOURCE` is currently false in responses.

Dependencies and integration points: integrates internal snapshot traits, `ReplicaFactory`, `GrpcReplicaFactory`, `PoolGrpc`, `nexus_lookup`, `ResourceLockManager`, `UntypedBdev`, and v1 snapshot/replica protobufs.

Risks: `filter_snapshots_by_snapshot_query_type` appears to match `query.invalid` against `valid_snapshot`, which is easy to misread and may be semantically wrong; timestamp parsing defaults silently; snapshot UUID collision only checks bdev UUID globally; list suppresses backend errors. Test signals should cover query filtering, duplicate snapshot/clone UUIDs, discarded snapshot clone rejection, pool verification, nexus lock timeout, skipped replica status mapping, and timestamp/reference-byte fields.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/snapshot_rebuild.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/snapshot_rebuild.rs

Purpose: this v1 service exposes snapshot rebuild job lifecycle and status APIs. It creates jobs that rebuild a replica from a snapshot, lists active jobs, and destroys/stops jobs.

Important APIs/types/functions: `SnapshotRebuildService` stores a `ReplicaService` clone but currently does not lock through it. `create_snapshot_rebuild`, `list_snapshot_rebuild`, and `destroy_snapshot_rebuild` implement the generated RPC trait. `SnapRebuild` pairs an `Arc<SnapshotRebuildJob>` with current `RebuildStats`. Conversion impls map `SnapRebuild` to protobuf, `RebuildState` to rebuild status, and `RebuildError` to tonic statuses.

Control flow: create rejects bitmap requests, returns an existing job idempotently if present, otherwise builds/stores a job, looks it up, starts it, and returns status. List either returns all jobs or looks up a single job keyed by `replica_uuid` field. Destroy looks up a job, force-stops it through either async channel or immediate result, logs the outcome, destroys the job, and returns empty success.

State and persistence: mutates in-memory snapshot rebuild job registry and calls `store()` on creation. It reports stats-derived byte totals and timestamps but has fixed `persisted_checkpoint = 0` and `target_remote = false`.

Dependencies and integration points: integrates `SnapshotRebuildJob`, `RebuildStats`, `RebuildError`, `SnapshotRebuildError`, `spdk_submit!`, and v1 snapshot-rebuild protobufs.

Risks: list filtering uses `replica_uuid` as a lookup key even though create/destroy use job UUID, which may confuse clients; no explicit service/resource locking; bitmap unsupported; persisted checkpoint is not implemented. Test signals should cover idempotent create, bitmap rejection, destroy of running/stopped/missing jobs, byte conversions, state mapping, and lookup semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/snapshot_rebuild.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/stats.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/stats.rs

Purpose: this v1 service reports and resets pool, nexus, and replica I/O statistics while coordinating with pool/replica/nexus locks to avoid concurrent mutation races.

Important APIs/types/functions: `StatsService` stores its own lock plus cloned `PoolService` and `ReplicaService`. It implements `Serializer::locked` for reset operations that take stats write lock, pool/replica read locks, and global resource lock. Helper methods `shared` and `nexus_lock` coordinate read paths. RPCs are `get_pool_io_stats`, `get_nexus_io_stats`, `get_replica_io_stats`, and `reset_io_stats`. Conversion impls map `BdevStats` to `IoStats` and `ReplicaBdevStats` to `ReplicaIoStats`.

Control flow: pool and replica stats take stats read lock plus the corresponding service read lock, list matching backend objects, issue concurrent `stats()` futures via `join_all`, and collect errors. Nexus stats take stats read lock plus global lock, optionally selecting one nexus by name. Reset takes stronger locks and submits a reactor future that iterates every bdev and resets counters.

State and persistence: read calls do not persist; reset mutates in-memory/SPDK bdev I/O counters for all bdevs. Statistics include latency ticks and tick rate.

Dependencies and integration points: integrates `ResourceLockManager`, `GrpcPoolFactory`, `GrpcReplicaFactory`, `nexus`, `UntypedBdev`, `BdevStater`, and v1 stats protobufs.

Risks: pool/replica listing suppresses backend list errors with `unwrap_or_default`, but later stat errors fail the whole response; reset affects all bdevs, not only Mayastor-owned objects; panic logging loses request args in some shared paths. Test signals should cover lock ordering/deadlock, partial stat failures, named and all-object stats, reset side effects, and conversion of latency fields.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/stats.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/test.rs -->
# sources/control-plane/mayastor/io-engine/src/grpc/v1/test.rs

Purpose: this v1 test service exposes non-production operations used by tests and diagnostics: feature discovery, streamed replica wiping, and optional fault injection management.

Important APIs/types/functions: `TestService` wraps a `ReplicaService`. `get_features` advertises wipe methods and CRC32C checksums. `wipe_replica` returns a `ReceiverStream<WipeReplicaResponse>`. `TryFrom<&Option<StreamWipeOptions>>` validates stream wipe options and maps protobuf wipe methods to core wipe methods. `WiperStream` adapts wiper notifications to an mpsc stream. Fault-injection RPCs compile only behind the `fault-injection` feature.

Control flow: `wipe_replica` creates a bounded mpsc channel, parses options before spawning work, then `core::spawn`s an async task that takes the replica service shared lock, optionally verifies the pool, finds a replica allowing snapshots, creates a `Wiper`, wraps it in `StreamedWiper`, runs the wipe, and streams progress via nonblocking `try_send`. Errors are sent to the stream unless the client has disconnected.

State and persistence: wiping destructively changes replica/snapshot data according to the selected method. Fault injection mutates global fault-injection state. No durable metadata is written here.

Dependencies and integration points: integrates core wiper types, replica factory/wrapper, pool verification, `tokio_stream`, optional `core::fault_injection`, and v1 test protobufs.

Risks: destructive API is exposed through gRPC when test service is enabled; backpressure drops into `ChunkNotifyFailed` because `try_send` fails if the buffer fills; options allow methods not advertised by `get_features` if core supports them; fault injection availability changes at compile time. Test signals should cover client disconnect, channel saturation, invalid options, pool mismatch, snapshot wiping allowance, checksum progress, and feature-disabled fault-injection statuses.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/grpc/v1/test.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/host/blk_device.rs -->
# sources/control-plane/mayastor/io-engine/src/host/blk_device.rs

Purpose: this host module implements block-device discovery for gRPC host APIs. It uses udev and mountinfo to return disks/partitions and decide whether each device is available for pool creation.

Important APIs/types/functions: data structs are `Partition`, `FileSystem`, and `BlockDevice`. `Property` conversion impls safely parse optional udev values into strings and numbers. Availability helpers are `usable_device`, `usable_partition`, and `mayastor_device`. Builders are `new_partition`, `new_filesystem`, and `new_device`. Discovery functions are `get_mounts`, `get_disks`, `get_partitions`, and public async `list_block_devices`.

Control flow: `list_block_devices(all)` reads mountinfo, enumerates udev block devices with `DEVTYPE=disk`, gathers child partitions for each disk, builds a disk record with `include = partitions.is_empty()`, then builds partition records. It returns all records when `all` is true or only records marked available. A device is available when included, nonzero size, not Mayastor-presented, allowed major number, acceptable partition type if partitioned, and no filesystem/mount evidence.

State and persistence: read-only. It reflects current kernel/udev/mount state and does not cache. Size is the raw udev `size` attribute value as exposed by the device.

Dependencies and integration points: depends on `udev`, `devinfo::mountinfo`, Mayastor constants identifying internal devices, and host gRPC conversion code in v0/v1 services.

Risks: allowed major numbers are hardcoded and include broad dynamic ranges; filesystem detection depends on udev properties plus mount source matching; partition type allowlist only accepts Linux GPT/MBR IDs; constructing `Vec::new()` inside `unwrap_or` creates a temporary reference pattern that is safe for the call but easy to alter incorrectly; async function performs blocking udev scans. Test signals should use mocked udev/mount data or integration fixtures for disks with partitions, mounted filesystems, Mayastor devices, rotational/bus fields, and `all` filtering.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/host/blk_device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/host/mod.rs -->
# sources/control-plane/mayastor/io-engine/src/host/mod.rs

Purpose: this module is the host subsystem namespace for io-engine. It publicly exposes `blk_device` discovery and `resource` usage modules to gRPC and other callers.

Important APIs/types/functions: it contains only `pub mod blk_device;` and `pub mod resource;`. The important behavior is module visibility, not local logic.

Control flow: none locally. Rust module resolution makes `crate::host::blk_device` and `crate::host::resource` available to v0/v1 gRPC services.

State and persistence: none.

Dependencies and integration points: used by `grpc/v0/mayastor_grpc.rs` and `grpc/v1/host.rs` for block-device listing and process resource usage. Any change here is a public module tree change for the crate.

Risks: removing or privatizing either module breaks host-related gRPC APIs. Test signals are compile-time: host gRPC modules should build and resolve both submodules.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/host/mod.rs -->
