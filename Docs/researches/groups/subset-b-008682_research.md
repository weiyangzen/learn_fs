# subset-b-008682 research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_reader.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_reader.cc

Purpose: implements `PlainTableReader`, RocksDB's table reader for plain-table SSTs, including open-time property validation, optional mmap setup, index and bloom initialization, point lookup, and forward iteration over encoded records.

Important APIs/types/functions: `PlainTableReader::Open` reads table properties, validates prefix extractor compatibility unless full-scan mode is requested, resolves encoding, builds the reader, optionally populates the index, and stores properties. `PopulateIndex`, `PopulateIndexRecordList`, `AllocateBloom`, and `FillBloom` build or load the plain table hash/sub-index and bloom data. `GetOffset`, `Next`, `Get`, and `Prepare` are the lookup path. The local `PlainTableIterator` implements `InternalIterator` with `SeekToFirst`, prefix-aware `Seek`, and forward `Next`; reverse operations are unsupported.

Control flow: opening rejects oversized files, reads table properties, mmaps the whole file when requested, then either builds/loads index metadata or marks `full_scan_mode_`. Lookups compute a total-order full-key hash or prefix hash, consult bloom, find a candidate offset through direct bucket lookup or sub-index binary search, then scan forward until the target internal key is reached or the prefix changes. Iterator seek follows the same offset lookup, then advances until the first key greater than or equal to the target.

State and persistence behavior: source data is immutable SST file content referenced by `PlainTableReaderFileInfo`. Index and bloom allocations are held by `Arena` and cache allocation pointers, while `table_properties_` persists read metadata for callers. `dummy_cleanable_` is used for immortal mmap tables when values can reference file-backed memory.

Dependencies/integration points: integrates with `ReadTableProperties`, `ReadMetaBlock`, `PlainTableKeyDecoder`, `PlainTableIndexBuilder`, `PlainTableBloomV1`, RocksDB `GetContext`, perf counters, and `TableReader` callers. It depends heavily on a correct `SliceTransform` matching the file's stored prefix extractor name.

Risks: full-scan mode intentionally disables `Get` and `Seek`; reverse iteration is asserted/not supported. Prefix extractor mismatch is a hard error except in full scan. Corrupt offsets, non-seekable first keys, malformed internal keys, or index/data disagreement surface as `Status::Corruption`/parse errors. Approximate offset/size return zero, so consumers must not rely on meaningful size estimates for plain tables.

Test signals: behavior is indirectly exercised by table reader benchmarks, SST dumper paths that open plain tables in full-scan mode, and plain-table format tests elsewhere. This file itself has no local unit tests in the listed subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_reader.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_reader.h

Purpose: declares the `PlainTableReader` table-reader implementation and its file-info helper for RocksDB plain-table SSTs.

Important APIs/types/functions: `PlainTableReaderFileInfo` records mmap mode, mmapped data, logical data end offset, and the owned `RandomAccessFileReader`. `PlainTableReader` derives from `TableReader` and exposes `Open`, `NewIterator`, `Prepare`, `Get`, approximate size/offset methods, `SetupForCompaction`, `GetTableProperties`, and `ApproximateMemoryUsage`. Protected and private helpers cover bloom matching, index population, mmap setup, record decoding, offset lookup, and prefix extraction.

Control flow: the header makes `Open` the only factory-style construction path, with constructor public but specialized for callers already holding properties. Query flow is organized around prefix extraction, bloom check, index offset lookup, and `Next` record decoding. Iterator access is granted through friendship to `PlainTableIterator`.

State and persistence behavior: persistent reader state includes comparator, encoding type, status, index, full-scan flag, fixed or variable user-key length, prefix extractor pointer, bloom, file info, arena-backed allocations, immutable options reference, optional cleanable, file size, and shared table properties. `data_start_offset_` is fixed at zero, and `data_end_offset_` comes from table properties.

Dependencies/integration points: the API sits between RocksDB's generic `TableReader` contract and plain-table-specific components from `table/plain`. It also uses `TableCache` friendship, `GetContext`, `InternalKeyComparator`, and table property metadata.

Risks: lifetime is important: `prefix_extractor_` and `ioptions_` are non-owning references/pointers and must outlive the reader as expected by RocksDB option lifetimes. Full-scan and total-order modes have different capabilities. Fixed-key length logic assumes internal-key trailers are eight bytes.

Test signals: exposed methods are used by plain table factory/open paths and by higher-level SST tooling. The listed tests mainly validate generic reader behavior through `SstFileReader`, not this header directly.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_dumper.cc -->
# sources/storage-engines/rocksdb/table/sst_file_dumper.cc

Purpose: implements `SstFileDumper`, the utility-facing reader for inspecting SST files, verifying checksums, dumping key/value content, reading table properties, and estimating compression-size outcomes.

Important APIs/types/functions: constructor initializes read options and immediately calls `GetTableReader`. `GetTableReader` opens the file, reads footer/properties/meta-index, selects the right table factory, recreates mmap-capable files for plain/cuckoo formats, configures comparators from table properties, and constructs the `TableReader`. `ReadSequential`, `ReadTableProperties`, `VerifyChecksum`, `DumpTable`, `ShowAllCompressionSizes`, `ShowCompressionSize`, `CalculateCompressedTableSize`, `SetTableOptionsByMagicNumber`, and `NewTableReader` provide the public behaviors.

Control flow: file open checks emptiness, tail-prefetches for footer reading, uses the magic number to load properties and select format-specific options, then opens a table reader. Sequential scan creates an internal iterator, optionally seeks to `from`, applies timestamp-normalized range bounds, parses internal keys, prints values according to type, and verifies scanned count against properties for full scans. Compression reporting rewrites the existing table into a memory-env SST for each compression setting and times write/read passes.

State and persistence behavior: owns the target `RandomAccessFileReader`, `TableReader`, cached `TableProperties`, meta-index contents, mutable options, read options, comparator, output settings, and `read_num_`. It does not mutate the source SST except by reading it; compression-size estimates write temporary in-memory files.

Dependencies/integration points: integrates with `Footer`, `ReadTableProperties`, `ReadMetaIndexBlockInFile`, table factories, block-based/plain/cuckoo formats, blob index decoding, wide-column serialization, compression manager/statistics, `NewMemEnv`, and ldb tooling conventions.

Risks: format selection depends on valid magic number and properties; unsupported formats return invalid argument. Plain/cuckoo need mmap reads. `ReadSequential` skips unparsable keys but continues printing. Count verification subtracts range deletions but does not verify range tombstone contents. Compression-size code assumes iterator output can be rebuilt through a block-based builder.

Test signals: exercised by SST dump CLI/tool tests outside this subset; listed code overlaps with `SstFileReader` tests for checksum, properties, and iterator correctness.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_dumper.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_dumper.h -->
# sources/storage-engines/rocksdb/table/sst_file_dumper.h

Purpose: declares the `SstFileDumper` utility class for SST inspection, dumping, checksum verification, property reads, and compression-size experiments.

Important APIs/types/functions: constructor accepts RocksDB `Options`, file name, file temperature, readahead size, checksum/output/decode flags, `EnvOptions`, silence mode, and sequence-number display flag. Public methods include `ReadSequential`, `ReadTableProperties`, `VerifyChecksum`, `DumpTable`, `ShowAllCompressionSizes`, `ShowCompressionSize`, `GetReadNumber`, `GetInitTableProperties`, `getStatus`, and `GetMetaIndexContents`.

Control flow: the header separates initialization (`GetTableReader`, `ReadTableProperties`, `SetTableOptionsByMagicNumber`, `NewTableReader`) from inspection operations. `ReadSequential` can limit count, bound by from/to keys, or treat `from` as a prefix.

State and persistence behavior: object state caches options, immutable/mutable options, read options, comparator, table properties, meta-index block contents, the open file reader, table reader, file temperature, output flags, and count of sequentially read entries.

Dependencies/integration points: it bridges public utility commands to table internals (`TableReader`, `TableBuilderOptions`, `BlockContents`, `RandomAccessFileReader`) and RocksDB option structures.

Risks: callers must check `getStatus()` or public method statuses because construction performs real IO. `GetInitTableProperties()` returns a raw pointer owned by the dumper. Output modes can affect stdout/stderr but not stored state.

Test signals: no direct tests in this subset; behavior is validated by utility tests and by table-reader tests that share the same table-reader contracts.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_dumper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_reader.cc -->
# sources/storage-engines/rocksdb/table/sst_file_reader.cc

Purpose: implements the public `SstFileReader` utility API for opening an SST file outside a DB, reading keys through DB-style or raw table iterators, point lookup, multi-get, table property access, checksum verification, and entry-count verification.

Important APIs/types/functions: private `Rep` stores `Options`, `EnvOptions`, immutable/mutable options, a persistent `ReadOptions` for raw table iterators, and the opened `TableReader`. `Open` creates `RandomAccessFileReader` and calls the configured table factory. `Get`, `MultiGet`, `NewIterator`, `NewTableIterator`, `ParseTableIteratorKey`, `GetTableProperties`, `VerifyChecksum`, and `VerifyNumEntries` map public APIs to `TableReader` primitives.

Control flow: `Open` reads file size, opens a random-access file, constructs `TableReaderOptions`, sets `largest_seqno` to `kMaxSequenceNumber` for global-seqno compatibility, then opens the table. `Get` wraps the user key in a `LookupKey`, passes a `GetContext` to the table, reports counters, and translates context state to public `Status`. `MultiGet` constructs parallel `KeyContext`/`GetContext` arrays, sorts key contexts by comparator, calls `TableReader::MultiGet`, and post-processes statuses. DB-style iteration wraps a table internal iterator in `ArenaWrappedDBIter`; raw iteration returns `TableIterator`.

State and persistence behavior: the reader owns one opened immutable table. `roptions_for_table_iter` is intentionally stored in `Rep` so raw table iterators are not backed by a caller-owned temporary `ReadOptions`. Values are returned through `PinnableSlice` or copied strings.

Dependencies/integration points: integrates with table factories, `TableReader`, `GetContext`, `MultiGetContext`, `LookupKey`, `ArenaWrappedDBIter`, `TableIterator`, `ParseEntry`, comparators, merge operators, and statistics.

Risks: caller options must match the SST format/comparator. Blob-backed wide-column values cannot be fetched because no `BlobFetcher` is provided, so lookup should return corruption instead of crashing. Raw table iterators expose internal keys and require parsing. `VerifyNumEntries` trusts table properties and only subtracts range deletions.

Test signals: `sst_file_reader_test.cc` covers basic reads, comparators, global sequence numbers, timestamp behavior, raw table iterators, parsing invalid keys, single get vs multiget, checksum, and entry-count corruption.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_reader.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_reader_test.cc -->
# sources/storage-engines/rocksdb/table/sst_file_reader_test.cc

Purpose: provides unit tests for `SstFileReader` and related `SstFileWriter` behavior, focusing on reading externally created SSTs, parsing raw table keys, timestamps, entry-count verification, and get/multiget edge cases.

Important APIs/types/functions: helper functions `EncodeAsString` and `EncodeAsUint64`; fixture `SstFileReaderTest` with `CreateFile`, `CheckFile`, and `CreateFileAndCheck`; timestamp fixtures using `BytewiseComparatorWithU64TsWrapper`; `SstFileReaderTableIteratorTest`; and parameterized `SstFileReaderTableGetTest` over single-get vs multiget.

Control flow: tests create SSTs with `SstFileWriter` or a temporary DB, open them with `SstFileReader`, then verify DB-style iteration, raw table iteration, checksum verification, parsing of internal keys, point lookups, merge resolution, and corruption handling. Timestamp tests write entries in comparator order and check snapshot-time visibility via `ReadOptions.timestamp`.

State and persistence behavior: tests create per-thread temporary SST/DB paths and clean them in destructors or via `DestroyDB`. Some tests intentionally ingest files into a DB to produce global sequence numbers or use sync points to corrupt table properties.

Dependencies/integration points: integrates test harness, DB test utilities, merge operators, custom comparators, external SST writer properties, convenience registration, blob/wide-column APIs, snapshots, live-file metadata, and sync points.

Risks covered: out-of-scope `ReadOptions` lifetime for `NewIterator`; timestamp size mismatch; timestamp ordering; non-persisted timestamp min-only rules and metadata stripping; corrupted `num_entries`; invalid short internal keys; blob-backed wide-column lookup without a fetcher; raw table iterator semantics differing from DB iterator semantics.

Test signals: this is the main test signal for the listed reader/writer APIs. It explicitly checks both `Get` and `MultiGet` via parameterization, and it distinguishes visible DB results from raw table entries including deletions and timestamps.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_reader_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_writer.cc -->
# sources/storage-engines/rocksdb/table/sst_file_writer.cc

Purpose: implements `SstFileWriter`, the API for creating external SST files that can later be read or ingested by RocksDB.

Important APIs/types/functions: static external property names define version and global sequence number keys. `SstFileWriter::Rep` owns the file writer, table builder, options, comparator, file metadata, timestamp policy, and helper methods `AddImpl`, timestamp-aware `Add`, `AddEntity`, `DeleteRangeImpl`, timestamp-aware `DeleteRange`, and `InvalidatePageCache`. Public methods include `Open`, `Put`, `PutEntity`, `Merge`, `Delete`, `DeleteRange`, `Finish`, `FileSize`, and `CreatedBySstFileWriter`.

Control flow: `Open` creates a writable file with no-reopen/no-reader contract, selects compression from bottommost/per-level/default options, builds internal property collector factories including external-SST metadata, constructs `TableBuilderOptions`, wraps the file in `WritableFileWriter`, and creates the table builder. Add/delete paths validate open state, builder status, key/value sizes, timestamp compatibility, strict key ordering, and value type before encoding internal keys and adding to the builder. `Finish` rejects empty files, finishes and syncs/closes the builder/file, records checksums, deletes failed files, optionally strips timestamps from returned metadata, and releases the builder.

State and persistence behavior: persistent output is an SST file plus `ExternalSstFileInfo` metadata. In-memory state tracks smallest/largest point and range-delete keys, entry counts, file size, checksum, fake DB/session identity, and fake file numbers for cache-key uniqueness. Destructor abandons an unfinished builder.

Dependencies/integration points: integrates with `WritableFileWriter`, `TableBuilder`, `TableBuilderOptions`, table-property collectors, wide-column serialization, range tombstones, DB session ID generation, file checksum handoff, environment/file-system APIs, and external file ingestion metadata.

Risks: keys must be strictly ascending according to the configured user comparator including timestamp ordering. Timestamp-aware comparators reject timestamp-less APIs; non-persisted timestamp mode accepts only minimum timestamps. Failed finish deletes the target file but ignores delete failures. Page-cache invalidation is best-effort and treats unsupported as OK.

Test signals: `sst_file_reader_test.cc` covers basic writer output, timestamp ordering/mismatch, non-persisted timestamp rules and metadata stripping, empty/corrupt property implications via reader checks, and external-SST global sequence compatibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_writer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_writer_collectors.h -->
# sources/storage-engines/rocksdb/table/sst_file_writer_collectors.h

Purpose: defines table-property collector support for marking SST files created by `SstFileWriter`.

Important APIs/types/functions: `ExternalSstFilePropertyNames` declares `kVersion` and `kGlobalSeqno`. `SstFileWriterPropertiesCollector` implements `InternalTblPropColl`, ignores per-key/block stats, and writes fixed-width version/global-seqno properties in `Finish`. `SstFileWriterPropertiesCollectorFactory` creates collectors with configured version and global sequence number.

Control flow: during table building, the factory creates a collector; each key/block callback is a no-op; `Finish` serializes version with `PutFixed32` and global seqno with `PutFixed64` into user collected properties.

State and persistence behavior: collector state is only `version_` and `global_seqno_`; persisted state is two user-collected table properties embedded in the SST. Readable properties expose the version as text.

Dependencies/integration points: used by `SstFileWriter::Open` as part of `InternalTblPropCollFactories`. Reader/test code detects these properties through `ExternalSstFilePropertyNames`.

Risks: readable properties omit global sequence number, so diagnostics needing it must inspect raw user properties. The collector does not validate or update values after construction.

Test signals: `ReadFileWithGlobalSeqno` checks that external SST properties include `kGlobalSeqno` after ingestion, and writer-created files are recognized through `CreatedBySstFileWriter`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/sst_file_writer_collectors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_builder.h -->
# sources/storage-engines/rocksdb/table/table_builder.h

Purpose: declares the generic table-building options and abstract `TableBuilder` interface used by all RocksDB table formats.

Important APIs/types/functions: `TableReaderOptions` bundles immutable options, prefix extractor, compression manager, env options, comparator, filter skipping, immortality, prefetch flags, level, tracing, cache pinning, DB/session/file identity, unique ID, protection bytes, tail size, timestamp persistence, and metadata-cache policy. `TableBuilderOptions` extends table-property collector context with immutable/mutable/read/write options, comparator, collector factories, compression settings, column-family identity, level, key-time metadata, bottommost/reason flags, DB identity, target size, file number, and sequence threshold. `TableBuilder` defines `Add`, `status`, `io_status`, `Finish`, `Abandon`, size/entry/property/checksum accessors, compaction hint, sequence-time mapping, and worker CPU reporting.

Control flow: factories consume these option structs when opening readers or constructing builders. Builder lifecycle requires monotonic `Add` calls, exactly one terminal `Finish` or `Abandon`, and destruction only after terminal handling.

State and persistence behavior: the header itself has no storage, but its interfaces define persistence metadata that table implementations emit into SST properties, checksums, identities, and file size accounting.

Dependencies/integration points: central integration surface for block-based, plain, cuckoo, external SST writer, compaction, table cache, compression manager, table property collectors, block cache tracing, and timestamp persistence.

Risks: many fields are references or non-owning pointers, so factories/builders must respect caller lifetimes. Misconfigured comparator, compression manager, timestamp persistence, or identity fields can produce unreadable or misleading SSTs. Builders are not internally synchronized for mutation.

Test signals: used by `SstFileWriter`, `SstFileDumper` compression estimation, and `table_reader_bench.cc`; concrete builder behavior is tested through table-format and external-SST tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_builder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_factory.cc -->
# sources/storage-engines/rocksdb/table/table_factory.cc

Purpose: registers built-in table factories and implements string-based creation of `TableFactory` instances.

Important APIs/types/functions: `RegisterTableFactories` uses `std::once_flag` to register block-based, plain, and cuckoo table factories with the default `ObjectLibrary`. `TableFactory::CreateFromString` registers built-ins, then calls `LoadSharedObject<TableFactory>`.

Control flow: the first create call installs three factory lambdas; subsequent calls reuse the loaded registry. Each lambda fills a `std::unique_ptr<TableFactory>` guard and returns the raw factory pointer required by the object registry interface.

State and persistence behavior: process-global registry state is mutated once. No SST or DB persistent data is written.

Dependencies/integration points: integrates `rocksdb/convenience`, customizable/object registry utilities, and concrete table factory classes for block-based, plain, and cuckoo formats. Used by config parsing and tools that load table factories by name.

Risks: only these built-ins are registered here; custom factories require object library/shared-object mechanisms. Factory creation returns defaults, not caller-customized table options.

Test signals: indirectly covered by configuration and object registry tests. Tools such as `SstFileDumper` also rely on table factory identity strings.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_factory.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_iterator.h -->
# sources/storage-engines/rocksdb/table/table_iterator.h

Purpose: provides an `Iterator` wrapper around a heap-allocated `InternalIterator` returned by `TableReader::NewIterator`, intended for raw table iteration through public APIs.

Important APIs/types/functions: `TableIterator` deletes copy operations, supports move construction/assignment, owns `InternalIterator*`, forwards all iterator movement/access/status methods, exposes `operator->` and `get`, and returns `NotSupported` for `GetProperty`.

Control flow: constructor takes an already-valid internal iterator. `reset` deletes any existing iterator before taking a new one; move assignment transfers ownership. All public iterator calls delegate directly to the wrapped internal iterator.

State and persistence behavior: state is a single owning raw pointer. It does not persist data; it controls iterator lifetime and deletion.

Dependencies/integration points: used by `SstFileReader::NewTableIterator` to expose raw table keys as an `Iterator`. Integrates public `rocksdb::Iterator` API with table-internal iteration.

Risks: constructor assumes non-null input; forwarded methods dereference `iter_` without null checks. It is only correct for iterators allocated with the default allocator, not arena placement. `GetProperty` asserts false and is not usable.

Test signals: `SstFileReaderTableIteratorTest` verifies raw iteration exposes all internal entries, supports seek/seek-for-prev where the underlying table iterator does, and differs from DB iterator visibility.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_iterator.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_properties.cc -->
# sources/storage-engines/rocksdb/table/table_properties.cc

Purpose: implements formatting, aggregation, serialization/parsing, equality, memory accounting, and compression display helpers for `TableProperties`.

Important APIs/types/functions: `TableProperties::ToString`, `Add`, `GetAggregatablePropertiesAsMap`, `ApproximateMemoryUsage`, `Serialize`, `Parse`, `AreEqual`, debug-only `TEST_SetRandomTableProperties`, and `ParseCompressionNameForDisplay`. The file defines all `TablePropertiesNames` persisted property-key strings and an `OptionTypeInfo` map describing how each field serializes.

Control flow: `ToString` appends human-readable property lines, including derived averages, unique ID, and sequence-number-to-time mapping. `Add` aggregates numeric counters across properties. Serialization delegates to `OptionTypeInfo` with the static field map. Compression display parsing handles old names directly and new format-version-7 compatibility-name plus hex-code lists with custom compression manager lookup.

State and persistence behavior: this file defines the canonical persisted property names for SST table properties and the parse/serialize shape for in-memory `TableProperties`. It does not own table files but controls metadata representation and diagnostics.

Dependencies/integration points: integrates with `SeqnoToTimeMapping`, `CompressionManager`, unique ID helpers, options type metadata, malloc usable-size support, random test helpers, and string utilities. Many table builders/readers rely on these property keys.

Risks: comments warn manual updates are required when new string properties are added to memory accounting and when the struct layout changes for debug randomization. Serialization correctness depends on `offsetof` entries matching `TableProperties`. Compression display intentionally differs from decompression validation by filtering invalid/no-compression codes for display.

Test signals: debug helper supports property serialization tests. Reader/dumper tests use properties for count verification, comparator selection, timestamp persistence, and external-SST metadata checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_properties.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_properties_internal.h -->
# sources/storage-engines/rocksdb/table/table_properties_internal.h

Purpose: declares an internal debug-only helper for randomizing `TableProperties` in tests.

Important APIs/types/functions: `TEST_SetRandomTableProperties(TableProperties* props)` is declared only when `NDEBUG` is not defined.

Control flow: consumers include this header when they need access to the test helper implemented in `table_properties.cc`.

State and persistence behavior: no state is defined here; the function mutates a caller-provided `TableProperties` object in debug builds.

Dependencies/integration points: includes public `rocksdb/table_properties.h` and is used by tests/internal code that validate serialization/equality behavior.

Risks: unavailable in release builds. Its implementation assumes a specific field layout of `TableProperties`, so adding fields requires care.

Test signals: supports internal table-properties tests; no direct test appears in the listed subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_properties_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_reader.h -->
# sources/storage-engines/rocksdb/table/table_reader.h

Purpose: declares the abstract `TableReader` interface for immutable persistent SST/table formats.

Important APIs/types/functions: pure virtual methods include `NewIterator`, `ApproximateOffsetOf`, `ApproximateSize`, `SetupForCompaction`, `GetTableProperties`, `ApproximateMemoryUsage`, and `Get`. Optional methods include range tombstone iterators, approximate key anchors, `Prepare`, `MultiGetFilter`, `MultiGet`, coroutine multiget, `Prefetch`, `DumpTable`, `VerifyChecksum`, and `MarkObsolete`. `Anchor` describes approximate user-key range anchors.

Control flow: callers open concrete readers through table factories, then use this uniform interface for point lookups, scans, metadata, checksum verification, dumping, and cache/compaction hints. Default `MultiGet` loops over keys and calls `Get`; specialized readers can override. Default optional features return no-op or `NotSupported`.

State and persistence behavior: the interface represents immutable persistent table data and requires thread-safe access. It stores no data itself but defines lifetime rules such as `ReadOptions` outliving returned iterators unless wrapped by higher layers.

Dependencies/integration points: central contract between DB/table cache/compaction/tooling and concrete table formats including block-based, plain, and cuckoo. Integrates `GetContext`, `MultiGetContext`, range tombstones, internal iterators, table properties, and table reader caller attribution.

Risks: implementers must honor arena allocation semantics for iterators and thread-safety for immutable access and `MarkObsolete`. Optional defaults can hide unsupported features unless callers check status. `skip_filters` semantics are format-specific.

Test signals: `sst_file_reader_test.cc` exercises concrete `TableReader` behavior through `SstFileReader`, including `Get`, `MultiGet`, `NewIterator`, `VerifyChecksum`, and table properties.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_reader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_reader_bench.cc -->
# sources/storage-engines/rocksdb/table/table_reader_bench.cc

Purpose: standalone benchmark for measuring table-reader point lookup and iterator performance, either directly through a table reader or through a DB.

Important APIs/types/functions: `MakeKey` builds deterministic user or internal keys; `Now` selects microsecond/nanosecond timing; `TableReaderBenchmark` builds/populates data, opens table or DB, runs randomized get/iterator workloads, records a `HistogramImpl`, and prints results. `main` parses gflags and selects block-based, plain, or cuckoo table factory options.

Control flow: when `through_db` is false, the benchmark builds a table file directly with `TableBuilder`, writes about `num_keys1 * num_keys2` keys, reopens it through `NewTableReader`, then performs repeated randomized lookups or range iterations. When `through_db` is true, it opens a temporary DB, writes keys, flushes, and benchmarks DB APIs. Iterator mode verifies expected sequential keys.

State and persistence behavior: creates temporary per-thread table/DB paths, writes benchmark data, and deletes/destroys them at the end. No production state is modified.

Dependencies/integration points: integrates gflags, RocksDB DB APIs, table factories, file readers/writers, `GetContext`, internal iterators, test utilities, histograms, and env/system clock.

Risks: compiled fallback without gflags only prints an error. Benchmark asserts on iterator count mismatches. Direct table-reader mode uses internal keys, so `MakeKey` must match table expectations. Some flag combinations, especially prefix/plain-table choices, affect validity and measured behavior.

Test signals: this is not a correctness test but provides performance and smoke coverage for direct table-reader get/iterator paths across table factories.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/table_reader_bench.cc -->
