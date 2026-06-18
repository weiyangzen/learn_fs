# Research: subset-b-008256

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/init.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store/init.rs

## Purpose
This file owns `ECStore` construction and post-construction initialization. It converts endpoint pool topology into initialized disk handles, validates/loads erasure format metadata, builds `Sets` pools, publishes global local-disk and deployment identity state, loads pool/rebalance metadata, and starts background store services such as lifecycle expiry, stale multipart cleanup, transition state, tiering migration, and optional decommission resume.

## Important APIs, Types, And Functions
- `ECStore::new(address, endpoint_pools, ctx) -> Result<Arc<Self>>` is the high-level constructor. It initializes peer identity, disks, storage formats, `Sets`, global local disk maps, `S3PeerSys`, `PoolMeta`, decommission cancelers, and global object layer publication.
- `ECStore::init(&Arc<Self>, rx) -> Result<()>` performs second-stage initialization after the `ECStore` is built: rebalance metadata load/start, pool metadata load/validation/save, resumable decommission scheduling, bucket monitor setup, lifecycle/tiering background routines, and tier manager initialization.
- `pool_first_endpoint_is_local` and `should_resume_local_decommission` protect startup ownership decisions so expansion/decommission work is resumed only by the node owning the first endpoint in the relevant pool.
- `resume_local_decommission_after_init` waits and retries decommission resume, handling `ConfigNotFound` with a bounded retry loop and restarting workers if the decommission state is already running.
- `resolve_store_init_stage_result` wraps stage-specific failures with startup context.
- `single_pool` is a small predicate used throughout store handlers.

## Control Flow
`ECStore::new` first derives host/port from the socket address or global config and calls `init_local_peer`. For each endpoint pool it computes/validates parity, initializes disks with cleanup and health checks enabled but not started, checks fatal disk errors, then retries `connect_load_init_formats` up to ten times with exponential backoff. On each format retry it listens for Ctrl-C and resets disk health so reused disk handles can reconnect to peers that came online later. After formats load, health checks are enabled, deployment IDs are verified across pools, local disks are collected, and `Sets::new` builds each pool.

Once pools are assembled, non-distributed deployments publish local disk path mappings. The constructor builds `ECStore`, conditionally publishes the global deployment ID, retries `ec.init(ctx)` up to a local budget, publishes the object layer, attaches any global bucket monitor, and returns the shared store.

`ECStore::init` is stage-oriented. It records boot time, loads rebalance metadata, starts rebalance if metadata exists, loads pool metadata from the first pool, validates it against current pools, and either installs the loaded metadata or creates/saves a repaired `PoolMeta`. Only the first local cluster node persists validated pool metadata to avoid distributed startup races. It then resolves resumable decommission pool command lines against current endpoints, schedules a delayed local resume task if the first resumable pool is local, initializes bucket/lifecycle/tiering background systems, and logs rather than fails tier manager init errors.

## State And Persistence Behavior
The file persists or updates several pieces of cluster state:
- Erasure format metadata is loaded from disks and deployment IDs are validated across pools. Nil deployment IDs are replaced with a new UUID.
- Global deployment ID is set once if missing.
- `GLOBAL_LOCAL_DISK_MAP` is populated in non-distributed mode from local disk endpoint strings.
- `PoolMeta` is loaded from storage, validated, and sometimes saved back through `PoolMeta::save` when topology metadata requires repair.
- `rebalance_meta` is loaded into an `RwLock<Option<_>>` and can trigger rebalance startup.
- Decommission state is not directly persisted here, but resumable decommission pools from `PoolMeta` can cause delayed calls into `decommission` and `spawn_decommission_routines`.
- Background lifecycle, stale multipart cleanup, transition, tier migration, and tier manager initialization establish long-running runtime state.

## Dependencies And Integration Points
The module depends on endpoint topology, disk initialization, erasure format loading, storage class parity validation, pool metadata, global object layer state, bucket monitor globals, tiering config, lifecycle modules, `S3PeerSys`, `Sets`, tracing, Tokio timing/signal handling, and cancellation tokens. It is the bridge between raw endpoint configuration and all higher-level `ECStore` object/list/multipart/rebalance handlers.

## Risks And Edge Cases
- Startup behavior is heavily global-state-dependent; ordering mistakes can affect local disk maps, deployment ID publication, bucket monitor, and object layer visibility.
- Format loading retries reuse disk handles and must reset transient health markers; without that, temporary peer failures can become sticky.
- Pool metadata repair is persisted by only one local node, which reduces races but depends on correct `is_first_cluster_node_local` behavior.
- Decommission resume is delayed and bounded, but it clones cancellation tokens and pool indices into a detached task; shutdown correctness depends on token propagation.
- `ECStore::new` retries `init` with a fixed counter and returns a broad `other` error after exhaustion, so callers lose detailed final-stage error typing.
- Several local disk collection paths use unwrap after checking `is_some`; safe today but sensitive to refactoring.

## Test Signals
The file contains focused unit tests for decommission resume ownership, missing pool/endpoint error messages, retry policy for `ConfigNotFound`, stage error wrapping, cancellable delay behavior, and `pool_first_endpoint_is_local` behavior for expansion pools where the global first endpoint is remote but the new pool's first endpoint is local. These tests cover recent startup/decommission regression boundaries, but no full `ECStore::new` integration test is present.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/init.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/list.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store/list.rs

## Purpose
This file is a thin `ECStore` list/walk façade. It exposes store-level handler methods for S3 object listing, object version listing, and internal walking, forwarding requests to lower-level internal implementations while keeping the public handler surface in the `store` module cohesive.

## Important APIs, Types, And Functions
- `handle_list_objects_v2(self: Arc<Self>, ...) -> Result<ListObjectsV2Info>` delegates to `inner_list_objects_v2`.
- `handle_list_object_versions(self: Arc<Self>, ...) -> Result<ListObjectVersionsInfo>` delegates to `inner_list_object_versions`.
- `handle_walk(self: Arc<Self>, rx, bucket, prefix, result, opts) -> Result<()>` delegates to `walk_internal`.
- The handlers traffic in `ListObjectsV2Info`, `ListObjectVersionsInfo`, `ObjectInfoOrErr`, `WalkOptions`, and `CancellationToken` from surrounding modules.

## Control Flow
There is no additional branching or storage selection logic here. Each handler is instrumented where appropriate and immediately awaits its corresponding inner operation with the same arguments. `handle_walk` passes the cancellation token and result channel through so the underlying walker owns traversal and streaming.

## State And Persistence Behavior
This file does not mutate persistent state directly. Listing and walking behavior, metadata reads, version selection, cache usage, and object emission are all controlled by the delegated inner implementations. Its state impact is limited to async call boundaries and tracing spans.

## Dependencies And Integration Points
The module depends entirely on `super::*` for `ECStore`, result types, options, and inner methods. It integrates the object-store API layer with the internal list/walk engines and likely participates in trait implementations or higher-level S3 handlers through `ECStore` methods.

## Risks And Edge Cases
- Because this is a pass-through layer, most correctness risks live in the inner methods. The local risk is argument drift if handler signatures evolve independently from inner functions.
- `fetch_owner`, delete inclusion, continuation markers, version markers, and delimiters are all passed through without validation here; validation must be enforced downstream.
- `handle_walk` relies on the downstream implementation to honor cancellation and handle backpressure on the `mpsc::Sender`.

## Test Signals
No tests are defined in this file. Coverage must come from tests of `inner_list_objects_v2`, `inner_list_object_versions`, `walk_internal`, or higher-level S3 list/walk API tests. A simple delegation unit test would have little value unless mocks are introduced; integration tests should verify marker/delimiter/version behavior.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/list.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/multipart.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store/multipart.rs

## Purpose
This file implements `ECStore` multipart-upload handlers. It validates multipart arguments, routes operations to the correct erasure pool, handles multi-pool lookup by skipping suspended pools and invalid upload IDs, chooses a pool for new uploads, and delegates part/list/abort/complete operations to `Sets`.

## Important APIs, Types, And Functions
- `handle_list_object_parts` validates list-parts input, then finds the pool containing the upload ID.
- `handle_list_multipart_uploads` validates list-multipart input and merges uploads from all non-suspended pools in multi-pool deployments.
- `handle_new_multipart_upload` and `handle_new_multipart_upload_with_pool_idx` create a new upload and return the selected pool index for callers that need it.
- `handle_put_object_part`, `handle_get_multipart_info`, `handle_abort_multipart_upload`, and `handle_complete_multipart_upload` scan pools until the upload ID is found, returning the first non-invalid-upload error.
- `handle_copy_object_part` is present but returns `StorageError::NotImplemented`.

## Control Flow
All handlers short-circuit to `self.pools[0]` for single-pool deployments. In multi-pool mode:
- Read/update operations over an existing upload iterate pools in order, skip suspended pools, and treat `InvalidUploadID` as "try the next pool".
- Non-`InvalidUploadID` errors are returned immediately so real disk/quorum failures are not hidden.
- If no pool has the upload, handlers return `StorageError::InvalidUploadID(bucket, object, upload_id)`.
- `handle_list_multipart_uploads` is different: it queries all non-suspended pools and concatenates upload entries into one `ListMultipartsInfo`.
- `handle_new_multipart_upload_with_pool_idx` first looks for existing uploads for the same object in non-suspended, non-rebalancing pools and creates the new upload in that pool if found. Otherwise it calls `get_pool_idx` to select a target by object key and capacity. During data movement it rejects creating a target upload in the source pool.

## State And Persistence Behavior
Persistent multipart state lives in pool/set implementations. This file controls which pool receives mutations:
- New uploads create upload metadata in one selected pool.
- `put_object_part` stores part data in the pool owning the upload ID.
- Abort removes upload state in the owning pool.
- Complete finalizes multipart state into an object via the owning pool.
- List operations aggregate transient metadata views and do not persist state.

## Dependencies And Integration Points
The module depends on argument checkers such as `check_list_parts_args`, multipart result types, `ObjectOptions`, `PutObjReader`, pool suspension/rebalance state, upload ID error classifiers, `MAX_UPLOADS_LIST`, and pool selection methods from `rebalance.rs`. It integrates S3 multipart APIs with erasure pool placement and data movement safeguards.

## Risks And Edge Cases
- Namespace locking is marked TODO for list parts and not implemented locally for other multipart operations; correctness depends on lower-level pool/set locking.
- `handle_list_multipart_uploads` concatenates uploads from all pools but does not sort, truncate, deduplicate, or compute continuation state across pools, which can affect S3 marker semantics in multi-pool deployments.
- `handle_new_multipart_upload_with_pool_idx` calls `list_multipart_uploads(bucket, object, ...)` using the object as prefix to detect existing uploads; broad prefix matching could be surprising if lower layers do not enforce exact object matching.
- `handle_copy_object_part` is not implemented, so multipart copy workflows relying on UploadPartCopy will fail.
- `handle_put_object_part` passes a single mutable reader through sequential pool attempts; if a pool consumes bytes before returning an `InvalidUploadID`-classified error, later attempts may see a partially consumed stream. The expected lower-layer behavior should be verified.
- Data movement rejects source-pool overwrites only at new-upload selection time; subsequent part/complete paths rely on upload placement.

## Test Signals
No tests are defined in this file. Current signal is through shared error classifiers and higher-level multipart integration tests, if present. High-value tests would cover multi-pool invalid-upload fallback, suspended/rebalancing pool skips, data-movement source-pool rejection, list aggregation ordering/limits, and the unimplemented copy-part API contract.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/multipart.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/object.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store/object.rs

## Purpose
This file implements the core `ECStore` object operations: GET reader/info, PUT, COPY, DELETE, batch delete, tags, metadata, transition/restore, data movement/decommission handling, and object-integrity verification. It also wraps namespace-lock acquisition with diagnostics and adapts multi-pool object placement to versioning, delete markers, rebalance, decommission, and tiered-object workflows.

## Important APIs, Types, And Functions
- `LockGuardedReader` keeps a read namespace lock alive while a `GetObjectReader` stream is consumed and releases it after EOF when lock optimization is disabled.
- `ObjectLockDiagMode` and `ObjectLockDiagGuard` record lock hold/acquire metrics and warn when thresholds are exceeded.
- `acquire_object_write_lock_if_needed` / `acquire_object_read_lock_if_needed` create namespace locks through `handle_new_ns_lock`, map quorum failures to `StorageError::NamespaceLockQuorumUnavailable`, set `opts.no_lock = true`, and return diagnostic guards.
- `select_data_movement_pool_idx`, `find_data_movement_target_info`, `has_equivalent_data_movement_delete_marker`, and `has_equivalent_data_movement_tiered_object` protect decommission/data-movement resume semantics.
- `decommission_tiered_object` relocates metadata for already transitioned objects during pool decommission.
- `handle_get_object_reader`, `handle_get_object_info`, `handle_put_object`, `handle_copy_object`, `handle_delete_object`, and `handle_delete_objects` are the primary object API handlers.
- Metadata/tag/transition helpers include `handle_add_partial`, `handle_transition_object`, `handle_restore_transitioned_object`, `handle_put_object_metadata`, `handle_get_object_tags`, `handle_put_object_tags`, `handle_delete_object_version`, `handle_delete_object_tags`, and `handle_verify_object_integrity`.

## Control Flow
Object names are normalized through `encode_dir_object` before pool calls and decoded for returned user-visible names where needed. Single-pool deployments usually delegate directly to `self.pools[0]`. Multi-pool deployments first locate the latest accessible object or choose a target pool:
- GET reader/info acquires a read lock unless `opts.no_lock`, finds the latest object across pools, rejects delete markers with S3-like not-found/method-not-allowed semantics, applies preconditions for info, and delegates to the selected pool.
- PUT validates arguments, encodes directory objects, selects a target by existing object/data-movement logic or capacity, rejects data movement writes that would land back in the source pool, then delegates to the chosen pool.
- COPY handles same-source/destination specially. Same object/version metadata copies stay in the existing pool. Non-versioned self-copy of transitioned objects may restore by writing from `put_object_reader`. Other copies choose a destination pool and write through `put_object`.
- DELETE handles prefix deletes separately, acquires a write lock for exact deletes, performs data-movement-specific target selection/resume checks when requested, otherwise locates the pool containing the object. For non-versioned deletes with multiple candidate pools/read-quorum signals it can call `delete_object_from_all_pools`; otherwise it scans pools and ignores not-found/version-not-found until a delete succeeds.
- Batch delete currently broadcasts the full encoded object list to every pool, then for each object picks the first successful found deletion or the first recorded error/result.
- Transition, restore, tags, and metadata update operations find the latest accessible pool and delegate.

## State And Persistence Behavior
Persistent object data and metadata are written by the pool/set layers, but this file determines placement, locking, and cross-pool mutation semantics:
- Writes and deletes mutate the selected erasure pool.
- Batch deletes mutate all pools and reconcile per-object results after the fact.
- Data movement paths avoid overwriting source-pool versions and allow idempotent resume when an equivalent target delete marker or transitioned object already exists.
- `opts.metadata_chg` is set for version-aware lookups and metadata updates so lower layers preserve version IDs instead of coercing to latest lookups.
- Read locks can be held until stream EOF to preserve atomic-read semantics unless lock optimization is enabled.
- `verify_object_integrity` drains a GET reader stream to `tokio::io::sink`, exercising the read path without storing the object in memory.

## Dependencies And Integration Points
The file integrates with namespace locking (`rustfs_lock`), object lock diagnostics metrics (`rustfs_io_metrics`), storage class/data movement pool selection from `rebalance.rs`, object and file metadata types from `rustfs_filemeta`, lifecycle/tiering transition types, HTTP headers and range specs, object option precondition checks, erasure pool methods, error classifiers, directory-object encoding/decoding, and async I/O traits. It is one of the main consumers of `get_latest_object_info_with_idx`, `get_pool_info_existing_with_opts`, `get_pool_idx`, and `delete_object_from_all_pools`.

## Risks And Edge Cases
- Batch delete has a TODO for namespace locks and currently broadcasts all deletes to all pools, which may be expensive and has more mutation surface than targeted deletes.
- `handle_delete_object_version` is not implemented for multi-pool deployments.
- `handle_copy_object` relies on `src_info.put_object_reader` for data-copy paths and returns `InvalidArgument` if absent; callers must prepare the reader.
- Lock guard lifetime differs based on `ENV_OBJECT_LOCK_OPTIMIZATION_ENABLE`; readers must be drained or dropped promptly to avoid long lock holds.
- Delete marker semantics are intentionally split: low-level latest lookup can return delete markers, while higher-level access converts them to errors. New callers must use the correct helper.
- Data movement resume equivalence checks compare version, mod time, etag/checksum/transition fields; missing or inconsistent metadata can cause safe but disruptive overwrite errors.
- Several TODO/commented paths indicate incomplete lock optimization/batch-delete redesign.

## Test Signals
The file has extensive unit tests around data movement target selection, delete-marker equivalence and resume, tiered-object equivalence and resume, latest-object delete-marker access semantics, contextual decommission error wrapping, version-aware lookup option construction, data movement skip flags, and lock-guard behavior with optimization disabled. The lock tests verify that read locks block writers until reader drop or EOF. Integration coverage is still needed for full multi-pool object placement, copy, batch delete, and transition/restore flows.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/object.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/peer.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store/peer.rs

## Purpose
This file handles local disk discovery, local disk ID caching, lock-client initialization, local peer naming, disk information collection, and capacity checks used by `ECStore` startup and placement decisions. It is the local-node hardware/topology utility layer for store initialization and admin/storage introspection.

## Important APIs, Types, And Functions
- `find_local_disk` looks up a `DiskStore` by endpoint/path in `GLOBAL_LOCAL_DISK_MAP`.
- `find_local_disk_by_ref` resolves either an endpoint/path or disk UUID, using and prewarming `GLOBAL_LOCAL_DISK_ID_MAP`.
- `get_disk_via_endpoint` maps an `Endpoint` to a disk through `GLOBAL_LOCAL_DISK_SET_DRIVES` when populated, falling back to endpoint string lookup.
- `all_local_disk_path`, `all_local_disk`, and `prewarm_local_disk_id_map` enumerate local disks and cache UUID-to-path mappings.
- `init_local_disks(endpoint_pools)` constructs `DiskStore`s for local endpoints and fills global path and pool/set/disk-index maps.
- `init_lock_clients(endpoint_pools)` creates local or remote namespace-lock clients per unique host:port and publishes global lock client maps.
- `init_local_peer(endpoint_pools, host, port)` sets `GLOBAL_LOCAL_NODE_NAME`.
- `get_disk_infos` gathers `DiskInfo` from available disks.
- `has_space_for` enforces usable-capacity and inode guards for an erasure set.

## Control Flow
Local disk lookup first tries direct endpoint/path strings. UUID lookup parses the reference, checks the cached UUID map, and if necessary scans all local disks calling `get_disk_id` until a match is found. `init_local_disks` preallocates the global pool/set/disk matrix based on endpoint topology, creates disks only for local endpoints, stores them by endpoint string, and also places them into the indexed matrix.

`init_lock_clients` deduplicates endpoints by host:port, creates `LocalClient` for local endpoints and `RemoteClient` for remote URLs, publishes the first local client as the global lock client, then publishes the full map. `init_local_peer` prefers the host portion of local URL endpoints and falls back to configured host/port or `127.0.0.1`.

`has_space_for` doubles known object sizes, requires more than half the disks to have info, rejects low-inode disks outside single-drive erasure mode, checks per-disk free space, and ensures remaining aggregate free space stays above the configured fill fraction.

## State And Persistence Behavior
The module mutates process-global runtime maps rather than durable storage:
- `GLOBAL_LOCAL_DISK_MAP` maps endpoint string to local disk handle.
- `GLOBAL_LOCAL_DISK_ID_MAP` maps disk UUID to endpoint/path.
- `GLOBAL_LOCAL_DISK_SET_DRIVES` maps pool/set/disk indices to local disk handles.
- Global lock clients are published through `set_global_lock_client` and `set_global_lock_clients`.
- `GLOBAL_LOCAL_NODE_NAME` is set for peer identity.
No on-disk metadata is written here except whatever `new_disk` or disk info calls perform internally.

## Dependencies And Integration Points
This file depends on endpoint topology, `DiskStore`, `DiskOption`, `new_disk`, global store maps, lock client types (`LocalClient`, `RemoteClient`, `LockClient`), disk info APIs, erasure mode flags, disk capacity constants, UUID parsing, tracing, and `ECStore` placement logic. `init.rs` and `rebalance.rs` rely on these helpers for startup and pool capacity selection.

## Risks And Edge Cases
- Global vectors are appended in `init_local_disks`; repeated calls without clearing could duplicate topology entries.
- `init_lock_clients` deduplicates by host:port, so different endpoints sharing a host:port but different paths collapse to one lock client, which is likely intended for node-level locks but should remain explicit.
- `find_local_disk_by_ref` may perform a full local disk scan and disk ID I/O when the cache is cold.
- `all_local_disk` unwraps values after filtering `is_some`; safe in current code but brittle under refactor.
- `init_local_peer` unwraps URL host after checking `has_host`.
- `has_space_for` uses `disk.total - disk.used` and assumes disk info invariants prevent underflow.

## Test Signals
No tests are defined in this file. Related tests in `init.rs` cover local peer/pool ownership indirectly. High-value direct tests would cover UUID cache lookup/fallback, indexed disk lookup with and without `GLOBAL_LOCAL_DISK_SET_DRIVES`, lock-client deduplication, repeated `init_local_disks` behavior, and `has_space_for` edge cases for half-online disks, inode exhaustion, unknown sizes, and fill fraction limits.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/peer.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/rebalance.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store/rebalance.rs

## Purpose
This file contains pool-selection, cross-pool object lookup, rebalance/decommission deletion helpers, storage/admin introspection, namespace-lock factory routing, disk inventory lookup, and pool/set resolution for `ECStore`. Despite the filename, it is the central multi-pool placement and discovery layer used by object and multipart operations.

## Important APIs, Types, And Functions
- `LatestObjectInfoCandidate` and `resolve_latest_object_info_candidates` sort pool lookup results by object modification time, tie-breaking toward higher pool index.
- `RebalanceDeletePoolResult` and `resolve_rebalance_delete_from_all_pools_results` aggregate delete results across pools while preserving non-ignorable errors.
- `build_server_pools_available_space` computes per-pool available capacity and max-used percentage from disk info.
- `get_available_pool_idx` and `get_available_pool_idx_excluding` perform weighted random pool selection based on available capacity after reserve/fill filtering.
- `get_pool_idx`, `get_pool_idx_no_lock`, `get_pool_idx_existing_with_opts`, and `get_pool_info_existing_with_opts` locate the pool containing an existing object or choose capacity for a new object.
- `get_latest_object_info_with_idx` queries all pools and returns the latest object info without converting delete markers into access errors.
- `delete_object_from_all_pools` supports cleanup of objects that may exist in several pools or have read-quorum ambiguity.
- Admin/storage helpers include `reload_pool_meta`, `deduplicate_disks`, `handle_backend_info`, `handle_storage_info`, `handle_local_storage_info`, `handle_get_disks`, `handle_set_drive_counts`, and `handle_get_pool_and_set`.
- `handle_new_ns_lock` returns a namespace lock wrapper from the first pool.

## Control Flow
Capacity selection queries each pool concurrently, skipping suspended or actively rebalancing pools. It collects disk inventory for the object key, maps disks to `DiskInfo`, computes available capacity, filters pools over the reserve threshold, then picks a random point in total available capacity so larger free pools are more likely targets.

Existing-object lookup queries every pool concurrently. Unless `metadata_chg` is set, per-pool lookup clears `version_id` to find latest object state. Results are sorted by modification time. The scan skips decommissioned/rebalancing pools when requested, returns the first successful pool, treats `ErasureReadQuorum` as a usable pool indicator for non-metadata changes, honors delete-marker/precondition special cases, and otherwise returns not-found or the first non-not-found error.

Latest-object lookup is similar but simpler: query all pools, collect candidates, sort by mod time/high pool index, return the first object info, or propagate non-not-found errors, or synthesize object/version-not-found.

Delete-from-all-pools iterates supplied pool/error records, records write-quorum errors as hard failures, deletes from indexed pools, and requires aggregate success without hiding later non-ignorable errors.

Admin methods aggregate backend/storage info from pools or notification systems, defensively deduplicate disk entries, and resolve pool/set/disk index by disk UUID in stored erasure format metadata.

## State And Persistence Behavior
This file mostly reads state and delegates persistence:
- Pool metadata is read for suspension checks and can be reloaded into `self.pool_meta`.
- Rebalance state is consulted through `is_pool_rebalancing`.
- Object deletes persist through pool-level `delete_object`.
- Storage/admin info is read from notification systems and local pool snapshots.
- Capacity selection reads disk info but does not reserve space; actual allocation occurs later in pool PUT/complete paths, so placement is advisory and race-prone under concurrent writes.

## Dependencies And Integration Points
The module depends on global storage class configuration, storage admin traits, pool metadata, disk info helpers from `peer.rs`, object options and error classifiers, random selection, async `join_all`, madmin data types, namespace locks, erasure format metadata, and `PoolAvailableSpace`/`ServerPoolsAvailableSpace` filtering helpers. It is heavily consumed by `object.rs`, `multipart.rs`, and admin APIs.

## Risks And Edge Cases
- Weighted random placement is based on a point-in-time disk info snapshot; concurrent writes can still race into full pools.
- Existing-object lookup clears `version_id` unless `metadata_chg` is set; callers needing exact version lookup must set the right option, and helper functions in `object.rs` do this explicitly.
- Tie-breaking latest objects by higher pool index on identical modification times is deterministic but encodes a policy that may matter during rebalance/expansion.
- `is_suspended` has a TODO for locking; it currently reads `pool_meta` under an async `RwLock`, but broader consistency with updates may need review.
- `delete_object_from_all_pools` is sequential over supplied pools, not concurrent; large multi-pool cleanup could be slower.
- Defensive disk deduplication hides upstream duplicate reporting but may also mask topology/reporting bugs unless warnings are monitored.

## Test Signals
This file contains unit tests for latest-object candidate ordering, delete-marker latest selection, non-not-found error propagation, version-aware not-found synthesis, pool lookup not-found errors, rebalance pool-meta error wrapping, aggregate rebalance delete behavior across success/not-found/write-quorum/non-ignorable failures, disk set lookup error formatting, and available-space computation including meta-bucket capacity guard bypass. Additional integration tests are needed for live pool selection, suspension/rebalance skips, storage info deduplication with notification systems, and namespace-lock routing.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store/rebalance.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_api.rs -->
# sources/object-store/rustfs/crates/ecstore/src/store_api.rs

## Purpose
This file is the public store API prelude for the ecstore crate. It centralizes imports, constants, submodules, and re-exports for bucket/object/storage types, reader utilities, traits, and API-facing type definitions used by `ECStore` and callers.

## Important APIs, Types, And Functions
- Constants: `ERASURE_ALGORITHM = "rs-vandermonde"` and `BLOCK_SIZE_V2 = 1 MiB`.
- Submodules: `readers`, `traits`, and `types`.
- Re-exports: `readers::*`, `traits::*`, `types::*`, plus storage API bucket option/info types (`BucketInfo`, `BucketOptions`, `DeleteBucketOptions`, `MakeBucketOptions`).
- Imports establish the API vocabulary for object metadata, replication, lifecycle, tiering, checksums, compression, HTTP headers, namespace locks, healing, and async readers.

## Control Flow
There is no executable control flow beyond module declarations and re-exports. The file shapes compilation and public API access by collecting dependencies and exposing submodule contents.

## State And Persistence Behavior
This file does not manage state or persistence. Its constants influence erasure metadata/chunking behavior in downstream code, and its re-exported types carry persistent metadata fields, but no runtime mutation occurs here.

## Dependencies And Integration Points
The file binds together `rustfs_storage_api`, `rustfs_filemeta`, lifecycle/transition modules, replication status helpers, restore status parsing, HTTP header constants, checksum/compression utilities, `NamespaceLockWrapper`, healing types, async I/O, UUIDs, and Tokio cancellation. It is a central dependency surface for the `store` module and external code importing ecstore store APIs.

## Risks And Edge Cases
- As a prelude-style module, unused or overly broad imports can hide coupling and increase rebuild surface.
- Public wildcard re-exports make API changes in `readers`, `traits`, or `types` immediately visible to downstream callers.
- Constants such as `ERASURE_ALGORITHM` and `BLOCK_SIZE_V2` are compatibility-sensitive; changing them would affect stored metadata expectations and object layout assumptions.
- Because many metadata/status helper imports are centralized here, changes can create subtle compile/API churn outside this file.

## Test Signals
No tests are defined in this file. Signal comes from compilation and downstream tests that import store API types or rely on erasure constants. API compatibility tests or crate-level public API checks would be the most relevant coverage.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/store_api.rs -->
