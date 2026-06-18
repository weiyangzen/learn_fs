# subset-b-008248 Research

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/error.rs -->
# sources/object-store/rustfs/crates/ecstore/src/error.rs

Purpose: This file defines the ecstore storage error contract. It aliases `Error` to `StorageError`, provides the crate-local `Result<T>`, enumerates disk, volume, bucket, object, multipart, erasure/quorum, operational, and generic error variants, and translates those variants across disk, file metadata, S3, I/O, RPC, serialization, and storage-admin code boundaries.

Important APIs and types: `StorageError` is the core enum. Its key helpers are `other`, `is_not_found`, `is_quorum_error`, `to_u32`, `from_u32`, and the private `code` mapper to `rustfs_storage_api::StorageErrorCode`. The file implements `From<DiskError>`, `From<StorageError> for DiskError`, `From<BucketMetadataError>`, `From<std::io::Error>`, `From<StorageError> for std::io::Error`, and conversions to and from `rustfs_filemeta::Error`. Public classification and mapping helpers include `is_err_object_not_found`, `is_err_version_not_found`, `is_err_bucket_exists`, `is_err_read_quorum`, `classify_system_path_failure_reason`, `is_err_invalid_upload_id`, `is_err_bucket_not_found`, `is_err_data_movement_overwrite`, `is_err_decommission_running`, `is_err_rebalance_running`, `is_err_operation_canceled`, `is_err_not_initialized`, `is_err_io`, `is_all_not_found`, `is_all_volume_not_found`, `to_object_err`, `is_network_or_host_down`, `error_resp_to_object_err`, and `storage_to_object_err`. `GenericError`, `ObjectApiError`, and `ErrorResponse` model object-layer and S3 response details.

Control flow: Low-level errors enter through `DiskError`, `std::io::Error`, filemeta, serde/RMP/XML/status/UUID/time conversions, or direct construction by storage code. `to_object_err` upgrades disk-volume errors into bucket/object-aware public variants using supplied path parameters and decodes directory object names. `error_resp_to_object_err` maps remote S3 response codes or network strings into `std::io::Error` values wrapping storage/object errors. `storage_to_object_err` currently has a narrow S3 conversion path for `MethodNotAllowed` and otherwise emits a custom S3 error code with the storage error text. Numeric serialization goes through `StorageErrorCode`; `from_u32` reconstructs parameterized variants with default strings because the numeric code only preserves the class.

State and persistence behavior: The file owns no durable state, but it defines stable numeric error codes used across serialization and API boundaries. Equality intentionally ignores payload strings for non-I/O variants by comparing numeric codes, while I/O equality compares kind and message. `Clone` manually preserves variant payloads where possible and reconstructs `std::io::Error` by kind/message. The risk of persistence drift is concentrated in the `StorageErrorCode` contract and in conversion fallbacks that collapse unknown variants into generic I/O errors.

Dependencies and integration points: The module is imported throughout `store`, `set_disk`, `pools`, `bucket`, lifecycle, tier, quota, and RPC-facing paths. It depends on `crate::disk::error::DiskError`, `crate::bucket::error::BucketMetadataError`, `rustfs_storage_api::StorageErrorCode`, `rustfs_filemeta`, `rustfs_lock`, `rustfs_utils::path::decode_dir_object`, and `s3s` S3 error types. `NamespaceLockQuorumUnavailable` is produced by object and set-disk lock code, while lifecycle warm-backend paths use `error_resp_to_object_err`.

Risks: Some conversions are intentionally lossy: unknown disk/filemeta errors become `StorageError::Io`, numeric round trips discard bucket/object/version payloads, and `storage_to_object_err` maps most storage errors to a generic custom S3 code. `is_err_bucket_not_found` treats `VolumeNotFound` and `DiskNotFound` as bucket-not-found equivalents, which is useful in object paths but can hide storage topology differences. `is_all_not_found` and `is_all_volume_not_found` return false on `None`, so callers must pass complete error vectors. Network detection is string based and may miss new transport messages or overmatch unrelated text.

Test signals: The unit tests cover numeric code mapping, invalid-code handling, parity with `StorageErrorCode`, partial equality semantics, decommission/rebalance/cancel helper predicates, not-initialized string detection, system-path failure classification, disk/I/O/filemeta conversion round trips, object and upload error messages, nested I/O downcast recovery, payload-preserving I/O conversion for wrapped variants, and parameterized error message consistency.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/event/mod.rs

Purpose: This is the public event module root for ecstore. It exposes the event compatibility and target bookkeeping submodules under `crate::event`.

Important APIs and types: The file declares `pub mod name`, `pub mod targetid`, and `pub mod targetlist`. It does not define functions or data itself.

Control flow: There is no runtime control flow. Consumers import through paths such as `crate::event::name::EventName`, `crate::event::targetid::TargetID`, and `crate::event::targetlist::TargetList`.

State and persistence behavior: The module root owns no state and persists nothing.

Dependencies and integration points: `event_notification.rs` depends on `targetlist::TargetList`, while lifecycle, replication, and set-disk code use the event notification API that sits beside this module. `name.rs` keeps old `rustfs_ecstore::event::name::EventName` imports working while delegating the canonical enum to `rustfs_s3_types`.

Risks: Because this file only re-exports submodules, the main compatibility risk is removing or renaming one of these module paths. The underlying event implementation is still skeletal, so the module surface can look more complete than the runtime behavior behind it.

Test signals: There are no direct tests for this module root. Compilation of downstream imports is the primary signal.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event/name.rs -->
# sources/object-store/rustfs/crates/ecstore/src/event/name.rs

Purpose: This file preserves the legacy `rustfs_ecstore::event::name::EventName` path while moving the canonical event name definition to `rustfs_s3_types::EventName`.

Important APIs and types: The only public API is `pub use rustfs_s3_types::EventName`.

Control flow: There is no runtime behavior. The Rust compiler resolves imports through this re-export.

State and persistence behavior: The file has no state. Any serialization, parsing, or event-name compatibility behavior lives in `rustfs_s3_types::EventName`, not here.

Dependencies and integration points: Lifecycle and replication paths construct event names such as object-created, object-removed, lifecycle-expiration, and replication events through `EventName`. Keeping the old module path avoids a broad source migration while centralizing the enum in the shared S3 types crate.

Risks: This file can mask changes in the canonical type. If `rustfs_s3_types::EventName` changes variant names, serde behavior, or string formatting, ecstore callers observe that change through this compatibility path. There are no local guards here.

Test signals: There are no local tests. Build success of import sites and tests in `rustfs_s3_types` are the relevant signals.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event/name.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event/targetid.rs -->
# sources/object-store/rustfs/crates/ecstore/src/event/targetid.rs

Purpose: This file defines a minimal target identifier type for event notification targets. It appears to be an early or compatibility scaffold for MinIO-style target IDs.

Important APIs and types: `TargetID` stores private `id: String` and `name: String` fields. Its only method is a private inherent `to_string(&self) -> String` that formats `id:name`.

Control flow: There is no external construction or dispatch logic in this file. Formatting is a simple string interpolation when the private method is called inside the module, though no current target file calls it.

State and persistence behavior: `TargetID` is an in-memory value only. It derives no `Clone`, `Debug`, `Eq`, `Hash`, or serde traits, so it is not currently usable as the active map key hinted by commented code in `targetlist.rs`.

Dependencies and integration points: `targetlist.rs` imports `TargetID` and uses it in an unused private `TargetIDResult` struct. The commented target map in `TargetList` suggests future integration with concrete event targets and per-target stats.

Risks: The inherent `to_string` method is private and does not implement `Display`, so callers cannot use standard formatting or `ToString`. Private fields and lack of constructor make the type impossible to construct outside this module. If it becomes a hash-map key, it will need equality and hash implementations plus careful parsing rules for IDs or names containing `:`.

Test signals: There are no tests. Current compile success only proves that the unused scaffold type is syntactically valid.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event/targetid.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event/targetlist.rs -->
# sources/object-store/rustfs/crates/ecstore/src/event/targetlist.rs

Purpose: This file defines the runtime counter shell for notification targets. It is currently a partial implementation: counters exist, while concrete target storage, queues, and target stats are commented out.

Important APIs and types: `TargetList` has public atomic counters `current_send_calls`, `total_events`, `events_skipped`, and `events_errors_total`, all `AtomicI64`. `TargetList::new` returns the default value. Private unused structs `TargetStat` and `TargetIDResult` sketch per-target counters and target-result error reporting.

Control flow: There is no send, add, remove, or queueing logic here. The only active flow is constructing zeroed atomics via `Default`.

State and persistence behavior: The counters are process-local atomics, intended for concurrent notification metrics. They are not persisted and are currently only read by `EventNotifier::get_arn_list` for a warning log count. No code in this file increments them.

Dependencies and integration points: `EventNotifier` embeds a `TargetList`. The file imports `TargetID` for the private result struct and has comments for a future `HashMap<TargetID, Target>`, async event queue, and `HashMap<TargetID, TargetStat>`.

Risks: The public counters can be modified by external code if the `TargetList` is visible, but there is no API-level invariant tying them to actual dispatch. Because target storage is commented out, reporting based on these counters can imply notification support that does not exist. The private stat/result structs are unused and may drift from any eventual target implementation.

Test signals: There are no local tests. The only indirect signal is `event_notification` construction and dispatch-hook tests, which do not touch target counters.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event/targetlist.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event_notification.rs -->
# sources/object-store/rustfs/crates/ecstore/src/event_notification.rs

Purpose: This file provides the ecstore event notification facade. The full notifier methods are mostly no-op stubs that log warnings, while the active dispatch path is a global one-shot hook used by `send_event`.

Important APIs and types: `EventNotifier::new` returns `Arc<RwLock<EventNotifier>>` with an embedded `TargetList`. Private methods `get_arn_list`, `set`, `init_bucket_targets`, and `send` currently log not-implemented warnings and either return empty values or `Ok(())`. `EventArgs` carries `event_name`, `bucket_name`, `ObjectInfo`, request parameters, response elements, host, and user agent. `EventDispatchHook` is `Arc<dyn Fn(EventArgs) + Send + Sync + 'static>`, stored in `EVENT_DISPATCH_HOOK: OnceLock<_>`. Public functions `register_event_dispatch_hook` and `send_event` are the active API.

Control flow: Callers construct `EventArgs` at object, lifecycle, replication, and restore points and call `send_event`. If a hook has been registered, `send_event` invokes it synchronously and returns. If no hook exists, the event is dropped after a warning. `register_event_dispatch_hook` succeeds only once because `OnceLock::set` rejects subsequent hooks. The `EventNotifier` instance in global/store state is not used by `send_event`.

State and persistence behavior: The only active mutable state is the process-global hook. It is not resettable, which affects test isolation and embedding. `EventArgs` is transient and no events are persisted or queued. `TargetList` counters are present but not incremented by `send_event`.

Dependencies and integration points: `global.rs` creates `GLOBAL_EventNotifier`, and `store/init.rs` passes it into `ECStore`. `set_disk.rs`, lifecycle operations, and replication resyncer call `send_event` for object restore, lifecycle deletion, tiering, and replication notifications. `EventArgs` depends on `ObjectInfo`; notifier stubs reference `BucketMetadata` and `ECStore`.

Risks: In the default build, events are dropped unless an external hook is registered before use. The hook is one-shot and cannot be unregistered or replaced, which can make tests order-dependent and makes runtime reconfiguration difficult. Synchronous hook execution means a slow or panicking hook directly affects the caller. The private no-op `EventNotifier` methods can mislead integration code expecting bucket rules or target ARNs to work.

Test signals: A unit test registers a hook that increments an atomic counter and verifies `send_event` dispatches once. It deliberately tolerates the one-shot global by ignoring registration failure and comparing the counter before and after the send.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/event_notification.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/global.rs -->
# sources/object-store/rustfs/crates/ecstore/src/global.rs

Purpose: This file centralizes ecstore process-wide configuration and singleton handles: object store, endpoint layout, erasure-mode flags, local disk maps, lifecycle/tier/event systems, boot and region metadata, lock clients, bucket monitor, and background-service cancellation.

Important APIs and types: Constants define disk safety assumptions: `DISK_ASSUME_UNKNOWN_SIZE`, `DISK_MIN_INODES`, `DISK_FILL_FRACTION`, and `DISK_RESERVE_FRACTION`. Global handles include `GLOBAL_OBJECT_API`, `GLOBAL_IsErasure`, `GLOBAL_IsDistErasure`, `GLOBAL_IsErasureSD`, local disk maps, `GLOBAL_Endpoints`, `GLOBAL_TierConfigMgr`, `GLOBAL_LifecycleSys`, `GLOBAL_EventNotifier`, `GLOBAL_BOOT_TIME`, node-name constants, `GLOBAL_REGION`, local and distributed lock clients, and `GLOBAL_BUCKET_MONITOR`. Public APIs set/get the RustFS port, deployment ID, endpoints, erasure flags, tier manager, object layer and resolver, region, background cancellation token, lock clients, and bucket monitor.

Control flow: Initialization code calls setters such as `set_global_endpoints`, `set_object_layer`, `set_global_region`, `set_global_lock_client`, and `init_global_bucket_monitor`. Read paths call getters that either clone initialized values or return defaults. `resolve_object_store_handle` first consults an optional custom resolver and falls back to `GLOBAL_OBJECT_API`. `update_erasure_type` writes three async `RwLock<bool>` flags based on the endpoint `SetupType`, setting distributed erasure as a subtype of erasure. `create_background_services_cancel_token` creates and installs a `CancellationToken`; `shutdown_background_services` cancels it if present.

State and persistence behavior: Most state is in-memory singleton state guarded by `OnceLock`, `OnceCell`, `RwLock`, or `Arc`. `OnceLock` values are one-time initializations; repeated setters usually panic, return an error, or are ignored with a warning depending on the API. No durable persistence happens here, but global deployment ID, endpoints, and object-store handles are authoritative runtime state used by admin, storage, metrics, and background services.

Dependencies and integration points: This module wires together `ECStore`, `DiskStore`, endpoint pools, `LifecycleSys`, `TierConfigMgr`, `EventNotifier`, bucket bandwidth `Monitor`, `rustfs_lock::LockClient`, `CancellationToken`, `s3s::region::Region`, `uuid::Uuid`, and `lazy_static`. `lib.rs` re-exports endpoint, erasure, object-layer, and lock-client APIs. `metrics_realtime`, `notification_sys`, admin server info, store initialization, pools, lifecycle, and tiering rely on these globals.

Risks: Global one-shot setters make test isolation and restart-in-process scenarios difficult. Some setters panic on reinitialization while `init_global_bucket_monitor` only warns, so caller expectations differ by API. `GLOBAL_LocalNodeName` is statically set to `127.0.0.1:9000` while other RustFS address globals come from `rustfs_common`, so node-name consistency must be managed elsewhere. `resolve_object_store_handle` can return `None`; callers must handle uninitialized object-store state. The sequential writes in `update_erasure_type` briefly expose intermediate flag combinations to concurrent readers.

Test signals: This file has no direct tests. Indirect signals come from store initialization, metrics collection, notification system, lock paths, lifecycle/tier tests, and any tests that re-export and call the global APIs.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/global.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/lib.rs -->
# sources/object-store/rustfs/crates/ecstore/src/lib.rs

Purpose: This is the ecstore crate root. It declares the crate's public module tree, hides selected implementation modules, and re-exports key global and storage traits for downstream crates.

Important APIs and types: Public modules include admin, batch processing, bitrot, bucket, cache, compression, config, data usage, disk, layout, endpoints, erasure coding, error, global, realtime metrics, notification system, pools, rebalance, RIO, RPC, set-disk, store, store API, list objects, store utils, client, event, event notification, and tier. Private modules include `data_movement`, `sets`, and `store_init`. Re-exports include `set_global_endpoints`, `update_erasure_type`, lock-client getters/setters, `new_object_layer_fn`, `resolve_object_store_handle`, `set_object_store_resolver`, `GLOBAL_Endpoints`, and `StorageAPI`.

Control flow: There is no runtime control flow outside test code. The crate root determines which modules compile into the public API and which names are available from `rustfs_ecstore::*`.

State and persistence behavior: The file owns no state. It exposes stateful global APIs from `global.rs`.

Dependencies and integration points: The module declarations bind together the ecstore object-store stack. The event, metrics, notification, error, and global files in this work item are all public modules through this root. The `rio_tests` module checks feature-selected backend identity via `crate::rio::backend_name()`.

Risks: `#![allow(dead_code)]` at the crate root can hide unused public or private scaffolding, including partial event-notification structures. Public module declarations are compatibility commitments; renaming or privatizing modules affects external crates. Feature-dependent RIO behavior is guarded only by a small backend-name test here.

Test signals: The root-level test `uses_expected_rio_backend` asserts that the selected RIO backend name matches the `rio-v2` feature flag. Broader compile and integration tests validate module visibility and re-export correctness.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/metrics_realtime.rs -->
# sources/object-store/rustfs/crates/ecstore/src/metrics_realtime.rs

Purpose: This file collects and translates local realtime metrics for admin APIs. It supports disk, scanner, internode network, and RPC metrics today, while defining flags for additional OS, batch, site resync, memory, and CPU metrics.

Important APIs and types: `CollectMetricsOpts` carries host filters, disk filters, job ID, and deployment ID. `MetricType` is a bitflag-like wrapper with constants `NONE`, `SCANNER`, `DISK`, `OS`, `BATCH_JOBS`, `SITE_RESYNC`, `NET`, `MEM`, `CPU`, `RPC`, and `ALL`. `collect_local_metrics` is the public collector. `collect_local_disks_metrics` gathers disk details from `StorageAdminApi::local_storage_info`. `to_madmin_scanner_metrics` maps `rustfs_common::metrics::ScannerMetricsReport` into `rustfs_madmin::metrics::ScannerMetrics`, including last-minute action/ILM maps, pacing, lifecycle transition, maintenance control, checkpoint, source work, and distributed scan status fields.

Control flow: `collect_local_metrics` returns an empty `RealtimeMetrics` for `MetricType::NONE`. It chooses a host label from `GLOBAL_RUSTFS_ADDR`, the local server property, and `GLOBAL_LOCAL_NODE_NAME`, and returns empty metrics if a non-empty host filter does not include this node. For disk metrics, it aggregates per-disk metrics from the object-store handle into `by_disk` and merged `aggregated.disk`. For scanner metrics, it snapshots `global_metrics().report()`, optionally overwrites `current_started` with global init time, and translates it to madmin format. NET and RPC metrics use `global_internode_metrics().snapshot()` to synthesize internode counters. The function finally writes the aggregate under `by_host` and pushes the host into `hosts`.

State and persistence behavior: The module persists nothing. It reads live global state from the object-store resolver, RustFS address/name locks, scanner metrics, internode metrics, and storage admin snapshots. Disk metrics include offline synthetic entries for drives whose state is neither `Ok` nor `Unformatted`, plus healing counts, lifetime operation maps, last-minute operation maps, and Linux drive I/O stats when available.

Dependencies and integration points: It integrates `admin_server_info::get_local_server_property`, `resolve_object_store_handle`, `rustfs_common` globals and scanner metrics, `rustfs_io_metrics` internode counters, `rustfs_madmin::metrics` DTOs, `rustfs_storage_api::StorageAdminApi`, `rustfs_utils::os::get_drive_stats`, chrono timestamps, and tracing. `notification_sys::get_metrics` fans this collector out across peers through RPC clients.

Risks: `MetricType::contains` treats `NONE` as contained by every flag set because zero bits always match; tests currently assert that behavior for `ALL`. Disk metrics silently return an empty map if the object store is not initialized. Host filtering depends on endpoint string equality and special handling for addresses beginning with `:`, which can misclassify nodes if endpoint formats differ. OS, batch, site-resync, memory, and CPU flags are defined but not implemented. RPC connected state is inferred from last dial timestamp and some stream/queue fields are fixed at zero.

Test signals: Tests validate bitflag behavior, NET/RPC metrics generated from internode counters, scanner mapping of partial-source status, pacing pressure, lifecycle transition status, maintenance control status, and a broad set of distributed scanner status/checkpoint/source-work fields. These tests are strong mapping-contract guards but do not cover disk metrics with a real store.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/metrics_realtime.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/notification_sys.rs -->
# sources/object-store/rustfs/crates/ecstore/src/notification_sys.rs

Purpose: This file implements the cluster notification/admin fan-out system for ecstore. It creates peer REST clients, broadcasts configuration and identity changes, gathers peer admin health and metrics, coordinates rebalance/pool metadata notifications, and provides cached fallbacks for peer storage/server info during transient failures.

Important APIs and types: `GLOBAL_NotificationSys` is a `OnceLock<NotificationSys>`, initialized by `new_global_notification_sys` and read by `get_global_notification_sys`. `NotificationSys` stores `peer_clients`, `all_peer_clients`, and per-peer `Mutex<PeerAdminCache>`. `PeerAdminCache` keeps last successful `StorageInfo` and `ServerProperties` plus independent failure counters. `NotificationPeerErr` reports per-peer host and optional `Error`. Public methods include `rest_client_from_hash`, policy/user/group/service-account load/delete methods, dynamic config reloads, config snapshot refresh, `storage_info`, `server_info`, `reload_pool_meta`, `load_rebalance_meta`, `stop_rebalance`, `load_bucket_metadata`, `delete_bucket_metadata`, profiling, health probes, `get_metrics`, site replication reload, and transition-tier config load.

Control flow: `NotificationSys::new` builds peer clients from endpoint pools and allocates one admin cache per active peer client. Most fan-out methods build one future per peer, call the matching `PeerRestClient` method through `join_all`, and return either a vector of `NotificationPeerErr` or default DTOs for unreachable peers. `storage_info` and `server_info` wrap peer calls in five-second timeouts, evict timed-out connections, update caches on success, and call failure handlers on errors/timeouts. `storage_info` also appends local storage info and backend info from the provided local `StorageAdminApi`. Rebalance and metadata reload methods aggregate peer failures into a single `Error`. `stop_rebalance` additionally requires a local object store, fans out peer stop requests, stops the local store, and saves local rebalance stopped-at stats.

State and persistence behavior: Runtime state consists of peer client pools and per-peer admin caches. Cache success resets only the matching storage or server failure counter. On failure, cached data is returned before `CONSECUTIVE_FAILURE_THRESHOLD` is reached; after three consecutive failures, storage info synthesizes offline disks and server info synthesizes offline server properties using endpoint metadata, boot-time uptime, and commit ID. Rebalance stop persists local rebalance stats through the object store. Other methods mostly trigger remote peers to reload or delete their own persisted metadata/config state.

Dependencies and integration points: The module integrates `PeerRestClient`, global endpoints and boot time, object-store resolution, `StorageAdminApi`, rebalance save options, madmin health/metrics/net DTOs, futures `join_all`, Tokio timeouts, and tracing. `admin_server_info` uses `get_global_notification_sys` for cluster-wide views, `pools` uses it for pool/rebalance metadata coordination, and metrics RPCs use `CollectMetricsOpts` and `MetricType`.

Risks: `new_global_notification_sys` currently ignores the `OnceLock::set` error after mapping it and always returns `Ok(())`, so duplicate initialization can be silently accepted by callers even though the global was not replaced. Most simple fan-out methods report unreachable peers in-band rather than failing the whole operation; callers must inspect every `NotificationPeerErr`. Health probe methods default failed calls to default structs, which can hide errors unless the caller has separate reachability checks. The cache can temporarily serve stale admin data, intentionally trading freshness for stability; after threshold, offline disk synthesis depends on endpoint host matching. `rest_client_from_hash` uses `DefaultHasher`, so hash-to-peer stability is only process/build scoped, not a durable sharding contract.

Test signals: Tests cover timeout helper success/error/timeout behavior, aggregate failure formatting, unreachable peer handling for bucket metadata and transition-tier config, storage-info cache first-failure behavior, cached data on transient failure, offline transition after threshold, server-info cached/initializing/offline fallbacks, independent storage/server counters, poisoned cache mutex recovery paths, and success updates after poisoned locks.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/notification_sys.rs -->
