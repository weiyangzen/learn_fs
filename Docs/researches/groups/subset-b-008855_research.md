# subset-b-008855 research

Grouped research for TiKV raftstore snapshot, routing, transaction-extension, backup snapshot, and unsafe recovery sources. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/snap.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/snap.rs

## Purpose

Implements raftstore v1 snapshot file lifecycle plus compatibility hooks for raftstore v2 tablet snapshots. It defines snapshot keys, per-CF file metadata, snapshot build/send/receive/apply state, snapshot directory management, encryption metadata handling, disk-space limiting, receive concurrency precheck, snapshot statistics, and cleanup of generated, received, temporary, clone, and tablet snapshot files.

## Important APIs, Types, And Functions

`SNAPSHOT_CFS` fixes the data column families included in snapshots: default, lock, and write; raft CF is explicitly excluded. `SnapKey` names v1 snapshots by `region_id`, raft `term`, and `idx`; `TabletSnapKey` adds `to_peer` for v2 tablet snapshots. `CfFile` records one CF's file prefix/suffix, generated paths, per-file sizes/checksums, send readers, receive writers, and key count. `Snapshot` owns a key, directory, CF file list, meta file, manager core, and read/write cursor indexes. Its constructors split by use case: `new_for_building`, `new_for_sending`, `new_for_receiving`, `new_for_applying`, and v2 compatibility `new_for_tablet_snapshot`.

`gen_snapshot_meta`, `set_snapshot_meta`, `load_snapshot_meta`, `validate`, `save_meta_file`, `save`, `build`, and `apply` are the core data-path methods. `SnapManager` is the public manager with `init`, `get_snapshot_for_building`, `get_snapshot_for_sending`, `get_snapshot_for_receiving`, `get_snapshot_for_applying`, `list_idle_snap`, `delete_snapshot`, registry methods, speed/size limit setters, stats collection, receive precheck/complete, and tablet manager access. `SnapManagerBuilder` constructs configured managers with write throttling, total-size cap, per-file cap, encryption key manager, receive concurrency limit, ingest threshold, and optional tablet snapshot receive support. `SnapRecvConcurrencyLimiter` enforces region-keyed receive admissions with a TTL and reserved capacity. `TabletSnapManager` manages v2 snapshot directories, receive guards, stats, list/delete paths, and size accounting.

## Control Flow

Build flow starts with `SnapManager::get_snapshot_for_building`, which may scan and delete old idle generated snapshots when total snapshot size exceeds `max_total_snap_size`. `Snapshot::build` initializes `RaftSnapshotData`, calls `do_build`, records total size/count and generation duration, and returns metadata for raft transfer. `do_build` validates an existing snapshot and reuses it if intact; corrupted existing files are deleted with registry checks and then rebuilt. For each snapshot CF, lock CF uses `snap_io::build_plain_cf_file`, while default/write use `snap_io::build_sst_cf_file_list` with per-file split limits, IO limiter, encryption key manager, and load-balance/replication IO type. Non-empty temp CF files are renamed to final names and checksummed; empty CF temp files and encryption metadata are removed. Finally `SnapshotMeta` is written through a temporary meta file and renamed atomically.

Send flow opens an existing generated snapshot via `new_for_sending`, loads metadata, opens one reader per non-empty CF file, and, when encryption is enabled, replaces plain readers with decrypting readers. `impl Read for Snapshot` streams CF files in metadata order and advances between files and CFs on EOF. Receive flow uses `new_for_receiving` with incoming `SnapshotMeta`, creates a temp meta file and temp CF files, optionally creates encryption file metadata and AES-CTR crypters for final file paths, then `impl Write for Snapshot` writes incoming bytes across CF file boundaries while updating plaintext CRC32/size counters and enforcing the manager limiter in 4 KiB chunks. `save` flushes and syncs received files, verifies written size and checksum against metadata, renames temp CF files to final names, syncs the directory, writes and renames the meta file, and clears the temp-file cleanup flag.

Apply flow opens a received snapshot with `new_for_applying`, validates all non-empty files by size and checksum over decrypted content, prepares clone files for SST ingestion or copy-symlink ingestion, and then applies CFs. Plain lock CF data is decoded and batch-written through `snap_io::apply_plain_cf_file`. SST CFs are either read back and batch-written when the snapshot is small enough for `can_apply_cf_without_ingest`, or ingested through `snap_io::apply_sst_cf_files_by_ingest` with the region's encoded key range. Coprocessor hooks are invoked after plain key batches or SST apply. Deletion and GC use `SnapManager::list_idle_snap`, the `registry`, and `delete_snapshot` to avoid removing snapshots currently generating, sending, receiving, or applying.

## State And Persistence Behavior

Snapshot persistence is file-based. Data files are named `gen_<key>_<cf>.sst` or `rev_<key>_<cf>.sst`, with numbered suffixes for multi-file snapshots, `.tmp` for in-progress writes, `.clone` for ingestion-prepared files, and `.meta` for serialized `SnapshotMeta`. A snapshot is considered existent only when all non-empty CF files from metadata exist and the meta file exists. Data integrity is enforced by metadata sizes/checksums, and encrypted deployments compute checksums over decrypted contents. Temporary files are guarded by `hold_tmp_files`; if a build or receive `Snapshot` drops before success, `Drop` calls `delete`.

`SnapManagerCore::registry` is in-memory only and prevents GC/delete races with active snapshot work. `max_total_size`, `max_per_file_size`, `enable_multi_snapshot_files`, `offlined`, receive limiter state, stats, and temporary SST IDs are also process state. The durable snapshot contract is the directory contents plus encryption metadata maintained through `DataKeyManager`. Tablet snapshots use directories under `<base>_v2`; generated tablet snapshots are treated as checkpoints, and only received tablet snapshots are counted by `total_snap_size`. V1 compatibility for v2 receive is represented by an empty v1 snapshot meta with `tablet_snap_path` set.

## Dependencies And Integration Points

This module depends on `snap/io.rs` for concrete plain/SST build and apply routines, `engine_traits::KvEngine` and SST traits for snapshots and ingestion, `file_system` for filesystem abstraction, `encryption` and OpenSSL AES-CTR for encrypted snapshot files, raft and kvproto snapshot metadata types, `keys` for encoded region ranges, `sst_importer` for ingestion preparation, `CoprocessorHost` apply hooks, and raftstore metrics. Snapshot generation workers call `SnapManager` through raftstore store/worker code; peer storage applies snapshots through `Snapshot::apply`; snapshot GC and stats consumers use manager registry/listing/stat APIs. Receive precheck integrates with raft message handling to reduce unnecessary snapshot generation when receivers are saturated.

## Risks

The code is sensitive to crash windows around file rename and encryption metadata rename/link/delete. The comments explicitly rely on the meta file being absent to make partially moved CF files harmless. Corrupt meta files can cause broad best-effort deletion, so registry checks must remain correct. `set_snapshot_meta` assumes CF files are grouped by CF in metadata order; changing metadata order would break reconstruction. `Snapshot::Write` updates CRC before encryption, so the expected checksum is plaintext; any alternate encryption path must preserve that invariant. The receive concurrency limiter uses TTL eviction; too short a TTL can admit too many receives and reintroduce busy/drop cycles. `get_snapshot_for_building` scans directories and can delete old generated snapshots, so it must stay off hot raftstore threads as noted. Clone/symlink ingestion paths need care because wrong handling can ingest mutable or deleted files.

## Test Signals

In-file tests cover metadata generation, display paths, empty and non-empty snapshot build/send/receive/apply, multi-file snapshots, validation reuse, checksum and meta corruption, manager directory initialization, v2 manager behavior, registry-protected deletion, total-size eviction, temporary SST cleanup, tablet stats, encryption build rebuilds, v2 tablet snapshot compatibility, tablet key parsing, and receive concurrency limiter behavior. The tests also exercise copied snapshots, altered CF order at destination, encrypted DB options, and failpoints for receive completion. These tests are strong regression signals for file naming, cleanup, integrity validation, encryption, and concurrency limiter semantics.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/snap.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/snap/io.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/snap/io.rs

## Purpose

Provides the concrete file IO routines used by `snap.rs`: build snapshot CF files from an engine snapshot, encode/decode the plain lock-CF format, build and verify SST files for default/write CFs, apply snapshots either by direct writes or external SST ingestion, enforce read IO throttling during SST generation, and open decrypting readers for encrypted snapshot files.

## Important APIs, Types, And Functions

`StaleDetector` abstracts cancellation for apply loops. `BuildStatistics` reports key count, logical KV bytes, generated SST bytes, plain-file bytes, and measured read IO bytes. `build_plain_cf_file` writes compact-length key/value pairs plus an empty-key sentinel for the plain format. `build_sst_cf_file_list` writes Zstd-compressed SST files, splitting when the raw key/value size exceeds `raw_size_per_file`, verifying block checksums through `SstReader`, syncing finished files, and tracking IO limiter consumption. `apply_plain_cf_file` decodes the plain format into write batches and invokes a callback after each batch. `apply_sst_cf_files_by_ingest` ingests prepared SSTs with an optional region key range and forced allow-write. `apply_sst_cf_files_without_ingest` and its helper iterate SST contents and write them to the KV engine in batches. `get_decrypter_reader` opens a plaintext or decrypting reader based on `DataKeyManager` file metadata.

## Control Flow

Plain build opens a new temp file, optionally wraps it in `EncrypterWriter`, scans the requested CF/range from the engine snapshot, compact-encodes every key and value, and syncs only if at least one key was found. Empty scans remove the temp file and leave `CfFile` without file entries. SST build creates the first temp SST writer, scans the CF/range, and rotates to a new SST when adding the next entry would exceed the raw-size budget. On rotation, it records the previous file in `CfFile`, finishes and verifies the old SST, syncs it, and then continues with the new writer. After scan completion it handles any remaining measured read IO, finishes/verifies the final SST if non-empty, records its path, and deletes the unused temp file if empty.

Apply by direct write uses the same batching pattern for plain and SST formats: read or iterate records, check `StaleDetector` before each item loop, accumulate `(key, value)` pairs until `batch_size`, write them to a reusable engine write batch, clear the batch, call the provided callback, and continue. Plain apply stops on the empty-key sentinel. SST direct apply stops when the SST iterator becomes invalid. Ingest apply delegates to `KvEngine::ingest_external_file_cf`, passing the snapshot region range and `force_allow_write = true`; comments document why overlapping foreground writes should not exist during snapshot apply.

## State And Persistence Behavior

This file does not own long-lived state. It creates, writes, verifies, syncs, removes, and reads snapshot temp files supplied by `CfFile`. For encrypted files, file encryption metadata is created by callers during receive/build setup; this helper either wraps writers or opens decrypting readers using that metadata. `BuildStatistics` is transient but feeds snapshot metrics in `snap.rs`. Batch writes during apply are durable according to the underlying engine write semantics, while comments note that callers remain responsible for flushing/syncing CFs after direct apply.

## Dependencies And Integration Points

Depends on `engine_traits` for snapshots, scanning, SST writer/reader/builders, iterators, write batches, ranges, and compression selection. It uses `file_system` for IO type guards, files, open options, and IO byte tracking; `tikv_util::Limiter` for throttling; `txn` byte codecs for plain snapshot encoding; `encryption` for encrypting/decrypting streams; and `fail` failpoints for corruption and IO tests. It is called almost exclusively by `snap.rs`, which chooses plain format for `CF_LOCK`, SST format for other snapshot CFs, and decides between ingest and direct apply.

## Risks

Correctness depends on matching build and apply formats exactly: plain files rely on an empty-key sentinel and compact byte framing, while SST files rely on engine SST semantics. `build_sst_cf_file_list` only limits measured read IO at intervals, and the TODO notes snapshot file write IO is not part of that limiter. The file split threshold is based on raw key/value bytes, not compressed SST bytes, so actual disk sizes vary. The ingest path uses `force_allow_write`; its safety relies on raftstore region worker ordering, unapplied snapshot state, and ingest latch behavior documented in comments. Direct apply can be aborted between batches; callers must handle partially applied state according to the broader snapshot apply protocol. Corruption detection depends on SST block checksum verification and later size/checksum validation in `snap.rs`.

## Test Signals

Tests build and apply plain files across empty/non-empty and encrypted/non-encrypted DBs, verifying callback-collected keys match engine scans. SST tests cover empty/non-empty builds, encryption, multi-file splitting, clone/tmp/path metadata lengths, ingestion into a destination DB, and data equality. The failpoint-gated IO limiter test verifies measured read IO and elapsed time under a mocked read-byte counter. These tests directly exercise the encoding, split, encryption reader/writer, ingestion, and throttling paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/snap/io.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/snapshot_backup.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/snapshot_backup.rs

## Purpose

Coordinates disk snapshot backup preparation with raftstore peers. It provides a router-facing handle for waiting until peers have applied logs, a coprocessor observer that temporarily rejects ingests, selected admin commands, and leader transfers while disk snapshot backup is prepared, and syncer/state types that report wait-apply success or abort back to backup callers.

## Important APIs, Types, And Functions

`SnapshotBrWaitApplyRequest` wraps a `SnapshotBrWaitApplySyncer`, an optional expected region epoch, and a flag that aborts on term changes. `relaxed` waits only to the last index; `strict` also checks epoch and term/commit safety. `SnapshotBrHandle` abstracts `send_wait_apply`, `broadcast_wait_apply`, and `broadcast_check_pending_admin`; the `Arc<Mutex<RaftRouter>>` implementation sends `SignificantMsg::SnapshotBrWaitApply` or `CheckPendingAdmin` through raftstore routing and increments wait-apply metrics.

`PrepareDiskSnapObserver` is a coprocessor with an atomic lease deadline (`before`) and initialized flag. It registers query, admin, and transfer-leader observers, exposes `remained_secs`, `allowed`, `update_lease`, and `reset`, and returns `CopError::RequireDelay` while backup suspension is active. `SnapshotBrWaitApplySyncer` owns a shared `SyncerCore` with `report_id` and a oneshot sender. `SyncReport` reports success or an `AbortReason` (`EpochNotMatch`, `StaleCommand`, or `Duplicated`). `SnapshotBrState::WaitLogApplyToLast` is peer FSM state for waiting until a target index is applied under an optional valid term.

## Control Flow

Backup control code creates a wait-apply request and sends it to one region or broadcasts it. Peer FSM handlers receive the significant message, validate epoch/term requirements, set `SnapshotBrState::WaitLogApplyToLast`, and eventually drop the syncer when the target apply index is reached. `SyncerCore::Drop` sends a success `SyncReport` when the last syncer reference is dropped without abort. Calling `SnapshotBrWaitApplySyncer::abort` takes the oneshot sender immediately, sends an abort report, records the corresponding metric, and makes later drops log that wait apply was aborted.

The prepare observer flow is lease-based. `update_lease` extends the suspension deadline if the new deadline is later, updates a gauge, and records create or renew metrics. `allowed` returns true when no lease exists; when the stored deadline has expired it atomically resets the deadline to zero, updates metrics, and allows traffic again. While the lease is active, query proposals containing `ingest_sst`, admin proposals for split, prepare merge, change peer, witness switch, compact log, and transfer leader requests are rejected with `RequireDelay`.

## State And Persistence Behavior

All state is in memory. The suspension lease is an atomic coarse epoch-second deadline, not persisted. Syncer completion is reference-counted via `Arc<Mutex<SyncerCore>>`; success is signaled by drop of the final clone, while abort consumes the oneshot sender. Metrics record sent/finished/abort events and lease lifecycle. No snapshot data is read or written here; this file protects the raftstore state while other BR components prepare disk snapshots.

## Dependencies And Integration Points

Depends on raftstore `RaftRouter`, `PeerMsg`, `SignificantMsg`, and metrics; `CoprocessorHost` observer registries; query/admin/transfer-leader observer traits; tokio oneshot channels; futures unbounded channels for pending-admin checks; and kvproto admin/epoch/check response types. Peer FSM code consumes `SnapshotBrState` and `SnapshotBrWaitApplyRequest`, while external backup orchestration uses `SnapshotBrHandle` and `PrepareDiskSnapObserver`.

## Risks

The observer deliberately blocks important raftstore operations and can affect transactional workloads if the lease is too long or not reset. `allowed` uses coarse monotonic seconds, so very short leases are approximate. Query rejection marks `cx.bypass = true` for ingests and rejects the entire command batch rather than just the ingest request. `CompactLog` is blocked to preserve logs for restore, which can increase log retention pressure. Syncer success depends on all peer-held clones being dropped; leaks or forgotten state transitions would delay the oneshot result. Duplicate or stale wait-apply commands must abort cleanly to avoid callers believing an unsafe snapshot point is ready.

## Test Signals

This file has no local `#[cfg(test)]` module. Test signals are expected from raftstore peer FSM and BR integration tests that send `SnapshotBrWaitApply`, exercise epoch/term mismatch aborts, wait apply to target index, duplicate requests, pending admin checks, and coprocessor rejection under active backup leases. Operational metrics `SNAP_BR_WAIT_APPLY_EVENT`, `SNAP_BR_LEASE_EVENT`, `SNAP_BR_SUSPEND_COMMAND_LEASE_UNTIL`, and `SNAP_BR_SUSPEND_COMMAND_TYPE` are important runtime signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/snapshot_backup.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/transport.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/transport.rs

## Purpose

Defines raftstore transport and router traits plus concrete adapters for the production `RaftRouter` and test/std channels. It gives store, peer, proposal, casual, significant, and async-read code a small common API while normalizing full/disconnected channel errors into raftstore `Error`/`DiscardReason` values.

## Important APIs, Types, And Functions

`Transport` is the network-facing raft message sender abstraction with `send`, `set_store_allowlist`, `need_flush`, and `flush`. `CasualRouter<EK>` routes best-effort peer messages to a region. `SignificantRouter<EK>` routes forced significant messages to a region, using `EK::Snapshot` in the message type. `ProposalRouter<S>` sends raft commands carrying an engine snapshot. `StoreRouter<EK>` routes messages to the store FSM. Implementations exist for `RaftRouter<EK, ER>`, `&Mutex<T>` wrappers, `mpsc::SyncSender` test channels, and `mpsc::Sender<StoreMsg<EK>>`. `AsyncReadNotifier` is implemented for `RaftRouter` to send fetched raft logs back as a significant peer message.

## Control Flow

Production casual sends call `RaftRouter.router.send(region_id, PeerMsg::CasualMessage(...))`; full mailboxes become `Error::Transport(DiscardReason::Full)`, while disconnected mailboxes become `Error::RegionNotFound(region_id)`. Significant sends call `force_send` so they bypass normal bounded-send behavior; if delivery fails, the code logs at warn for ignorable send failures and error otherwise, then returns `RegionNotFound`. Store routing delegates to `send_control` and maps full/disconnected control mailbox failures to transport discard reasons. Proposal routing delegates to `send_raft_command` and preserves `TrySendError<RaftCommand<S>>`.

The std-channel implementations are mainly adapters for tests or small components: `SyncSender<(u64, CasualMessage<EK>)>` uses `try_send`, `SyncSender<RaftCommand<S>>` maps std `TrySendError` into crossbeam `TrySendError`, and `mpsc::Sender<StoreMsg<EK>>` treats send failure as disconnected. `notify_logs_fetched` ignores missing regions because async-read log fetches can race with region removal; `notify_snapshot_generated` is unreachable for this router implementation.

## State And Persistence Behavior

This file owns no persistent state. Its behavior is defined by the underlying mailbox/router state and channel capacity. The distinction between casual bounded send and significant force send is the important runtime state interaction: significant messages are intended for control paths where dropping on full mailboxes would violate higher-level progress or cleanup expectations.

## Dependencies And Integration Points

Depends on `engine_traits::{KvEngine, RaftEngine, Snapshot}`, kvproto `RaftMessage`, raftstore message enums (`CasualMessage`, `SignificantMsg`, `StoreMsg`, `RaftCommand`, `PeerMsg`), `RaftRouter`, async read notification types, and `crossbeam`/std channel errors. It is re-exported by `store/mod.rs` and used by snapshot generation workers, read workers, PD workers, backup snapshot handling, unsafe recovery, peer FSM helpers, and tests that substitute channel routers.

## Risks

The error mapping is semantically important. Casual peer send treats disconnection as region-not-found, while store send treats it as transport disconnected; changing this can alter retry/drop behavior. Significant messages use force send, so overuse can pressure mailboxes but is required for recovery, snapshot, and control events. The `&Mutex<T>` adapters lock synchronously and can propagate poisoning panics through `unwrap`. `notify_snapshot_generated` being unreachable assumes no caller uses `RaftRouter` as a snapshot-generation notifier; a new caller would panic.

## Test Signals

There are no local tests, but many raftstore worker and FSM tests instantiate mock routers or std-channel implementations of these traits. Useful regression signals include full-channel handling, disconnected-region handling, significant message delivery for unsafe recovery and snapshot backup, proposal routing through read workers, and async-read `RaftlogFetched` notifications being ignored when the region disappears.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/transport.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/txn_ext.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/txn_ext.rs

## Purpose

Stores transaction-related in-memory extensions for a raftstore peer: max timestamp synchronization status after leadership changes and the peer's in-memory pessimistic lock table. It supports memory accounting, lock migration during split/merge/leader transfer, lock scanning for reads/diagnostics, and global metrics for pessimistic lock memory use.

## Important APIs, Types, And Functions

`TxnExt` contains `max_ts_sync_status` and `pessimistic_locks`. The timestamp sync status packs a synced bit, 31 bits of region epoch version, and 32 bits of raft term so stale PD update tasks cannot mark a newer leadership epoch as synced; `is_max_ts_synced` checks the low bit. `INSTANCE_MEM_SIZE` is a process-wide Prometheus gauge for pessimistic lock memory. `PeerPessimisticLocks` owns a `BTreeMap<Key, (PessimisticLock, bool)>`, a `LocksStatus`, raft `term`, region `version`, and per-peer `memory_size`. The bool marks locks that have a proposed but unapplied write deleting them.

`LocksStatus` distinguishes `Normal`, `TransferringLeader`, `MergingRegion`, `NotLeader`, and `IsInFlashback`. Public lock-table methods include `insert`, `remove`, `clear`, `is_empty`, `len`, `is_writable`, `get`, `get_mut`, `group_by_regions`, and `scan_locks`. `IntoIterator for &PeerPessimisticLocks` exposes map iteration. `Drop` subtracts remaining memory from the global gauge. `PessimisticLockPair` abstracts owned/borrowed insertion pairs and is implemented for `(Key, PessimisticLock)`.

## Control Flow

Insertion first computes incremental memory for keys not already present; overwrites do not add memory because the code assumes primary lock memory is stable for overwrite semantics. It rejects the entire input vector if the peer memory limit or global instance memory limit would be exceeded. After passing precheck, it inserts every lock with deleted flag false, updates peer memory, and increments the global gauge. `remove`, `clear`, and `Drop` subtract exactly the recorded key plus lock memory.

`group_by_regions` is used during region split. It requires regions sorted by start key, retains locks still belonging to the derived region, removes locks outside the derived range, clears their deleted marker, binary-searches the destination region by encoded key, moves them into corresponding new `PeerPessimisticLocks`, and transfers memory accounting from the original table to the returned tables. `scan_locks` performs a bounded BTree range scan over optional start/end keys, applies a caller filter, clones matching pessimistic locks into normal `Lock` values, and returns a `has_more` flag when the caller's limit is reached before the scan is exhausted.

## State And Persistence Behavior

All state is volatile peer memory. Pessimistic locks are not persisted here; they are part of raftstore peer runtime state and are coordinated through raft proposals, leadership changes, split/merge flows, and read snapshots. Memory accounting is explicit and mirrored in `INSTANCE_MEM_SIZE`, so every path that moves, removes, clears, or drops locks must keep gauge deltas balanced. The `LocksStatus` state gates writability and migration behavior during topology changes and flashback.

## Dependencies And Integration Points

Depends on `txn_types::{Key, Lock, PessimisticLock}`, kvproto `metapb::Region`, `parking_lot::RwLock`, and Prometheus. `TxnExt` is attached to peers and region snapshots, used by read workers for transactional extra operations, by PD worker max timestamp update tasks, and by peer FSM logic for leader transfer, split, merge, flashback, and applying proposed lock changes. `store/mod.rs` re-exports `LocksStatus`, `PeerPessimisticLocks`, `PessimisticLockPair`, and `TxnExt`.

## Risks

The deleted flag has different required behavior across leader transfer, split, and merge; the long in-code comment documents subtle ordering cases. Incorrectly filtering deleted-marked locks can either resurrect deleted locks or lose locks that must migrate. Memory accounting is manual and global; missed subtracts or double subtracts would skew the metric and potentially reject future locks incorrectly. `group_by_regions` uses `unwrap_or_else(|idx| idx - 1)`, which assumes all removed keys belong to some supplied region and regions cover the keyspace; invalid region inputs can underflow or misroute locks. `scan_locks` clones lock data and can be expensive for large limits. The packed timestamp status must be updated with compare/exchange discipline outside this file or stale sync tasks can incorrectly enable reads after leadership changes.

## Test Signals

Local tests cover per-peer and global memory accounting on insert/overwrite/remove/clear/drop, rejection when peer or global memory limits are exceeded, grouping locks by split regions including deleted-marked locks and rightmost/leftmost ranges, and `scan_locks` behavior for start/end bounds, filters, limits, and `has_more`. The tests serialize global gauge access with a mutex and reset it with `defer`, which is important because the gauge is process-global.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/txn_ext.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/unsafe_recovery.rs -->
# sources/storage-engines/tikv/components/raftstore/src/store/unsafe_recovery.rs

## Purpose

Defines the raftstore side of PD-driven online unsafe recovery. It routes force-leader and recovery-plan commands to peers/store FSMs, models force-leader and unsafe-recovery peer states, coordinates multi-peer phases through drop-triggered syncers, collects peer reports into store reports, and builds raft admin requests for exiting joint state and demoting failed voters.

## Important APIs, Types, And Functions

`UnsafeRecoveryHandle` is the orchestration interface used by PD worker/recovery code. It can send enter-force-leader, create-peer, destroy-peer, demote-peers, broadcast wait-apply, broadcast fill-out-report, broadcast exit-force-leader, and send a final store report. The `Mutex<RaftRouter>` implementation converts these into `SignificantMsg` or `StoreMsg` variants, using force send for store-level recovery messages and treating destroy of an already missing region as success.

`ForceLeaderState` models force-leader progression: `WaitTicks`, `WaitForceCompact`, `PreForceLeader`, and `ForceLeader`. `InvokeClosureOnDrop` runs a boxed closure when the last shared reference drops. `UnsafeRecoveryForceLeaderSyncer`, `UnsafeRecoveryExecutePlanSyncer`, `UnsafeRecoveryWaitApplySyncer`, and `UnsafeRecoveryFillOutReportSyncer` are cloneable phase coordinators. `UnsafeRecoveryState` is per-peer recovery state: `WaitApply`, `DemoteFailedVoters`, `Destroy`, `WaitInitialize`, and `Failed`, with `check_timeout`, `is_abort`, and `abort`. `exit_joint_request` and `demote_failed_voters_request` build raft admin requests for recovery plan execution.

## Control Flow

Unsafe recovery proceeds in phases documented in the file. Report phase starts with `start_unsafe_recovery_report`, which creates a wait-apply syncer and broadcasts `UnsafeRecoveryWaitApply`. When all peer-held wait-apply syncer clones drop, the closure optionally broadcasts exit-force-leader, creates a fill-out-report syncer, and broadcasts `UnsafeRecoveryFillOutReport`. Each peer reports itself into the shared vector; when the last fill-out-report syncer drops, the closure builds a `StoreReport`, sets the report step, and schedules it through `send_report`.

Force-leader phase creates `UnsafeRecoveryForceLeaderSyncer`; when all target peers finish entering force leader and drop it, its closure starts a new report without exiting force leader. Plan execution uses `UnsafeRecoveryExecutePlanSyncer`; when all create/destroy/demote operations drop the syncer without abort, its closure starts a report with `exit_force_leader = true`. If any execution path calls `abort`, the shared flag prevents the drop closure from scheduling the next report. Peer FSM code consumes `UnsafeRecoveryState` to wait for apply indexes, destroy peers, initialize created peers, demote failed voters, and handle timeout/abort.

`demote_failed_voters_request` creates a `ChangePeerV2` admin request: failed voters become learners, failed learners are removed, and the local peer is promoted to voter if it is currently learner. It returns `None` when no changes are needed. `exit_joint_request` builds an empty `ChangePeerV2` request to leave joint consensus before demotion when required.

## State And Persistence Behavior

This file owns in-memory coordination state only. Long-lived recovery progress is represented by peer/store FSM state and PD reports outside this file. Syncer state is reference-counted; progress to the next phase depends on all relevant clones being dropped. Abort flags are shared `Arc<Mutex<bool>>`, and report collection is an `Arc<Mutex<Vec<PeerReport>>>`. The generated raft admin requests are persisted only when later proposed and applied by raftstore.

## Dependencies And Integration Points

Depends on raftstore routing (`RaftRouter`, `SignificantRouter`, `PeerMsg`, `StoreMsg`, `SignificantMsg`), peer FSM/admin helpers (`new_admin_request`, `new_change_peer_v2_request`), kvproto PD and metapb recovery/report/change-peer types, raft `ConfChangeType`, and `collections::HashSet`. PD worker code constructs the syncers and calls `UnsafeRecoveryHandle`; peer FSM code handles the corresponding significant messages and uses `ForceLeaderState`, `UnsafeRecoveryState`, `exit_joint_request`, and `demote_failed_voters_request`.

## Risks

The drop-driven coordination is compact but fragile: leaked syncer clones stall phases, and premature drops can advance phases before peer work really finished. Abort only suppresses future closure action; it does not undo already sent peer/store messages. Force leader intentionally bypasses normal raft safety assumptions for recovery, so message routing, failed-store sets, and demotion request construction must be exact. `demote_failed_voters_request` contains a duplicated `let mut cp` inside the learner removal branch, which is harmless after shadowing but easy to misread. The request builder assumes the supplied `failed_voters` and `region.peers` roles are current enough for the recovery plan. `send_destroy_peer` treats missing regions as success, which is correct for idempotent destruction but could hide an unexpected region-id mismatch.

## Test Signals

There are no local unit tests in this file. Regression coverage should come from PD worker and peer FSM unsafe-recovery tests that enter force leader, wait for apply, create peers, destroy peers, demote failed voters from joint and non-joint states, abort timed-out states, collect reports, and verify generated `ChangePeerV2` requests. Runtime logs around phase completion/abort and PD `StoreReport` contents are important operational signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/raftstore/src/store/unsafe_recovery.rs -->
