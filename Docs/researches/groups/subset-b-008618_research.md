# subset-b-008618 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/multi_cf_iterator_impl.h -->
# sources/storage-engines/rocksdb/db/multi_cf_iterator_impl.h

## Purpose
`multi_cf_iterator_impl.h` implements the shared heap-based engine behind RocksDB iterators that merge multiple column-family iterators into one user-key stream. It supports both forward and reverse traversal, duplicate-key coalescing across column families, bounds inherited from child iterators, and deferred value materialization through `ReadOptions::allow_unprepared_value`.

## Important APIs, Types, And Functions
`MultiCfIteratorInfo` is the heap item: a column-family handle, a raw child `Iterator*`, and an `order` tie-breaker preserving the caller's column-family priority.

`MultiCfIteratorImpl<ResetFunc, PopulateFunc>` owns the child `(ColumnFamilyHandle*, unique_ptr<Iterator>)` pairs, the comparator, a status accumulator, and callback hooks. `reset_func_` is invoked before seeks/advances to clear higher-level coalesced state. `populate_func_` receives all heap entries for the current user key after values/columns have been prepared.

The public surface is iterator-like: `SeekToFirst`, `Seek`, `SeekToLast`, `SeekForPrev`, `Next`, `Prev`, `key`, `Valid`, `status`, and `PrepareValue`. Internally it uses a `std::variant` of `BinaryHeap` instances: `MultiCfMinHeap` for forward order and `MultiCfMaxHeap` for reverse order. `MultiCfHeapItemComparator` compares child iterator keys with the supplied RocksDB comparator and breaks equal-key ties by `order`.

## Control Flow
Seek operations switch to the correct heap direction through `GetHeap`, call `reset_func_`, clear the heap, seek every child iterator, and push valid children. If a child is invalid with a non-OK status, `considerStatus` records the first error and clears the heap so the composite iterator becomes invalid.

`Next` and `Prev` first ensure the heap direction matches the traversal. If switching direction, they rebuild the opposite heap around the current key via `Seek` or `SeekForPrev`. `AdvanceIterator` pops the top item, advances any other child iterators with the same key so duplicate keys appear only once, advances the original top iterator, and reinserts valid children. After a successful seek or advance, values are eagerly populated unless `allow_unprepared_value_` is enabled.

`PrepareValue` is meaningful only when unprepared values are allowed. It collects the current top entry and all same-key entries, calls each child iterator's `PrepareValue`, restores the heap, and calls `populate_func_` with the same-key group. A failed child preparation records the child status, clears the heap, and makes the multi-CF iterator invalid.

## State And Persistence Behavior
This header does not persist database state; it manages transient iterator state over child iterators created elsewhere. The important state is the active heap direction, current heap contents, accumulated `Status`, and any coalesced value/column state owned by the caller through `reset_func_` and `populate_func_`.

Duplicate-key elimination is stateful across advances. Child iterators that share the current user key are consumed together so a key is returned once even if several column families contain it. The `order` tie-breaker determines deterministic conflict resolution by controlling how same-key entries are ordered before population.

## Dependencies And Integration Points
The implementation depends on RocksDB `Iterator`, `ColumnFamilyHandle`, `Comparator`, `ReadOptions`, `Status`, `Slice`, `autovector`, and `util/heap.h`. It is designed to be embedded by higher-level coalescing and attribute-group iterators that define how same-key values or wide columns are combined.

Integration points include child iterator status semantics, child `PrepareValue`, comparator compatibility across column families, prefix-iteration behavior, and `ReadOptions::allow_unprepared_value`.

## Risks
All child iterators must use compatible comparators. A different comparator order can violate heap ordering, which is why callers/tests reject mixed comparator configurations.

The implementation assumes equal keys are grouped by comparator equality and that `order` is unique for same-key tie-breaking. If a child iterator becomes invalid because of manual prefix iteration, comments acknowledge the composite result is undefined. Direction switches rebuild heaps around copied current keys; any bug there can skip or repeat the current key.

Deferred value handling is error-sensitive. A child `PrepareValue` failure must invalidate the whole iterator so callers do not observe a key without a valid merged value.

## Test Signals
`multi_cf_iterator_test.cc` validates this engine indirectly through coalescing and attribute-group iterators: forward/reverse traversal, `Seek`/`SeekForPrev`, lower and upper bounds, empty column families, duplicate-key tie-breaking by column-family order, wide-column merging, same/different comparator handling, unprepared blob values, corruption propagation, snapshot auto-refresh, and blob-backed wide columns.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/multi_cf_iterator_impl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/multi_cf_iterator_test.cc -->
# sources/storage-engines/rocksdb/db/multi_cf_iterator_test.cc

## Purpose
`multi_cf_iterator_test.cc` is the behavioral test suite for RocksDB's multi-column-family iterator APIs. It verifies `DB::NewCoalescingIterator` and `DB::NewAttributeGroupIterator` across duplicate keys, column-family priority, forward/reverse movement, bounds, snapshots, custom comparators, wide columns, and deferred value preparation.

## Important APIs, Types, And Functions
`CoalescingIteratorTest` extends `DBTestBase` and provides `VerifyCoalescingIterator`, which checks `SeekToFirst`/`Next` and `SeekToLast`/`Prev` against expected keys, values, and optional wide columns. `VerifyExpectedKeys` verifies the natural order of a single column-family iterator.

`AttributeGroupIteratorTest` similarly provides `VerifyAttributeGroupIterator`, checking `AttributeGroupIterator::attribute_groups()` and deferred `PrepareValue`.

The tests use public APIs including `NewCoalescingIterator`, `NewAttributeGroupIterator`, `Put`, `PutEntity`, `GetSnapshot`, `ReleaseSnapshot`, `Flush`, `CompactRange`, `Iterator::PrepareValue`, `Iterator::columns`, `AttributeGroups`, `IteratorAttributeGroups`, wide-column helpers, and RocksDB sync points.

## Control Flow
The coalescing tests start with invalid input (`NewCoalescingIterator` with no column families), then cover simple values. Unique keys across column families must produce globally sorted keys independent of supplied CF order. Duplicate keys must collapse to one result; the chosen scalar value follows the priority implied by the caller's CF handle order.

Bounds tests repeat unique-key and duplicate-key scenarios with inclusive lower bounds and exclusive upper bounds, including explicit `Seek` and `SeekForPrev` calls around the bounds. Snapshot tests install sync-point dependencies so a flush or update races with multi-CF snapshot acquisition, then verify explicit snapshots see old values and implicit snapshots see a consistent current view.

Wide-column tests insert `AttributeGroups` with overlapping column names and verify coalesced columns. Some columns are merged, and overlapping non-default columns resolve according to CF order. Comparator tests ensure a coalescing iterator rejects column families with different comparator names/orders while accepting independently allocated but semantically identical custom comparators.

The unprepared-value tests enable blob files and `ReadOptions::allow_unprepared_value`. They expect values or attribute groups to be empty before `PrepareValue`, then populated after successful preparation. One test tampers with blob-index data through a sync point and expects `PrepareValue` to return false, invalidate the iterator, and expose corruption.

## State And Persistence Behavior
The tests create real column families, memtables, SSTs, and blob files. Flushes move data into persistent table/blob files so deferred value preparation exercises storage-backed reads, not only memtable values. Snapshot tests verify visibility across flushes and compactions while an iterator is being created or used.

For duplicate keys, persistent state can contain several values or wide-column groups under the same user key in different column families. The multi-CF iterator exposes one logical entry per key, with conflict resolution determined by the supplied handle order and by column-name coalescing rules.

## Dependencies And Integration Points
The file depends on `db/db_test_util.h`, `db/wide/wide_column_test_util.h`, `rocksdb/attribute_groups.h`, SyncPoint instrumentation, comparator test utilities, blob-file support, and DBTestBase helpers.

Integration points include `DBImpl` multi-CF snapshot creation, child iterator bounds, blob reader `PrepareValue`, wide-column serialization, custom comparator identity/name checks, and auto-refresh with snapshots during compaction.

## Risks
The most important correctness risk is equal-key coalescing. Scalar values and overlapping wide columns intentionally depend on CF handle order, so a heap tie-breaker or population-order bug can produce stable but wrong values.

Snapshot races are subtle. The tests use sync points to force updates between version references and snapshot checks; a change in snapshot acquisition order could reintroduce inconsistent cross-CF views. Deferred value mode must not expose stale empty values after `PrepareValue`, and corruption during blob preparation must not leave the iterator apparently valid.

Comparator compatibility is another risk. Accepting truly different comparators would break global ordering, while rejecting distinct instances of the same comparator would be unnecessarily strict.

## Test Signals
Success signals include expected `IterStatus` strings for seek/advance operations, exact key/value vectors in both traversal directions, invalid-argument statuses for bad CF lists or mixed comparators, expected wide-column sets, old/new snapshot visibility, empty pre-`PrepareValue` values followed by correct populated values, corruption status after blob tampering, and valid attribute-group iteration before and after blob-backed flushes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/multi_cf_iterator_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/multi_scan.cc -->
# sources/storage-engines/rocksdb/db/multi_scan.cc

## Purpose
`multi_scan.cc` implements RocksDB's `MultiScan` wrapper, which scans a sequence of ranges using a DB iterator and optional table-level prepare/prefetch support. It coordinates `ReadOptions::iterate_upper_bound` with each requested scan range and falls back to a slower iterator-recreation path when ranges mix bounded and unbounded scans.

## Important APIs, Types, And Functions
`MultiScan::MultiScan` captures `ReadOptions`, `MultiScanArgs`, `DB*`, and a `ColumnFamilyHandle*`. It normalizes `scan_opts_.use_async_io`: async IO is disabled when the DB file system does not report `FSSupportedOps::kAsyncIO`.

`MultiScanIterator::operator++` advances from one scan range to the next. It checks the underlying iterator status, increments the range index, updates `iterate_upper_bound`, optionally recreates the DB iterator, resets the scan wrapper, and seeks to the next range start.

The implementation uses `db->NewIterator`, `Iterator::Prepare(scan_opts_)`, `Iterator::Seek`, `MultiScanException`, and `MultiScanArgs::GetScanRanges`.

## Control Flow
Construction starts with the first scan range. If that range has a limit, the limit string is copied into `upper_bound_` and `read_options_.iterate_upper_bound` points to it; otherwise the upper bound pointer is cleared. The constructor then checks all scan ranges. If every range either has a limit or every range is unbounded, it can call `Prepare(scan_opts_)` once on the underlying DB iterator. If the set is mixed, it takes the slow path because switching between a non-null and null upper-bound pointer requires creating a new iterator.

Incrementing a `MultiScanIterator` first propagates any non-OK child iterator status as a `MultiScanException`. It then moves to the next scan option. If the next range changes from bounded to unbounded or vice versa, it updates `ReadOptions`, recreates the DB iterator, and calls `scan_.Reset`. If both ranges are bounded, it only overwrites the existing `upper_bound_` value. Finally it seeks to the next range start and throws on seek status failure.

## State And Persistence Behavior
This file has no persistence side effects. It manages transient scan state: the copied read options, the mutable upper-bound string, the current range index, the owned DB iterator, and whether the prepared fast path was available.

The lifetime of `read_options_.iterate_upper_bound` is controlled by `upper_bound_`, avoiding dangling pointers to caller-owned scan arguments. Iterator recreation is used when the upper-bound pointer itself must change between null and non-null.

## Dependencies And Integration Points
The implementation depends on RocksDB public `DB`, `ReadOptions`, `MultiScanArgs`, `ColumnFamilyHandle`, `Iterator`, `FileSystem`, and the helper `CheckFSFeatureSupport` from `file/file_util.h`.

Integration points include `ArenaWrappedDBIter::Init`-style async IO feature checks, DB iterator `Prepare`, block/table multi-scan prefetch paths, and scan-range validation in lower iterator layers.

## Risks
The constructor assumes `scan_opts_.GetScanRanges()[0]` exists; empty `MultiScanArgs` must be rejected before or below this layer. Mixed bounded/unbounded scans intentionally skip `Prepare`, which may reduce performance but avoids invalid iterator state.

Because `iterate_upper_bound` is a pointer in `ReadOptions`, pointer lifetime and pointer/null transitions are delicate. Incorrect reuse could make an iterator consult a stale bound or a non-null pointer for an unbounded range.

## Test Signals
Direct tests are elsewhere in the RocksDB tree, especially table/user-defined-index multi-scan tests. Relevant signals are successful range-by-range iteration, exceptions on invalid child status, correct behavior for mixed bounded/unbounded ranges, no async IO request on file systems without support, and table-level `Prepare` calls only when scan options are compatible.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/multi_scan.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/obsolete_files_test.cc -->
# sources/storage-engines/rocksdb/db/obsolete_files_test.cc

## Purpose
`obsolete_files_test.cc` validates RocksDB obsolete-file discovery and purge behavior for WALs, options files, SST/blob files, direct-write blobs, and no-op purge synchronization. It focuses on safety: obsolete files should be deleted, live or ambiguous files should be kept, and purge bookkeeping should not race with DB close or WAL listing.

## Important APIs, Types, And Functions
Helpers include `WriteFooterlessBlobFile`, which writes a blob log header and record without a footer, and `ListBlobFileNumbers`, which parses `.blob` children in a directory.

`ObsoleteFilesTest` extends `DBTestBase` and defines `AddKeys`, `createLevel0Files`, `CheckFileTypeCounts`, and `ReopenDB`. `ReopenDB` configures low L0 compaction trigger, full obsolete-file purge (`delete_obsolete_files_period_micros = 0`), WAL TTL/size, a separate WAL directory, and disabled stats dumping to avoid unrelated races.

The tests use `DBImpl::FindObsoleteFiles`, `PurgeObsoleteFiles`, `DisableFileDeletions`, `EnableFileDeletions`, `SetOptions`, blob metadata APIs, `JobContext`, sync points, `GetSortedWalFiles`, and test mutex/purge wait hooks.

## Control Flow
`RaceForObsoleteFileDeletion` forces a background compaction to find obsolete files, then starts a user thread that also calls `FindObsoleteFiles` and `PurgeObsoleteFiles` under controlled sync points. It asserts deletion statuses are OK and close-helper pending purge state is empty.

`DeleteObsoleteOptionsFile` disables file deletions while toggling options several times, re-enables deletions, closes the DB, and verifies only two current options files remain.

`BlobFiles` manually adds one obsolete blob file to `VersionSet` and one live blob file to current `VersionStorageInfo`, runs `FindObsoleteFiles`, checks delete/live lists and `files_grabbed_for_purge`, then adds full-scan candidates and verifies purge deletes only old and obsolete blobs while retaining live and pending blobs.

`FooterlessBlobFileIsKeptDuringPurge` creates a blob file without a footer, makes it a full-scan candidate, and verifies purge does not delete it. `SealedDirectWriteBlobFileIsKeptDuringPurge` enables direct blob writes, writes two large values, identifies a sealed blob file, schedules purge, waits for purge completion, verifies the key still reads, and checks the file was not deleted.

`GetSortedWalFilesHangsAfterNoopPurge` reproduces a previous hang: an iterator destruction triggers a purge path with no files to delete while another thread waits in `GetSortedWalFiles`. Sync points force the wait ordering and joining the thread proves the condition variable was signaled.

## State And Persistence Behavior
The suite manipulates real DB directories, WAL directories, manifests, options files, SSTs, and blob files. It verifies both in-memory purge bookkeeping (`JobContext`, `files_grabbed_for_purge`, live blob metadata) and file-system-visible results.

Blob purge safety is conservative. Files listed as live, pending output, pending minimum blob number, footerless/possibly incomplete, or direct-write sealed and still referenced must remain on disk. Only files known obsolete or old full-scan candidates below pending thresholds are deleted.

Options-file persistence is tested by repeated option changes while deletion is disabled. On close/re-enable, obsolete options files should be cleaned so only the latest bounded set remains.

## Dependencies And Integration Points
The file depends on DB internals (`DBImpl`, `VersionSet`, `VersionStorageInfo`, `JobContext`), blob log writer/metadata, filename parsing, file read/write helpers, SyncPoint, and DBTestBase.

Integration points include compaction-generated obsolete files, WAL TTL/size cleanup, manifest/live metadata, delayed file deletion, scheduled purge workers, DB close cleanup, direct blob write partitioning, and `DB::GetSortedWalFiles`.

## Risks
File deletion is race-prone. The same file can be discovered by background compaction, a forced user scan, or close cleanup; the grabbed-for-purge set must prevent double deletion and must be cleared after purge.

Blob files have several ambiguous states. Footerless files may be incomplete and should not be purged merely because they appear old. Direct-write blobs can be sealed yet still required by unflushed or visible keys. No-op purge paths must notify waiters even without deleting files.

Assertions depend on file-name parsing and exact file-type counts. Changes in options-file retention policy or blob naming would require test updates while preserving safety invariants.

## Test Signals
Success signals include OK delete statuses, exact WAL/options file counts, `JobContext` delete/live blob lists, expected blob filenames in deletion callbacks, retained footerless/direct-write blob files, successful reads after scheduled purge, empty pending-purge sets on close, and `GetSortedWalFiles` returning without hanging.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/obsolete_files_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/options_file_test.cc -->
# sources/storage-engines/rocksdb/db/options_file_test.cc

## Purpose
`options_file_test.cc` verifies RocksDB options-file naming and retention. It ensures repeated DB opens keep a bounded number of current `OPTIONS-*` files and that regular and temporary options filenames parse as the intended file types and numbers.

## Important APIs, Types, And Functions
`OptionsFileTest` is a simple GoogleTest fixture with a per-thread DB path.

`UpdateOptionsFiles` lists DB directory children, parses names with `ParseFileName`, counts `kOptionsFile` entries, and accumulates the historical names seen. `VerifyOptionsFileName` lists current option files and verifies any newly retained file name is lexicographically newer than past names that have disappeared.

The tests use `DestroyDB`, `DB::Open`, `DB::GetEnv`, `DB::GetName`, `OptionsFileName`, `TempOptionsFileName`, `ParseFileName`, and `kTempFileNameSuffix`.

## Control Flow
`NumberOfOptionsFiles` destroys the DB, then opens and closes it twenty times. After each open it counts options files, requiring at least one and no more than two, then verifies retained names correspond to the latest files rather than old historical ones.

`OptionsFileName` constructs an options filename for number `12345` and checks parsing returns `kOptionsFile` and the same number. It then constructs a temporary options filename for number `54352`, verifies the temp suffix is present, and checks parsing reports `kTempFile` with the same number.

## State And Persistence Behavior
This test observes persistent metadata files in the DB directory. Reopen cycles create new options-file state, while RocksDB cleanup removes older options files. The retention invariant is bounded to two files and latest-file preserving.

Temporary options files are not treated as durable options files. They parse as temp files so incomplete writes can be distinguished from committed `OPTIONS-*` metadata.

## Dependencies And Integration Points
The file depends on `db/db_impl/db_impl.h`, `db/db_test_util.h`, public options/table headers, filename parsing, and the default Env directory listing.

Integration points include DB open/close, options-file creation, obsolete-file cleanup, and filename parser conventions shared with other metadata files.

## Risks
The freshness check uses filename string ordering, which is valid only if options filenames preserve monotonic numeric ordering lexicographically. Retention policy changes that keep more historical files would break the test but not necessarily the DB.

On Windows release builds, the test `main` returns without running tests because of platform/debug constraints, so coverage differs by build environment.

## Test Signals
Success signals are one or two options files after each reopen, retained current filenames newer than removed historical names, correct parsing of `OPTIONS-12345`, and temp options names parsing as `kTempFile` with the temp suffix.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/options_file_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/output_validator.cc -->
# sources/storage-engines/rocksdb/db/output_validator.cc

## Purpose
`output_validator.cc` implements `OutputValidator::Add`, a compact validator used while building SST output. It checks internal-key structural validity, enforces nondecreasing internal-key order, and optionally maintains a rolling paranoid hash over emitted keys and values.

## Important APIs, Types, And Functions
The single function is `Status OutputValidator::Add(const Slice& key, const Slice& value)`. It uses `NPHash64` for rolling key/value hashing when hashing is enabled, `kNumInternalBytes` to reject keys too short to contain an internal suffix, and `InternalKeyComparator::Compare` to detect out-of-order output.

## Control Flow
`Add` first updates `paranoid_hash_` with the key and then the value if `enable_hash_` is true. It then rejects any key shorter than RocksDB's internal key trailer. If a previous key exists and the new key compares less than it, the function returns corruption. Otherwise it copies the current key into `prev_key_` and returns OK.

## State And Persistence Behavior
The validator keeps only transient state: previous internal key and rolling hash. It does not persist the hash and the header explicitly says the hash is not a stable cross-release format. Its purpose is runtime validation and comparison between produced and read-back output sequences.

## Dependencies And Integration Points
The file depends on `db/output_validator.h`, `util/hash.h`, and `InternalKeyComparator`. It is integrated with compaction/table-building paths that feed every output key/value through a validator and may compare validators after reading output back.

## Risks
Ordering is only as correct as the supplied internal comparator. The check permits equal keys because it only rejects `Compare < 0`; this matches the broad invariant of nondecreasing order but relies on upstream compaction rules for duplicate internal-key constraints.

Hashing includes raw key and value bytes in sequence. Any caller expecting a persisted or portable checksum would be wrong; `GetHash` is intentionally unstable between releases.

## Test Signals
Expected signals are corruption statuses for keys shorter than `kNumInternalBytes` and for out-of-order internal keys, stable matching hashes for identical key/value streams, and OK status for correctly ordered SST output.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/output_validator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/output_validator.h -->
# sources/storage-engines/rocksdb/db/output_validator.h

## Purpose
`output_validator.h` declares `OutputValidator`, a small helper for validating key/value sequences inserted into SST files. It checks ordering and can compute a rolling hash used to compare what was written with what is later read back.

## Important APIs, Types, And Functions
The constructor takes an `InternalKeyComparator`, an `enable_hash` flag, and an optional precalculated hash seed. `Add` validates and records each key/value pair. `CompareValidator` compares two validators by `GetHash`. `GetHash` exposes the current hash with a warning that it is not intended as a persisted format.

Private state includes the comparator reference, previous-key buffer, rolling `paranoid_hash_`, and `enable_hash_`.

## Control Flow
Callers construct one validator per output/read-back stream, call `Add` for every internal key and value in order, and optionally compare validators after both streams have been processed. The header leaves the validation implementation to `output_validator.cc`.

## State And Persistence Behavior
The class stores transient validation state only. `prev_key_` grows to hold the most recently observed internal key. The rolling hash can be seeded, enabling continuation or comparison with a known earlier state, but the comments explicitly avoid persistence guarantees.

## Dependencies And Integration Points
The header depends on `db/dbformat.h`, `rocksdb/slice.h`, and `rocksdb/status.h`. It integrates with compaction and SST creation/readback code that can supply internal keys, values, and an `InternalKeyComparator`.

## Risks
`CompareValidator` compares hashes only; a hash collision could theoretically hide differences. The hash is also gated by `enable_hash_`, so comparing validators with hashing disabled compares identical zero/default hashes and should only be done when hashing was intentionally enabled or seeded.

The comparator is held by reference, so it must outlive the validator.

## Test Signals
Tests or callers should see OK for sorted internal-key streams, corruption from `Add` for malformed or descending keys, and matching hashes for identical streams when hashing is enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/output_validator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/perf_context_test.cc -->
# sources/storage-engines/rocksdb/db/perf_context_test.cc

## Purpose
`perf_context_test.cc` validates RocksDB's thread-local `PerfContext` counters and timers across reads, writes, iterators, mutex instrumentation, merge operations, per-level counters, CPU timers, and command-line profiling modes. It is both a correctness suite and an optional diagnostic benchmark when verbose flags are used.

## Important APIs, Types, And Functions
Global flags configure key count, random insertion, memtable type, write buffer sizes, and verbose output. `OpenDb` opens the per-thread DB with those options and optional hash skip-list memtable.

`ProfileQueries` is the central helper. It writes keys with a mid-stream flush, collects histograms from `get_perf_context()` for Put/Get/MultiGet counters and timers, optionally asserts timing counters are positive, reopens read-only, and repeats read measurements.

Tests use `SetPerfLevel`, `get_perf_context()->Reset`, `PerfContext::ToString`, per-level macros such as `PERF_COUNTER_BY_LEVEL_ADD`, `StopWatch`/`StopWatchNano`, `InstrumentedMutex`, `InstrumentedCondVar`, merge operators, snapshots, `GetEntity`, `MultiGetEntity`, iterators, and CPU-time perf levels.

## Control Flow
`SeekIntoDeletion` creates many keys, deletes all but one, then profiles `Get`, `SeekToFirst`, `Seek`, and `Next` over tombstone-heavy state. `StopWatchNanoOverhead` and `StopWatchOverhead` measure timer overhead into histograms.

`KeyComparisonCount` runs `ProfileQueries` under count-disabled/time-enabled levels, ensuring counters can be enabled, disabled, and time-validated. `SeekKeyComparison` profiles put and seek comparison counts after sequential or random insertion.

Mutex tests create instrumented locks and condition variables and verify DB mutex wait counters are populated only for DB mutex stats codes and only at relevant perf levels. `ToString` verifies zero-inclusion/exclusion formatting.

Merge tests validate both timing and counts. `MergeOperatorTime` expects merge operator time after memtable reads, flushed SST reads, and compaction. `MergeOperandCount` writes keys with increasing merge operand counts protected by snapshots, then verifies point lookup, entity lookup, MultiGet, MultiGetEntity, and forward/backward iteration counters in memtable and table-file states.

Copy/move and per-level tests verify `PerfContext` ownership semantics, enable/disable behavior, by-level aggregation, and string rendering. `CPUTimer` skips if CPU nanos are unsupported, then asserts CPU-time counters monotonically increase for Get and iterator operations. `WriteMemtableTimePerfLevel` checks write memtable time is present under wait timing but not under count-only perf level.

## State And Persistence Behavior
The file repeatedly destroys and reopens a real DB. Flushes split reads between memtable and SST paths; read-only reopen verifies counters in read-only DB mode. Snapshots in the merge-count test preserve merge operands through flush so counters reflect unresolved operands rather than collapsed state.

`PerfContext` itself is thread-local transient state. Tests reset it around each operation and assert counters reflect only the current measured call. Per-level state can be enabled, disabled, copied, moved, cleared, and rendered.

## Dependencies And Integration Points
Dependencies include public `rocksdb/perf_context.h`, DB APIs, memtable factories, merge operators, histogram and stop-watch utilities, instrumented mutex/condition variable classes, thread-status test hooks, CPU clock support, and string utilities.

Integration points span DB read/write internals, WAL writing, memtable insertion, output-file lookup, read-only open, mutex wait instrumentation, merge resolution, iterator movement, per-level Bloom/cache counters, and performance level selection.

## Risks
Timing assertions can be environment-sensitive. The suite uses `EXPECT_GT`/`ASSERT_GT` only when perf level should enable timers, but very fast operations or unsupported CPU timers require care; CPU timer tests skip when unsupported.

Global flags can make the test more expensive or alter behavior. Debug-only mutex delay hooks are guarded, so release/debug builds have different expectations for mutex wait totals. Per-level copy/move tests mutate the global thread-local context with `std::move`, so they must reset and clear state carefully.

## Test Signals
Success signals include nonzero or zero counters at the expected perf levels, correct `ToString` filtering, DB mutex wait counters only for DB mutex stats codes, positive merge operator time, exact merge operand counts for keys with 1/2/3 operands, monotonic CPU iterator timers, correct per-level string fragments, and write memtable timing only when the selected perf level records it.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/perf_context_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/periodic_task_scheduler.cc -->
# sources/storage-engines/rocksdb/db/periodic_task_scheduler.cc

## Purpose
`periodic_task_scheduler.cc` implements `PeriodicTaskScheduler`, the DB-owned scheduler for recurring tasks such as stats dumping, stats persistence, info-log flushing, sequence-number time recording, and periodic compaction triggering. It wraps a global single-threaded `Timer` with serialized register/unregister operations and one active task per task type per scheduler.

## Important APIs, Types, And Functions
The file defines global `timer_mutex`, default repeat periods, and short task-name prefixes. `Register` has overloads for default and explicit repeat periods. `Unregister` cancels a task and shuts the timer down if no tasks remain. `Default` returns a static global `Timer` backed by `SystemClock::Default`. Debug builds expose `TEST_OverrideTimer`.

`kDefaultPeriodSeconds` sets `kFlushInfoLog` to 10 seconds and other optional tasks to `kInvalidPeriodSec` until configured explicitly. `kPeriodicTaskTypeNames` supplies readable prefixes for unique timer IDs.

## Control Flow
`Register(task_type, fn, run_immediately)` delegates to the explicit-period overload using the default period. The explicit overload locks `timer_mutex`, rejects period zero, checks for an existing task of the same type, and returns OK without work if the period is unchanged. If the period changed, it cancels and erases the old timer entry.

The scheduler starts the global timer, creates a unique ID from the task prefix and global `id_`, staggers initial delays with an atomic counter modulo the repeat period, and adds the function to the timer. If `run_immediately` is false, it adds a full period to the initial delay. On success it inserts `TaskInfo` into `tasks_map_` and fires a debug sync-point callback with the registered type and period.

`Unregister` locks the same mutex, cancels and erases a registered task if present, and shuts down the timer when it has no pending tasks.

## State And Persistence Behavior
The scheduler has only in-memory state. Per-instance `tasks_map_` tracks the task name and repeat period for each task type. The global timer and global ID are process-level state shared by DB instances. No task registration survives DB process restart; DB open/options code must re-register tasks.

Initial delay staggering spreads tasks registered by different DBs or task types over the period to reduce synchronized wakeups. Info-log flushing is expected to keep the timer available even when other periodic tasks are disabled.

## Dependencies And Integration Points
The implementation depends on `util/timer.h`, `rocksdb/system_clock.h`, `port::Mutex`, `MutexLock`, and SyncPoint in debug builds. It integrates with DBImpl startup/options code that registers/unregisters periodic work and with tests that override the timer clock.

## Risks
The global mutex is intentionally coarse because `Timer::Start`, `Shutdown`, `Add`, and `Cancel` are not independently thread-safe. Any new caller bypassing this mutex could race global timer state or `tasks_map_`.

Registering a task with the same period does not update the callback function. This is part of the current semantics but can surprise callers expecting function replacement. The initial-delay modulo uses `repeat_period_seconds`; period zero is rejected before modulo to avoid division by zero.

Global timer sharing means multi-DB behavior depends on correct unique IDs and cancellation by stored name. A leaked task would keep the timer running after DB close.

## Test Signals
`periodic_task_scheduler_test.cc` checks task firing under a mock clock, dynamic unregister/re-register through DB options, trigger-compaction period registration, multiple DB instances sharing the global timer, and multiple Env wrappers with the same clock.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/periodic_task_scheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/periodic_task_scheduler.h -->
# sources/storage-engines/rocksdb/db/periodic_task_scheduler.h

## Purpose
`periodic_task_scheduler.h` declares the scheduler used by DB instances to manage periodic DB maintenance tasks. It defines the task types, the task function signature, default invalid-period constant, and debug-only inspection hooks.

## Important APIs, Types, And Functions
`PeriodicTaskFunc` is `std::function<void()>`. `kInvalidPeriodSec` is zero and marks disabled/invalid repeat periods. `PeriodicTaskType` enumerates `kDumpStats`, `kPersistStats`, `kFlushInfoLog`, `kRecordSeqnoTime`, `kTriggerCompaction`, and `kMax`.

`PeriodicTaskScheduler` is noncopyable and nonmovable. Public APIs are `Register(task_type, fn, run_immediately)`, `Register(task_type, fn, repeat_period_seconds, run_immediately)`, and `Unregister(task_type)`. Debug builds add `TEST_OverrideTimer`, `TEST_WaitForRun`, `TEST_GetValidTaskNum`, and `TEST_HasTask`.

Private state includes `TaskInfo` with timer task name and period, `tasks_map_`, a pointer to the shared timer returned by `Default`, global task `id_`, and `kMicrosInSecond`.

## Control Flow
Callers register each task type with a callback and period. Re-registering a task type updates the repeat period when it changes, otherwise it is a no-op. Unregister cancels by task type. Debug helpers route to the timer or inspect `tasks_map_`.

## State And Persistence Behavior
The class stores per-scheduler in-memory registration state while using a global timer for execution. It does not own persisted settings; DB options determine which registrations are made. `tasks_map_` is the source of whether a task type is registered for the scheduler instance.

## Dependencies And Integration Points
The header depends on `util/timer.h` and forward-declares `SystemClock`. It is used by `DBImpl` periodic maintenance code and by tests that need deterministic mock-clock scheduling.

## Risks
Because timer state is global but task maps are per instance, all register/unregister operations must stay synchronized with the implementation's global mutex. The debug accessors read `tasks_map_` without local locking in the header, relying on test-controlled access patterns.

`kMax` is used in tests/counts; adding a new enum value requires updating default periods, task names, and expectations.

## Test Signals
Tests check registered task counts, specific task presence, mock-clock waiting, multi-instance aggregate counts, dynamic DB option updates, and trigger-compaction registration periods.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/periodic_task_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/periodic_task_scheduler_test.cc -->
# sources/storage-engines/rocksdb/db/periodic_task_scheduler_test.cc

## Purpose
`periodic_task_scheduler_test.cc` verifies periodic DB task scheduling with deterministic mock time and selected real-time integration. It covers basic task firing, dynamic DB option changes, periodic compaction trigger period computation, time-based column-family selection, multiple DB instances sharing the global timer, and multiple Env wrappers.

## Important APIs, Types, And Functions
`PeriodicTaskSchedulerTest` extends `DBTestBase`, installs a `MockSystemClock` through a `CompositeEnvWrapper`, and uses a sync point (`DBImpl::StartPeriodicTaskScheduler:Init`) to call `PeriodicTaskScheduler::TEST_OverrideTimer`.

`TriggerCompactionTest` is a separate `DBTestBase` fixture that avoids mock-clock interactions for multi-CF trigger-compaction selection.

The tests use DB options such as `stats_dump_period_sec`, `stats_persist_period_sec`, `periodic_compaction_seconds`, `ttl`, `bottommost_file_compaction_delay`, FIFO file-temperature thresholds, `max_compaction_trigger_wakeup_seconds`, and `read_triggered_compaction_threshold`. They observe sync points in `DumpStats`, `PersistStats`, `FlushInfoLog`, `TriggerPeriodicCompaction`, and scheduler registration.

## Control Flow
`Basic` opens a DB with dump/persist periods, counts periodic callback invocations under mock sleeps, disables dump/persist through `SetDBOptions`, verifies info-log flush keeps running, re-enables dump stats with a new period, and checks trigger compaction fires after its non-immediate period.

`TriggerCompactionPeriodComputation` captures the period used when registering `kTriggerCompaction`. It opens/reopens DBs under many option combinations: 12-hour cap from long stats dump, stats dump/persist periods, periodic compaction divided by the trigger divisor, TTL, bottommost delay, FIFO file-temperature thresholds, minimum across multiple column families, clamping to 1 second, and `max_compaction_trigger_wakeup_seconds` caps.

`QueuesAllTimeBasedOptions` creates multiple column families with different compaction-related options and waits for periodic compaction. A sync point records which CFs have compaction scores computed. CFs with periodic, TTL, bottommost, FIFO temperature, or read-triggered options should be considered; default and explicitly none should not.

`MultiInstances` opens ten DBs with the same mock Env, verifies aggregate pending task counts, advances mock time to count callbacks across instances, closes half the DBs, and verifies only remaining instances fire. `MultiEnv` opens DBs through different Env wrappers sharing the mock clock to ensure scheduler/timer use is compatible.

## State And Persistence Behavior
The scheduler state is in-memory and tied to DB lifetime/options. These tests verify that DB option updates mutate registered tasks without reopening and that closing DB instances unregisters their tasks. Multi-CF tests persist CF descriptors and reopen with distinct options to validate trigger-period computation across stored/opened column families.

Periodic compaction selection is not testing compaction output; it tests that configured CFs enter the scoring path when the periodic trigger fires.

## Dependencies And Integration Points
The file depends on `db/periodic_task_scheduler.h`, `db/column_family.h`, `db/db_test_util.h`, `env/composite_env_wrapper.h`, and `test_util/mock_time_env.h`.

Integration points include DBImpl scheduler startup, DB option mutation, ColumnFamilyData iteration, trigger-compaction period computation, FIFO compaction options, mock clock timed waits, SyncPoint, and global timer sharing.

## Risks
Mock-clock scheduling can be sensitive to timer wait points, so the fixture installs `InstallTimedWaitFixCallback` and uses `TEST_WaitForPeriodicTaskRun`. Trigger compaction uses `run_immediately=false`, so tests account for elapsed mock time carefully.

Global timer sharing means tests can interfere if callbacks/sync points are not cleared by fixture teardown; these tests rely on DBTestBase and SyncPoint handling. The period-computation test destroys/reopens DBs repeatedly to avoid persisted CF/options leakage.

## Test Signals
Success signals include exact callback counters after mock sleeps, expected pending task counts, scheduler changes after `SetDBOptions`, captured trigger-compaction periods for 13 option cases, CF names observed or not observed during trigger scoring, aggregate callback counts across ten DB instances, and clean close across multiple Env wrappers.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/periodic_task_scheduler_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/pinned_iterators_manager.h -->
# sources/storage-engines/rocksdb/db/pinned_iterators_manager.h

## Purpose
`pinned_iterators_manager.h` defines `PinnedIteratorsManager`, a `Cleanable` helper that owns iterators or arbitrary pointers pinned during iterator operation and releases them together when pinned data is no longer needed.

## Important APIs, Types, And Functions
The class derives from `Cleanable`. `StartPinning` enables pinning. `PinningEnabled` reports state. `PinIterator` registers an `InternalIterator*` for either normal `delete` or arena-style destructor-only release. `PinPtr` registers any pointer with a release callback. `ReleasePinnedData` releases unique pinned pointers, clears the vector, disables pinning, and calls `Cleanable::Reset`.

Private release helpers are `ReleaseInternalIterator` and `ReleaseArenaInternalIterator`.

## Control Flow
Callers must call `StartPinning` before pinning. Each non-null pointer is appended with its release function. On release or destruction while enabled, the manager sorts the vector of `(ptr, release_func)` pairs, removes duplicate pairs with `std::unique`, invokes each release callback, clears state, and resets inherited cleanups.

## State And Persistence Behavior
The manager stores transient ownership state only. `pinning_enabled` guards lifecycle, and `pinned_ptrs_` stores release work. Move construction/assignment are defaulted, allowing ownership transfer. The destructor releases pinned data if pinning remains enabled.

## Dependencies And Integration Points
The header depends on `table/internal_iterator.h` for `InternalIterator` and `Cleanable`. It integrates with DB/table iterators that need to keep child iterators or resources alive while exposing pinned slices/data to callers.

## Risks
`PinPtr` asserts pinning is enabled, so caller lifecycle ordering matters. Duplicate removal sorts pairs, not just raw pointers; the same pointer registered with different release functions would be released twice, which should never happen.

Arena iterators are destroyed with an explicit destructor call and no deallocation. Passing the wrong `arena` flag would either leak memory or delete arena-owned storage incorrectly. After `ReleasePinnedData`, inherited `Cleanable` cleanup callbacks are also reset, so callers must not expect them to survive.

## Test Signals
Relevant signals are absence of leaks/double frees in iterator tests, pinned resources released on explicit release and destructor paths, and correct behavior when arena-backed internal iterators are pinned.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/pinned_iterators_manager.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/plain_table_db_test.cc -->
# sources/storage-engines/rocksdb/db/plain_table_db_test.cc

## Purpose
`plain_table_db_test.cc` is a comprehensive test suite for RocksDB's PlainTable format. It validates non-mmap reads, option compatibility, flushing, bloom/index metadata, read-only/mmap pinning, iteration, long keys, custom comparators, hash bucket conflicts, compaction triggering, adaptive table opening, and unsupported range deletes.

## Important APIs, Types, And Functions
`PlainTableKeyDecoderTest.ReadNonMmap` tests `PlainTableFileReader` buffering over a `StringSource`.

`PlainTableDBTest` is parameterized by mmap mode. It builds default PlainTable options with prefix extractor, hash-link-list memtable, and disabled concurrent/unordered writes. Helpers provide reopen/destroy, `Put`, `Delete`, `Get`, level file counts, and iterator status.

`TestPlainTableReader` subclasses `PlainTableReader` to verify metadata, populate index, and assert Bloom matches/misses. `TestPlainTableFactory` subclasses `PlainTableFactory` to read table properties/meta blocks, verify on-file Bloom/index blocks when configured, and create the test reader.

## Control Flow
Option tests verify that PlainTables built with a prefix extractor cannot be reopened without one or with a different one, while tables built without a prefix extractor require `hash_table_ratio == 0`. Flush tests iterate over huge-page size, encoding type, Bloom/full-scan mode, total-order mode, and index-in-file mode, checking reads, table-reader memory, table properties, and full-scan iteration behavior.

`Flush2`, `BloomSchema`, and iterator tests use `TestPlainTableFactory` to verify Bloom behavior, table properties, column-family metadata, and seek behavior. `Immortal` compares value pin/copy behavior in normal and read-only reopen, with mmap mode avoiding copies after reopen.

Iterator tests cover fixed and variable key length, prefix and plain encoding, long keys, reverse suffix comparator ordering, and bucket-conflict behavior. Hash bucket tests force conflicts and validate both point lookups and seeks for existing and non-existing keys under normal and reverse suffix comparators.

`CompactionTrigger` configures small write buffers and an L0 trigger to ensure PlainTable output participates in normal compaction scheduling. `AdaptiveTable` writes PlainTable data, reopens with an adaptive factory, verifies existing and new data, then demonstrates that opening with only the wrong table factory fails to read expected values when paranoid checks are disabled. `DeleteRangeNotSupported` verifies range deletes fail directly and inside a write batch, preserve atomicity, poison subsequent flush/put until reopen, and do not corrupt recoverable WAL state.

## State And Persistence Behavior
The tests repeatedly create real PlainTable SSTs and reopen them with compatible or incompatible options. They inspect persisted table properties, optional persisted Bloom/index meta blocks, table-reader memory estimates, and level file counts.

Read-only and mmap behavior affects whether value reads are copied or pinned. Range-delete unsupported state demonstrates an error path where WAL recovery remains valid but the current memtable/flush path rejects unsupported range tombstones.

Compaction tests verify PlainTable files are normal LSM participants: flush creates L0 files and reaching the trigger compacts to L1.

## Dependencies And Integration Points
The file depends on DB internals, version set/write batch helpers, filename utilities, cache/table APIs, PlainTable reader/factory/key-coding/Bloom/index classes, meta-block readers, table builders, hash utilities, random/string utilities, merge operators, and GoogleTest parameterization.

Integration points include table factory option serialization, prefix extractors, Bloom filters, `ReadTableProperties`, meta-block lookup, column-family properties, DB open/read-only open, compaction, adaptive table factory dispatch, and write-batch atomicity.

## Risks
PlainTable option compatibility is strict. Reopening with missing/different prefix extractors or hash mode without prefixes can fail or produce unreadable tables. Tests cover both expected hard failures and adaptive-factory success.

Bloom schema tests rely on known false-positive bit patterns and cache-line size; legitimate Bloom implementation changes can require updating expected patterns. Many iterator tests depend on comparator-specific ordering and prefix extractor behavior, so comparator/prefix mismatches are high risk.

Unsupported range deletes are dangerous because a WriteBatch must remain atomic and existing keys must survive even though the operation leaves the DB unable to flush until reopen.

## Test Signals
Success signals include exact error strings for bad options, correct table property values, Bloom miss callbacks for absent keys, correct iteration order under normal and reverse comparators, successful long-key scans, expected file movement from L0 to L1, adaptive factory reads across reopen, `NotSupported` for range deletes and subsequent writes/flushes, and recovery preserving pre-error keys.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/plain_table_db_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/post_memtable_callback.h -->
# sources/storage-engines/rocksdb/db/post_memtable_callback.h

## Purpose
`post_memtable_callback.h` declares `PostMemTableCallback`, an internal write-path callback invoked after a write has been applied to the memtable but before the sequence number is published to readers.

## Important APIs, Types, And Functions
`PostMemTableCallback` is an abstract class with a virtual destructor and pure virtual `Status operator()(SequenceNumber seq, bool disable_memtable)`.

The parameters expose the sequence number associated with the write and whether the memtable is disabled. The return `Status` allows the callback to signal failure to the write path.

## Control Flow
Write-path code can accept an implementation of this callback and invoke it at the post-memtable/pre-publication point. Implementations perform their side effect and return OK or an error.

## State And Persistence Behavior
The header contains no state. Implementations may update external state while the write is not yet visible to readers. Because invocation happens after memtable insertion, callback failure semantics must be coordinated carefully by the write path.

## Dependencies And Integration Points
The header depends on `rocksdb/status.h` and `rocksdb/types.h` for `Status` and `SequenceNumber`. It integrates with RocksDB write queues, memtable insertion, and sequence-number publication. The comment notes write-prepared/write-unprepared transactions with two write queues call `PreReleaseCallback` before publishing sequence numbers to readers, clarifying ordering with the sibling callback type.

## Risks
Callbacks run in a sensitive visibility window. A slow callback delays sequence publication; a failed callback after memtable insertion needs write-path handling that avoids exposing inconsistent state. Implementations must understand `disable_memtable` semantics, which are tied to write queue modes.

## Test Signals
Relevant tests would assert callback ordering relative to memtable writes and sequence publication, propagation of non-OK status, and correct behavior in write-prepared/write-unprepared transaction modes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/post_memtable_callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/pre_release_callback.h -->
# sources/storage-engines/rocksdb/db/pre_release_callback.h

## Purpose
`pre_release_callback.h` declares `PreReleaseCallback`, an internal write-thread hook invoked after WAL writing and before memtable writing/sequence-number release. It lets RocksDB perform ordered side effects on the write thread before a write becomes visible.

## Important APIs, Types, And Functions
`PreReleaseCallback` is an abstract class with a virtual destructor and pure virtual:

`Status Callback(SequenceNumber seq, bool is_mem_disabled, uint64_t log_number, size_t index, size_t total)`.

Parameters provide the sequence number to be released, whether the memtable is disabled, the WAL log number when nonzero, the callback's index within the write group, and the total callbacks in the group. The index/total pair lets implementations reduce redundant group-level work.

## Control Flow
The write thread calls callbacks after WAL write and before memtable write. If a callback returns non-OK, the sequence number is not released and the same status is propagated to all writers in the write group.

## State And Persistence Behavior
The callback itself has no storage in this header, but implementations can update external state while write ordering is serialized by the write thread. Because the WAL may already contain the write, failure handling must preserve recovery and visibility semantics.

## Dependencies And Integration Points
The header depends on `rocksdb/status.h` and `rocksdb/types.h`. It integrates with write groups, WAL logging, memtable-disabled queues, sequence-number release, and transaction/write-prepared modes.

## Risks
This hook is on a critical write-path latency and correctness boundary. A failing callback affects every writer in the group. Misusing `index`/`total` can duplicate or omit group-level work. The `is_mem_disabled` flag is described as debug-oriented, so production logic should not overfit to it unless the write queue contract guarantees it.

## Test Signals
Relevant signals are callback invocation order after WAL and before memtable/sequence release, correct propagation of callback failure to all grouped writers, unreleased sequence numbers on failure, and correct log-number/index/total values.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/pre_release_callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/prefix_test.cc -->
# sources/storage-engines/rocksdb/db/prefix_test.cc

## Purpose
`prefix_test.cc` tests prefix-aware memtable and iterator behavior using a custom binary key comparator. It covers prefix hash memtable factories, prefix bloom/filter behavior, prefix-limited iteration, mixed Put/Merge/Delete histories, backward iteration in prefix seek mode, and several performance/profiling flows gated by gflags.

## Important APIs, Types, And Functions
When `GFLAGS` is unavailable, the file builds a stub `main` that prints a skip message. With gflags, it defines flags controlling bucket counts, prefix/random workloads, write buffers, memtable prefix bloom, huge pages, value size, and debug printing.

`TestKey` stores `prefix` and `sorted` `uint64_t` fields. `TestKeyToSlice` and `SliceToTestKey` encode/decode fixed64 binary keys. `TestKeyComparator` compares by prefix first, then suffix, and supports prefix-only slices. Helpers `PutKey`, `MergeKey`, `DeleteKey`, `SeekIterator`, and `Get` operate on encoded keys.

`SamePrefixTransform` is a `SliceTransform` that maps all keys in a configured domain to one fixed prefix. `PrefixTest` configures DB options with `TestKeyComparator`, fixed 8-byte prefix extractor, block-based Bloom filter with whole-key filtering disabled, and selectable hash skip-list/hash link-list memtable factories.

## Control Flow
`SamePrefixTest.InDomainTest` verifies a transform whose domain excludes some keys does not break seeking/flushing for keys outside the domain.

`TestResult` iterates over hash memtable options and one/two buckets, inserting keys into the same and different prefixes. It verifies `Seek`, `Next`, and `Get` return expected values for head, middle, tail, smaller-prefix, and larger-prefix cases.

`PrefixValid` writes keys for one prefix plus a deleted key in another prefix, enables `prefix_same_as_start`, and verifies iteration stops at the prefix boundary and seeking past the prefix returns invalid. `DynamicPrefixIterator` bulk-loads many prefixes, optionally shuffled, then profiles puts, existing-prefix scans, and non-existing seeks. A flag can intentionally delete during scans to reproduce deadlock scenarios.

`PrefixSeekModePrev` builds three layers of entries using puts/merges/deletes, tracks expected visible state in `std::map`, and randomly alternates `Next` and `Prev` within a prefix to compare iterator values with the map. `PrefixSeekModePrev2` targets a case where a child iterator becomes invalid due to Bloom filtering during reverse movement. `PrefixSeekModePrev3` verifies `SeekToLast` respects `iterate_upper_bound` in prefix seek mode.

## State And Persistence Behavior
The tests create real DB state with memtables and flushed SSTs. Prefix behavior is exercised across both mutable/immutable memtables and table files. Merge and delete histories are included so iterator traversal must resolve internal records correctly, not just scan sorted puts.

The comparator supports prefix-only keys, allowing prefix extractor outputs to participate in comparisons. `prefix_same_as_start` changes iterator validity: iteration is expected to stop when leaving the starting prefix.

## Dependencies And Integration Points
The file depends on DBImpl test hooks, block-based table Bloom filters, memtable factories (`HashSkipList`, `HashLinkList`, `SkipList`), perf context, histograms, stop watches, gflags compatibility, fixed64 coding, merge operators, and a custom comparator/prefix extractor pair.

Integration points include memtable prefix hashing, memtable prefix Bloom, block-based prefix Bloom with whole-key filtering disabled, iterator prefix mode, `SeekForPrev`/`Prev` across merging iterators, `iterate_upper_bound`, merge resolution, and DB flush/reopen lifecycle.

## Risks
Prefix iteration is intentionally narrower than total-order iteration. If callers set `prefix_same_as_start`, seeking outside or past a prefix can produce invalid results even when later keys exist. The tests document that boundary.

The custom comparator decodes fixed64 from slices and assumes valid key sizes except for prefix-only cases. Arbitrary strings would be unsafe with this comparator. The dynamic performance test can be expensive with default high prefix counts, and `trigger_deadlock` intentionally performs deletes during iteration.

Reverse prefix movement is particularly fragile because child iterators can be invalidated by Bloom filters or upper bounds. The last three tests target those edge cases.

## Test Signals
Success signals include exact values from `Get` and iterator movement within prefix groups, invalid iterators when seeking outside prefix constraints, matching iterator/map values while alternating `Next` and `Prev`, no deadlock unless intentionally requested, correct `Prev` result after a seek gap, and `SeekToLast` returning the last key below the upper bound.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/prefix_test.cc -->
