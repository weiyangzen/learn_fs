# subset-b-008609 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_with_timestamp_basic_test.cc -->
# sources/storage-engines/rocksdb/db/db_with_timestamp_basic_test.cc

## Purpose
`db_with_timestamp_basic_test.cc` is RocksDB's broad behavioral test suite for user-defined timestamps (UDT) on ordinary DB operations. It verifies that timestamp-enabled column families enforce API contracts, that reads combine timestamp visibility with sequence-number and snapshot visibility, and that iterators, `Get`, `MultiGet`, range tombstones, merges, row cache, prefix filters, table timestamp metadata, history trimming, and `full_history_ts_low` all preserve correct time-travel semantics.

The file is intentionally integration-heavy. Most tests open real DB instances, write timestamped records, flush SSTs, compact across levels, reopen databases, and validate both returned values and returned key timestamps. It also exercises both persisted UDT mode and memtable-only UDT mode, where SST file boundaries and manifest metadata must compensate for stripped timestamps.

## Important APIs, Types, And Functions
`DBBasicTestWithTimestamp` is the main fixture and derives from `DBBasicTestWithTimestampBase`. It uses the helper `TestComparator`, which orders user keys by bytewise key and then orders timestamps in reverse timestamp order so newer timestamped versions sort before older versions for the same user key. `EncodeAsUint64()` is a local helper for the 8-byte timestamp mode used by RocksDB's built-in U64 timestamp wrapper.

Parameterized fixtures expand coverage across table and storage options:

- `DBBasicTestWithTimestampTableOptions` runs Get, MultiGet, seek, bound, and prefix tests across block-based index types.
- `DBBasicTestWithTimestampFilterPrefixSettings` combines Bloom filter policies, prefix extractors, memtable Bloom settings, whole-key filtering, cache-index/filter settings, and index types.
- `DBBasicTestWithTimestampCompressionSettings` combines compression algorithms, compression dictionaries, parallel compression threads, and filters.
- `DBBasicTestWithTimestampPrefixSeek` verifies prefix iteration over high unsigned-key ranges.
- `DBBasicTestWithTsIterTombstones` validates iterator behavior when timestamped deletions hide alternating keys.
- `DeleteRangeWithTimestampTableOptions` tests range tombstones under persisted and stripped UDT modes.
- `HandleFileBoundariesTest`, `EnableDisableUDTTest`, `DataVisibilityTest`, `UpdateFullHistoryTsLowTest`, and `GetNewestUserDefinedTimestampTest` focus on specific cross-cutting contracts.

The key RocksDB APIs under test include timestamped `Put`, `Merge`, `Delete`, `SingleDelete`, `DeleteRange`, `WriteBatch::UpdateTimestamps`, `Get` overloads returning key timestamps, all major `MultiGet` overloads, `NewIterator`, `NewIterators`, snapshots, `CompactRange`, `CompactFiles`, `IncreaseFullHistoryTsLow`, `GetFullHistoryTsLow`, `GetNewestUserDefinedTimestamp`, `DB::OpenAndTrimHistory`, `GetApproximateSizes`, `GetApproximateMemTableStats`, `GetPropertiesOfAllTables`, row cache, prefix Bloom filters, block-based table index types, and merge operators.

## Control Flow
The opening API tests establish legal and illegal combinations. Timestamped writes on a non-UDT column family must fail, non-timestamped writes on a UDT column family must fail, wrong-sized timestamps must fail, and `WriteBatch::UpdateTimestamps()` must allow mixed column-family batches when the timestamp-size callback returns the correct size per CF. Mixed-CF tests then close and reopen the DB to verify timestamped data survives manifest/recovery paths.

Lookup and iteration tests build multiple timestamped versions of each key and read at later timestamps. They verify forward and reverse scans, direction changes, `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, explicit key lower/upper bounds, `iter_start_ts`, `max_sequential_skip_in_iterations`, and reseek ticker accounting. The iterator tests intentionally cover cases where internal timestamp skipping must reseek to a target timestamp, a next user key, or a user key before a saved key.

`DataVisibilityTest` adds sequence-number visibility to timestamp visibility. It uses sync points and writer threads to interleave reads with later writes and flushes. The expected rule is that a record is visible only when both its user timestamp is at or below the read timestamp and its sequence number is visible to the read's implicit or explicit snapshot. The tests repeat this for point lookup, range scan, MultiGet, snapshots, no snapshots, and cross-column-family MultiGet.

History-management tests cover `full_history_ts_low`, `OpenAndTrimHistory`, compaction with `CompactRangeOptions::full_history_ts_low`, and public `IncreaseFullHistoryTsLow`. They verify increasing the low watermark, rejecting decreasing/empty/wrong-sized low timestamps, rejecting partial-range compactions with `full_history_ts_low`, preserving the latest version below the low watermark, collapsing timestamps to minimum timestamps when history is compacted, and returning `InvalidArgument` when a read timestamp falls below the SuperVersion's low watermark.

Table and filter tests flush and compact data under multiple block-based table index types, Bloom configurations, compression modes, prefix extractors, and row-cache setups. They verify `Get`, `MultiGet`, and iterators never treat timestamp suffix bytes as part of user-key prefixes or row-cache keys incorrectly. `TimestampFilterTableReadOnGet` specifically checks timestamp min/max file metadata can skip table reads and increments `TIMESTAMP_FILTER_TABLE_CHECKED` and `TIMESTAMP_FILTER_TABLE_FILTERED` tickers.

Delete, range tombstone, and merge tests validate timestamp semantics for `Delete`, `SingleDelete`, `DeleteRange`, and merge operands. They cover preserving range tombstones when no or too-small `full_history_ts_low` is set, dropping covered keys and tombstones only when the low watermark allows it, correct key timestamps in `Get` and `MultiGet` NotFound results, snapshot interactions with range tombstones, and merge results/timestamps across put-then-merge and delete-then-merge histories.

UDT mode transition tests write data without timestamps, reopen the same DB with timestamp support enabled, read old data as if it had minimum timestamps, write timestamped data with UDT stripped from SSTs, reopen with UDT disabled, and continue ordinary reads/writes. File-boundary tests inspect `FileMetaData` after reopen to ensure manifest encoding pads stripped boundaries with min or max timestamps as appropriate, including range-deletion sentinel boundaries.

## State And Persistence Behavior
This file treats timestamp support as both a logical read feature and a persisted storage-format feature. Flushes create SSTs whose internal keys, table properties, file boundaries, and timestamp min/max metadata must match the configured UDT mode. Compactions may drop expired history, zero sequence numbers, collapse timestamps to the minimum timestamp, or preserve tombstones depending on `full_history_ts_low` and bottommost-level state.

Snapshot and sequence state is part of the tested persistence model. A timestamp alone is not enough to make a newer write visible if the reader captured an older sequence number. Snapshot tests use sync points to make this race deterministic and confirm `Get`, iterators, and all `MultiGet` paths use a consistent sequence snapshot.

The suite also validates manifest and reopen behavior. `OpenAndTrimHistory` rewrites history during open and must preserve the correct value or tombstone visible at the trim timestamp. File-boundary tests close and reopen to ensure the manifest records either real timestamped boundaries or timestamp-stripped boundaries that are reconstructed with min/max timestamps. `GetNewestUserDefinedTimestamp` verifies newest UDT tracking through mutable memtables, immutable memtables, flush, manifest persistence, and reopen when timestamps are not persisted in SST user keys.

Row cache state is timestamp-sensitive. The tests deliberately mix `Get` calls with and without returned key timestamps and with different snapshots/read timestamps, expecting cache hits only when the cached entry is valid for the same logical visibility constraints and expecting the cached entry to carry the correct returned timestamp.

## Dependencies And Integration Points
The test depends on `db/db_with_timestamp_test_util.h` for timestamp encoding, timestamp-aware comparator behavior, and iterator assertions. It integrates with `db/db_test_util.h` through the base fixture for DB lifecycle, flushing, compaction helpers, snapshots, CF helpers, and file movement. It uses `test_util/sync_point.h` for deterministic concurrency, `rocksdb/perf_context.h`, `rocksdb/utilities/debug.h`, block-based table internals, `utilities/fault_injection_env.h`, and the string append test merge operator.

Integration points include RocksDB public DB APIs, `ColumnFamilyHandleImpl`/`ColumnFamilyData` internals for `full_history_ts_low` and memtable switching, `VersionEdit` sync points for concurrent low-watermark updates, table-property collectors for timestamp min/max, block-based table readers/builders, Bloom filters, prefix extractors, compression libraries, row cache statistics, iterator reseek statistics, and range tombstone sentinels.

## Risks
The highest-risk area is the interaction between user timestamp ordering and RocksDB's internal sequence ordering. Many tests rely on the comparator ordering timestamped versions in reverse timestamp order and on reads additionally filtering by sequence visibility. Bugs here can return future data to a snapshot, skip visible older versions, or report the wrong key timestamp with a value or tombstone.

`full_history_ts_low` is another correctness-sensitive boundary. If the low watermark is applied too aggressively, reads below a still-valid SuperVersion can become inconsistent or history can be dropped too early. If applied too conservatively, compaction can retain obsolete history or repeatedly compact bottommost files. The tests cover both invalid read rejection and read consistency when the SuperVersion still contains the needed history.

Persisted-vs-stripped UDT mode is subtle. When timestamps are stripped from SST user keys, manifest file boundaries and table timestamp metadata must still allow correct reads, compactions, and tombstone handling. Boundary padding with min/max timestamps and range tombstone sentinel encoding are easy places for off-by-one or comparator errors.

Prefix filtering, row cache, and MultiGet fast paths can accidentally use raw user keys including timestamp bytes, or omit timestamp/snapshot state from cache/filter decisions. The suite stresses these paths with multiple API overloads, long keys, prefix extractors, Bloom filters, and index types.

## Test Signals
Primary pass signals are exact `OK`, `NotFound`, `InvalidArgument`, `TryAgain`, and `NotSupported` statuses; exact values and returned key timestamps for `Get`, `MultiGet`, and iterators; preserved or collapsed timestamps after compaction; expected iterator validity at bounds; expected reseek and row-cache ticker deltas; expected table timestamp properties; expected file metadata boundaries after reopen; and correct behavior across persisted and stripped UDT modes.

High-value regression signals include a future write becoming visible to an older snapshot, a timestamped tombstone returning an empty or wrong tombstone timestamp, failure to reject reads below `full_history_ts_low`, compaction dropping range tombstones too early, `MultiGet` overloads disagreeing, row-cache hits returning values for the wrong timestamp/snapshot, prefix filters missing timestamped keys, and `GetNewestUserDefinedTimestamp` losing state across memtable switch, flush, or reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_with_timestamp_basic_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_with_timestamp_compaction_test.cc -->
# sources/storage-engines/rocksdb/db/db_with_timestamp_compaction_test.cc

## Purpose
`db_with_timestamp_compaction_test.cc` is a targeted RocksDB integration test suite for compaction behavior when a column family uses user-defined timestamps. It verifies that compaction picks complete timestamp-compatible input ranges, preserves timestamp visibility across file boundaries and subcompactions, handles `CompactFiles()` range expansion, applies `full_history_ts_low` correctly to sequence-number zeroing and bottommost compaction scheduling, and persists file timestamp ranges through flush, compaction, external SST ingestion, manifest reopen, and table properties.

Compared with the broader basic timestamp suite, this file focuses on compaction metadata and file-level correctness. It inspects `FileMetaData::min_timestamp` and `max_timestamp`, compaction input lists, output file counts, and sync-point events in addition to read results.

## Important APIs, Types, And Functions
The local helpers `Key1(uint64_t)` and `Timestamp(uint64_t)` encode ordered test keys and 8-byte timestamps. `TimestampCompatibleCompactionTest` derives from `DBTestBase` and provides:

- `Get(key, ts)`, a timestamped read wrapper returning `"NOT_FOUND"` or status text for assertions.
- `GetAllFileTimestamps()`, which reaches through `ColumnFamilyHandleImpl` and current `VersionStorageInfo` to collect every live file's level, min timestamp, and max timestamp.
- `GetOverallTimestampRange()`, which decodes file timestamp ranges and computes the DB-wide min/max.
- `VerifyTimestampRangeWithPersistence()`, which checks min/max before and after `Reopen()`.
- `CreateTimestampOptions()`, which enables level compaction, `persist_user_defined_timestamps`, and `BytewiseComparatorWithU64TsWrapper`.
- `WriteDataWithTimestampRange()`, `HasFileWithTimestampRange()`, and `VerifyDataReadable()` helpers.

`TestFilePartitioner` and `TestFilePartitionerFactory` force compaction output partitioning and disallow trivial moves so tests can observe range expansion and output file construction. The file also uses `CompactionJobInfo`, `CompactFiles`, `CompactRange`, `RunManualCompaction`, `SstFileWriter`, `SstFileReader`, external file ingestion, table properties, `IncreaseFullHistoryTsLow`, snapshots, and sync points such as `CompactionIterator::PrepareOutput:ZeroingSeq`.

## Control Flow
`UserKeyCrossFileBoundary` creates three L0 files with overlapping user key `99` at increasing timestamps. A sync point verifies level compaction picks all three L0 files as one timestamp-compatible input group. After compaction, reads at saved timestamps must return the historical values `foo_99`, `bar_99`, and `foo1_99`, proving compaction did not split versions of the same user key across incompatible file boundaries.

`MultipleSubCompactions` writes 1000 timestamped keys under universal compaction with `max_subcompactions=3`, small target files, and statistics. It runs a manual compaction and asserts the `NUM_SUBCOMPACTIONS_SCHEDULED` histogram sum is greater than one, then reads every key at a high timestamp to validate subcompaction boundary handling with timestamped keys.

`CompactFilesRangeCheckL0` and `CompactFilesRangeCheckL1` exercise `DB::CompactFiles()` input expansion. The L0 test supplies one middle L0 file for a repeated user key and expects older overlapping L0 files to be included. The L1 test first compacts repeated timestamp versions to L1 using a forced partitioner, then adds L0 files and supplies a mixed input set; it expects all relevant L1 and L0 files to be included and each partitioned output to be accounted for.

`EmptyCompactionOutput` writes only a timestamped range tombstone, compacts with `full_history_ts_low` beyond the tombstone timestamp and forced bottommost compaction, and expects success even when the compaction drops everything and produces no output.

`SeqnoZeroingWithUDT` installs a sync-point callback when compaction zeroes sequence numbers. It proves no zeroing happens when UDT is enabled but `full_history_ts_low` is unset, that keys below the low watermark are zeroed, and that a key with timestamp at or above the low watermark is not zeroed. It then confirms all values remain readable at a later timestamp.

The bottommost compaction tests ensure files are not repeatedly marked for bottommost compaction when their max timestamp is still at or above `full_history_ts_low`, or when `full_history_ts_low` has never been set. Once the low watermark moves beyond the file's max timestamp, snapshot release and compaction can proceed normally.

The final metadata tests validate timestamp-range persistence. One creates an external SST with UDT table properties, ingests it, checks `FileMetaData` min/max timestamps, reopens, and reads data. The flush test checks table properties and file metadata after one flush. The compaction test writes three L0 files with disjoint timestamp ranges, compacts them, and verifies the merged file range is the min of all inputs and max of all inputs before and after reopen.

## State And Persistence Behavior
This suite centers on persistent file metadata. Timestamp ranges collected during table building must become table properties, then `FileMetaData::min_timestamp` and `max_timestamp`, then manifest records that survive reopen. Compaction must merge input timestamp ranges into output metadata, and external SST ingestion must extract timestamp table properties into file metadata even though the file was built outside the DB.

Compaction state is also validated through input selection. When multiple files contain different timestamp versions of the same user key, compaction must include the complete overlapping set needed for correct visibility. `CompactFiles()` cannot blindly compact only the user-supplied file when timestamp-compatible older/newer inputs are necessary.

`full_history_ts_low` controls whether history is old enough for sequence-number zeroing or bottommost cleanup. The tests require the low watermark to be set and greater than a file/key timestamp before zeroing or marking is allowed. Otherwise data remains readable and files should not enter an infinite bottommost compaction loop.

## Dependencies And Integration Points
The file depends on `db/db_test_util.h`, `db/column_family.h`, `db/compaction/compaction.h`, `rocksdb/sst_file_reader.h`, `test_util/testutil.h`, and `port/stack_trace.h`. It integrates with public DB APIs, internal column-family and version-storage types, compaction picker behavior, compaction iterators, subcompaction statistics, file partitioners, external SST writer/reader/ingestion, table-property collectors, manifest reopen, and snapshot-triggered bottommost file marking.

The comparator used in most tests is `test::BytewiseComparatorWithU64TsWrapper()`, making these tests a direct exercise of RocksDB's built-in U64 timestamp mode rather than the custom 16-byte comparator used in parts of the basic suite.

## Risks
Compaction range selection is the main correctness risk. If files are split or omitted around the same user key with different timestamps, old reads can return the wrong version after compaction even when latest reads look correct. The tests for repeated key `99` and `CompactFiles()` input expansion are targeted at that hazard.

Metadata extraction is another risk. Missing min/max timestamps in `FileMetaData` can disable timestamp table filtering, break bottommost marking decisions, or lose newest/oldest timestamp information after reopen. External SST ingestion is especially sensitive because the file metadata is created outside normal flush/compaction paths.

`full_history_ts_low` must avoid two opposite failures: zeroing sequence numbers too early, which can expose data incorrectly across snapshots, and failing to zero/mark old files when safe, which can retain history or trigger repeated compactions. Tests use sync points and timeouts to detect both types.

## Test Signals
Success signals include correct historical values after cross-file compaction, more than one scheduled subcompaction, expanded `CompactionJobInfo::input_files` counts, expected partitioned output counts, successful empty compaction output, exact sync-point zeroed-key sets, no timeout in bottommost compaction waiting, table properties containing `rocksdb.timestamp_min` and `rocksdb.timestamp_max`, file metadata min/max ranges matching expected decoded values, and the same metadata after reopen.

Failures typically indicate incomplete compaction input expansion, invalid timestamp-aware subcompaction boundaries, incorrect sequence-number zeroing with UDT, bottommost compaction loops, missing timestamp table properties, or manifest persistence gaps for timestamp ranges.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_with_timestamp_compaction_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_with_timestamp_test_util.cc -->
# sources/storage-engines/rocksdb/db/db_with_timestamp_test_util.cc

## Purpose
`db_with_timestamp_test_util.cc` implements shared helpers for RocksDB timestamp tests. It provides deterministic key encodings, timestamp encodings, string-to-slice conversion, and assertion helpers that understand timestamped user keys and internal keys. The implementation keeps large timestamp test files focused on behavior rather than repeated encoding and iterator-parsing boilerplate.

## Important APIs, Types, And Functions
`DBBasicTestWithTimestampBase::Key1(uint64_t)` encodes a 64-bit integer with `PutFixed64()` and reverses the bytes. This produces fixed-length keys whose bytewise order matches the intended numeric ordering used throughout timestamp iterator and compaction tests.

`KeyWithPrefix(std::string prefix, uint64_t)` does the same integer encoding and prefixes it with caller-provided text. Prefix/filter tests use it to verify prefix extractors operate on user-key prefixes and do not accidentally include timestamp suffix bytes.

`ConvertStrToSlice(std::vector<std::string>&)` creates a parallel vector of `Slice` objects referring to the existing strings. It is used by `MultiGet` tests that must pass stable key slices without copying into separate buffers.

`Timestamp(uint64_t low, uint64_t high)` returns the 16-byte timestamp format used by the custom `TestComparator`: first the low component, then the high component, each fixed64 encoded.

`CheckIterUserEntry()` asserts an externally visible iterator entry: iterator validity, OK status, exact user key, expected value when the value type is `kTypeValue`, and exact `Iterator::timestamp()`.

The two `CheckIterEntry()` overloads assert internal-key-style iterator entries. They append the expected timestamp to the expected user key, parse `it->key()` with `ParseInternalKey()`, check value type and optionally sequence number, compare value for `kTypeValue`, and compare the iterator timestamp.

## Control Flow
The helper functions are mostly straight-line utilities. Key helpers build strings using RocksDB fixed-width coding helpers and byte reversal. Timestamp helpers build fixed-size timestamp strings. Assertion helpers first validate iterator status and validity, then either compare public iterator key/value/timestamp fields or parse internal keys before checking their timestamp-appended user key, sequence number, type, and value.

The internal-key assertion path constructs `ukey_and_ts` explicitly because timestamped internal keys store the timestamp as part of the user-key bytes. This gives tests a precise way to distinguish an iterator's logical user key from its timestamp-bearing internal key representation.

## State And Persistence Behavior
This file does not own persistent state. Its helpers encode the state that timestamp tests later persist into memtables, SST files, table properties, and manifests. The assertion helpers are important for persistence tests because they verify whether compaction or reopen preserved, stripped, collapsed, or returned timestamps exactly as expected.

`ConvertStrToSlice()` has a lifetime dependency: returned slices point into the input vector's strings. Callers must keep that vector alive until the DB API call completes. The test code follows that pattern by building slices immediately before `MultiGet`.

## Dependencies And Integration Points
The implementation includes `db/db_with_timestamp_test_util.h`, which pulls in `DBTestBase`, internal-key parsing declarations, RocksDB coding utilities, GoogleTest assertions, and test utilities. It integrates with `ParsedInternalKey`, `ParseInternalKey`, `ValueType`, `SequenceNumber`, `Slice`, and RocksDB fixed64 encoding.

The helpers are consumed by `db_with_timestamp_basic_test.cc` and other timestamp test files that derive from `DBBasicTestWithTimestampBase`.

## Risks
The key encoding helpers are foundational. If byte reversal were changed or removed, many iterator and prefix tests would no longer scan in the assumed numeric order. If the timestamp layout changed, the custom comparator and all expected timestamp comparisons would diverge.

The internal-key checks depend on the invariant that timestamp bytes are appended to the user key in internal keys. A storage-format change would require these helpers to change with it. `ConvertStrToSlice()` can produce dangling slices if callers pass a temporary vector or mutate strings before use.

## Test Signals
These helpers emit GoogleTest assertion failures with precise mismatches for iterator validity, status, key bytes, parsed internal key bytes, value type, sequence number, value bytes, and returned timestamp. Failures in tests using these helpers typically point to timestamp ordering, timestamp stripping/collapsing, tombstone type, or iterator value-preparation regressions rather than helper-local logic.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_with_timestamp_test_util.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_with_timestamp_test_util.h -->
# sources/storage-engines/rocksdb/db/db_with_timestamp_test_util.h

## Purpose
`db_with_timestamp_test_util.h` declares the shared fixture and comparator utilities used by RocksDB's timestamp DB tests. It centralizes a timestamp-aware base class, deterministic key/timestamp encoders, and iterator assertion helpers, and defines the custom comparator used by tests that require a 16-byte two-part timestamp.

## Important APIs, Types, And Functions
`DBBasicTestWithTimestampBase` derives from `DBTestBase` and passes `env_do_fsync=true` to its base constructor, making timestamp tests run against a DB fixture with durable fsync behavior enabled. The constructor accepts the DB name so specialized fixtures can isolate their database directories.

The protected static helpers are `Key1(uint64_t)`, `KeyWithPrefix(std::string, uint64_t)`, and `ConvertStrToSlice(std::vector<std::string>&)`. The protected instance helper `Timestamp(uint64_t low, uint64_t high)` encodes the custom two-component timestamp format.

`TestComparator` derives from `Comparator` with a configurable `timestamp_size()`. It delegates user-key comparison to `BytewiseComparator()` after stripping timestamps when present. Its `Compare()` first compares keys without timestamps; if user keys are equal and timestamps are enabled, it compares timestamps and negates the timestamp comparison so larger/newer timestamps sort before smaller/older timestamps for the same user key.

`CompareWithoutTimestamp()` validates timestamp-bearing key lengths, strips timestamp suffixes when requested with `StripTimestampFromUserKey()`, and delegates to the bytewise comparator. `CompareTimestamp()` supports null timestamp slices, then decodes each timestamp as `{low, high}` fixed64 values and orders first by `high`, then by `low`.

The declared assertion helpers are `CheckIterUserEntry()` for public iterator entries and two `CheckIterEntry()` overloads for parsed internal keys, with or without an expected sequence number.

## Control Flow
The comparator control flow mirrors RocksDB's timestamped-key contract. For two keys, it compares the user-key portion first. Only when the user-key portions are equal does it inspect timestamp suffixes. Null timestamp slices are ordered below non-null slices, equal fixed-size timestamps compare equal, and non-null timestamp bytes are decoded into high/low components. `Compare()` reverses the timestamp comparison result so newer timestamps appear earlier in internal ordering for a given user key.

The base class exposes helpers as protected members so derived GoogleTest fixtures can write compact tests without leaking these helpers into unrelated test code.

## State And Persistence Behavior
The header itself stores no persistent state, but `TestComparator` defines how timestamped keys are ordered in memtables, SST files, range tombstones, file metadata boundaries, and compaction iterators. That ordering is part of the persisted data contract for tests using this comparator. If an SST is written with this comparator, reopen and compaction must use a comparator with the same timestamp size and comparison semantics.

The two-part timestamp format is test-specific and differs from RocksDB's U64 timestamp wrapper used in some compaction tests. Its high-then-low ordering allows tests to exercise nontrivial timestamp comparison while still producing fixed-size timestamp strings.

## Dependencies And Integration Points
The header includes `db/db_test_util.h`, `port/stack_trace.h`, and `test_util/testutil.h`. It integrates with RocksDB's `Comparator` interface, `BytewiseComparator`, timestamp-size support, `StripTimestampFromUserKey`, fixed64 decoding helpers, `Slice`, `Iterator`, `ValueType`, and `SequenceNumber`.

Downstream tests use this base fixture to configure `Options::comparator`, build timestamped write/read options, create mixed timestamped and non-timestamped column families, and assert iterator internals after compaction or history trimming.

## Risks
Comparator correctness is critical. Reversing the timestamp ordering in `Compare()` is deliberate; removing that negation would invert version ordering for equal user keys and break reads that expect newest eligible versions first. Mis-decoding `{low, high}` or changing comparison priority would silently change test semantics.

`CompareTimestamp()` copies timestamp slices into mutable buffers before `GetFixed64()` because decoding advances the slice pointer. Any mismatch between `timestamp_size()` and the encoded timestamp size asserts in tests and can also lead to invalid comparator behavior in DB operations.

Because the comparator delegates timestamp-stripped user-key comparison to bytewise ordering, tests using it should not assume locale, numeric, or custom collation semantics beyond the helper's encoded-key patterns.

## Test Signals
The header's behavior is validated indirectly by all timestamp tests that use `TestComparator`. Strong signals include correct ordering of multiple versions per key, exact iterator timestamps, correct file-boundary comparisons after reopen, correct handling of range tombstones and prefix extractors, and `InvalidArgument` results when timestamp sizes do not match the comparator's configured timestamp size.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_with_timestamp_test_util.h -->
