# Research Group: subset-b-008726

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_test.cc -->
# Research: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_test.cc

## Purpose

This file is the primary GoogleTest coverage for RocksDB's experimental/user-defined trie index implementation under `utilities/trie_index`. It tests the low-level succinct data structures (`Bitvector`, `EliasFano`), the serialized `LoudsTrie` builder/reader/iterator, the `TrieIndexFactory` implementation of RocksDB's user-defined index API, end-to-end SST integration through block-based tables and `SstFileWriter`/`SstFileReader`, and a benchmark-style comparison against RocksDB's native `IndexBlockIter`.

The tests are especially focused on correctness at separator boundaries: bytewise trie ordering, prefix keys, dense/sparse trie transitions, path-compression chains, serialized data corruption, iterator invalidation/reseek behavior, multi-scan upper-bound checks, and same-user-key block boundaries where sequence numbers and value-type tags must be used to choose the same block that RocksDB's normal internal-key index would choose.

## Important APIs, Types, And Functions

- `SeekCtx(SequenceNumber)` and `EntryCtx(last_seq, first_seq)` are local helpers that convert readable sequence numbers into RocksDB's packed internal-key tag format. They feed `UserDefinedIndexIterator::SeekContext` and `UserDefinedIndexBuilder::IndexEntryContext`.
- `BitvectorTest` covers `BitvectorBuilder::Append`, `AppendMultiple`, `AppendWord`, `Reserve`, `BuildFrom`, and `Bitvector` APIs such as `GetBit`, `Rank1`, `Rank0`, `FindNthOneBit`, `FindNthZeroBit`, `NextSetBit`, `DistanceToNextSetBit`, `EncodeTo`, `InitFromData`, `SerializedSize`, move construction, and move assignment.
- `EliasFanoTest` covers `EliasFano::BuildFrom`, `Access`, `Count`, `Universe`, `EncodeTo`, `InitFromData`, `SerializedSize`, and move operations for monotone integer sequences used by trie/block-handle metadata compression.
- `LoudsTrieTest::BuiltTrie` owns a `LoudsTrieBuilder`, deserialized `LoudsTrie`, and `LoudsTrieIterator`; it has a custom move constructor because the iterator stores a raw pointer to the trie.
- `BuildTrieFromKeys`, `VerifyFullScan`, and `VerifyTrieIteration` are reusable trie fixtures that build sorted key sets with deterministic `TrieBlockHandle` offsets, then assert seek/scan/key reconstruction behavior.
- `TrieIndexFactoryTest::TestBlock` describes one data-block boundary with `last_key`, optional `next_key`, block handle, last sequence, and first sequence in the next block. `BuildTrieAndGetIterator` builds a full `UserDefinedIndexBuilder`/`Reader`/`Iterator` context from these blocks.
- `AssertSeekOffset` and `AssertFullForwardScan` are central assertions for user-defined index seek and next semantics. They validate both `IterateResult` status and the selected block offset.
- `TrieIndexSSTTest` integrates `TrieIndexFactory` with `BlockBasedTableOptions::user_defined_index_factory`, `SstFileWriter`, and `SstFileReader`.
- `TrieSeekBenchmark` creates synthetic trie and native index-block representations to compare seek cost against `IndexBlockIter`; it prints diagnostic timing to stderr but still runs as a test.

## Control Flow

The file starts at the smallest serialized primitives and moves outward. `BitvectorTest` builds bit patterns directly, materializes `Bitvector`s, checks rank/select/navigation invariants, then corrupts or truncates serialized buffers to verify defensive parsing. `EliasFanoTest` follows the same pattern for monotone offsets: empty/single/large/dense/constant distributions, serialization round trips, truncation, bad `low_bits`, and move behavior.

`LoudsTrieTest` then composes those primitives into trie behavior. The fixture adds sorted keys to `LoudsTrieBuilder`, calls `Finish`, initializes `LoudsTrie` from the builder's serialized slice, and uses `LoudsTrieIterator` for seeks and scans. The topology test table covers binary keys, all single-byte values, deep chains, high fanout, prefix-key chains, dense/sparse boundaries, mixed key lengths, long shared prefixes, and larger deterministic sets. Additional tests stress random key sets, exact/inexact seek, empty target seek, seek before/after all keys, repeated descending seeks, full-scan then reseek, empty trie iteration, key reconstruction, leaf-index accounting, sparse binary search, and path-compression chain comparisons.

The deserialization tests deliberately mutate or truncate trie headers and payloads. They check short data, wrong magic, unsupported version, excessive `max_depth`, progressive truncation with and without chains, misaligned input buffers, move construction/assignment, and auxiliary memory accounting. These tests exercise the reader's zero-copy design and pointer reseating logic after moves.

`TrieIndexFactoryTest` exercises the RocksDB user-defined index contract. It builds index entries the way a table builder would: last key, next first key when present, block handle, and sequence-tag context. It then verifies builder creation, reader creation, iterator creation, factory name, empty indexes, double `Finish` rejection, null comparator defaulting, non-bytewise comparator rejection, corrupted reader input, `OnKeyAdded` no-op behavior, approximate memory usage, and scan-bound preparation. Bounds tests verify that the UDI iterator returns `kInbound`, `kOutOfBound`, or `kUnknown` conservatively because separator keys are block upper bounds, not first keys in blocks.

The middle and later `TrieIndexFactoryTest` sections are a detailed same-user-key boundary suite. They build block layouts where multiple adjacent data blocks contain the same user key at different sequence numbers, so the index must use packed tags, overflow runs, and post-seek correction to mimic internal-key ordering. Tests cover large overflow runs, mixed and adjacent runs, zero-sequence bottommost-compaction cases, last-block real tags, non-boundary separators with sentinel tags, full tag comparisons for same sequence but different value types, all-`0xff` separator edge cases, randomized layouts, overflow BFS reordering, reverse iteration, `SeekToFirst`/`SeekToLast`, `Prev` inside overflow runs, and exhaustion followed by forward scanning through later overflow runs.

The SST integration tests write real SST files. They first prove native index reading still works because the UDI is stored alongside the normal index, then read with `ReadOptions::table_index_factory` set to the trie factory. They cover normal scans, point seeks, upper bounds, very small SSTs, mixed Put/Delete/Merge/SingleDelete-like internal key types, large mixed-type SSTs with many data blocks, and the compression-dictionary buffered replay path where `OnKeyAdded` must preserve first internal-key state for all operation types.

The benchmark test constructs a trie from fixed-width separator keys and a native index block using `BlockBuilder`, `IndexValue`, `Block`, and `IndexBlockIter`. For each key-count scale it generates random internal-key seeks, measures the production-like trie path (`ParseInternalKey`, user-key trie seek, key materialization, block-handle lookup) and the native index-block path (`IndexBlockIter::Seek`, `value`), and prints nanoseconds per operation and relative winner.

## State And Persistence Behavior

The test file itself has no persistent production state, but it validates many serialized states:

- `Bitvector` stores a header, packed words, rank lookup tables, and select hints. Tests verify `SerializedSize`, byte-for-byte consumption, non-aligned logical bit counts, out-of-range select behavior, and corruption on impossible headers or truncated auxiliary tables.
- `EliasFano` stores count/universe/low-bit metadata, low words, and a high bitvector. Tests validate empty and large sequences, access after deserialization, corrupted `low_bits`, truncated low-word/high-bitvector sections, and move safety when initialized from external serialized memory.
- `LoudsTrieBuilder` serializes a trie header, dense and sparse structures, block-handle arrays, path-compression chains, and auxiliary lookup data. Tests validate zero-copy initialization, misaligned buffer handling, maximum depth validation, unsupported versions, progressive truncation rejection, and `ApproximateAuxMemoryUsage`.
- `TrieIndexFactory` serializes user-defined index contents into `Slice index_contents` owned by the builder. The reader and iterator depend on that memory remaining alive, which is why helper contexts own builder, reader, and iterator together.
- SST integration writes temporary SST files under `test::PerThreadDBPath("trie_index_sst_test.sst")`; `TearDown` deletes the file through `Env::Default()->DeleteFile`.

## Dependencies And Integration Points

The tests depend on RocksDB core test infrastructure (`test_util/testharness.h`, `test_util/testutil.h`, `port/port.h`), core key-format helpers (`db/dbformat.h`, `PackSequenceAndType`, `InternalKey`, `ParsedInternalKey`, `AppendInternalKeyFooter`, `ParseInternalKey`), table infrastructure (`BlockBuilder`, `Block`, `IndexBlockIter`, `IndexValue`, `TableBuilder`, `BlockBasedTableOptions`, `NewBlockBasedTableFactory`), SST tools (`SstFileWriter`, `SstFileReader`), and trie-index components (`bitvector.h`, `louds_trie.h`, `trie_index_factory.h`).

Integration with RocksDB's block-based table stack is explicit. The trie factory is installed as `BlockBasedTableOptions::user_defined_index_factory`, then activated for reads through `ReadOptions::table_index_factory`. The tests also validate `UserDefinedIndexIteratorWrapper`, the adapter that exposes trie UDI results as internal keys to the block-based table iterator.

The file uses `MergeOperators::CreateStringAppendOperator()` to make Merge entries readable in SST tests and `GetSupportedDictCompressions()` plus compression dictionary options to trigger table-builder buffered mode.

## Risks And Edge Cases

- Many trie structures use zero-copy slices into serialized builder output. Tests maintain owner lifetimes carefully; future helper changes that return iterators without owning the serialized buffer can create dangling pointers.
- `LoudsTrieIterator` stores raw trie pointers, so moving a fixture requires rebuilding the iterator. The custom `BuiltTrie` move constructor documents and tests this risk.
- Sequence-number selection is subtle because RocksDB internal keys order higher packed tags before lower tags for the same user key. Tests verify that correction is only applied when target and separator user keys are equal; applying seqno logic to smaller user keys would skip valid blocks.
- Non-boundary shortened separators use tag `0` as a sentinel. Tests cover cases where separator shortening fails and confirm real sequence-number seeks do not advance incorrectly.
- Overflow runs have both key-sorted and BFS leaf-order dimensions. The `OverflowBfsReordering` test is a targeted guard against associating overflow block metadata with the wrong trie leaf.
- Bounds checks are intentionally conservative because separator keys are not first-in-block keys. Returning `kOutOfBound` too early can drop blocks that contain in-range data; returning `kUnknown` on SST exhaustion is necessary because another SST may still contain in-bound keys.
- Last block behavior differs from intermediate shortened separators because the last block stores its actual last key/tag. Tests ensure real-seqno seeks on the last separator match native index behavior.
- Compression dictionary buffered mode replays previously buffered data blocks. If UDI `OnKeyAdded` ignores non-Put internal value types, the table builder can assert or build an incomplete index.
- Randomized tests use time-derived seeds and print them through `SCOPED_TRACE`; failures require capturing the seed from test output for reproduction.

## Test Signals

This file is itself the test signal for the trie index feature. Strong signals include:

- Primitive invariants: rank/select correctness, select out-of-range sentinels, builder reserve/no-op append behavior, serialization size equality, and corruption on malformed bitvector/Elias-Fano payloads.
- Trie reader/iterator invariants: exact seek, inexact seek, `Next`, `Prev`, empty trie, prefix keys, chain compression, dense/sparse traversal, sparse binary-search fallback, full scans, move behavior, and progressive truncation rejection.
- UDI API invariants: builder/reader status behavior, comparator validation, null comparator defaults, bounds preparation, multi-scan state advancement, wrapper internal-key materialization, empty-index seek results, and corrupted index data handling.
- Same-user-key invariants: same-key boundary detection, overflow run seek/next/prev, zero sequence numbers, packed value-type tags, BFS-reordered overflow metadata, last-block tag handling, non-boundary sentinel behavior, and randomized block layouts.
- SST integration signals: reading with and without trie UDI, upper-bound iteration, small SSTs, mixed key types, large multi-block SSTs, deleted-key seek advancement, and compression dictionary replay.

Running this file's test binary exercises both unit-level serialized structure validation and end-to-end RocksDB table integration for the trie UDI implementation.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/trie_index/trie_index_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/ttl/db_ttl_impl.cc -->
# Research: sources/storage-engines/rocksdb/utilities/ttl/db_ttl_impl.cc

## Purpose

This file implements RocksDB's `DBWithTTL` wrapper. The wrapper stores an internal 4-byte creation timestamp at the end of every value written through the TTL API, strips that timestamp from user-visible reads and iterators, and installs compaction filters that delete expired values during compaction. It also wraps user merge operators and compaction filters so they see timestamp-free values while TTL metadata remains preserved internally.

The implementation bridges public `DBWithTTL::Open`/column-family APIs, `StackableDB` forwarding, RocksDB option serialization/registry support, and the TTL-specific compaction/merge behavior declared in `db_ttl_impl.h`.

## Important APIs, Types, And Functions

- `TtlMergeOperator` wraps a user `MergeOperator`. `FullMergeV2` and `PartialMergeMulti` remove TTL timestamps from existing values and operands, delegate to the user operator, then append a fresh current timestamp to the merge result.
- `TtlMergeOperator::PrepareOptions` lazily fills `clock_` from `ConfigOptions::env`; `ValidateOptions` requires both a user merge operator and a system clock.
- `DBWithTTLImpl::SanitizeOptions` rewrites column-family options at open/create time. It wraps an existing raw compaction filter in `TtlCompactionFilter`, otherwise wraps/creates a `TtlCompactionFilterFactory`; it also wraps any merge operator in `TtlMergeOperator`.
- `TtlCompactionFilter` extends `LayeredCompactionFilterBase`. Its `Filter` first drops stale TTL values, then optionally delegates to the user compaction filter using the timestamp-stripped value. If the user filter changes the value, it appends the original timestamp to the replacement.
- `TtlCompactionFilterFactory` owns the active TTL and optional user compaction-filter factory. `CreateCompactionFilter` instantiates a `TtlCompactionFilter` with a user-created inner filter when available. `SetTtl`/`GetTtl` mutate and expose the live TTL.
- `RegisterTtlObjects` registers `TtlMergeOperator`, `TtlCompactionFilterFactory`, and `TtlCompactionFilter` constructors with an `ObjectLibrary`; `DBWithTTLImpl::RegisterTtlClasses` installs that library once in the default registry.
- `DBWithTTL::Open` has single-CF and multi-CF overloads. They validate TTL vector size, derive the system clock from `DBOptions::env` or default clock, sanitize each CF descriptor, open base RocksDB normally or read-only, then wrap the result in `DBWithTTLImpl`.
- `DBWithTTLImpl::AppendTS`, `SanityCheckTimestamp`, `IsStale`, and `StripTS` implement the timestamp encoding/checking/removal contract.
- `Put`, `Merge`, and `Write` intercept writes. `Write` iterates the caller's `WriteBatch`, appends timestamps to `PutCF` and `MergeCF` records, preserves deletes, range deletes, and log data, then writes the transformed batch to the underlying DB.
- `Get`, `MultiGet`, `KeyMayExist`, and `NewIterator` intercept reads. They strip timestamps from found values or return a `TtlIterator` that strips timestamps from iterator values.
- `Close` cancels background work, closes the base DB, deletes the default raw compaction filter pointer if one was installed, and sets an idempotence flag. The destructor calls `Close` if needed.

## Control Flow

Opening a TTL DB starts by registering TTL object factories. The multi-column-family `Open` checks `ttls.size() == column_families.size()`, chooses a clock, copies the CF descriptors, and calls `SanitizeOptions` for every CF. Sanitization ensures the underlying DB always receives timestamp-aware filters and merge operators. The base DB is opened through `DB::Open` or `DB::OpenForReadOnly`; on success the raw `DB` is moved into a new `DBWithTTLImpl`.

Writes are transformed at batch granularity. Public `Put` and `Merge` create a small `WriteBatch` and call `Write`; caller-supplied batches are handled by a local `WriteBatch::Handler`. For each put or merge record the handler calls `AppendTS`, then emits a corresponding record into `updates_ttl` with the same column-family id. Deletes and range deletes are forwarded unchanged. If timestamp acquisition fails, iteration stops with that status; otherwise the transformed batch is sent to `db_->Write`.

Reads delegate to the base DB first, then validate and strip TTL metadata. `Get` rejects the timestamp-returning overload, reads into `PinnableSlice`, checks the suffix length and minimum timestamp, then removes the suffix. `MultiGet` rejects the timestamp array overload, delegates to the base DB, then for every successful value moves/pins it locally, validates the timestamp, and strips it. `KeyMayExist` only strips the optional returned string when the base DB says a value was found.

Compaction filtering is deletion-first. `TtlCompactionFilter::Filter` calls `DBWithTTLImpl::IsStale`; stale values are dropped regardless of user filter. Fresh values are passed to the user filter without the timestamp. If the user filter requests a value rewrite, the TTL filter appends the original internal timestamp so the rewritten value remains readable by TTL readers.

Merge wrapping strips all operand timestamps before invoking the user merge operator. After successful full or partial merge, it appends the current timestamp, making merge output creation time equal to merge execution time. `existing_operand` outputs from `FullMergeV2` are copied into `new_value` before timestamping.

Iterator creation enforces `ReadOptions::io_activity` to be either unknown or `kDBIterator`, normalizes unknown to `kDBIterator`, then wraps the base iterator in `TtlIterator`. `TtlIterator::value()` asserts timestamp sanity and returns a slice shortened by four bytes; `ttl_timestamp()` exposes the decoded internal timestamp for callers that know they are using the wrapper.

Close is staged to avoid background compaction using filter state after wrapper teardown. It snapshots default options, cancels all background work with wait, closes the base DB, deletes the default `compaction_filter` raw pointer captured from options, and marks the wrapper closed.

## State And Persistence Behavior

TTL metadata is stored inline at the end of every value as a fixed-width little-endian `int32_t` generated from `SystemClock::GetCurrentTime`. This means all persisted SST/WAL/memtable values written through `DBWithTTL` contain user bytes plus a 4-byte timestamp suffix. Normal non-TTL RocksDB reads against the same data would see the suffix.

Expiration is not enforced at read time. `IsStale` is used by compaction filters, so stale keys are physically removed only when compaction processes them. A non-positive TTL means data is always fresh. If the clock cannot be read during stale checking, the value is treated as fresh to avoid accidental deletion.

`SanityCheckTimestamp` rejects values smaller than the timestamp suffix or values whose decoded timestamp predates `kMinTimestamp`, which helps catch corrupted data or an ordinary RocksDB opened incorrectly through TTL mode. `kMaxTimestamp` is declared in the header but not enforced here.

`SetTtl` mutates the TTL inside the installed `TtlCompactionFilterFactory` obtained from current column-family options. This affects future compaction-filter creation but does not rewrite already stored timestamps. `GetTtl` reads that factory value. If TTL was configured with a raw compaction filter rather than a factory, the static cast can yield no usable factory and `GetTtl` reports invalid configuration.

Object-registry state is process-global and registered once through `std::call_once`. Option-string serialization uses registered option metadata for TTL, inner filters, filter factories, and wrapped merge operators.

## Dependencies And Integration Points

This implementation depends on:

- `DBWithTTL`, `StackableDB`, `DB`, `ColumnFamilyHandle`, `WriteBatch`, `Iterator`, `PinnableSlice`, `ReadOptions`, and `WriteOptions` from RocksDB public APIs.
- `WriteBatchInternal` for emitting transformed records with original column-family ids.
- `SystemClock` and `Env` for timestamp generation and option preparation.
- `LayeredCompactionFilterBase` for composing TTL filtering with user compaction filters.
- `ObjectRegistry`, `ObjectLibrary`, `OptionTypeInfo`, and `RegisterOptions` for option-string construction and validation.
- `EncodeFixed32`/`DecodeFixed32` for timestamp serialization.
- `CancelAllBackgroundWork` from RocksDB DB utilities to quiesce compaction before close.

The main integration points are public `DBWithTTL::Open`, `CreateColumnFamilyWithTtl`, `SetTtl`, `GetTtl`, user-provided merge operators and compaction filters/factories, and RocksDB option loading via registry strings such as `TtlCompactionFilter`, `TtlCompactionFilterFactory`, and `TtlMergeOperator`.

## Risks And Edge Cases

- TTL is compaction-driven, so expired values can still be returned by `Get`, `MultiGet`, `KeyMayExist`, and iterators until a compaction drops them.
- The timestamp is a 32-bit signed wall-clock value. The code declares a 2038-era `kMaxTimestamp` but does not validate it in `AppendTS` or `SanityCheckTimestamp`; time overflow remains a long-term format risk.
- If the clock fails during writes or merges, user writes fail. If it fails during compaction stale checks, values are retained.
- `SanitizeOptions` wraps raw `compaction_filter` by allocating a new `TtlCompactionFilter` and later `Close` deletes only the default CF raw filter pointer captured from `GetOptions`. Ownership is subtle because RocksDB options historically use raw compaction-filter pointers.
- `SetTtl`/`GetTtl` assume the installed `compaction_filter_factory` is a `TtlCompactionFilterFactory`. When a TTL DB was sanitized around a raw `compaction_filter`, there may be no TTL factory to mutate.
- User compaction filters only see timestamp-free values. If they rewrite a value, the original timestamp is preserved, not refreshed.
- User merge output receives a fresh timestamp, which means merge compaction/read behavior can change the creation time of logically merged values.
- `MultiGet` intentionally ignores its `sorted_input` parameter when delegating to the base API overload visible here; any behavior dependent on sorted input is not preserved by this wrapper method.
- `TtlIterator::value()` asserts timestamp sanity rather than returning an error for corrupt timestamp suffixes, so corruption handling differs from `Get`/`MultiGet`.
- Opening a non-TTL database in TTL mode can report corruption on reads because ordinary values lack valid TTL suffixes.

## Test Signals

Relevant test coverage is in `utilities/ttl/ttl_test.cc` and related RocksDB DB tests. The option tests load `TtlCompactionFilter`, `TtlCompactionFilterFactory`, and `TtlMergeOperator` by registry string, check TTL option values, validate nested dummy filters/factories/operators, verify `ToString`/`CreateFromString` round trips, and confirm `TtlMergeOperator` without a registered user operator fails validation.

Behavioral TTL tests should cover writes appending timestamps, reads stripping them, stale data disappearing after compaction rather than immediately, non-positive TTL retaining data, column-family-specific TTLs, `SetTtl`/`GetTtl`, user compaction filter composition, user merge operator composition, corrupted or missing timestamp suffixes, read-only open, multiple column-family open with mismatched TTL vector rejection, write batch preservation of deletes/range deletes/log data, and close/destructor idempotence.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/ttl/db_ttl_impl.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/ttl/db_ttl_impl.h -->
# Research: sources/storage-engines/rocksdb/utilities/ttl/db_ttl_impl.h

## Purpose

This header declares the internal implementation of RocksDB's TTL database wrapper. It defines `DBWithTTLImpl`, `TtlIterator`, `TtlCompactionFilter`, `TtlCompactionFilterFactory`, `TtlMergeOperator`, and the `RegisterTtlObjects` C entry point used by the object registry. The declarations describe how the public `DBWithTTL` API is layered on top of a base `DB`, how TTL metadata is added/removed, and how compaction/merge/iterator behavior is adapted for timestamp-suffixed values.

## Important APIs, Types, And Functions

- `DBWithTTLImpl : public DBWithTTL` is the concrete stackable DB wrapper. It owns close idempotence state and overrides TTL-aware DB APIs.
- `DBWithTTLImpl::SanitizeOptions` is the static hook that wraps column-family options with TTL compaction filtering and merge behavior before DB or column-family creation.
- `DBWithTTLImpl::RegisterTtlClasses` registers TTL custom object factories once for option-string support.
- `Close`, destructor, and `GetBaseDB` define wrapper lifecycle and access to the underlying `DB`.
- `CreateColumnFamilyWithTtl` and `CreateColumnFamily` expose TTL-aware CF creation. The non-TTL overload defaults to TTL `0`.
- `Put`, `Merge`, and `Write` override write paths to add timestamp suffixes.
- `Get`, `MultiGet`, `KeyMayExist`, and `NewIterator` override read paths to strip timestamp suffixes.
- `IsStale`, `AppendTS`, `SanityCheckTimestamp`, and `StripTS` are static helpers for timestamp expiry, encoding, validation, and removal.
- `kTSLength` is the fixed timestamp suffix length (`sizeof(int32_t)`). `kMinTimestamp` guards against pre-feature/corrupt timestamps. `kMaxTimestamp` documents the signed-32-bit upper timestamp limit.
- `SetTtl` and `GetTtl` mutate/read the TTL on a column family's TTL compaction-filter factory.
- `TtlIterator : public Iterator` wraps a base iterator, delegates positioning/key/status calls, decodes `ttl_timestamp()`, and returns timestamp-stripped `value()`.
- `TtlCompactionFilter : public LayeredCompactionFilterBase` composes TTL expiry with an optional user compaction filter and exposes option validation/registration hooks.
- `TtlCompactionFilterFactory : public CompactionFilterFactory` stores mutable TTL, clock, and optional user factory; it creates per-compaction `TtlCompactionFilter` objects and exposes `Inner()` for customization introspection.
- `TtlMergeOperator : public MergeOperator` stores a user merge operator and clock, wraps full/partial merge, and exposes `Inner()` for customization introspection.
- `RegisterTtlObjects(ObjectLibrary&, const std::string&)` is declared `extern "C"` for dynamic/static object-library registration.

## Control Flow

The header defines a wrapper-oriented call graph. Open/create code in the `.cc` file sanitizes options first, then constructs a base `DB`, then wraps it in `DBWithTTLImpl`. Public write calls route through `DBWithTTLImpl::Write`, where timestamps are appended before forwarding to the base DB. Public read calls route to the base DB and then strip suffixes before returning to the user. Iterator reads create a `TtlIterator`, which delegates traversal to the base iterator and trims values lazily.

Compaction flow is declared as a layered filter: RocksDB asks `TtlCompactionFilterFactory::CreateCompactionFilter` for a filter, then `TtlCompactionFilter::Filter` decides whether to drop stale values before delegating to any user filter. Merge flow is declared through `TtlMergeOperator`, which makes the user's merge operator operate on logical values and reattaches TTL metadata afterward.

Option loading flow is represented by `PrepareOptions`, `ValidateOptions`, `Name`, `kClassName`, `IsInstanceOf`, and `Inner` declarations on the custom objects. These let RocksDB's customization registry instantiate, prepare, validate, compare, and introspect TTL wrappers.

## State And Persistence Behavior

`DBWithTTLImpl` itself only adds `closed_`, a process-local lifecycle flag. The persistent TTL state is the four-byte timestamp suffix appended to each stored value by implementation code. The static timestamp constants define the on-disk logical contract: every readable TTL value must be at least four bytes long and have a timestamp not older than `kMinTimestamp`.

`TtlIterator` owns the wrapped iterator pointer and deletes it in its destructor. It does not own value memory; `value()` returns a `Slice` pointing into the base iterator's value with its length shortened by `kTSLength`.

`TtlCompactionFilter` stores `ttl_` and a raw `SystemClock*` plus inherited user-filter ownership/state from `LayeredCompactionFilterBase`. `TtlCompactionFilterFactory` stores a mutable `ttl_`, raw clock pointer, and shared user filter factory. `TtlMergeOperator` stores a shared user merge operator and raw clock pointer. The raw clock pointers are expected to come from `Env`/`SystemClock` singletons or DB options and outlive the wrappers.

`SetTtl` changes the TTL value in the installed factory for future compactions; it does not change already-encoded timestamps or immediately delete old data. `GetTtl` reports the current factory value.

## Dependencies And Integration Points

This header includes:

- `db/db_impl/db_impl.h` for DB implementation utilities used by the TTL wrapper implementation.
- Public RocksDB APIs: `rocksdb/db.h`, `rocksdb/utilities/db_ttl.h`, `rocksdb/compaction_filter.h`, `rocksdb/merge_operator.h`, and `rocksdb/system_clock.h`.
- `utilities/compaction_filters/layered_compaction_filter_base.h` for user compaction-filter composition.
- `ObjectLibrary`/`ObjectRegistry` forward declarations for registry integration.

The exposed classes integrate with the public `DBWithTTL` API, RocksDB's stackable DB layer, the compaction filter and merge operator plugin systems, option serialization/deserialization, and iterator API. The `extern "C"` registration function is an integration point for object-library loading.

## Risks And Edge Cases

- `TtlIterator::value()` asserts timestamp validity instead of surfacing a `Status`, so corrupt TTL suffixes in iterator reads can trip debug assertions.
- `TtlIterator::ttl_timestamp()` assumes the current value has at least `kTSLength` bytes and does not validate `Valid()` or value length itself.
- The header exposes raw pointers for `SystemClock`, raw compaction filters, and wrapped iterators. Correct lifetime is enforced by usage patterns rather than types.
- `SetTtl` returns `void` and silently returns if no factory is available, while `GetTtl` can report invalid arguments or missing TTL factory. This asymmetry can hide configuration mistakes.
- `CreateColumnFamily` defaulting to TTL `0` means CFs created through the non-TTL overload are still timestamp-suffixed but never expire by TTL.
- The fixed `int32_t` timestamp format has a documented maximum of `2147483647`; callers and tests should account for the eventual overflow boundary.
- `IsInstanceOf` aliases `"Delete By TTL"` and `"Merge By TTL"` preserve legacy/customization names, so option-equivalence logic must handle both canonical and alias names.

## Test Signals

The declarations are exercised by `db_ttl_impl.cc` and by TTL tests that instantiate the wrappers through both direct DB APIs and object-registry strings. Important signals include successful `DBWithTTL::Open`, CF creation with TTL, option-string creation of `TtlCompactionFilter`, `TtlCompactionFilterFactory`, and `TtlMergeOperator`, validation failures when required inner objects or clocks are missing, iterator value trimming, stale-value compaction, mutable TTL changes, and correct composition with user merge operators and compaction filters.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/utilities/ttl/db_ttl_impl.h -->
