# sources/storage-engines/rocksdb/tools/db_bench_tool.cc lines 6630-9891

## Scope

This chunk covers the final portion of RocksDB's `db_bench_tool.cc`. It starts in the tail of deterministic-fill verification, then contains many `Benchmark` workload methods for sequential reads, random reads, `MultiGet`, `MultiScan`, approximate-size probes, mixed graph-style workloads, iterator creation, seeks, deletes, concurrent background writers/scanners, read-modify-write workloads, merge workloads, transaction stress, random key replacement, time-series read/write/delete, manual compaction/flush/stat reporting, trace replay, backup/restore, the `Benchmark` thread-local guard definitions, and the top-level `db_bench_tool()` entry point.

The code is benchmark and tool orchestration code, not core storage-engine implementation. It is still storage-critical because it drives public RocksDB APIs under many option combinations and acts as an integration exerciser for reads, writes, merges, range deletes, timestamps, snapshots, column families, multi-DB selection, transactions, backup, restore, compaction, filesystem/environment selection, and statistics reporting.

## Purpose

- Implement the executable benchmark workloads selected by `Benchmark::Run()` and earlier command-line parsing.
- Exercise point reads, sequential iteration, reverse iteration, seek scans, batched `MultiGet`, prepared `MultiScan`, approximate memtable stats, approximate file sizes, and checksum verification.
- Model mixed production-like workloads: graph/social access distributions, concurrent read/write or read/merge paths, append/read-modify-write workloads, MyRocks-like secondary-index replacement, transaction increments, and time-series keys with embedded timestamps.
- Provide benchmark-side state management around `ThreadState`, `Duration`, `Stats`, per-thread random generators, rate limiters, user timestamps, snapshots, column-family handles, and multi-DB routing.
- Expose operational commands inside `db_bench`: compact, compact all, compact L0/L1-like levels, flush, wait for compaction, reset stats, print DB properties and stats history, cache problem reporting, replay traces, backup, and restore.
- Convert command-line flags into concrete RocksDB runtime state in `db_bench_tool()`: statistics objects, compaction/compression enums, environment/filesystem selection, seed, DB/backup/restore directories, background thread counts, and final benchmark execution.

## Important APIs, Types, And Functions

- `ReadSequential(ThreadState*)` and `ReadSequential(ThreadState*, DB*)` iterate from the beginning with optional user timestamp, adaptive readahead, async IO, auto readahead, and optional explicit snapshot. They count key/value bytes and honor the shared read rate limiter every 1024 reads.
- `ReadToRowCache()` scans deterministic key IDs and calls `DB::Get()` to populate or exercise row cache behavior. It routes column-family reads through `DBWithColumnFamilies::GetCfh()` when multiple CFs are enabled.
- `ReadReverse()` mirrors sequential reads from `SeekToLast()` through `Prev()`.
- `ReadRandomFast()` uses a power-of-two mask to generate keys quickly, intentionally issuing keys outside `FLAGS_num` when the rounded power-of-two range is larger. It tracks not-found and non-existing-key counts.
- `GetRandomKey()` centralizes random key selection. It supports uniform distribution or an exponential distribution controlled by `read_random_exp_range_`, then remaps through a fixed large prime to avoid locality.
- `ReadRandom()` is the main point-read benchmark. It supports strided batches, user timestamps, multi-CF routing, `PinnableSlice` value reads, optional `GetMergeOperands()`, incomplete operand retries with a resized operand vector, byte accounting, and shared read throttling.
- `MultiReadRandom()` implements batched point reads through either vector-returning `DB::MultiGet(ReadOptions, keys, values)` or the lower-level batched API using a default CF, key array, `PinnableSlice` array, and status array.
- `MaybeCreateIODispatcher()` builds an `IODispatcher` when `FLAGS_io_dispatcher_max_prefetch_memory_bytes` is set and wires it to `dbstats`.
- `MultiScan()` builds a fixed set of non-overlapping scan ranges from a random start, configures `MultiScanArgs`, optionally attaches an IO dispatcher, runs `DB::NewMultiScan()`, and counts keys across returned ranges.
- `MultiScanRandom()` generates a random batch of sorted non-overlapping ranges capped by roughly 1 MiB per range. It can execute either the `NewMultiScan()` path or a normal iterator `Seek`/`Next` path for comparison.
- `ApproximateMemtableStats()` calls `DB::GetApproximateMemTableStats()` over random ranges and records a histogram of reported entry counts.
- `ApproximateSizeRandom()` calls `DB::GetApproximateSizes()` over batches of random `Range` objects and reports the average approximate byte size.
- `ParetoCdfInversion()`, `PowerCdfInversion()`, and `AddNoise()` generate distribution-dependent value sizes, iterator lengths, key IDs, and sine-rate noise for synthetic workloads.
- `QueryDecider` maps configured operation ratios onto an integer range and chooses operation type by modulo. It is used by `MixGraph()`.
- `KeyrangeUnit` and `GenerateTwoTermExpKeys` model prefix/key-range hotness with a two-term exponential distribution plus optional power-distributed key offsets inside a selected range.
- `MixGraph()` mixes `Get`, `Put`, and `Seek` workloads using the distribution helpers. It supports sine-wave QPS rate changes, prefix hotness modeling, Pareto-distributed value sizes, Pareto-distributed scan lengths, and per-operation stats.
- `IteratorCreation()` repeatedly creates and destroys iterators, with optional user timestamps. `IteratorCreationWhileWriting()` assigns thread 0 to `BGWriter()` and other threads to iterator creation.
- `SeekRandom()` is the main random seek benchmark. It supports tailing iterators, explicit snapshots, auto-prefix upper bounds, explicit max scan distance bounds, forward or reverse scans, optional deletion after scan, value copying, and multi-DB iterator selection.
- `DoDelete()`, `DeleteSeq()`, and `DeleteRandom()` batch point tombstones through `WriteBatch`, with optional batch timestamp assignment.
- `ReadWhileWriting()`, `MultiReadWhileWriting()`, `ReadWhileMerging()`, `SeekRandomWhileWriting()`, and `SeekRandomWhileMerging()` are thread-role dispatchers: thread 0 runs `BGWriter()`, other threads run the corresponding read or seek workload.
- `BGWriter()` continuously writes or merges until other benchmark threads finish, or until `FLAGS_finish_after_writes` reaches `writes_`. It supports benchmark write rate limiting, user timestamps, `FLAGS_use_existing_keys`, range tombstone generation, and expansion of range tombstones into point deletes.
- `ReadWhileScanning()` and `BGScan()` pair random readers with a background scanner that loops over a single DB iterator.
- `PutMany()`, `DeleteMany()`, and `GetMany()` implement three-key atomic write/delete/read helpers for `RandomWithVerify()`. They append `"0"`, `"1"`, and `"2"` suffixes, use snapshots for read consistency, and support write-batch timestamp assignment.
- `RandomWithVerify()` mixes `GetMany`, `PutMany`, and `DeleteMany` over `FLAGS_numdistinct` keys to catch inconsistent multi-key atomic state.
- `ReadRandomWriteRandom()` mixes reads and writes in one thread according to `FLAGS_readwritepercent`.
- `UpdateRandom()`, `XORUpdateRandom()`, and `AppendRandom()` implement read-modify-write variants with normal replacement, XOR transformation, and string append semantics.
- `MergeRandom()` and `ReadRandomMergeRandom()` drive merge-operator benchmarks over `merge_keys_`, with optional interleaved reads controlled by `FLAGS_mergereadpercent`.
- `WriteSeqSeekSeq()` writes a full sequential dataset, restarts stats, then seeks every key and optionally walks subsequent keys.
- `binary_search()` and `GetMergeOperands()` provide a targeted demonstration comparing full `Get()` merge resolution against `GetMergeOperands()` over sorted-list operands.
- `VerifyChecksum()` and `VerifyFileChecksums()` call the corresponding DB verification APIs with read options derived from benchmark flags.
- `RandomTransaction()` stress-tests `TransactionDB`, `OptimisticTransactionDB`, or plain `DB` insert paths through `RandomTransactionInserter`; `RandomTransactionVerify()` validates the transaction invariant across key sets.
- `RandomReplaceKeys()` repeatedly deletes and inserts non-overwriting random keys, simulating MyRocks secondary-index update shape.
- `TimeSeriesReadOrDelete()`, `TimeSeriesWrite()`, and `TimeSeries()` implement a single-writer/multiple-reader or deleter workload over keys whose bytes include an emulated timestamp.
- `Compact()`, `CompactAll()`, `CompactLevelHelper()`, `CompactLevel()`, `Flush()`, `WaitForCompaction()`, `ResetStats()`, `PrintStatsHistory()`, `PrintStats()`, and `CacheReportProblems()` expose operational maintenance and observability actions.
- `Replay()` opens a file trace with `NewFileTraceReader()`, creates a default DB replayer, prepares it, and replays it with configurable replay threads and fast-forward.
- `Backup()` and `Restore()` use `BackupEngine` and `BackupEngineReadOnly` with optional IO rate limiters.
- `db_bench_tool()` is the public entry point for this translation unit. It installs stack traces, registers validators, parses flags, initializes global statistics, converts string flags to enum values, selects or constructs the `Env`, sets default paths, configures background threads, builds a `Benchmark`, runs it, and optionally prints malloc stats.

## Control Flow

The chunk begins by finishing deterministic-fill verification. In debug builds, previous code has recorded sorted runs; lines in this chunk compare those sorted-run keys and sequence-number ranges against current column-family metadata, then print the LSM layout per DB. After verification, it restores dynamic options such as `disable_auto_compactions`, `level0_slowdown_writes_trigger`, and `level0_stop_writes_trigger`.

Read workloads follow a common pattern: clone `read_options_`, optionally attach a timestamp from `mock_app_clock_`, optionally attach a snapshot or iterator bounds, select a DB or `DBWithColumnFamilies`, allocate a reusable key buffer, run until a `Duration` object reports done, update `ThreadState::stats`, and periodically request tokens from `thread->shared->read_rate_limiter`. Iterator-based workloads copy values into local buffers to make the read cost observable and assert iterator status during scan loops.

Random key selection is layered. Most random point and seek paths call `GetRandomKey()`, which can produce uniform or exponentially biased IDs. Higher-level workloads can add stride behavior, prefix/key-range hotness, Pareto-distributed sizes, or power-distributed key offsets. `GenerateKeyFromInt()` and `GenerateKeyFromIntForSeek()` translate those numeric IDs into benchmark key bytes.

`ReadRandom()` branches between normal `Get()` and `GetMergeOperands()`. In operand mode, it starts with eight `PinnableSlice` slots, retries after `Status::Incomplete()` with the required operand count, then accounts all returned operands. In normal mode, it routes through the selected CF for multi-CF runs and returns a timestamp string when user timestamps are enabled.

`MultiReadRandom()` creates `entries_per_batch_` reusable key buffers and either issues the high-level vector `MultiGet()` call or the lower-level batched API. The non-batched path supports the API taking `std::vector<Slice>` and `std::vector<std::string>`, while the batched path uses `db->DefaultColumnFamily()` and resets statuses and pinned values after each call.

`MultiScan()` constructs regular strided ranges from a single random start. `MultiScanRandom()` builds a more varied model: random batch size, random range sizes, sort by start, trim overlaps, then execute either prepared multiscan or standard iterator scans. Both treat each multiscan as one benchmark operation while using the observed key count to advance `Duration`.

`MixGraph()` chooses an operation by `QueryDecider` and then executes one of three branches. Gets perform a point lookup and throttle read QPS every 100 read-like operations. Puts choose a Pareto-distributed value size and write generated bytes. Seeks build a one-shot iterator, seek the generated key, and scan a Pareto-distributed number of entries. When sine-rate mode is enabled, it periodically recomputes read/write rate limits from `SineRate()` plus `AddNoise()`.

Concurrent workloads use `thread->tid` to assign roles. Thread 0 usually becomes a special background writer or scanner and calls `SetExcludeFromMerge()` on its stats, while other threads perform the measured read/seek/iterator workload. `BGWriter()` checks shared completion state under `thread->shared->mu`, optionally continues after readers finish until a write target is met, writes or merges one random key per loop, and injects range tombstones at configured write intervals.

Verification-style workloads build their own small protocols. `RandomWithVerify()` writes, deletes, and reads three suffixed keys per logical key, using a snapshot in `GetMany()` to ensure the three reads see the same DB state. `RandomTransaction()` delegates to `RandomTransactionInserter`, then `RandomTransactionVerify()` checks cross-set sums only when a transaction DB mode is enabled.

Time-series flow is also thread-role based. Thread 0 writes keys containing a random key ID and an embedded timestamp from `timestamp_emulator_`; other threads seek by key-ID prefix and either read matching entries or delete expired entries according to `KeyExpired()`. The writer reports its own stats separately with the label `"timeseries write"`.

Operational commands are thin wrappers over DB APIs. Compaction paths either compact a whole range, compact all DBs, or inspect live file metadata to compact all files from L0 or the first populated nonzero level into the next populated level. Flush handles single DB and multi-DB, single CF and multi-CF. Stats printing iterates DBs and properties. Replay/backup/restore create helper engines/readers, execute the requested operation, and report status.

`db_bench_tool()` is straight-line initialization followed by `benchmark.Run(hooks)`. It validates incompatible flags, creates statistics from either a config string or default factory, parses fanout and compression strings, resolves environment URI or simulated filesystem flags, derives defaults for `FLAGS_db`, `FLAGS_backup_dir`, and `FLAGS_restore_dir`, seeds randomness, configures Env background threads, and exits early for build info. After `Run()`, it optionally dumps malloc stats.

## State And Persistence Behavior

- Read methods maintain only per-thread counters and temporary buffers, but they can pin RocksDB snapshots and values for the duration of each loop iteration or full benchmark call.
- User timestamp support is pervasive. Reads set `ReadOptions::timestamp` from `mock_app_clock_->GetTimestampForRead()`, while writes and batches use `mock_app_clock_->Allocate()` and either timestamp-aware `Put/Delete/SingleDelete` overloads or `WriteBatch::UpdateTimestamps()`.
- `BGWriter()`, `DoDelete()`, update methods, merge methods, random replacement, transactions, and time-series writes persist real mutations to the selected DB. Depending on flags, these mutations include puts, merges, point deletes, single deletes, range deletes, timestamped records, and transaction-protected increments.
- Snapshot behavior appears in sequential reads, seek reads, background scans, `WriteSeqSeekSeq()`, and `GetMany()`. Explicit benchmark snapshots preserve a stable read view; `GetMany()` obtains and releases a DB snapshot to verify three suffixed values consistently.
- Range tombstone state is intentionally created by `BGWriter()` after configured write thresholds. It can either emit one `DeleteRange()` over the default CF or expand the tombstone into point deletes for controlled comparison.
- Time-series persistence embeds timestamp bytes into the key rather than relying on RocksDB user timestamps. `TimeSeriesReadOrDelete()` seeks by zeroed timestamp suffix and deletes entries considered expired by `KeyExpired()`.
- Manual compaction and flush methods directly reshape persistent LSM state. `CompactLevelHelper()` reads live-file metadata, selects files from the requested source level or first dynamic nonzero level, and calls `CompactFiles()` into the next populated level.
- `Backup()` creates backup metadata and files under `FLAGS_backup_dir`, first destroying old backup-engine data. `Restore()` restores the latest backup into `FLAGS_restore_dir`.
- `Replay()` reads a persisted RocksDB trace file from `FLAGS_trace_file` and replays operations into the active DB/CF.
- `db_bench_tool()` mutates global benchmark/tool state: `hooks_`, `dbstats`, `FLAGS_*` converted enum globals, `FLAGS_env`, `env_guard`, `seed_base`, default paths, and environment background-thread counts.

## Dependencies And Integration Points

- Core DB APIs: `DB::Get`, `Put`, `Merge`, `Delete`, `SingleDelete`, `DeleteRange`, `Write`, `NewIterator`, `NewMultiScan`, `MultiGet`, `GetApproximateSizes`, `GetApproximateMemTableStats`, `VerifyChecksum`, `VerifyFileChecksums`, `CompactRange`, `CompactFiles`, `Flush`, `WaitForCompact`, `GetProperty`, `GetStatsHistory`, `GetSnapshot`, and `ReleaseSnapshot`.
- Column-family integration: `DBWithColumnFamilies`, `ColumnFamilyHandle`, `DefaultColumnFamily()`, `GetCfh()`, and metadata/descriptor APIs such as `GetColumnFamilyMetaData()`, `GetLiveFilesMetaData()`, and `ColumnFamilyDescriptor`.
- Iterator and scan APIs: `Iterator`, `ManagedSnapshot`, `ReadOptions` bounds and timestamp fields, tailing iterators, `MultiScanArgs`, `MultiScanException`, `IODispatcher`, and `IODispatcherOptions`.
- Write APIs: `WriteOptions`, `WriteBatch`, write-batch protection bytes, timestamp updates, merge operators, `BytesXOROperator`, and `RandomGenerator`.
- Benchmark infrastructure: `ThreadState`, `SharedState`, `Stats`, `Duration`, `OperationType`, `SelectDB()`, `SelectDBWithCfh()`, key allocation/generation helpers, `Random64`, `RandomTransactionInserter`, `SortList`, `timestamp_emulator_`, and `mock_app_clock_`.
- Rate limiting and IO priority: shared read/write limiters, local benchmark write limiter, backup/restore rate limiters, `Env::IO_HIGH`, `Env::IO_USER`, `Env::IO_TOTAL`, and `RateLimiter::OpType`.
- Operational/storage services: `BackupEngine`, `BackupEngineReadOnly`, `BackupEngineOptions`, `BackupInfo`, `TraceReader`, `Replayer`, `ReplayOptions`, `NewFileTraceReader()`, `NewGenericRateLimiter()`, and cache problem reporting through `cache_->ReportProblems()`.
- Environment/config integration: `Env::CreateFromUri()`, `NewCompositeEnv()`, `SimulatedHybridFileSystem`, `FileSystem::Default()`, `ConfigOptions`, command-line flag parsing, statistics factories, compression/compaction enum conversion, build/version information, malloc stats dumping, and background thread configuration.
- Standard-library dependencies include vectors, strings, smart pointers, random distributions, sorting, math functions, assertions, formatted output, and low-level memory operations for key/timestamp encoding.

## Risks And Edge Cases

- Several benchmark paths assume flag combinations are sane. `MultiScan()` can underflow its unsigned range calculation if `FLAGS_num` is too small for `scan_size`, `FLAGS_multiscan_stride`, and `FLAGS_multiscan_size`; strided reads can similarly compute negative starts if `FLAGS_num < entries_per_batch_ * FLAGS_multiread_stride`.
- `MultiScanRandom()` computes `per_key_size = FLAGS_key_size + FLAGS_value_size`; pathological zero sizes would make the max-range calculation invalid, though normal db_bench flags make this positive.
- `QueryDecider::Initiate()` divides by the sum of configured ratios. A zero total for get/put/seek ratios would produce invalid probabilities. `MixGraph()` also reports `total_val_size / puts` and `total_scan_length / seek`, which can divide by zero when ratios suppress puts or seeks.
- `AddNoise()` uses `rand() % static_cast<int>(FLAGS_sine_a)`. If sine amplitude converts to zero, this is invalid.
- `GenerateTwoTermExpKeys::DistGetKeyID()` modulo-divides by `keyrange_rand_max_`; all-zero prefix hotness or very small probabilities can leave that value unusable.
- `SeekRandom()` creates an explicit snapshot from `db_.db`; in multi-DB mode `db_.db` may be null even though later code selects `multi_dbs_`, so explicit snapshot mode is risky with multi-DB benchmarks.
- `SeekRandom()` increments the last prefix byte to build an auto-prefix upper bound without guarding byte overflow.
- `SeekRandom()` deletes keys while using the same iterator to continue scanning. This is an intentional benchmark stress shape, but iterator visibility after writes can depend on RocksDB iterator semantics and snapshot configuration.
- The batched `MultiReadRandom()` path uses only the default column family, unlike `ReadRandom()`'s multi-CF routing. Results differ when multiple column families are enabled.
- `BGWriter()` error messages for expanded range deletes and `DeleteRange()` print `s.ToString()` from a prior operation rather than the failing delete status. That can obscure the true error.
- `BGWriter()` accounts write bytes for puts/merges but explicitly does not include `DeleteRange()` bytes or throttle requests for range-delete cost.
- `GetMany()` obtains a snapshot and releases it, but `RandomReplaceKeys()` calls `db->GetSnapshot()` without storing or releasing the returned snapshot. That can pin resources until DB close and may be accidental.
- `Backup()` opens a raw `BackupEngine*` and does not delete it in this chunk after creating the backup. In a short-lived benchmark this may be tolerated, but it is still resource-management risk.
- `Restore()` restores latest backup into `FLAGS_restore_dir` as both DB and WAL directory, not the original `FLAGS_db`. This is expected for the benchmark but can surprise users expecting in-place restore.
- Many errors call `abort()`, `ErrorExit()`, or `db_bench_exit(1)` directly. That is normal for a command-line benchmark but means workloads are not designed as recoverable library calls.
- Numerous debug-only assertions protect iterator status, deterministic fill metadata, and sequential seek invariants. Release builds will not catch those mismatches unless the surrounding API returns an error that is explicitly checked.

## Test Signals

- Sequential and reverse read benchmarks should report bytes read and operation counts, and should work with explicit snapshots, user timestamps, adaptive readahead, async IO, and auto readahead flags.
- Random read benchmarks should report found/read counts. `ReadRandomFast()` should additionally report deliberately issued non-existing keys when the power-of-two mask exceeds `FLAGS_num`.
- `ReadRandom()` with `read_operands_` is a signal for `GetMergeOperands()` correctness, including the `Status::Incomplete()` retry path and operand byte accounting.
- `MultiReadRandom()` compares the high-level vector `MultiGet()` path and the lower-level batched/pinnable API path, with found counts and status handling as the main correctness signals.
- `MultiScan()` and `MultiScanRandom()` are integration signals for prepared multi-range scans, IO dispatcher prefetch memory limits, async/coalesced multiscan options, and iterator fallback behavior.
- `ApproximateMemtableStats()` should produce a histogram centered around `entries_per_batch_` when the target range is fully resident in memtables. `ApproximateSizeRandom()` should report a non-crashing average over random ranges.
- `MixGraph()` should produce plausible get/put/seek counts, found counts, average value size, and average scan length under configured distributions and sine-rate changes.
- Concurrent read/write and read/merge workloads should terminate when reader threads finish, exclude background-writer stats from merged reader stats, and optionally continue to a target write count when `FLAGS_finish_after_writes` is set.
- `RandomWithVerify()` should not print inconsistent values for the three suffixed keys. Inconsistency indicates snapshot, write-batch atomicity, or read/write ordering problems.
- Update, XOR update, append, merge, and read/merge benchmarks should complete without get/put/merge errors and report update/read/merge hit statistics.
- `WriteSeqSeekSeq()` asserts every sequentially written key can be found by seek and subsequent next/prev traversal. It is a strong iterator ordering signal.
- `GetMergeOperands()` prints side-by-side timing and sample data for full merge resolution versus operand retrieval over sorted-list operands.
- `VerifyChecksum()` and `VerifyFileChecksums()` should exit successfully; failures directly signal data or file checksum verification problems.
- `RandomTransactionVerify()` should print success after transaction benchmarks in transaction DB modes. Failure signals lost or non-atomic increments across transaction sets.
- `RandomReplaceKeys()` exercises delete plus insert churn without overwriting old key versions and reports whether single deletes and the configured normal-distribution standard deviation were used.
- Time-series workloads should show writer stats separately and reader/deleter found counts, while deletion mode should remove only expired timestamped keys.
- Compaction, flush, wait-for-compaction, stats-history, and property-printing commands provide operational signals through stdout/stderr messages and DB status returns.
- Replay should report completion from `FLAGS_trace_file` or an explicit replay error. Backup should create exactly one backup entry after destroying old data, and restore should succeed from the latest backup.
- `db_bench_tool()` initialization is validated by early error exits for incompatible statistics flags, mutually exclusive environment URI flags, invalid existing-key combinations, and invalid missing-prefix seek settings.
