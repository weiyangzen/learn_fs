# sources/storage-engines/rocksdb/utilities/transactions/transaction_test.cc lines 8840-10360

## Chunk Purpose

This chunk covers the tail of `TransactionTest.SecondaryIndexOnKey`, several `TransactionDBTest` cases, and the full `CommitBypassMemtableTest` fixture and test group. The main behavioral focus is transaction correctness around secondary-index iteration, merge operand collapsing, WAL durability for prepared transactions, commit-bypass-memtable writes, snapshot visibility, recovery, merge semantics, deadlock timeout behavior, and automatic large-transaction commit optimization thresholds.

The chunk is test code, but it exercises production integration points across `TransactionDB`, `WriteCommittedTxn`, `DBImpl`, `ColumnFamilyHandle`, merge operators, snapshots, WAL sync/recovery, memtable switching/flush, write queues, and transaction lock management.

## Important APIs, Types, and Functions

- `SecondaryIndex`, `SecondaryIndexIterator`, and `TransactionDBOptions::secondary_indices`: the local `KeySecondaryIndex` maps a primary CF to a secondary CF, indexes the key suffix after a three-byte prefix, and stores a reversed primary key as secondary value.
- `TransactionDBTest` helpers: `ReOpen()`, `ReOpenNoDelete()`, `Put`, `Merge`, `Flush`, `Get`, `GetMergeOperands`, `BeginTransaction`, and `VerifyDBFromMap` are used to assert persisted and in-memory state.
- `Transaction::CollapseKey(ReadOptions, key)`: collapses existing merge operands for one key into a single logical operand while preserving read value semantics.
- `Transaction::SetName`, `Prepare`, `Commit`, and `Rollback`: this chunk exercises prepared transaction lifecycles, named transactions, transaction reuse, and rollback after lock release.
- `TransactionOptions`: key fields under test are `commit_bypass_memtable`, `large_txn_commit_optimize_threshold`, `large_txn_commit_optimize_byte_threshold`, `lock_timeout`, and `deadlock_detect`.
- `CommitBypassMemtableTest`: a parameterized fixture over `(Options::two_write_queues, TransactionDBOptions::use_per_key_point_lock_mgr)` that opens a `WRITE_COMMITTED` `TransactionDB`, enables 2PC, increases `max_write_buffer_number`, and optionally enables `atomic_flush`.
- `DBImpl` test hooks: `TEST_SwitchMemtable()`, `GetLastPublishedSequence()`, `TEST_GetBGError()`, and sync points are used to force precise concurrency and failure windows.
- `SyncPoint`: coordinates writer, flush, WAL creation failure, and bypass decision callbacks. The named sync points around `DBImpl::WriteImpl:AfterWBWIIngestBeforeSetLastSequence`, `DBImpl::InitSnapshotContext:BeforeInit`, `DBImpl::BackgroundCallFlush:ContextCleanedUp`, `DBImpl::SwitchMemtable:AfterCreateWAL`, and `WriteCommittedTxn::CommitInternal:bypass_memtable` are critical test controls.
- Merge support APIs: `MergeOperators::CreateFromStringId("stringappend")`, `MergeOperators::CreateFromStringId("uint64add")`, `GetMergeOperandsOptions`, `PinnableSlice`, and `PutFixed64`.
- Column-family APIs: `CreateColumnFamily`, `CreateColumnFamilies`, `handles_`, `FlushOptions`, per-CF `GetIntProperty(DB::Properties::kNumImmutableMemTable)`, and `ColumnFamilyHandleImpl::cfd()->imm()/mem()` for atomic-flush assertions.

## Control Flow and Tested Behavior

### Secondary Index On Key Tail

The chunk begins inside `KeySecondaryIndex::GetSecondaryValue`, which reverses the primary key and returns it as the secondary value. The test registers the index, reopens the database, creates primary CF `cf1` and secondary CF `cf2`, wires them into the index, inserts keys such as `123foo`, `456bar`, and `789baz` through a transaction, then scans `cf2` through `SecondaryIndexIterator`.

The iterator assertions show the intended ordering and translation: seeking `foo` returns primary keys `123foo`, `456foo`, and `789foo` with values `oof321`, `oof654`, and `oof987`; seeking `bar` and `baz` follows the same suffix grouping. This validates that secondary key prefixes are derived from primary-key suffixes while iterator-visible keys are mapped back to primary keys.

### CollapseKey

`TransactionDBTest.CollapseKey` writes and flushes `hello=world`, then performs two flushed merges on `hello`. Before collapsing, `GetMergeOperands` returns three operands and `Get` resolves to `world,world,world`. A transaction calls `CollapseKey` and commits; afterwards `GetMergeOperands` returns one operand while `Get` still returns the same resolved value. The negative path checks `CollapseKey` on `dummy` returns `NotFound`.

### WAL Sync With Pending Prepare

`FlushedLogWithPendingPrepareIsSynced` reproduces a durability bug where flush skipped syncing an old WAL even though it contained a prepared transaction without its commit record. The test writes a normal key, prepares a named transaction, marks the fault filesystem directly writable so later unsynced records can still be recovered, flushes, commits the prepared transaction, writes another key, reopens without deleting, and verifies all keys. The expected behavior is that the old WAL containing the prepare record is synced before it can be needed by crash recovery.

### CommitBypassMemtable Fixture

`CommitBypassMemtableTest` resets the DB for each configuration, opens `TransactionDB` with `allow_2pc=true`, `write_policy=WRITE_COMMITTED`, `max_write_buffer_number=8`, the test parameter's `two_write_queues`, and the test parameter's per-key point lock manager setting. Tests in this fixture are therefore run across both write queue modes and both lock manager implementations unless explicitly bypassed.

### Single-CF Commit Bypass

`SingleCFUpdate` writes 10,000-key baseline state, takes a snapshot, commits a large transaction using `commit_bypass_memtable=true`, and verifies both snapshot and latest reads before and after flush. It also runs with background work paused, forcing reads from immutable memtables until flush resumes.

`SingleCFUpdateWithOverWrite` builds a layered LSM/memtable state: SST data, a normal transaction moved to immutable memtable, a bypass transaction ingested as WBWI-backed immutable memtables, and a later normal live-memtable update. It tests both `Delete` and `SingleDelete`, snapshots before bypass commit, background-flush-paused and normal modes, immutable-memtable counts, and final flush/compaction. The expected result is that latest state reflects bypass updates/deletes while old snapshots retain pre-bypass state.

### Published Sequence Snapshot Protection

`FlushPreservesPublishedValueDuringBypassOverwriteTwoWriteQueue` and `FlushPreservesPublishedValueDuringBypassOverwriteSingleWriteQueue` force a race in which a bypass commit ingests future versions into immutable memtables before the writer publishes the sequence number. A flush initializes its snapshot context during that gap, and the test takes a snapshot at the old published sequence. The held snapshot must keep seeing `old_value`, while latest reads must see `new_value` after publication.

These tests specifically guard `WRITE_COMMITTED` published-boundary tracking. Without it, flush retention could drop the old visible version because a newer future version exists, leaving the snapshot with `NotFound` or an older delete.

### Multi-CF Commit Bypass

`MultiCFOverwrite` creates three column families, randomizes updates across 10,000 keys, and validates a mix of `Put`, `Delete`, `SingleDelete`, and commit-time write-batch writes. The first transaction always bypasses memtable; the second randomly bypasses. The test tracks expected maps and not-found sets per CF, optionally captures and verifies snapshots between transactions, checks immutable-memtable counts under paused flush, and verifies final state after flush or compaction. CF `meta` exercises `GetCommitTimeWriteBatch()` and should not create bypass immutable memtables.

### Recovery and Sequence Reservation

`Recovery` commits two bypass transactions, reusing the transaction object for the second one, then closes and reopens the DB. The comment explains the key risk: bypass ingest must reserve enough sequence numbers so recovery, which inserts through the normal memtable path, does not produce duplicate key/sequence pairs. Expected values are `k1=v3` and `k2=v4` before and after reopen.

### Large Transaction Optimization Thresholds

`OptimizeLargeTxnCommitThreshold` checks count-based `large_txn_commit_optimize_threshold`. With default options, a 100-op transaction does not bypass. With threshold `10`, a one-op transaction does not bypass and a ten-op transaction does. The same logic is tested across two column families. Explicit `commit_bypass_memtable=true` takes precedence even when the threshold is set high.

`OptimizeLargeTxnCommitWriteBatchSizeThreshold` checks byte-based `large_txn_commit_optimize_byte_threshold`. A large write below default settings does not bypass. With a 100-byte threshold, a transaction whose write batch data size reaches the threshold bypasses, a smaller one does not, and explicit `commit_bypass_memtable=true` still overrides. It also verifies that count-based and byte-based thresholds are OR-like triggers and that byte size is computed across column families.

`WBWIOpCountMismatchWBCount` protects the optimization eligibility check: if code writes directly to the transaction's underlying `WriteBatch` rather than through WBWI-tracked transaction operations, bypass optimization must not apply even if the byte/count threshold would otherwise be met. The direct metadata writes are still committed and readable.

### Atomic Flush

`AtomicFlushTest` opens with `atomic_flush=true`, seeds data into CF1 and CF2, then commits a threshold-sized optimized transaction into CF0. After compaction, all three CFs should have no unflushed immutable memtables and empty mutable memtables. This verifies that bypass optimization cooperates with atomic flush and flushes all relevant non-empty CF memtables consistently.

### SwitchMemtable Failure

`SwitchMemtableFailureStopsDBUntilReopen` injects a retryable WAL creation error at `DBImpl::SwitchMemtable:AfterCreateWAL` during a sync bypass commit. The commit is expected to return `Corruption`, the DB background error becomes fatal corruption, and further writes fail with the same fatal severity. After close/reopen, the prepared transaction's keys are recovered (`k1`, `k2`) and a new write succeeds. This test encodes both failure escalation and recovery expectations.

### Merge Behavior

`MergeAndMultiCF` creates merge-enabled CFs using `stringappend` and `uint64add`, plus a plain data CF. It commits a bypass transaction containing combinations of put, merge, delete, and merge-after-delete, then a normal transaction adding more merge operands. Expected results cover operand resolution (`k1=v1,v2,v3`, `k2=v1`, `k3` not found, numeric count equals 4) and preservation after flush/compaction. With flush paused, it also verifies the raw merge operands for `k1` are visible in order before flushing.

`MergeMiniStress` repeatedly runs 50-operation transactions over random keys with 80% merge, 10% put, and 10% delete probability, randomly choosing bypass or normal commit. It captures a snapshot before each transaction and periodically verifies both current expected state and snapshot state. The loop runs with `min_write_buffer_number_to_merge` set to 1 and 4, exercising different memtable merge-read shapes.

### Lock Timeout Regression

`TransactionDBTest.SelfDeadlockBug` creates two transactions with deadlock detection and a 50 ms lock timeout. Both take shared locks on `shared_key`; then one transaction attempts an exclusive update while the other still holds a shared lock. The expected result is timeout, an empty deadlock-info buffer, and no false self-deadlock report. After rolling back the second transaction, the first can update and roll back.

The chunk then instantiates `TransactionDBTest` for the basic transaction parameter matrix and ends with the file-level `main()` that installs RocksDB's stack trace handler and runs GoogleTest.

## State and Persistence Behavior

- Secondary-index state is persisted through writes to the configured secondary CF and read back via `SecondaryIndexIterator`, which reconstructs primary keys and index values from encoded secondary records.
- Merge state is tested at two levels: logical reads through `Get` and raw operand visibility through `GetMergeOperands`. `CollapseKey` intentionally reduces persisted merge operand count without changing logical value.
- Prepared transaction durability depends on WAL sync ordering. A flushed memtable cannot make an old WAL safely ignorable if that WAL has an unresolved prepare record.
- Commit-bypass-memtable writes produce WBWI-backed immutable memtables instead of first writing to the mutable memtable. Tests verify both read paths before flush and durable recovery after reopen.
- Snapshot state is explicitly preserved across bypass commits, flushes, compactions, and published-sequence gaps. Several tests hold `ReadOptions::snapshot` and compare against copied expected maps.
- Immutable memtable counts are observable state in paused-background-work tests. Expected counts distinguish WBWI immutable memtables, empty immutable memtables created during commit, ordinary immutable memtables, and metadata CFs not involved in bypass ingest.
- Fatal background error state after switch-memtable failure blocks further writes until reopen, but recovery replays the prepared transaction successfully.

## Dependencies and Integration Points

- Depends on RocksDB test infrastructure from `DBTestBase`, transaction test fixtures, `ASSERT_OK`, `SCOPED_TRACE`, `ROCKSDB_GTEST_BYPASS`, and `SyncPoint`.
- Integrates transaction code with lower-level `DBImpl` sequence publication, memtable switching, flush snapshot context, WAL creation/sync, atomic flush, and background error handling.
- Integrates with column-family behavior by mixing primary/data/metadata CFs, merge-enabled CFs, and atomic flush across multiple CF handles.
- Integrates with merge operators by using both string append and fixed-width unsigned addition semantics.
- Integrates with transaction lock managers through fixture parameterization over the per-key point lock manager.
- Uses `fault_fs` to model filesystem durability behavior and direct writability during recovery-oriented tests.

## Risks and Edge Cases Captured

- Secondary index key transformation must preserve grouping, ordering, and value reconstruction for suffix-derived index prefixes.
- `CollapseKey` must not alter logical reads and must return `NotFound` for absent keys.
- WAL sync optimizations are unsafe when old WALs contain prepares that crash recovery may need.
- Flush retention must protect the latest published version, not only explicit snapshots known before a bypass commit publishes its sequence.
- Bypass commit must reserve sequence numbers compatible with normal recovery insertion order.
- `SingleDelete` cases avoid illegal overwrite patterns while still verifying deletion visibility.
- Commit-time write-batch mutations can coexist with bypass transactions but should not cause unrelated CFs to acquire bypass immutable memtables.
- Large-transaction optimization must be disabled when WBWI operation counts diverge from the underlying write batch because direct writes bypass transaction tracking.
- Injected switch-memtable failures must leave the DB in a fatal state rather than allowing partial or ambiguous writes.
- Randomized stress tests can expose ordering bugs, snapshot regressions, and merge operand mishandling that fixed-case tests may miss, but they rely on deterministic test randomness from RocksDB's test random source.

## Test Signals

- Positive signals are mostly `ASSERT_OK`, exact value equality, `VerifyDBFromMap`, immutable-memtable property checks, snapshot sequence checks, and post-reopen verification.
- Negative signals include `IsNotFound` for absent `CollapseKey`, `IsTimedOut` for lock upgrade timeout, `IsCorruption` plus fatal severity for injected switch-memtable failure, and bypass flag callbacks expected to be false in ineligible optimization cases.
- Concurrency-sensitive tests use sync-point dependencies and threads to force writer/flush interleavings that would be difficult to reproduce with timing alone.
- Parameterization multiplies coverage over two write-queue modes and lock-manager choices, with explicit bypasses for tests that target only one write-queue mode.
