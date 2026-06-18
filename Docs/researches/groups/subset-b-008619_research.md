# subset-b-008619 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_del_aggregator.cc -->
# sources/storage-engines/rocksdb/db/range_del_aggregator.cc

## Purpose

`range_del_aggregator.cc` implements RocksDB's in-memory aggregation layer for fragmented range deletion tombstones. It answers point-key visibility questions during reads and compactions, truncates per-file tombstone iterators to SST file bounds, splits tombstone visibility by snapshots, and creates a merged tombstone iterator for compaction output.

## Important APIs, Types, and Functions

The central implemented types are `TruncatedRangeDelIterator`, `ForwardRangeDelIterator`, `ReverseRangeDelIterator`, `RangeDelAggregator::StripeRep`, `ReadRangeDelAggregator`, `CompactionRangeDelAggregator`, and the file-local `TruncatedRangeDelMergingIter`. Important methods include `Seek`, `SeekInternalKey`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `SplitBySnapshot`, direction-specific `ShouldDelete`, `IsRangeOverlapped`, `AddTombstones`, `CompactionRangeDelAggregator::NewIterator`, and `TruncatedRangeDelMergingIter::key/value/Next/SeekToFirst`.

## Control Flow and State Behavior

`TruncatedRangeDelIterator` wraps a `FragmentedRangeTombstoneIterator` and clips its apparent start/end keys to optional SST smallest/largest internal keys. The constructor parses boundaries and adjusts the largest bound carefully: artificial range-deletion extensions are preserved, sequence-zero largest keys are left alone, and straddling user keys have the end sequence decremented so the truncated tombstone covers the file but not the next SST.

Forward and reverse aggregators maintain active and inactive heaps. Forward scans activate iterators whose starts are at or before the lookup key and retire fragments whose ends are before the key. Reverse scans mirror that with start/end ordering reversed. Active iterators are also kept in a sequence-ordered multiset, so `ShouldDelete` is determined by whether the highest visible covering tombstone sequence is newer than the queried internal key sequence.

`StripeRep` owns truncated iterators for a sequence-number stripe and invalidates the opposite traversal cache whenever the caller switches between forward and backward mode. `ReadRangeDelAggregator` has one stripe from `0` through the read upper bound. `CompactionRangeDelAggregator` splits added iterators by snapshot stripes and optionally applies timestamp upper bounds for `full_history_ts_low` and `trim_ts` during deletion decisions.

`NewIterator()` reuses the original parent iterators, merges them by start key with `TruncatedRangeDelMergingIter`, and feeds the stream back through `FragmentedRangeTombstoneList` for compaction persistence.

## Persistence, Dependencies, and Integration

This file does not write durable state itself, but it decides which point keys are hidden by durable range tombstones and which tombstone fragments are emitted into compaction output. It depends on `dbformat`, `range_tombstone_fragmenter`, `InternalIterator`, `TableBuilder`-adjacent types, `BinaryHeap`, and comparator timestamp semantics. It integrates with DB reads, iterator traversal, file-boundary metadata, snapshot-aware compaction, and range tombstone output building.

## Risks and Test Signals

Risks concentrate around internal-key boundary comparisons, user-defined timestamp bounds, traversal-direction cache invalidation, and snapshot stripe selection. Off-by-one sequence handling at SST boundaries can either leak deleted keys or delete keys from neighboring files. Tests in `range_del_aggregator_test.cc` cover truncation, forward/reverse deletion checks, overlap checks, snapshots, and bounded compaction iterators; fragmenter tests also indirectly protect the expected input shape.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_del_aggregator.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_del_aggregator.h -->
# sources/storage-engines/rocksdb/db/range_del_aggregator.h

## Purpose

`range_del_aggregator.h` declares the range deletion aggregation API used by RocksDB readers and compactions. It defines how fragmented range tombstone iterators are clipped to file boundaries, cached for directional scans, split across snapshot stripes, queried for point-key deletion, and re-exposed as a compaction output iterator.

## Important APIs and Types

`TruncatedRangeDelIterator` is a boundary-aware wrapper around `FragmentedRangeTombstoneIterator`. Its API exposes top-fragment navigation, internal-key and user-key seek methods, `start_key`, `end_key`, `seq`, timestamp access, `SplitBySnapshot`, and upper/lower sequence bounds.

`ForwardRangeDelIterator` and `ReverseRangeDelIterator` are traversal caches. They keep inactive iterators ordered by start/end key and active iterators ordered both by range endpoint and maximum sequence number. `SeqMaxComparator` and `StartKeyMinComparator` supply heap/set ordering.

`RangeDelAggregator` is the abstract base with `AddTombstones`, `ShouldDelete`, `InvalidateRangeDelMapPositions`, `IsEmpty`, and `AddFile`. Its nested `StripeRep` owns the actual iterator set for one sequence interval and supports `ShouldDelete` plus `IsRangeOverlapped`.

`ReadRangeDelAggregator` is the read-path implementation with one stripe. `CompactionRangeDelAggregator` adds snapshot striping, `full_history_ts_low`/`trim_ts` filtering for deletion decisions, and `NewIterator()` for persisted compaction tombstones.

## Control Flow and State Behavior

The header encodes an important split between read-time and compaction-time behavior. Reads need a single visible snapshot upper bound, so `ReadRangeDelAggregator` can query one `StripeRep`. Compaction must preserve snapshot-visible history, so `CompactionRangeDelAggregator` maps snapshot upper bounds to `StripeRep` instances and chooses the first stripe whose upper bound is at least the queried sequence.

Directional traversal is explicit through `RangeDelPositioningMode`. Callers that scan forward or backward can reuse heap state, while random seeks or direction changes must invalidate cached positions. This is why the public base exposes `InvalidateRangeDelMapPositions`.

The `files_seen_` set in the base class tracks table file numbers already added to avoid duplicated range tombstone processing by integration code.

## Persistence, Dependencies, and Integration

The declared APIs bridge `FragmentedRangeTombstoneIterator` from table/memtable range-delete metadata to read iterators, compaction iterators, and table-building logic. Dependencies include `dbformat`, `range_tombstone_fragmenter`, `InternalIterator`, `BinaryHeap`, `TableBuilder`, `VersionEdit`, and comparator/timestamp APIs.

## Risks and Test Signals

The header's contracts are tight: `Seek` targets are user keys with timestamps when enabled, while `SeekInternalKey` accepts internal keys. `SplitBySnapshot` children are lifetime-dependent on the parent tombstone list. Timestamp upper bounds affect deletion decisions but should not accidentally filter persisted tombstone output. Tests assert expected behavior through the concrete implementation in `range_del_aggregator_test.cc`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_del_aggregator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_del_aggregator_bench.cc -->
# sources/storage-engines/rocksdb/db/range_del_aggregator_bench.cc

## Purpose

`range_del_aggregator_bench.cc` is a gflags-based microbenchmark for range tombstone fragmentation, aggregator insertion, and `ShouldDelete` lookup cost. It can benchmark either `ReadRangeDelAggregator` or `CompactionRangeDelAggregator` over randomly generated tombstones.

## Important APIs, Types, and Functions

The benchmark exposes flags for tombstone count, run count, random seed, key-space bounds, tombstone width distribution, number of `ShouldDelete` calls per run, number of `AddTombstones` batches per run, and whether to use the compaction aggregator. `Stats` records nanoseconds spent in fragmentation, `AddTombstones`, first `ShouldDelete`, and later `ShouldDelete` calls. `PersistentRangeTombstone` owns backing strings for `RangeTombstone` slices. `MakeRangeDelIterator` serializes tombstones into a `VectorIterator`, and `Key()` encodes integers as big-endian fixed-width strings so lexicographic bytewise order matches numeric order.

## Control Flow and State Behavior

For each run, the benchmark constructs a fresh aggregator and a vector of fragmented tombstone lists. Each batch fills `FLAGS_num_range_tombstones` with random starts and normally distributed widths, serializes them, times `FragmentedRangeTombstoneList` construction, creates a `FragmentedRangeTombstoneIterator`, and times `AddTombstones`. It then creates a `ParsedInternalKey` at the midpoint sequence and performs one or more forward `ShouldDelete` calls over adjacent generated keys, separating the first lookup from subsequent lookups to show cache warm-up effects.

When compaction mode is enabled, the benchmark uses `CompactionRangeDelAggregator` with a snapshot vector containing `0`; otherwise it uses `ReadRangeDelAggregator` with `kMaxSequenceNumber`.

## Persistence, Dependencies, and Integration

The file has no persistence behavior; it is a standalone executable. It depends on gflags, `SystemClock`, `Random64`, `StopWatchNano`, `VectorIterator`, internal key serialization, and the range tombstone aggregator/fragmenter code under test.

## Risks and Test Signals

The benchmark is performance signal only, not correctness coverage. Because tombstones are regenerated inside the timed loop, comments note possible cache-warming artifacts. The workload uses forward traversal only and bytewise keys only, so it does not measure reverse scans, timestamp comparators, file-boundary truncation, or realistic table-reader lifetimes. Useful signals are relative timings for fragmentation, add cost, first lookup, and cached subsequent lookups under controlled flag changes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_del_aggregator_bench.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_del_aggregator_test.cc -->
# sources/storage-engines/rocksdb/db/range_del_aggregator_test.cc

## Purpose

`range_del_aggregator_test.cc` is the focused GoogleTest suite for the range deletion aggregator. It validates truncated iterator navigation, read-path deletion decisions, range-overlap checks, compaction snapshot semantics, and bounded compaction tombstone output.

## Important APIs, Types, and Helpers

The fixture is `RangeDelAggregatorTest`. Helpers include `MakeRangeDelIter`, `MakeFragmentedTombstoneLists`, `UncutEndpoint`, `InternalValue`, `VerifyIterator`, `VerifySeek`, `VerifySeekForPrev`, `VerifyShouldDelete`, `VerifyIsRangeOverlapped`, `CheckIterPosition`, and `VerifyFragmentedRangeDels`. Local structs describe scan expectations, seek expectations, point deletion cases, and overlap cases.

## Control Flow and State Behavior

The early tests build `FragmentedRangeTombstoneList` objects and wrap them in `TruncatedRangeDelIterator`. `EmptyTruncatedIter`, `UntruncatedIter`, and `UntruncatedIterWithSnapshot` exercise forward/reverse iteration and user-key seeking with and without snapshot upper bounds. `TruncatedIterPartiallyCutTombstones` and `TruncatedIterFullyCutTombstones` verify that SST smallest/largest internal keys clip visible tombstone endpoints exactly.

Read aggregator tests add one or more fragmented iterators to `ReadRangeDelAggregator` and call `ShouldDelete` in forward order and reverse order. They verify deletion depends on both key coverage and tombstone sequence being newer than the queried internal key. Multiple truncated iterator tests simulate adjacent SST file bounds and same-level incremental additions. `IsRangeOverlapped` cases cover empty before/after ranges, boundary-touching ranges, and actual overlaps.

Compaction tests create `CompactionRangeDelAggregator` with no snapshots or snapshots `{9, 19}`. They verify `ShouldDelete` per snapshot stripe and inspect `NewIterator()` output to ensure fragments needed by snapshots are preserved. Bounded iterator tests pass lower/upper internal key slices and confirm empty, clipped, and extra-fragment behavior.

## Persistence, Dependencies, and Integration

The tests are in-memory but model persistent table metadata: serialized range tombstone internal keys, SST file bounds, snapshot stripes, and compaction output fragments. Dependencies include the DB test utilities, `range_tombstone_fragmenter`, `VectorIterator`, and bytewise internal-key comparator.

## Risks and Test Signals

The strongest signals are exact expected tombstone endpoints and sequence numbers after truncation and compaction fragmentation. The suite protects against forward/backward cache divergence, snapshot-stripe deletion mistakes, and bounded compaction output regressions. It does not cover timestamped range tombstones, non-bytewise comparators, or full DB read/compaction integration.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_del_aggregator_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_tombstone_fragmenter.cc -->
# sources/storage-engines/rocksdb/db/range_tombstone_fragmenter.cc

## Purpose

`range_tombstone_fragmenter.cc` implements conversion from serialized range deletion records into non-overlapping tombstone fragments. It also implements iterators that expose either every fragment sequence or only the top visible tombstone for a sequence/timestamp visibility window.

## Important APIs, Types, and Functions

Implemented APIs include `FragmentedRangeTombstoneList` construction, `FragmentTombstones`, `ContainsRange`, `FragmentedRangeTombstoneIterator` constructors, `SeekToFirst`, `SeekToTopFirst`, `SeekToLast`, `SeekToTopLast`, `Seek`, `SeekForPrev`, `TopNext`, `TopPrev`, `MaxCoveringTombstoneSeqnum`, and `SplitBySnapshot`.

## Control Flow and State Behavior

The list constructor first scans input to count tombstones, measure payload bytes, and detect whether input is sorted by internal start key. If unsorted, or if timestamped tombstone end keys need minimum timestamp padding, it copies keys/values into a `VectorIterator` so fragmentation sees ordered input.

`FragmentTombstones` keeps a working set of currently open tombstones in `cur_end_keys`, ordered by parsed end key. When the start key changes, `flush_current_tombstones` emits one or more non-overlapping `[cur_start_key, cur_end_key)` fragments. For each fragment it gathers covering tombstone sequence numbers, sorts them descending, and optionally sorts timestamps descending. For compaction without user-defined timestamps, only the top sequence visible in each snapshot stripe is preserved; for reads, and for timestamp-enabled compaction, all relevant entries are preserved.

The iterator stores a position into `tombstones_` and a sequence-position into the flattened sequence vector. `SeekToTopFirst`, `SeekToTopLast`, `Seek`, and `SeekForPrev` call `SetMaxVisibleSeqAndTimestamp()` and then scan to the next fragment with a sequence in `[lower_bound_, upper_bound_]` and, when configured, timestamp at or below the timestamp upper bound.

## Persistence, Dependencies, and Integration

The list pins copied slices and the source iterator through `PinnedIteratorsManager`, so fragment slices remain valid. It exposes metadata counts used by table property/reporting paths. It integrates with table range-delete meta blocks, memtable range tombstone iterators, read aggregation, compaction aggregation, and `BuildTable` range tombstone output.

## Risks and Test Signals

Risks include sorted-input detection, timestamp padding, lifetime of pinned slices, empty tombstones, repeated starts/ends, and snapshot compaction dropping too much history. `FragmentedRangeTombstoneIterator` intentionally does not implement normal `InternalIterator` seek semantics, so callers must use it only in expected range-tombstone contexts. `range_tombstone_fragmenter_test.cc` covers overlap fragmentation, unordered input, visible top tombstones, snapshot splitting, seek behavior, and count accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_tombstone_fragmenter.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_tombstone_fragmenter.h -->
# sources/storage-engines/rocksdb/db/range_tombstone_fragmenter.h

## Purpose

`range_tombstone_fragmenter.h` declares RocksDB's fragmented range tombstone storage and iterator interfaces. These abstractions provide compact non-overlapping stacks of range deletions and visibility-filtered navigation for reads and compactions.

## Important APIs and Types

`FragmentedRangeTombstoneList` owns `RangeTombstoneStack` entries, flattened sequence-number and timestamp vectors, pinned backing storage, source iterator pinning, and counters for unfragmented tombstones and payload bytes. `ContainsRange(lower, upper)` lazily builds a sequence set to test whether any tombstone sequence exists in a stripe.

`FragmentedRangeTombstoneListCache` is a reader cache wrapper with a mutex, unique list pointer, and atomic initialized flag.

`FragmentedRangeTombstoneIterator` derives from `InternalIterator` but documents that `Seek` and `SeekForPrev` are specialized for range tombstone coverage rather than generic internal-key iteration. It supports raw stack iteration (`SeekToFirst`, `Next`, `Prev`) and top-visible iteration (`SeekToTopFirst`, `TopNext`, `TopPrev`). It exposes `Tombstone`, `start_key`, `end_key`, `seq`, `timestamp`, `parsed_start_key`, `parsed_end_key`, `MaxCoveringTombstoneSeqnum`, `SplitBySnapshot`, and sequence bounds.

## Control Flow and State Behavior

The header's data model separates interval positions from sequence/timestamp positions. A `RangeTombstoneStack` represents one non-overlapping key range and indexes into the flattened seq/timestamp arrays. Visibility is calculated by `SetMaxVisibleSeqAndTimestamp()`, which finds the first sequence not above `upper_bound_`, then advances further if a timestamp upper bound requires an older timestamp. Lower-bound filtering is applied by forward/backward visible scans.

The header explicitly warns that `icmp_` may not outlive the iterator after construction. Long-lived navigation must use the stored user comparator `ucmp_`; only construction-time work such as `SplitBySnapshot` may dereference `icmp_`.

## Persistence, Dependencies, and Integration

This interface is used by table readers, memtables, range deletion aggregators, repair table scanning, and compaction output construction. Dependencies include `dbformat`, `PinnedIteratorsManager`, `InternalIterator`, `Status`, sequence-number types, and comparator timestamp APIs.

## Risks and Test Signals

The main risks are lifetime and comparator misuse, timestamp ordering consistency with sequence ordering, and callers assuming generic `InternalIterator` seek semantics. Tests in `range_tombstone_fragmenter_test.cc` validate stack ordering, visibility under sequence bounds, split-by-snapshot bounds, seek edge cases, and unordered input accounting.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_tombstone_fragmenter.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_tombstone_fragmenter_test.cc -->
# sources/storage-engines/rocksdb/db/range_tombstone_fragmenter_test.cc

## Purpose

`range_tombstone_fragmenter_test.cc` is the unit test suite for range tombstone fragmentation and iterator navigation. It specifies how overlapping, contiguous, repeated, unordered, and snapshot-filtered range tombstones are transformed into non-overlapping fragments.

## Important APIs, Types, and Helpers

The fixture is `RangeTombstoneFragmenterTest`. Helpers include `MakeRangeDelIter`, `CheckIterPosition`, `VerifyFragmentedRangeDels`, `VerifyVisibleTombstones`, `VerifySeek`, `VerifySeekForPrev`, and `VerifyMaxCoveringTombstoneSeqnum`. Test structs encode seek and max-covering-sequence expectations.

## Control Flow and State Behavior

Basic tests cover non-overlapping tombstones, overlapping tombstones, contiguous ranges, repeated start/end keys, repeated start keys with different end keys, and mixed repeated starts. Expected output lists show each non-overlapping fragment and each sequence in descending order within that fragment.

The overlap tests create multiple iterators over the same fragmented list with different upper bounds and verify both raw fragment iteration and top-visible iteration. They also verify `MaxCoveringTombstoneSeqnum` at starts, covered interior keys, exact end keys, gaps, and out-of-range positions.

Compaction-specific tests construct `FragmentedRangeTombstoneList` with `for_compaction=true`. Without snapshots, only the newest covering tombstone per fragment is retained. With snapshots, additional sequence numbers needed by snapshot stripes are preserved. `IteratorSplitNoSnapshots` and `IteratorSplitWithSnapshots` validate the map of split iterators and their lower/upper bounds.

Seek tests cover targets equal to start keys, inside covered ranges, equal to end keys, and outside all tombstones for both `Seek` and `SeekForPrev`. The unordered-input test confirms sorting is applied and the unfragmented tombstone counter remains correct.

## Persistence, Dependencies, and Integration

The suite is in-memory, using serialized `RangeTombstone` records through `VectorIterator`, but it reflects the format stored in range-delete meta blocks and consumed by table/memtable readers.

## Risks and Test Signals

The strongest signals are exact fragment streams and top-visible streams across overlapping data. Edge cases around exact end-key exclusivity, repeated starts, snapshot stripe bounds, and unordered input are explicitly covered. Timestamped range tombstone behavior is not covered here.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/range_tombstone_fragmenter_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/read_callback.h -->
# sources/storage-engines/rocksdb/db/read_callback.h

## Purpose

`read_callback.h` declares the `ReadCallback` abstraction used by RocksDB read paths that need custom sequence-number visibility checks, especially transaction-aware reads where some committed/uncommitted boundaries are more nuanced than a plain snapshot sequence.

## Important APIs and Types

`ReadCallback` stores `max_visible_seq_` and `min_uncommitted_`. Constructors accept either just the last visible sequence or both the last visible sequence and the minimum uncommitted sequence. Subclasses must implement `IsVisibleFullCheck(SequenceNumber seq)`. Inline `IsVisible(seq)` applies the fast path, and `Refresh(seq)` updates the maximum visible sequence.

## Control Flow and State Behavior

`IsVisible` first asserts a valid `min_uncommitted_`. Any sequence below `min_uncommitted_`, including sequence zero, is treated as committed and visible, with an assertion that it does not exceed the max visible sequence. A sequence above `max_visible_seq_` is invisible. Only the uncertain middle range calls the virtual `IsVisibleFullCheck`, allowing transaction implementations to decide visibility for prepared or uncommitted writes.

`Refresh` defaults to assigning a newer maximum visible sequence, letting callers advance a read view without replacing the callback object.

## Persistence, Dependencies, and Integration

This header has no persistence behavior. It depends on `dbformat` constants such as `kMinUnCommittedSeq` and sequence-number types. Integration points are DB/memtable/table read loops that test whether an internal key sequence should be visible under snapshots, transactions, or write-prepared/write-unprepared modes.

## Risks and Test Signals

The main risk is misuse of `min_uncommitted_` or `max_visible_seq_`, since the fast path bypasses the virtual check for all committed-below-min sequences. Implementations must ensure `IsVisibleFullCheck` is correct for the uncertain range. This file has no direct tests in the subset; coverage is likely through transaction and DB iterator suites that include prepared/uncommitted visibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/read_callback.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/repair.cc -->
# sources/storage-engines/rocksdb/db/repair.cc

## Purpose

`repair.cc` implements best-effort RocksDB database repair. It rebuilds a usable manifest from surviving WAL and SST files without promising time-consistent recovery. The file-level comments define four phases: find files, convert logs to tables, extract table metadata, and write a new descriptor.

## Important APIs, Types, and Functions

The file-local `Repairer` owns the workflow. Important methods are `Run`, `FindFiles`, `ConvertLogFilesToTables`, `ConvertLogToTable`, `ExtractMetaData`, `ScanTable`, `AddTables`, `ArchiveFile`, `AddColumnFamily`, and `Close`. Public overloads of `RepairDB` accept `Options`, `DBOptions` plus column-family descriptors, and optional unknown-column-family options.

`TableInfo` combines `FileMetaData` with column-family id/name. Repair uses `VersionSet`, `TableCache`, `MemTable`, `ColumnFamilyMemTablesImpl`, `log::Reader`, `WriteBatchInternal`, `BuildTable`, `VersionBuilder`, and `VersionEdit`.

## Control Flow and State Behavior

`Run` locks the DB, finds files across configured DB paths and separate WAL dir, archives old manifests, creates a fresh DB descriptor via temporary `DBImpl::NewDB`, recovers the new `VersionSet`, scans existing SST metadata, converts live WAL files to tables, scans those generated tables, and finally writes table additions to the manifest.

`ConvertLogToTable` reads WAL records with checksum validation. Corrupt records are logged and skipped. Valid write batches are checked for timestamp-size consistency, inserted into per-CF memtables, and each non-empty memtable is flushed with `BuildTable` using recovery table-builder options and any memtable range tombstones.

`ScanTable` opens table properties, reconstructs unique IDs when possible, discovers/creates column families, validates column-family names, scans point keys to update file boundaries and sequence bounds, then scans range tombstones to update range boundaries. `AddTables` groups recovered tables by CF, computes the max sequence, recovers epoch numbers through a dummy `VersionStorageInfo`, and writes a `VersionEdit` adding all files, currently at level 0 after dummy recovery ordering.

## Persistence, Dependencies, and Integration

Repair mutates persistent state: it archives manifests, WALs, and unreadable SSTs into `lost/`, creates new SSTs from WAL contents, writes a new MANIFEST, updates next file number and last sequence, and unlocks the DB at close. It integrates with filesystem naming, WAL format, table cache/properties, CF options, comparators, user-defined timestamp persistence, range tombstone metadata, unique SST IDs, and epoch-number ordering.

## Risks and Test Signals

Repair is intentionally lossy. It can skip corrupt WAL records or unreadable SSTs, and it does not guarantee a point-in-time consistent DB. High-risk areas are CF option selection for unknown CFs, timestamp-size validation, range tombstone boundary reconstruction, next-file-number selection, separate WAL dirs, and preserving newest values when all recovered files land in L0. `repair_test.cc` exercises these scenarios directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/repair.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/repair_test.cc -->
# sources/storage-engines/rocksdb/db/repair_test.cc

## Purpose

`repair_test.cc` is the DB-level regression suite for `RepairDB`. It verifies repair after missing/corrupt manifests, missing/corrupt SSTs, unflushed WAL-only data, timestamped keys, separate WAL directories, multiple column families, column-family-specific options, and DB paths with trailing slashes.

## Important APIs, Types, and Helpers

`RepairTest` derives from `DBTestBase` and adds `GetFirstSstPath` plus `ReopenWithSstIdVerify`, which uses `SyncPoint` to assert unique SST IDs in the repaired manifest can be verified. `RepairTestWithTimestamp` derives from timestamp test utilities and parameterizes paranoid file checks and user-defined timestamp persistence mode. Tests call `RepairDB` overloads, DB open/reopen helpers, `Put`, `Flush`, `DeleteRange`, `GetLiveFiles`, `GetSortedWalFiles`, `GetAllDataFiles`, `GetPropertiesOfAllTables`, and CF open/create/drop helpers.

## Control Flow and State Behavior

Manifest tests delete, corrupt, or replace the manifest and expect repair to rebuild a DB containing surviving SST data. `LostManifestMoreDbFeatures` includes an SST containing only a range tombstone and verifies deleted keys remain hidden after repair. `SortRepairedDBL0ByEpochNumber` checks recovered L0 files are ordered so the newest value wins.

SST damage tests delete or overwrite one SST while preserving metadata, then assert repair keeps exactly one of two key/value pairs. `UnflushedSst` deletes the manifest while data exists only in the WAL and expects repair to convert the WAL into an SST and remove WAL files. The timestamp parameterized test verifies WAL-to-SST repair with timestamped keys, persisted or stripped timestamps, paranoid checks, and correct repaired file boundaries.

`SeparateWalDir` repeats WAL repair across WAL option variants. `RepairMultipleColumnFamilies` verifies SSTs and WAL entries remain associated with original CFs. `RepairColumnFamilyOptions` verifies known and unknown CF option paths preserve comparators, including reverse bytewise comparator table properties. `DbNameContainsTrailingSlash` checks path normalization support.

## Persistence, Dependencies, and Integration

The suite manipulates real DB files under the test environment: deleting manifests, corrupting SSTs, copying descriptor files, and inspecting table/WAL files. It integrates repair with unique SST ID verification, timestamp comparators, WAL option matrix, table properties, column-family descriptors, and file utilities.

## Risks and Test Signals

Strong signals include successful reopen after repair with `verify_sst_unique_id_in_manifest`, expected key visibility, zero WALs after WAL conversion, nonzero SST size after repair, correct timestamp/file-boundary behavior, and comparator names in repaired CF tables. Residual risk remains around complex corruption patterns, blob files, custom merge operators, and time-consistent recovery, which repair explicitly does not guarantee.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/repair_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/seqno_time_test.cc -->
# sources/storage-engines/rocksdb/db/seqno_time_test.cc

## Purpose

`seqno_time_test.cc` is the regression suite for RocksDB sequence-number-to-time tracking, table-property encoding of that mapping, last-level hot/cold data placement, pre-populated mappings, and packed value helpers. It uses a mock clock to make time-sensitive behavior deterministic.

## Important APIs, Types, and Helpers

`SeqnoTimeTest` derives from `DBTestBase`, installs `MockSystemClock` through `CompositeEnvWrapper`, and overrides the periodic task scheduler timer with `SyncPoint`. `AssertKeyTemperature` checks IO stats and file temperature. `SeqnoTimeTablePropTest` parameterizes three option modes: `preserve_internal_time_seconds`, `preclude_last_level_data_seconds`, and both set with tracking duration determined by the smaller preserve value.

The tests exercise `SeqnoToTimeMapping` methods including `Append`, `SetCapacity`, `SetMaxTimeSpan`, `GetProximalSeqnoBeforeTime`, `GetProximalTimeBeforeSeqno`, `PrePopulate`, `CopyFromSeqnoRange`, `Enforce`, `AddUnenforced`, `EncodeTo`, and `DecodeFrom`. They also cover `PackValueAndWriteTime`, `ParsePackedValueWithWriteTime`, `PackValueAndSeqno`, and `ParsePackedValueWithSeqno`.

## Control Flow and State Behavior

`TemperatureBasicUniversal` and `TemperatureBasicLevel` write keys over simulated time, compact them, and verify hot data remains in proximal levels while old data moves to cold last-level files. They assert both file-temperature sizes and actual read IO temperature stats.

`BasicSeqnoToTimeMapping` writes at varying intervals, flushes SSTs, decodes each table's `seqno_to_time_mapping`, and validates sample counts and proximal sequence estimates. `MultiCFs` checks scheduler activation only when at least one CF needs tracking, in-memory mapping capacity behavior across CF options, compaction output mappings, and cleanup after dropping CFs. `MultiInstancesBasic` verifies multiple DB instances can run the periodic worker.

`SeqnoToTimeMappingUniversal` verifies universal compaction preserves mappings, avoids sequence zeroing while data is still hot, then zeroes expired sequences and eventually pushes all data to the last level. `PrePopulateInDB` documents when mappings are pre-populated for new DBs, not read-only opens, and how preallocated sequence numbers remain monotonic across reopen.

The remaining tests validate the pure mapping data structure: append merge rules, capacity/time-span enforcement, proximal query semantics, prepopulation interpolation, copying a sequence range, sorting/cleanup of unenforced mappings, compact encode/decode reduction, and minimizing time gaps during reduction.

## Persistence, Dependencies, and Integration

Persistent state under test includes table properties containing encoded seqno-time mappings, sequence numbers in SST keys, file temperatures, compaction placement, and DB latest sequence after prepopulation. The suite integrates options, periodic task scheduling, mock time, compaction, table properties, IO stats by temperature, multiple CFs, read-only open, and universal/level compaction.

## Risks and Test Signals

Risk areas include approximate mapping accuracy, capacity reductions biasing too new or too old, periodic worker lifecycle, CF option aggregation, preallocated sequence numbers, and interactions between last-level temperature and compaction sequence zeroing. Strong signals are decoded table mappings with expected sizes, proximal sequence bounds, temperature-specific SST sizes and read stats, scheduler task presence/absence, monotonic latest sequence after prepopulation, and correct packed-value round trips.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/seqno_time_test.cc -->
