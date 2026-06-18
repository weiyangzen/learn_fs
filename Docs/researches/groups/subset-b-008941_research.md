# subset-b-008941 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/prewrite.rs -->
# sources/storage-engines/tikv/src/storage/txn/commands/prewrite.rs

## Purpose
`prewrite.rs` implements the storage scheduler commands for optimistic and pessimistic transaction prewrite. This is the first phase of TiKV's 2PC protocol, with extensions for async commit, 1PC, pessimistic-lock checking, assertion checking, retry idempotence, and CDC old-value collection. The file centralizes both public commands behind a generic `Prewriter<K>` so most MVCC write-loop behavior is shared while transaction-kind specific differences are isolated.

## Important APIs, types, and functions
The command macro defines `Prewrite` and `PrewritePessimistic`, both returning `PrewriteResult`. `Prewrite` carries `Vec<Mutation>`, primary key, `start_ts`, TTL, transaction size, min/max commit timestamps, optional async-commit secondaries, `try_one_pc`, and assertion level. `PrewritePessimistic` carries `(Mutation, PrewriteRequestPessimisticAction)` plus `for_update_ts` and `for_update_ts_constraints`.

`Prewriter<K>` is the main executor. `PrewriteKind` abstracts `txn_kind()` and optimistic-only `can_skip_constraint_check()`. `MutationLock` abstracts plain optimistic mutations and `PessimisticMutation`, which adds pessimistic action and optional expected `for_update_ts`. Public helper functions include `one_pc_commit()` and crate-visible `fallback_1pc_locks()`.

## Control flow
`process_write` first handles a pessimistic retry special case by checking `txn_status_cache` for a known commit and forcing retry semantics. It then lets the transaction kind skip or enforce constraints, checks that the snapshot's max timestamp is synced for async commit or 1PC, creates an `MvccTxn` and `SnapshotReader`, and calls `prewrite()`.

`prewrite()` computes `CommitKind` as 1PC, async commit, or normal 2PC. It builds `TransactionProperties` and iterates all mutations. For the async primary key it passes the full secondary set; for other async keys it passes an empty set. Each mutation delegates to `actions::prewrite::prewrite`. Successful async or 1PC results update the final min commit timestamp and old-value map. A zero min-commit timestamp forces fallback to 2PC, clears async/1PC flags, moves pending 1PC locks into normal lock CF writes, and releases memory guards. Write conflict, missing pessimistic lock, key-locked, and commit-ts-too-large paths call `check_committed_record_on_err` to preserve idempotence for retried prewrites that already committed.

`write_result()` emits either a write batch with locks and optional 1PC commit writes, or a lock-error-only response with no writes. Async commit and successful 1PC may switch the response policy to `OnCommitted` when `async_apply_prewrite` is enabled.

## State and persistence behavior
The command writes MVCC locks, write records for 1PC, old-value metadata in `TxnExtra`, known committed transaction status for cache promotion, lock guards, and released-lock notifications. It persists normal lock CF records for 2PC/async commit, and for 1PC converts collected locks directly into write CF records at `final_min_commit_ts` before unlocking pessimistic locks. It also sets disk-full options from context and supports old-value collection when `ExtraOp::ReadOldValue` is requested.

## Dependencies and integration points
This file depends on `txn_types` mutations, locks, timestamps, writes, and old values; `MvccTxn` and `SnapshotReader`; `actions::prewrite`; `check_committed_record_on_err`; lock manager guards; scheduler `WriteCommand`; and metrics. It integrates with async commit/1PC timestamp safety through `SnapshotExt::is_max_ts_synced`, with conflict retry through `txn_status_cache`, with CDC through `TxnExtra`, and with commit/rollback commands through the locks it leaves or releases.

## Risks
The main correctness risks are atomicity during 1PC, retry idempotence after partial network failures, async/1PC fallback without leaving stale memory locks, commit timestamp bounds, and pessimistic `for_update_ts` validation. The optimistic bulk skip path sorts mutations and may skip constraint checks only when no write data exists in the target range; mistakes there can violate uniqueness or conflict semantics. Assertion errors are deliberately delayed behind more concrete errors, which is important for index-key conflict behavior.

## Test signals
The embedded tests are extensive. They cover skip-constraint checks and tombstones, optimistic and pessimistic 1PC, async commit fallback, max-ts sync rejection, response policy selection, `CheckNotExists`, committed and rolled-back retry idempotence, newer-lock encounters, commit-ts-too-large retry recovery, last-change timestamp calculation, pessimistic `for_update_ts` constraints, and shared-lock prewrite restrictions. These tests are strong regression signals for transaction protocol edge cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/prewrite.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock.rs -->
# sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock.rs

## Purpose
`resolve_lock.rs` implements the write phase of resolving stale or known transaction locks. It consumes a `txn_status` map from lock start timestamp to commit timestamp, plus a batch of key-lock pairs found by `ResolveLockReadPhase`, and either commits or rolls back each lock. It is used by GC and lock resolution paths after transaction status has already been determined.

## Important APIs, types, and functions
The `ResolveLock` command returns `()` and carries `HashMap<TimeStamp, TimeStamp>`, optional `scan_key`, and `Vec<(Key, Lock)>`. A zero commit timestamp means rollback; a nonzero timestamp greater than the lock timestamp means commit. `RESOLVE_LOCK_BATCH_SIZE` is 256 and is shared with the read phase. The command is marked as `is_sys_cmd`, uses `gen_lock!` on the resolved keys, and records write bytes as the encoded key sizes.

## Control flow
`process_write` creates an `MvccTxn` at timestamp zero and a zero-start `SnapshotReader`, then iterates the supplied key locks. For each lock it sets both `txn.start_ts` and `reader.start_ts` to the lock timestamp, looks up the transaction status, and dispatches to `cleanup()` for rollback or `commit()` for commit. A commit timestamp less than or equal to the lock timestamp is rejected as `InvalidTxnTso`. If `commit()` returns `TxnLockNotFound` for a pessimistic lock, the command treats it as harmless because such locks can be left behind after committed pessimistic conflict retries.

The loop stops early when `txn.write_size()` reaches `MAX_TXN_WRITE_SIZE`. In that case it records the current key as the next scan position and returns a `NextCommand` containing another `ResolveLockReadPhase`. Otherwise it returns `ProcessResult::Res`.

## State and persistence behavior
The command produces MVCC writes through `commit()` or rollback records and lock deletes through `cleanup()`. It accumulates released locks for wakeups, new acquired locks from MVCC side effects, and deduplicated `(start_ts, commit_ts)` pairs in `known_txn_status` for committed transactions. The output `WriteData` is explicitly allowed on almost-full disks because lock resolution and GC cleanup are system maintenance operations.

## Dependencies and integration points
It depends on `cleanup`, `commit`, `MvccTxn`, `SnapshotReader`, `MAX_TXN_WRITE_SIZE`, scheduler `WriteCommand`, and the paired `ResolveLockReadPhase`. It integrates with lock-manager wakeups through `ReleasedLocks`, with transaction-status caching through `known_txn_status`, and with the command scheduler by returning a follow-up read command when a batch is too large.

## Risks
The largest risk is resolving multiple shared sub-locks for the same key using a single snapshot. Since pending writes are invisible within the loop, repeated updates to one shared-lock record can overwrite each other unless lower-level shared-lock operations merge correctly. Other risks are incorrect scan continuation after write-size cutoff, missing transaction status entries due to the `expect`, and handling of stale pessimistic locks without hiding real commit errors.

## Test signals
The tests construct shared locks with multiple sub-locks on one key and validate all rollback and mixed commit/rollback results. They also verify an unresolved sibling sub-lock remains and that a final resolve unlocks the key. These tests directly target the snapshot-overwrite risk in batched shared-lock resolution.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock_lite.rs -->
# sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock_lite.rs

## Purpose
`resolve_lock_lite.rs` implements a compact lock-resolution command for a known transaction and an explicit key list. Unlike the full two-phase resolve path, it does not scan lock CF and does not batch by write size. It is intended for client-provided `resolve_keys` where the list is guaranteed to be small enough.

## Important APIs, types, and functions
The `ResolveLockLite` command carries `start_ts`, `commit_ts`, and `Vec<Key>`. It is a system write command using the `KvResolveLock` request type, latches all `resolve_keys`, and measures write bytes over those keys. A zero `commit_ts` means rollback; a nonzero `commit_ts` means commit all listed keys for `start_ts`.

## Control flow
`process_write` creates an `MvccTxn` and `SnapshotReader` at `start_ts`. It loops over `resolve_keys`, calling `commit()` with the given commit timestamp when nonzero or `cleanup()` when zero. It accumulates released locks and then builds a `WriteResult` with `ProcessResult::Res`.

## State and persistence behavior
The command persists the write records, rollback records, and lock removals produced by `commit()` or `cleanup()`. It marks the resulting write data as allowed on an almost-full disk. On commit it emits a single known transaction status tuple `(start_ts, commit_ts)`; on rollback it emits none. It does not use lock guards and always responds `OnApplied`.

## Dependencies and integration points
It depends on `MvccTxn`, `SnapshotReader`, `commit`, `cleanup`, and the scheduler write-command traits. It integrates with transaction status cache promotion via `known_txn_status`, with lock wakeups through `ReleasedLocks`, and with client-side lock resolver logic that chooses exact keys.

## Risks
The file relies on the client guarantee that `resolve_keys` is not too large. If that assumption breaks, this command can build an oversized write batch because it lacks the `MAX_TXN_WRITE_SIZE` continuation logic present in `ResolveLock`. It also assumes all keys belong to the same `start_ts`; mixed transactions will surface through lower-level MVCC errors.

## Test signals
There are no local tests in this file. Behavior is indirectly exercised by transaction lock resolver tests that use `commit()` and `cleanup()` and by any higher-level `KvResolveLock` tests that choose the lite path. Missing local tests make key-list size assumptions and shared-lock behavior important review points.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock_lite.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock_readphase.rs -->
# sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock_readphase.rs

## Purpose
`resolve_lock_readphase.rs` implements the read/scanning phase for full lock resolution. It scans storage for locks whose start timestamps appear in a supplied transaction-status map, flattens normal and shared-lock records into individual `(Key, Lock)` pairs, and schedules `ResolveLock` as the write phase.

## Important APIs, types, and functions
The `ResolveLockReadPhase` command carries `HashMap<TimeStamp, TimeStamp>` and optional `scan_key`. It is a readonly `KvResolveLock` command. Its main API is `ReadCommand::process_read`, which returns either `ProcessResult::Res` or `ProcessResult::NextCommand { Command::ResolveLock }`. It uses shared `RESOLVE_LOCK_BATCH_SIZE`.

## Control flow
`process_read` builds an `MvccReader` in forward scan mode and calls `scan_locks_from_storage` with an optional lower bound and a filter that accepts locks whose `lock.ts` is in `txn_status`. For normal locks it pushes one `(key, lock)`. For `SharedLocks`, it iterates contained timestamps, filters again against `txn_status`, and pushes one pair per matching sub-lock using the same key. It records key-read histogram data using the flattened count.

If no matching pairs are found, the command returns `Res`. Otherwise it computes `next_scan_key` from the last flattened key when the scanner reports remaining data, and returns a `ResolveLock` command containing the flattened batch.

## State and persistence behavior
This phase is read-only and does not mutate MVCC state. It updates read statistics from `MvccReader` and records key-read histograms. Its state handoff is the flattened lock list and optional continuation key embedded in the write-phase command.

## Dependencies and integration points
It depends on `MvccReader::scan_locks_from_storage`, `tikv_util::Either` for normal versus shared locks, scheduler `ReadCommand`, and `ResolveLock`. It is the front half of the system-command flow described in `resolve_lock.rs`, and its continuation key determines whether lock resolution loops through the whole lock CF.

## Risks
Flattening a single shared-lock key into many pairs creates duplicate keys in one write batch. That is necessary to resolve sub-locks but can stress write-phase snapshot behavior. Large shared-lock records also create progress risk: if continuation always restarts at the same key without resolving enough sub-locks, the loop could repeat. The included tests specifically target this risk.

## Test signals
Tests verify that shared pessimistic locks are filtered by transaction status, that unrelated shared sub-locks are ignored, and that a single key with more than `RESOLVE_LOCK_BATCH_SIZE` sub-locks progresses through multiple read/write rounds without duplicate unresolved subsets and eventually unlocks the key.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/resolve_lock_readphase.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/rollback.rs -->
# sources/storage-engines/tikv/src/storage/txn/commands/rollback.rs

## Purpose
`rollback.rs` implements the transaction rollback command for a set of keys at one `start_ts`. It is the explicit cleanup counterpart to prewrite and is used when a transaction is known to have failed or must be aborted.

## Important APIs, types, and functions
The `Rollback` command carries `Vec<Key>` and `start_ts`, returns `()`, uses `KvRollback`, and latches every key. Its only execution entry point is `WriteCommand::process_write`.

## Control flow
`process_write` creates an `MvccTxn` and `SnapshotReader` at `start_ts`, then loops through all keys and calls `cleanup()` with `TimeStamp::zero()` as the current timestamp and `protect_rollback` set to `false`. The comment explains that explicit rollback is called when the transaction is known to fail, so the rollback record does not need protection. It collects released locks and returns a normal applied write result.

## State and persistence behavior
The command persists rollback records and lock removals produced by `cleanup()`. It can also remove a sub-lock from `SharedLocks`. The write data is allowed on an almost-full disk. It emits no known committed transaction status and no lock guards.

## Dependencies and integration points
It depends on `MvccTxn`, `SnapshotReader`, `cleanup`, and scheduler write-command traits. It integrates with prewrite by removing locks left by the first phase, with lock-manager wakeups through `ReleasedLocks`, and with shared-lock storage through lower-level cleanup support.

## Risks
The primary risk is preserving idempotence when rollback records already exist or when pessimistic locks and prewrite locks for the same transaction are interleaved across keys. Since rollback records are unprotected here, callers must only use this command for known-aborted transactions. Shared-lock rollback must update only the matching sub-lock and leave siblings intact.

## Test signals
Tests cover rollback when a rollback record already exists, later pessimistic prewrite on another key with the same start timestamp, and shared-lock rollback. The shared-lock test verifies one sub-lock is removed while the other remains, then the final rollback unlocks the key and stores unprotected rollback records.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/rollback.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/txn_heart_beat.rs -->
# sources/storage-engines/tikv/src/storage/txn/commands/txn_heart_beat.rs

## Purpose
`txn_heart_beat.rs` implements transaction heartbeat handling for a primary lock. A heartbeat extends the TTL of an uncommitted transaction and can piggyback a newer min-commit timestamp for non-async-commit pipelined locks.

## Important APIs, types, and functions
The `TxnHeartBeat` command carries `primary_key`, `start_ts`, `advise_ttl`, and `min_commit_ts`, and returns `TxnStatus`. It is a write command using request type `KvTxnHeartBeat`. Test helpers expose `txn_heart_beat`, `must_success`, and `must_err`.

## Control flow
`process_write` creates an `MvccTxn` and `SnapshotReader` at `start_ts`, then loads the lock for `primary_key`. If it finds a normal lock with matching timestamp, it updates TTL when `advise_ttl` is larger. It updates `min_commit_ts` only when the lock is not async commit, has positive generation, the request carries a positive min commit timestamp, and the request value is larger than the current one. If anything changed, it writes the updated lock back with `put_lock`.

If the key contains `SharedLocks` with the requested start timestamp, the command rejects it with `PrimaryMismatch`, because a shared-locked key is not a valid primary key by design. Missing or mismatched locks produce `TxnNotFound`.

## State and persistence behavior
The only persistent mutation is an updated primary lock record. Heartbeat never releases locks, so `released_locks` is empty and no waiters are woken. The response contains `TxnStatus::uncommitted(lock, false)` reflecting the final lock state. Writes are allowed on almost-full disks.

## Dependencies and integration points
It depends on `MvccTxn`, `SnapshotReader`, `TxnStatus`, `txn_types::Lock`, and shared-lock detection via `tikv_util::Either`. It integrates with lock TTL management for long-running transactions, pipelined transaction min-commit timestamp propagation, and scheduler latching for the primary key.

## Risks
The command must not accidentally mutate shared-lock records, because heartbeats are only valid for primary locks. The min-commit timestamp update is intentionally narrow; broadening it to async-commit or non-pipelined locks could violate commit timestamp rules. Another risk is returning success for the wrong transaction if only the key matches; the code guards this by checking lock timestamp.

## Test signals
Tests cover TTL extension, no-op lower TTL requests, missing locks, wrong timestamps, committed/unlocked keys, pessimistic locks, piggybacked min-commit timestamp updates, and rejection of shared-lock keys including shared locks with pipelined fields. They also verify shared-lock records remain unchanged on heartbeat errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/commands/txn_heart_beat.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/flow_controller/mod.rs -->
# sources/storage-engines/tikv/src/storage/txn/flow_controller/mod.rs

## Purpose
`flow_controller/mod.rs` is the facade for transaction scheduler flow control. It exposes a single `FlowController` enum over the singleton engine-wide controller and the per-tablet controller, allowing the rest of storage code to call one API regardless of engine deployment mode.

## Important APIs, types, and functions
The module publicly re-exports `EngineFlowController` and `TabletFlowController`, declares submodules, and defines `FlowController::{Singleton, Tablet}`. It forwards `should_drop`, `consume`, `unconsume`, `is_unlimited`, `update_config`, `enable`, and `enabled`; tests also get `discard_ratio`, `total_bytes_consumed`, and `set_speed_limit`. The `flow_controller_fn!` macro reduces forwarding boilerplate.

## Control flow
All methods simply match on the enum variant and delegate to the underlying implementation. `consume(region_id, bytes)` returns a delay duration from the relevant limiter. `should_drop(region_id)` performs probabilistic admission control in the underlying controller. `update_config` mutates the shared online config tracker owned by the concrete controller.

## State and persistence behavior
This module owns no state beyond the enum variant. All mutable runtime state lives in `singleton_flow_controller.rs` or `tablet_flow_controller.rs`: limiters, discard ratios, background checker threads, config trackers, and per-region maps. No persistent storage is touched here.

## Dependencies and integration points
It depends on `online_config::ConfigChange` and `Duration`, and integrates transaction scheduler callers with both flow-control backends. The facade lets scheduler code remain independent of whether TiKV is using one RocksDB instance or tabletized per-region engines.

## Risks
The main risk is API drift between the singleton and tablet controllers. Because forwarding is manual or macro-generated, any new method must be implemented consistently in both concrete controllers and forwarded here. Region ID semantics also differ by backend: singleton ignores region ID, while tablet mode depends on it.

## Test signals
This file has no local tests, but the concrete controller tests exercise the facade by wrapping controllers in `FlowController` and calling common helper functions. That provides indirect coverage for forwarding correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/flow_controller/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/flow_controller/singleton_flow_controller.rs -->
# sources/storage-engines/tikv/src/storage/txn/flow_controller/singleton_flow_controller.rs

## Purpose
`singleton_flow_controller.rs` implements engine-wide scheduler flow control for a single RocksDB engine. It throttles foreground writes before raftstore/apply work is blocked by RocksDB write stalls. It combines a byte-rate `Limiter` with probabilistic request dropping driven by compaction pending bytes.

## Important APIs, types, and functions
`EngineFlowController` owns a global `discard_ratio`, global `Limiter`, control channel, background checker handle, and `VersionTrack<FlowControlConfig>`. Public APIs are `new`, `empty`, `should_drop`, `consume`, `unconsume`, `enable`, `enabled`, `update_config`, and `is_unlimited`. The background worker is `FlowChecker<E>`, parameterized by `FlowControlFactorStore`. `CfFlowChecker` stores per-CF smoothers for memtables, L0 files, L0 production and consumption flow, pending compaction bytes, unsafe destroy range handling, and startup suppression flags.

## Control flow
`EngineFlowController::new` builds a millisecond-refill limiter, wraps config in `VersionTrack`, creates `FlowChecker`, and starts a named background thread. The thread listens for close/enable/disable messages and RocksDB `FlowInfo` events. Flush events update L0 production, memtable state, and L0 state. L0/L0Intra events update consumption and L0 state. Compaction events update pending compaction bytes. Timeout ticks update aggregate foreground write-flow statistics and metrics.

Memtable control initializes throttling from recent foreground write p90, then adjusts speed by roughly 1 MiB/s per memtable trend. L0 control slows speed by `K_INC_SLOWDOWN_RATIO` while above threshold and releases control when below threshold. Pending-compaction control maps log2 pending bytes from soft to hard limits into a discard ratio, smoothed by EMA. Unsafe destroy range can freeze pending-bytes control when compaction bytes jump artificially.

## State and persistence behavior
All state is in memory: smoother windows, limiter speed/statistics, atomic discard ratio, selected throttle CF, last speed, startup flags, metrics, and background thread lifecycle. It does not persist data to RocksDB; it only observes RocksDB factors and controls scheduler admission or delay. `Drop` sends `Msg::Close` and joins the checker thread.

## Dependencies and integration points
It depends on RocksDB `FlowInfo`, engine traits for CF names and flow factors, `tikv_util::Limiter` and `Smoother`, online config, scheduler metrics, and thread naming utilities. It integrates at the scheduler boundary: callers check `should_drop`, call `consume`, and sleep or reject based on the result.

## Risks
Control stability is the key risk. Too aggressive speed reduction can collapse QPS; too weak control allows RocksDB write stalls. Startup suppression must avoid throttling on inherited backlog while still detecting new accumulation. Pending compaction bytes are noisy, so log scaling and EMA must avoid both NaN from zero and stale high averages after destroy range. Background thread channel sends use `unwrap` in enable/disable, so lifecycle misuse can panic if called after channel closure.

## Test signals
Tests use an `EngineStub` to exercise facade behavior, memtable thresholds, L0 thresholds, pending compaction bytes, zero pending bytes, and unsafe-destroy-range jump control. Helpers are shared with tablet tests, giving parity signals between both flow-control modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/flow_controller/singleton_flow_controller.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/flow_controller/tablet_flow_controller.rs -->
# sources/storage-engines/tikv/src/storage/txn/flow_controller/tablet_flow_controller.rs

## Purpose
`tablet_flow_controller.rs` adapts scheduler flow control to tabletized storage where each region can have its own engine instance and limiter. It preserves the singleton flow-checking logic per region while adding lifecycle management and a global pending-compaction discard controller.

## Important APIs, types, and functions
`TabletFlowFactorStore<EK>` wraps `TabletRegistry<EK>` and implements `FlowControlFactorStore` by querying the latest tablet for a region. `TabletFlowController` owns a control channel, dispatcher thread, `Limiters` map from region ID to `(Limiter, discard_ratio)`, a `global_discard_ratio`, and config tracker. `FlowInfoDispatcher` owns the background event loop. `CompactionPendingBytesChecker` aggregates per-region pending bytes by CF and feeds a global `FlowChecker`.

## Control flow
`TabletFlowController::new` creates the shared maps and starts the dispatcher. The dispatcher receives flow-control messages and `FlowInfo`. L0, L0Intra, and Flush events are routed only to an existing region checker. Compaction events update the region checker, report the current pending bytes to the global checker, and recompute global pending-byte discard ratio. Created events insert or reference-count a region `FlowChecker`, creating a limiter and per-region discard ratio if needed. Destroyed events decrement the checker reference count, remove the checker and limiter when it reaches zero, and remove that region's pending-byte contribution.

Read-side APIs look up the region limiter under an `RwLock`. Unknown regions are unlimited and never dropped. `should_drop` uses the maximum of the region discard ratio and global discard ratio.

## State and persistence behavior
State is in memory: per-region limiters, per-region atomic discard ratios, checker reference counts, global discard ratio, pending-byte aggregation, online config, and background thread lifecycle. No persistent data is modified. Region/tablet existence comes from `TabletRegistry`, but this module only observes it.

## Dependencies and integration points
It depends on `TabletRegistry`, `FlowInfo`, `FlowChecker` from the singleton module, online config, limiter utilities, and scheduler metrics. It integrates storage tablet lifecycle events with scheduler flow control and lets the facade in `mod.rs` treat tablet mode like singleton mode.

## Risks
Lifecycle races are the main risk. Events for a region before `Created` or after `Destroyed` are ignored, which is safe but can miss pressure signals. Reference counts must match create/destroy events or limiters can leak or disappear too early. Pending-compaction aggregation must remove destroyed regions promptly or global discard ratio can stay high. The global checker uses region ID 0 and a dummy limiter, so only discard-ratio behavior should be relied on there.

## Test signals
Tests create a temporary tablet registry, load tablet contexts, and exercise basic facade behavior, create/destroy lifecycle including duplicate creates, memtable control, L0 control, and pending-compaction discard behavior. These tests reuse singleton helper assertions, which checks consistency across controller modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/flow_controller/tablet_flow_controller.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/latch.rs -->
# sources/storage-engines/tikv/src/storage/txn/latch.rs

## Purpose
`latch.rs` implements scheduler latches that serialize commands touching overlapping keys before they enter MVCC write processing. It is an in-memory concurrency-control structure, not an MVCC lock. Commands hash their keys into latch queues and proceed only when they are first for every required key hash.

## Important APIs, types, and functions
`Lock` is the public per-command latch request. It contains sorted deduplicated `required_hashes` and `owned_count`, with helpers `new`, `hash`, `acquired`, `force_assume_acquired`, and `is_write_lock`. `Latches` is the public latch table with `new`, `acquire`, and `release`. Internal `Latch` stores a `VecDeque<Option<(key_hash, command_id)>>` and supports `get_first_req_by_hash`, `pop_front`, `wait_for_wake`, `push_preemptive`, and queue shrinking.

## Control flow
`Lock::new` hashes all keys, sorts them, and deduplicates them to avoid deadlock and repeated acquisition. `Latches::acquire` resumes from `lock.owned_count`, locks the slot for each key hash, and checks the first queued request with that exact hash. If the current command is already first, it counts as acquired. If no matching request exists, it enqueues itself and counts as acquired. If another command is first, it enqueues itself and stops, leaving the command partially acquired.

`release` removes the current command from every owned latch and returns command IDs to wake. It can transfer a subset of latches to a next command by preemptively pushing that command to the front instead of waking waiters for those hashes. This supports command chaining while preserving ordering. The caller must ensure the releasing command is at the front.

## State and persistence behavior
All state is volatile memory under `parking_lot::Mutex` and cache-padded slots. Holes are left in queues when a non-front matching entry is removed, and `maybe_shrink` removes front holes and shrinks large queues when they become small. No disk state is touched.

## Dependencies and integration points
It depends on Rust hashing, `VecDeque`, `parking_lot`, and `crossbeam::CachePadded`. It integrates with scheduler command definitions through `gen_lock!`, which builds `Lock` objects from command keys. MVCC write commands rely on latches to serialize conflicting key operations before snapshot/write processing.

## Risks
Correctness depends on the invariant that if command A precedes command B in one overlapping latch, it precedes B in all overlapping latches. Sorting and deduplication help preserve this. Partial acquisition must be retried with the same `Lock` and command ID; misuse can leave stale queue entries. The preemptive transfer path is powerful but risky: the kept latch set must be a sorted subset of the released lock, and the next command must force or complete acquisition consistently.

## Test signals
Tests cover wakeup ordering for overlapping keys, multiple independent commands, small latch-slot counts that force hash-slot collisions, and partial release/transfer behavior for single and multiple keys with and without queued waiters. They also verify latches become empty after release sequences.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/src/storage/txn/latch.rs -->
