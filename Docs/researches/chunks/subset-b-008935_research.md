# sources/storage-engines/tikv/src/storage/mod.rs lines 7121-12607

## Chunk Scope

This chunk is the tail of `sources/storage-engines/tikv/src/storage/mod.rs`. It is inside the module's storage test suite and starts in the closing assertions of a raw batch delete test, then covers raw KV scan/CAS/TTL tests, transactional lock scan and resolve tests, pessimistic-lock and lock-manager integration tests, in-memory lock checks, async commit/1PC cache behavior, API-version validation, and shared-lock scan coverage.

The researched source span is `sources/storage-engines/tikv/src/storage/mod.rs:7121-12607`. The production APIs under test are defined earlier in the same file and in storage transaction/raw command modules; this chunk exercises them through `TestStorageBuilder`, `sched_txn_command`, async raw storage methods, and mock engines/lock managers.

## Purpose

The chunk establishes behavioral guarantees for TiKV's storage facade across two major surfaces:

- RawKV operations: scans, batch scans, TTL reporting, atomic compare-and-swap, compare-and-delete, and API V1/V1ttl/V2 key-mode validation.
- Transactional MVCC operations: lock discovery, lock resolution, heartbeat/status checks, secondary-lock checks, pessimistic lock acquisition/rollback, lock waiting, async commit and 1PC timestamps, response callback policy, in-memory pessimistic locks, transaction status cache updates, and shared-lock reporting.

Most tests run through the top-level `Storage` abstraction instead of directly invoking lower-level MVCC readers/writers. This makes the tests useful integration signals for scheduler behavior, concurrency-manager timestamp maintenance, engine persistence, lock-manager callbacks, and protocol-level `kvrpcpb` response structures.

## Important APIs, Types, and Test Helpers

### RawKV API coverage

- `Storage::raw_scan(ctx, cf, start_key, end_key, limit, key_only, reverse)` is tested for forward and reverse scans, optional end keys, key-only output, limits, and API V2 raw key prefix constraints.
- `Storage::raw_batch_scan(ctx, cf, ranges, each_limit, key_only, reverse)` is tested over multiple `KeyRange` inputs with forward and reverse ordering and per-range limits.
- `Storage::raw_get`, `raw_batch_get`, `raw_put`, `raw_batch_put`, and `raw_batch_put_atomic` are used to seed and verify raw state.
- `raw_batch_delete`, `raw_batch_delete_atomic`, and the preceding chunk's delete setup are checked for complete key removal and for not leaking `global_min_lock_ts`.
- `raw_get_key_ttl` is validated against `ttl_current_ts()` and explicit TTLs, including no-TTL (`0`) and `u64::MAX` TTL values.
- `raw_compare_and_swap_atomic` is tested both as a put-style CAS and a delete-style CAS using the `is_delete` flag.

### Transactional command API coverage

The chunk exercises scheduler commands from `crate::storage::txn::commands`, including:

- `AcquirePessimisticLock`
- `Prewrite`
- `PrewritePessimistic`
- `Commit`
- `Rollback`
- `Cleanup`
- `PessimisticRollback`
- `ResolveLockReadPhase`
- `ResolveLock`
- `ResolveLockLite`
- `TxnHeartBeat`
- `CheckTxnStatus`
- `CheckSecondaryLocks`

Commands are submitted through `Storage::sched_txn_command`, and callbacks assert either success values or expected error chains such as `KeyIsLocked`, `WriteConflict`, `TxnNotFound`, and `TxnLockNotFound`.

### Lock and MVCC types

The tests construct or inspect:

- `Key`, `Mutation`, `TimeStamp`, `Lock`, `PessimisticLock`, `LastChange`, `LockType`, and `WriteType` from the MVCC/transaction type layer.
- Protocol response structures such as `LockInfo`, `SecondaryLocksStatus`, `TxnStatus`, and `Op`.
- `PessimisticLockResults` and `PessimisticLockKeyResult`, including `Empty`, `Value`, `Existence`, and `LockedWithConflict`.
- `KeyLockWaitInfo`, `LockDigest`, `LockWaitToken`, `WaitTimeout`, and `CancellationCallback` for lock-wait manager integration.

### Test infrastructure and custom lock manager

- `TestStorageBuilderApiV1` and `TestStorageBuilder::<_, _, F>` build storage instances over test engines and `MockLockManager`.
- `test_kv_format_impl!` runs RawKV tests over applicable API formats, especially API V1, API V1ttl, and API V2.
- `TxnExt` is used to inspect the in-memory pessimistic lock map.
- `ProxyLockMgr` implements `LockManager` and forwards `wait_for`/`remove_lock_wait` calls into a channel as `Msg` values, allowing direct verification of lock-wait messages.
- Helpers such as `expect_ok_callback`, `expect_fail_callback`, `expect_value_callback`, `expect_multi_values`, `must_locked`, `must_unlocked`, `must_written`, `must_rollback`, `must_have_locks`, `acquire_pessimistic_lock`, `prewrite_lock`, and `delete_pessimistic_lock_with_scan_first` assert persisted state and callback results.

## Control Flow and Behavioral Coverage

### Raw scans and batch scans

`test_raw_scan_impl` seeds 20 `r\0*` raw keys, then verifies:

1. Key-only scans return empty values while preserving key order.
2. Forward scans start at inclusive start keys and obey optional end-key upper bounds.
3. Reverse scans walk backward from the start key and obey optional lower bounds.
4. Limits cap output count.
5. API V2 uses explicit raw-mode range bounds such as `r\0z` and `r\0\0`, while API V1 permits unbounded raw scans.

`test_check_key_ranges` validates `StorageApiV1::check_key_ranges` for monotonic forward ranges, omitted end keys, invalid descending ranges, and reverse-scan ordering.

`test_raw_batch_scan_impl` extends the same dataset to multiple `KeyRange` inputs. It checks that each range contributes at most the requested per-range limit, that key-only mode strips values, and that reverse batch scans preserve reverse ordering independently per range and across descending ranges.

### Raw TTL and atomic CAS

`test_raw_get_key_ttl_impl` writes keys with TTL values and verifies the remaining TTL is between the elapsed-time adjusted lower bound and the original TTL. A TTL of `0` is reported as `0`.

`test_raw_compare_and_swap_impl` covers CAS transitions:

1. Mismatched expected value on an absent key fails and returns the previous value.
2. `None` expected on an absent key succeeds.
3. Matching current value succeeds and updates the value.
4. Mismatched current value fails without changing state.
5. CAS interleaves with atomic batch put/delete and leaves `global_min_lock_ts` unset.

`test_raw_compare_and_swap_delete_impl` exercises CAS delete semantics: matching existing value deletes, mismatching expected value preserves the current value, `None`/`None` delete is a successful no-op, and expecting `None` against an existing value fails.

### Lock scan, resolve, heartbeat, and transaction status

`test_scan_lock_with_memory_lock` verifies that `scan_lock` includes both in-memory pessimistic locks and persisted prewrite locks when in-memory pessimistic locks are enabled. It checks returned `LockInfo` fields for primary key, start version, for-update timestamp, min-commit timestamp, TTL, and lock type.

`test_scan_lock` prewrites two lock groups and verifies:

- `scan_lock` updates the concurrency manager's max timestamp.
- Start key, end key, and limit parameters are honored.
- Limit `0` means no limit.
- Memory locks with write lock types can trigger errors when they conflict with scanning, while resolved or newer locks are ignored where appropriate.
- `LockType::Lock` memory locks are not skipped by scan-lock conflict checks.

`test_resolve_lock_impl` creates non-target locks at transaction 99, then repeatedly prewrites different batch sizes for later start timestamps and resolves them by commit or rollback. It specifically covers boundaries around `RESOLVE_LOCK_BATCH_SIZE`, ensuring `ResolveLockReadPhase` resolves all target locks across batch boundaries while leaving unrelated transaction 99 locks intact.

`test_resolve_lock_lite` verifies targeted lock resolution. It rolls back or commits selected secondary keys while leaving another key locked, then checks the remaining lock with `scan_lock`.

`test_txn_heart_beat` checks lock TTL extension. Missing locks or mismatched start timestamps return `TxnNotFound`; smaller advised TTL values do not shrink the lock, while larger advised TTL values update it.

`test_check_txn_status` covers status-check behavior for missing transactions, rollback-if-not-exist, late prewrite conflicts caused by rollback records, unexpired locks, committed transactions, expired lock cleanup, and failure to commit after cleanup removed the lock.

`test_check_secondary_locks` verifies secondary-lock probing for async commit: all locks present returns `Locked`, one committed secondary returns `Committed(commit_ts)`, and missing secondaries indicate rollback.

### Pessimistic locking and lock waiting

`test_pessimistic_lock_impl` covers normal and pipelined pessimistic-lock modes. It validates returned previous values, existence checks, idempotent duplicate lock requests, waiting on existing locks, timeout cancellation through `MockLockManager`, write conflict detection against newer committed versions, and multi-key return vectors.

`test_pessimistic_lock_resumable_impl` runs with combinations of pipelined pessimistic lock and in-memory lock. It creates committed, locked, rolled-back, and conflict scenarios and then attempts resumable pessimistic locks with `allow_lock_with_conflict(true)`. The expected results include normal values/existence, `LockedWithConflict` carrying conflict commit timestamps, immediate `KeyIsLocked` when waiting is disabled, successful resume after delete/commit/rollback, idempotent retries, and queued waiters waking in start-ts order.

`ProxyLockMgr` and `validate_wait_for_lock_msg` test the integration between storage and the `LockManager` trait. When an acquire request encounters an existing lock, storage must call `wait_for` with the waiting transaction start timestamp, a `LockDigest` derived from the blocked key and lock timestamp, `is_first_lock`, and the requested timeout.

`test_wake_up` verifies wake-up behavior for blocked pessimistic-lock requests when locks are released by commit, cleanup, rollback, pessimistic rollback, resolve-lock-lite, resolve-lock read phase, and expired-lock cleanup by `CheckTxnStatus`. It also verifies that non-expired status checks do not wake blocked waiters.

### Memory locks, committed/resolved lock access, and async commit

`test_check_memory_locks` installs a lock directly into the concurrency manager memory lock slot. It verifies that `get`, `batch_get`, `scan`, and `batch_get_command` surface `KeyError.locked` under SI isolation, and that resolved locks in the request context suppress the memory-lock error.

`test_read_access_locks` prewrites locks and then reads through a context with `committed_locks`. It verifies point get, batch get, batch get command, and forward/reverse scans can read locked values as committed when the lock's start timestamp is listed as committed.

`test_async_commit_prewrite` verifies optimistic and pessimistic async-commit prewrite min-commit timestamps. The optimistic case returns start-ts plus one; the pessimistic case uses the current concurrency-manager max timestamp plus one when max-ts has advanced.

`test_overlapped_ts_rollback_before_prewrite` protects against overlapped commit/rollback timestamps. It rolls back one pessimistic transaction, then prewrites another transaction that includes that key as a secondary. The later async-commit secondary-lock check must report a `min_commit_ts` greater than the rolled-back transaction's start timestamp.

`test_scheduler_response_policy` uses a mock engine with expected write callbacks to assert that the scheduler respects `WriteResult.response_policy`: normal prewrite waits until applied, async-commit prewrite can respond on committed, pipelined pessimistic lock responds on proposed, and non-pipelined pessimistic lock falls back to applied behavior.

`test_resolve_commit_pessimistic_locks` checks non-lite resolve behavior when a committed transaction had leftover pessimistic locks. Resolving a pessimistic lock that was rolled back is tolerated, resolving normal prewrite locks succeeds, and resolving a normal lock that has already been unlocked reports `TxnLockNotFound`.

### API-version and key-mode validation

`test_check_api_version` validates `StorageApiV1::check_api_version` for point-key commands. It covers:

- API V1 backward compatibility for TiDB and raw-style keys.
- API V1ttl allowing RawKV but rejecting transactional commands.
- API V1 storage rejecting API V2 requests.
- API V2 storage accepting backward-compatible TiDB transactional requests only.
- API V2 key-mode separation between transactional keys (`x\0*`), raw keys (`r\0*`), and TiDB keys.

`test_check_api_version_ranges` extends the same matrix to scan ranges. It includes fully bounded valid ranges, omitted-bound invalid ranges under API V2, and command-specific errors: `API_VERSION_NOT_MATCHED` versus `INVALID_KEY_MODE`.

### In-memory pessimistic locks and transaction status cache

`test_write_in_memory_pessimistic_locks` enables pipelined and in-memory pessimistic locks, checks that `AcquirePessimisticLock` writes a `PessimisticLock` into `TxnExt::pessimistic_locks`, verifies a second transaction sees that lock and waits/fails, and verifies `PrewritePessimistic` removes the in-memory lock.

`test_disable_in_memory_pessimistic_locks` confirms that when the in-memory feature is disabled, acquiring a pessimistic lock does not populate `TxnExt::pessimistic_locks`, while subsequent pessimistic prewrite still succeeds via persisted state.

`test_prewrite_cached_committed_transaction_do_not_skip_constraint_check` protects retry behavior around cached committed transactions. A retrying pessimistic prewrite updates min-commit-ts, commits, populates the transaction-status cache, then a later prewrite retry after reads advance max-ts returns the original min-commit-ts and must not leave the key locked.

`test_updating_txn_status_cache` verifies all cache update paths:

- Successful `Commit` adds committed status; failed commit does not.
- 1PC prewrite records its one-PC commit timestamp.
- `ResolveLockReadPhase` and `ResolveLockLite` add committed statuses.
- `CheckTxnStatus` adds cache entries only when it discovers a committed transaction.
- `CheckSecondaryLocks` does not cache unknown/uncommitted or rolled-back status, but does cache committed status found through a committed secondary.

### Scan-first pessimistic rollback and shared locks

`test_pessimistic_rollback_with_scan_first` checks a scan-first rollback path for pessimistic locks, with in-memory locking both enabled and disabled. It first rolls back two locks in one request, then creates 400 keys where even keys are pessimistic locks and odd keys are normal prewrite locks. The scan-first rollback must remove only pessimistic locks, including across more than 256 keys, and preserve normal locks.

`test_scan_lock_with_shared_lock` acquires two shared pessimistic locks on the same key with different primaries, then prewrites a shared lock for one of them. `scan_lock` must return a single `LockInfo` of type `SharedLock` whose nested shared-lock entries preserve each participant's start timestamp, primary key, lock type, and for-update timestamp.

## State and Persistence Behavior

The tests use a mix of persisted engine state, scheduler-local state, and concurrency-manager memory state.

Persisted state includes RawKV key/value entries with TTL metadata, MVCC locks, writes, rollback records, committed versions, and pessimistic locks stored in the engine. The tests verify persistence with raw reads/scans and lower-level helpers such as `must_locked`, `must_unlocked`, `must_written`, and `must_rollback`.

Scheduler and storage state includes:

- `ConcurrencyManager::max_ts`, updated by read and lock-check paths.
- `ConcurrencyManager` per-key memory lock slots, consulted by read and scan-lock paths.
- `ConcurrencyManager::global_min_lock_ts`, checked after raw atomic operations to ensure temporary CAS/min-lock guards do not leak.
- `TxnExt::pessimistic_locks`, the in-memory pessimistic-lock map used when pipelined/in-memory pessimistic locking is enabled.
- The scheduler transaction-status cache, populated by successful commit-like resolution paths and checked with `get_committed_no_promote`, `remove_normal`, and related accessors.
- Lock-manager wait queues and wake-up callbacks, driven by `MockLockManager` or inspected through `ProxyLockMgr`.

The chunk also verifies time-derived state: TTL remaining values are bounded by `ttl_current_ts`, heartbeat can increase lock TTL but not decrease it, expired locks are cleaned by `CheckTxnStatus`, and async commit/1PC min-commit or commit timestamps are pushed above observed max-ts values and conflicting rollback timestamps.

## Dependencies and Integration Points

This chunk depends on the broader TiKV storage stack:

- `crate::storage::Storage`, `TestStorageBuilder`, scheduler command submission, raw APIs, and read APIs from the same module.
- `crate::storage::txn::commands` for transaction command implementations and response policies.
- `crate::storage::mvcc` and `txn_types` for locks, mutations, writes, timestamps, values, and MVCC error variants.
- `concurrency_manager` for max-ts tracking, memory locks, and lock guards.
- `lock_manager` for pessimistic-lock waiting, wait tokens, cancellation callbacks, and waiter wake-up.
- `engine_traits`, `TestEngineBuilder`, `RocksEngine`, and mock engine wrappers for persisted storage and expected write-stage callbacks.
- `kvproto::kvrpcpb` types such as `Context`, `IsolationLevel`, `KeyRange`, `LockInfo`, `Op`, and `GetRequest`.
- API-version helpers and formats: `ApiV1`, `ApiV2`, `ApiVersion`, `KvFormat`, API V2 raw/txn key prefixes, and command-kind validation.

Integration-wise, the tests deliberately cross module boundaries. Raw API tests validate the RawKV command path and API-format abstraction; transaction tests validate scheduler-to-MVCC command flow; lock wait tests validate scheduler-to-lock-manager messaging; response-policy tests validate raftstore/engine callback staging; and API-version tests validate client protocol compatibility before commands enter lower storage layers.

## Risks and Edge Cases

- The chunk starts mid-test around raw batch delete cleanup, so final reconciliation should merge it with the immediately preceding chunk to capture the full setup for the delete assertions.
- Many tests depend on short sleeps or `recv_timeout` values to prove a request is blocked. These are useful integration tests but can be timing-sensitive on overloaded CI hosts.
- API V2 key-mode validation depends on byte-prefix conventions (`r\0`, `x\0`, TiDB-style keys) and range-bound completeness. Any change to key encoding or compatibility rules can break broad matrices here.
- Raw reverse-scan semantics are easy to regress around inclusive start keys and exclusive end/lower bounds, especially for `b"key"` versus `b"key\0"` cases.
- CAS tests check `global_min_lock_ts` cleanup after sleeps. A future implementation that changes guard lifetime or async cleanup timing could make these tests flaky or require stronger synchronization.
- Lock scan mixes persisted locks, memory locks, resolved-lock context, committed-lock context, and lock types. Regressions can either hide real locks or surface false conflicts.
- `ResolveLock` and `ResolveLockReadPhase` batch-boundary behavior is sensitive to `RESOLVE_LOCK_BATCH_SIZE`; off-by-one errors can leave locks unresolved.
- Pessimistic-lock resumability is complex because it combines wait queues, conflict metadata, return-values/check-existence modes, in-memory locks, pipelined locks, and idempotent retries.
- Transaction-status cache updates must not cache uncertain or rolled-back states as committed. Incorrect promotion can cause stale reads or skipped conflict checks.
- Shared-lock scan results aggregate multiple logical locks into one `LockInfo`; changes to serialization or aggregation can lose participant-level metadata.

## Test and Validation Signals

The chunk itself is a dense test suite. Useful validation signals include:

- Run the storage unit tests for `storage::tests::test_raw_scan`, `test_raw_batch_scan`, `test_raw_get_key_ttl`, `test_raw_compare_and_swap`, and `test_raw_compare_and_swap_delete` to validate RawKV behavior across API formats.
- Run `test_scan_lock`, `test_scan_lock_with_memory_lock`, `test_resolve_lock`, `test_resolve_lock_lite`, `test_txn_heart_beat`, `test_check_txn_status`, and `test_check_secondary_locks` after changes to MVCC lock handling.
- Run `test_pessimistic_lock`, `test_pessimistic_lock_resumable`, `validate_wait_for_lock_msg`, and `test_wake_up` after changes to pessimistic lock waiting, lock manager integration, or wake-up events.
- Run `test_check_memory_locks` and `test_read_access_locks` after changes to SI reads, resolved-lock context, committed-lock context, or batch get command response handling.
- Run `test_async_commit_prewrite`, `test_overlapped_ts_rollback_before_prewrite`, `test_prewrite_cached_committed_transaction_do_not_skip_constraint_check`, and `test_updating_txn_status_cache` after changes to async commit, 1PC, min-commit-ts calculation, or transaction-status cache code.
- Run `test_scheduler_response_policy` when changing command `WriteResult` response policies, pipelined pessimistic lock behavior, or raftstore engine callback staging.
- Run `test_check_api_version` and `test_check_api_version_ranges` for API-version/key-prefix compatibility changes.
- Run `test_pessimistic_rollback_with_scan_first` and `test_scan_lock_with_shared_lock` when changing pessimistic rollback scanning or shared-lock representation.

## Chunk Handoff Notes

For final per-file reconciliation, this chunk should be merged as the last `storage/mod.rs` research segment. Earlier chunks define the `Storage` implementation, builders, helper callbacks, and the start of the test module; this chunk contributes the end-to-end behavioral matrix that proves those APIs interact correctly. The most important cross-chunk references are the raw API implementations, `check_api_version` and `check_key_ranges`, scheduler command plumbing, concurrency-manager usage, and test helper definitions used throughout this span.
