# Research Report: subset-b-008856

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/util.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/util.rs

## Purpose
This file is the raftstore store utility hub. It concentrates correctness-sensitive helpers for region key membership, raft first-message classification, empty snapshot construction, epoch validation, flashback request admission, leader lease tracking, raft entry decoding, region sibling/conf-state conversion, configuration-change safety validation, stale-read safe-ts tracking, and split validation. Most logic here is shared by peers, local reads, store message handling, split/merge flows, and admin command proposal/application.

## Important APIs, Types, and Functions
- Key and epoch helpers: `check_key_in_region_exclusive`, `check_key_in_region_inclusive`, `check_key_in_region`, `is_epoch_stale`, `check_req_region_epoch`, `check_region_epoch`, `compare_region_epoch`, `is_region_epoch_equal`, and `validate_split_region`.
- Raft message helpers: `is_first_append_entry`, private `is_first_vote_msg`, `is_first_message`, `is_vote_msg`, and `is_initial_msg` decide whether unknown-region raft traffic can initialize or should wait behind pending splits.
- Snapshot and command decoding helpers: `new_empty_snapshot`, `get_entry_header`, `parse_data_at`, `RaftCmd`, and `parse_raft_cmd_request`.
- Lease types: `Lease`, `RemoteLease`, and `LeaseState` encode leader lease validity/suspicion and expose a thread-shareable remote view for local-read threads.
- Configuration change abstractions: `AdminCmdEpochState`, `admin_cmd_epoch_lookup`, `ConfChangeKind`, `ChangePeerI`, and `check_conf_change` bridge legacy and v2 change-peer requests to raft-rs `ConfChangeI`.
- Read progress types: `RegionReadProgressRegistry`, `RegionReadProgress`, `RegionReadProgressCore`, `ReadState`, and `LocalLeaderInfo` track stale-read `safe_ts`/resolved-ts by region and publish leader identity plus applied-index-gated read states.
- Miscellaneous helpers: `gen_bucket_version`, `conf_change_type_str`, `build_key_range`, `is_region_initialized`, `u64_to_timespec`, `is_sibling_regions`, `conf_state_from_region`, `KeysInfoFormatter`, and `MsgType`.

## Control Flow
Request admission typically validates target store/peer/term, checks the request epoch according to normal-vs-admin command policy, and optionally checks flashback state. Epoch comparison is strict for the selected dimensions, returning `EpochNotMatch` with optional current region metadata.

First raft-message classification is used when a store receives raft messages for an unknown or overlapping region. Initial vote/pre-vote terms, first append entries, and heartbeat messages with `INVALID_INDEX` commit carry different creation/pending semantics.

Lease control starts with `Lease::renew`, `suspect`, `expire`, or `maybe_new_remote_lease`. The local lease owns the authoritative bound; `RemoteLease` receives atomic expiry updates only when bounds advance far enough, and `need_renew` asks for proactive renewal near the configured advance window.

Configuration changes are first simulated through raft-rs `Changer`, then checked for raftstore-level safety: operation/role matching, duplicate peer IDs, witness-switch rejection, leader removal/demotion policy, learner-only joint-change rejection, heartbeat-based availability, and log-availability safety via `maximal_committed_index`.

Read progress flows through `RegionReadProgress::update_safe_ts_with_time` and `update_applied`. Safe-ts records with future apply indexes are queued in sorted `pending_items`; once applied index catches up, the highest eligible ts is published through atomics and coprocessor hooks. Merges call `merge_safe_ts`, consume items through the merge index, lower target safe-ts to the source/target minimum, and reject stale pre-merge items thereafter.

## State and Persistence Behavior
Most state is in-memory but mirrors persistent raft/apply facts. `Lease` stores monotonic-clock bounds and has no durable persistence; lease loss is encoded by clearing the bound and expiring the remote atomic view. `timespec_to_u64` compresses monotonic times to millisecond precision for atomic sharing.

`RegionReadProgressCore` persists no data itself, but its `applied_index`, `read_state`, `pending_items`, `last_merge_index`, pause/discard flags, leader info, and diagnostic timestamps derive from applied raft progress, resolved-ts publication, leader check RPCs, and region metadata. The public `safe_ts` and `read_index_safe_ts` atomics are fast paths for read execution.

`new_empty_snapshot` serializes `RaftSnapshotData` containing region metadata, zero file size, current snapshot version, and witness flag into the raft snapshot data field. Entry parsing supports both simple-write v2 decoding and legacy protobuf raft command payloads.

## Dependencies and Integration Points
This file depends on `kvproto` region, raft command, raft server, and kvrpc types; raft-rs `RawNode`, `Changer`, `ConfState`, entries, and messages; `engine_traits::KvEngine`; `tikv_util` logging/time/codec helpers; `txn_types::WriteBatchFlags`; `tokio::sync::Notify`; and crate modules for config, metrics, peer storage, snapshots, simple-write decoding, and coprocessor hooks.

Integration is broad: peer proposal/application uses epoch, term, peer, flashback, and split validation; local read workers use `Lease` and `RemoteLease`; stale-read and check-leader workers use `RegionReadProgressRegistry`; raftstore membership paths use `ChangePeerI` and `check_conf_change`; snapshot generation and application use conf-state and empty snapshot helpers.

## Risks and Edge Cases
Epoch policy is explicitly compatibility-sensitive; comments warn against changing `admin_cmd_epoch_lookup` or normal-request epoch flags. `parse_data_at` and legacy header extraction panic on corrupted raft entry data, relying on upstream raft-entry integrity. `RegionReadProgressRegistry::with` holds a mutex during callback execution and warns against nested locking. Safe-ts lowering on merge is subtle; missing `last_merge_index` filtering could incorrectly raise safe-ts after merge. Witness peers pause/discard stale-read progress to prevent serving stale reads. Configuration-change checks mix raft simulation, heartbeat freshness, and store policy, so role mapping or heartbeat threshold changes can affect availability.

## Test Signals
The module has focused tests for lease state transitions and remote lease expiry, timespec encoding, raft command header extraction, conf-state generation, change-peer v2 transition selection, first vote/append/initial message classification, epoch staleness and request epoch policy, sibling detection, store/peer/term mismatch errors, read-progress pending queue behavior, leader-info updates, heartbeat-based conf-change availability rejection, unhealthy-cluster exceptions, and `read_index_safe_ts` pause/discard/merge reset behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/util.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/check_leader.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/check_leader.rs

## Purpose
This worker validates remote leader information against local region read progress and provides store-level safe-ts queries. It is part of TiKV stale-read/local-read coordination: followers consume leader-published read states, callers learn which regions still match their expected leader, and store-wide or key-range safe-ts can be computed.

## Important APIs, Types, and Functions
- `Task::CheckLeader { leaders, cb }` accepts `LeaderInfo` records and returns matching region IDs through a callback.
- `Task::GetStoreTs { key_range, cb }` returns the minimum non-zero safe-ts for all regions or for regions overlapping a key range.
- `Runner<S, E>` owns `store_meta`, a cloned `RegionReadProgressRegistry`, and a `CoprocessorHost<E>`.
- `Runner::new` extracts the registry from `StoreRegionMeta`.
- `get_range_safe_ts` implements the store-wide fast path and range-overlap path.

## Control Flow
For `CheckLeader`, the runner hits failpoints for stores 2 and 3, then delegates to `RegionReadProgressRegistry::handle_check_leaders`. That method consumes each incoming `LeaderInfo`, updates safe-ts/read-state if present, calls coprocessor hooks, and returns IDs whose leader term, peer ID, and epoch match local state. The task callback receives those IDs.

For `GetStoreTs`, an empty `KeyRange` scans the registry directly under its internal mutex and returns the minimum non-zero safe-ts, or zero if none are initialized. A non-empty range locks `store_meta`, searches overlapping regions with `StoreRegionMeta::search_region`, reads their registered safe-ts values, and returns the minimum non-zero value or zero.

## State and Persistence Behavior
The worker mutates in-memory `RegionReadProgress` via leader-info consumption. It does not write raft state or engine data. Safe-ts value zero is treated as uninitialized and excluded from minimum calculations. The range path depends on the current in-memory region range map and assumes every searched region has a registered read progress entry.

## Dependencies and Integration Points
The worker depends on `StoreRegionMeta`, `RegionReadProgressRegistry`, `CoprocessorHost`, `KvEngine`, `KeyRange`, `LeaderInfo`, and `tikv_util::worker::Runnable`. It integrates with stale-read/check-leader RPC handling and store metadata search over region key ranges.

## Risks and Edge Cases
The non-empty range branch calls `registry.get(&r.get_id()).unwrap()` for searched regions, so registry/meta consistency is required. Holding `store_meta` while scanning ranges can be more expensive than the empty-range fast path, which the comments say is the current common case. Zero safe-ts values are ignored, which avoids uninitialized peers but can hide a fully uninitialized range by returning zero.

## Test Signals
`test_get_range_min_safe_ts` builds synthetic regions and read-progress records, then verifies empty-store behavior, global minimum selection, zero safe-ts filtering, overlapping range minima, unbounded end ranges, and gaps returning zero.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/check_leader.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup.rs

## Purpose
This file is a small dispatcher that combines multiple cleanup-related raftstore workers behind one `Runnable`. It lets the store schedule compaction, imported SST deletion, and snapshot GC/delete tasks through a single cleanup worker interface.

## Important APIs, Types, and Functions
- `Task` wraps `CompactTask`, `CleanupSstTask`, and `GcSnapshotTask`.
- `Runner<E, R>` owns a `CompactRunner<E>`, `CleanupSstRunner<E>`, and `GcSnapshotRunner<E, R>`.
- `Runner::new` wires the three concrete runners.
- `impl Runnable for Runner` dispatches by enum variant.

## Control Flow
The worker receives a `Task`, formats it by delegating to the inner task's `Display`, and dispatches `Compact` to the compaction runner, `CleanupSst` to the SST importer cleanup runner, and `GcSnapshot` to the snapshot cleanup runner. There is no local retry or persistence logic in this wrapper.

## State and Persistence Behavior
This wrapper owns the concrete runners and mutably borrows them during dispatch. State and persistence effects are entirely delegated: RocksDB compaction in `compact`, importer filesystem deletion in `cleanup_sst`, and snapshot manager/router actions in `cleanup_snapshot`.

## Dependencies and Integration Points
It depends on `engine_traits::{KvEngine, RaftEngine}`, `tikv_util::worker::Runnable`, and sibling worker modules. It is an integration point for raftstore worker construction where separate cleanup responsibilities share a worker lane.

## Risks and Edge Cases
Because this is a serial dispatcher, long-running inner operations can block later cleanup tasks in the same worker. Error handling is delegated to inner runners, so wrapper-level observability only reflects task display strings.

## Test Signals
There are no direct tests in this file. Coverage comes indirectly from the concrete cleanup, compaction, snapshot, and SST worker tests and from raftstore worker integration tests that schedule `CleanupTask` variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup_snapshot.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup_snapshot.rs

## Purpose
This worker garbage-collects idle raft snapshots and deletes specific snapshot files. It coordinates snapshot manager state with raft peer routing so peers can decide whether snapshots are still needed, while also handling disconnected peers by directly removing stranded snapshot files.

## Important APIs, Types, and Functions
- `Task::GcSnapshot` scans idle snapshots and schedules per-region GC.
- `Task::DeleteSnapshotFiles { key, snapshot, check_entry }` deletes a specific snapshot after ensuring metadata is loaded.
- `Runner<EK, ER>` stores `store_id`, `RaftRouter`, and `SnapManager`.
- `handle_snap_mgr_gc` groups idle snapshots by region and sends `CasualMessage::GcSnap`.
- `delete_snapshot` delegates to `SnapManager::delete_snapshot`.

## Control Flow
`GcSnapshot` calls `handle_snap_mgr_gc`. That method lists idle snapshots, groups consecutive snapshot keys by `region_id`, and sends each group to the owning peer as a casual GC message. If the peer router is disconnected because the system is shutting down, it treats that as success. If a region mailbox is disconnected but the store is not shutting down, it loads each snapshot for GC and deletes it directly because the peer is considered destroyed. Full mailboxes are tolerated and the snapshots will be retried later. After GC handling, the runner sends `StoreMsg::GcSnapshotFinish` through the store router.

`DeleteSnapshotFiles` loads snapshot metadata if necessary, logs but continues on metadata-load failure, and then deletes the snapshot with the provided `check_entry` flag. Failures are logged.

## State and Persistence Behavior
The worker changes snapshot filesystem state through `SnapManager`. `GcSnapshot` itself schedules peer-side cleanup and only deletes directly on disconnected-region fallback. `DeleteSnapshotFiles` performs immediate deletion. No raft log or KV engine state is modified, but snapshot files are persistent artifacts, and `check_entry` controls whether deletion validates entry metadata.

## Dependencies and Integration Points
It depends on `KvEngine`, `RaftEngine`, crossbeam `TrySendError`, failpoints, `SnapKey`, `Snapshot`, `SnapManager`, `RaftRouter`, `StoreRouter`, `PeerMsg`, `CasualMessage`, and `StoreMsg`. It integrates with peer FSM casual messages and store-level GC completion bookkeeping.

## Risks and Edge Cases
The grouping assumes `list_idle_snap` returns keys in a useful region grouping order; otherwise duplicate region sends still work but are less efficient. Full mailboxes silently defer work. Direct deletion on disconnected peers depends on correctly distinguishing store shutdown from destroyed peer mailboxes. Metadata load failures are logged but do not stop deletion attempts.

## Test Signals
There are no direct unit tests in this file. Behavior is instrumented with failpoint `peer_2_handle_snap_mgr_gc` and is typically covered by snapshot manager, peer destruction, and raftstore snapshot GC integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup_snapshot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup_sst.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup_sst.rs

## Purpose
This worker deletes imported SST files from the SST importer. It is part of raftstore/import cleanup after ingestion, cancellation, or stale import artifacts.

## Important APIs, Types, and Functions
- `Task::DeleteSst { ssts }` carries a list of `import_sstpb::SstMeta`.
- `Runner<E>` owns an `Arc<SstImporter<E>>`.
- `handle_delete_sst` iterates through SST metadata and invokes `SstImporter::delete`.

## Control Flow
The runner receives `DeleteSst`, formats the count for logging/display, and deletes each SST via the importer. Individual delete results are intentionally ignored, so the task is best-effort.

## State and Persistence Behavior
The worker mutates filesystem/importer state by deleting SST files tracked by `SstImporter`. It does not alter raft log or KV engine records directly. The importer is shared by `Arc`, so deletion coordinates with the importer implementation.

## Dependencies and Integration Points
It depends on `KvEngine`, `SstMeta`, `sst_importer::SstImporter`, and `tikv_util::worker::Runnable`. It is wired through `cleanup.rs` and used by raftstore paths that need asynchronous cleanup of import artifacts.

## Risks and Edge Cases
Errors from `importer.delete` are dropped, so missing files, permission issues, or transient filesystem failures are not surfaced by this runner. Callers that need stronger cleanup guarantees must observe importer state elsewhere.

## Test Signals
There are no direct tests in this file. Coverage comes from SST importer behavior and higher-level import/cleanup tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup_sst.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/compact.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/compact.rs

## Purpose
This worker runs manual RocksDB compactions for raftstore. It supports explicit CF range compaction and experimental periodic full-store compaction split into ranges with load-sensitive pauses.

## Important APIs, Types, and Functions
- `Task::Compact { cf_name, start_key, end_key, bottommost_level_force }` compacts a CF range.
- `Task::PeriodicFullCompact { ranges, compact_load_controller }` launches asynchronous full compaction over provided ranges or the whole store.
- `FullCompactController` contains pause backoff settings and an `incremental_compaction_pred` predicate.
- `FullCompactController::pause` waits on `GLOBAL_TIMER_HANDLE` with exponential-style retry until the predicate allows progress.
- `Runner<E>` owns a `KvEngine` clone and a YATP `Remote`.
- `full_compact` performs incremental compaction and observes full/increment/pause metrics.
- `compact_range_cf` performs synchronous CF range compaction.
- `FULL_COMPACTION_IN_PROCESS` prevents concurrent periodic full compactions.

## Control Flow
For `Compact`, the runner starts the `COMPACT_RANGE_CF` timer, builds `ManualCompactionOptions` with bottommost-level forcing as requested, calls `engine.compact_range_cf`, logs success or failure, and observes duration.

For `PeriodicFullCompact`, the runner atomically checks and sets `FULL_COMPACTION_IN_PROCESS`. If another full compaction is active, it logs and returns. Otherwise it clones the engine and spawns an async task on the future pool. The async task converts ranges into optional start/end slices, inserts a whole-store `(None, None)` range when no ranges are provided, compacts each increment with `compact_range`, and before moving to the next increment pauses when the predicate is false. Completion or failure clears the global in-process flag.

## State and Persistence Behavior
Compaction mutates RocksDB storage layout and can remove obsolete versions/tombstones, but it does not change logical KV contents or raft metadata. Full compaction uses `ManualCompactionOptions::new(false, 1, false)`, while range compaction can force bottommost compaction. The only local process state is the global atomic in-process flag and metrics.

## Dependencies and Integration Points
The worker depends on `engine_traits::{KvEngine, ManualCompactionOptions}`, YATP futures, `GLOBAL_TIMER_HANDLE`, failpoints, and Prometheus metrics from `worker::metrics`. It is exported through `worker/mod.rs` and wrapped by `cleanup.rs`.

## Risks and Edge Cases
`FullCompactController::pause` updates `duration_secs` with `max(max_pause, duration * 2)`, which jumps to at least the configured max after a failed predicate rather than capping at max; that may be intentional or a subtle backoff issue. If the spawned async task panics before clearing `FULL_COMPACTION_IN_PROCESS`, future full compactions could be suppressed. Full compaction is explicitly experimental and has a TODO for stopping/cancellation. Manual compaction can be disabled at the engine level, in which case compaction may not reduce SST size.

## Test Signals
Tests verify disabling/enabling manual compaction affects SST size, explicit compact-range reduces duplicated SST data, full compaction removes delete/tombstone overhead in MVCC write CF, and incremental full compaction can pause until the predicate becomes true.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/compact.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/consistency_check.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/consistency_check.rs

## Purpose
This worker computes region consistency hashes from engine snapshots and reports them back to the store/coprocessor dispatch path. It is used by raftstore consistency checking to compare replicated region data at a specific raft index.

## Important APIs, Types, and Functions
- `Task<S>::ComputeHash { index, context, region, snap }` carries the raft index, observer context, region metadata, and snapshot.
- `Task::compute_hash` is a constructor for compute-hash tasks.
- `Runner<EK, C>` owns a `StoreHandle` router and `CoprocessorHost<EK>`.
- `compute_hash` invokes coprocessor consistency-check observers and reports results.

## Control Flow
The runner receives `ComputeHash` and calls `compute_hash`. Empty context is skipped for backward compatibility. Otherwise it increments compute metrics, starts a hash timer, calls `coprocessor_host.on_compute_hash(&region, &context, snap)`, and handles errors by logging and incrementing failure metrics. Successful `(context, crc32)` results are encoded as big-endian four-byte checksums and sent to `router.update_compute_hash_result(region_id, index, ctx, checksum)`.

## State and Persistence Behavior
The worker reads from an engine snapshot and does not mutate engine state. It emits hash results through the store handle, which schedules result updates elsewhere. Metrics counters/histograms are updated in memory/exported Prometheus state.

## Dependencies and Integration Points
It depends on `engine_traits::{KvEngine, Snapshot}`, `kvproto::metapb::Region`, byteorder encoding, `CoprocessorHost`, `StoreHandle`, raftstore metrics, and worker metrics. Consistency-check observers registered in the coprocessor host provide the actual hash algorithms.

## Risks and Edge Cases
Empty context silently skips work, preserving compatibility but hiding malformed modern requests. Errors from coprocessor hashing stop all result reporting for the task. The checksum format is fixed at big-endian u32, so consumers must match that encoding.

## Test Signals
`test_consistency_check` registers a raw consistency-check observer, writes sample keys, computes the expected CRC including region state key, runs the task over a snapshot, and verifies that `SchedTask::UpdateComputeHashResult` carries the region ID, index, context, and encoded checksum.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/consistency_check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/disk_check.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/disk_check.rs

## Purpose
This worker measures disk I/O latency for TiKV health inspection. It writes a small probe file, records the observed latency into a `LatencyInspector`, and finishes the inspector callback asynchronously through a bound background worker.

## Important APIs, Types, and Functions
- `Task::InspectLatency { inspector }` carries a health-controller latency inspector.
- `Runner::new(inspect_dir)` targets `.disk_latency_inspector.tmp` inside the inspect directory.
- `Runner::dummy` creates a local test runner.
- `bind_background_worker` attaches a `tikv_util::worker::Worker` for async execution.
- `inspect` delegates to `ProbeRunner::probe_once`.
- `execute` drains at most one queued task with `try_recv`.

## Control Flow
`run` tries to enqueue the incoming task into a bounded channel of capacity three. If enqueue succeeds and a background worker is bound, it clones the runner and spawns an async task that calls `execute`. `execute` receives one pending inspect task, runs a disk probe, records the duration with `inspector.record_apply_process`, and calls `inspector.finish`. Probe failures and enqueue failures are logged.

## State and Persistence Behavior
The worker creates/overwrites a temporary probe file via `ProbeRunner` and removes it in `Drop`. The bounded channel intentionally drops pressure when too many inspections arrive; older or excess health probes are treated as stale. It records latency into the supplied inspector but does not persist health state itself.

## Dependencies and Integration Points
It depends on crossbeam bounded channels, `health_controller::types::LatencyInspector`, `tikv_util::worker::Worker`, and `crate::store::disk_probe::ProbeRunner`. It integrates with server health monitoring that schedules disk checks and consumes inspector completion callbacks.

## Risks and Edge Cases
If no background worker is bound, accepted tasks remain queued but are not executed until future runs with a worker, and capacity can fill. `execute` processes only one queued task per spawned async task. Drop always attempts to remove the probe path and logs if the file is already gone or cannot be removed.

## Test Signals
`test_disk_check_runner` binds a background worker, verifies a positive latency is recorded, then removes the worker and submits more inspections to verify they do not complete and capacity/backpressure prevents uncontrolled accumulation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/disk_check.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/metrics.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/metrics.rs

## Purpose
This file defines Prometheus metrics for raftstore workers and local-read paths. It centralizes counters, gauges, histograms, static label enums, and thread-local local-read metric buffering.

## Important APIs, Types, and Functions
- Static metric label enums and wrappers: `SnapType`, `SnapStatus`, `SnapCounter`, `CheckSplitCounter`, `SnapHistogram`, `RejectReason`, `LocalReadRejectCounter`, `ClearOverlapRegionType`, and `ClearOverlapRegionDuration`.
- `LocalReadMetrics` groups per-thread local counters and last flush time.
- `TLS_LOCAL_READ_METRICS` initializes thread-local local metric handles.
- `maybe_tls_local_read_metrics_flush` flushes thread-local counters every 10 seconds.
- Lazy Prometheus collectors include snapshot counters/histograms, split-check metrics, compaction metrics, process CPU gauge, hash metrics, stale-peer cleanup gauge, raft-log GC metrics, local-read counters/reject reasons, and clear-overlap-region duration.

## Control Flow
Metrics are registered lazily with `lazy_static!`. Callers increment local or global collectors directly. For local reads, worker threads update thread-local counters to reduce contention; `maybe_tls_local_read_metrics_flush` checks elapsed coarse time and flushes all local counters and reject-reason vectors when the interval has passed.

## State and Persistence Behavior
All state is in process memory and exported through Prometheus. Thread-local counters buffer increments until flush. There is no disk persistence. Metric names and labels form an external observability contract and should be treated as stable.

## Dependencies and Integration Points
The file depends on `prometheus`, `prometheus_static_metric`, `lazy_static`, and `tikv_util::time::Instant`. It is imported by compaction, consistency check, snapshot, split, local read, raft log GC, and cleanup paths.

## Risks and Edge Cases
Metric label enums must stay synchronized with call sites; invalid label values would fail at compile time for static metrics but dynamic vectors still require care. Thread-local metrics depend on periodic flush calls; low-traffic threads may retain increments longer than expected. The name `CHECK_SPILT_*` preserves an existing typo in the metric variable names while metric strings use check-split wording.

## Test Signals
There are no direct tests in this file. Runtime validation comes from compilation of static metric labels, Prometheus registration success at startup, and call-site tests that observe worker behavior while incrementing metrics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/metrics.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/mod.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/worker/mod.rs

## Purpose
This module declares raftstore worker submodules and re-exports their public runner/task types and key helper types. It is the public facade for background workers used by raftstore construction and scheduling.

## Important APIs, Types, and Functions
- Private submodules include check leader, cleanup, cleanup snapshot/SST, compact, consistency check, disk check, PD, raft log GC, local read, refresh config, region, snapshot generation, split check/config/controller/validator.
- Public module: `metrics`.
- Re-exports include `CheckLeaderRunner/Task`, `CleanupRunner/Task`, `CompactRunner/Task`, `FullCompactController`, `ConsistencyCheckRunner/Task`, `DiskCheckRunner/Task`, PD reporting types, raftlog GC types, local read types, refresh config types, region worker types, snapshot generation types, split check/config/controller types, and `SplitValidator`.

## Control Flow
There is no runtime control flow in this file. Compile-time module declarations determine which worker implementations are included, and `pub use` blocks define the external import surface for other raftstore modules.

## State and Persistence Behavior
The module itself has no state and no persistence effects. It shapes access to workers that do hold engine handles, routers, metadata references, metrics, and filesystem-backed components.

## Dependencies and Integration Points
It integrates all sibling worker files into `crate::store::worker`. Store/bootstrap code can import a stable facade rather than each concrete submodule path. It also exposes constants and helper types from split and snapshot generation workers that are needed outside their implementation modules.

## Risks and Edge Cases
Because most submodules are private, removing or renaming a re-export can break downstream raftstore code even when the implementation remains. The facade mixes many domains, so accidental visibility changes may widen or shrink APIs unexpectedly.

## Test Signals
There are no direct tests. The signal is compile-time: if a worker module, type alias, or re-export is wrong, dependent raftstore modules fail to compile. Runtime behavior is covered by the individual worker modules.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/worker/mod.rs -->
