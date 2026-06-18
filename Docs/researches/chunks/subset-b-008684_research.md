# sources/storage-engines/rocksdb/table/table_test.cc lines 6733-10416

## Scope

This chunk covers the end of a block-cache role-option validation test, the full `ExternalTableTest` fixture and its tests, and the `UserDefinedIndexTestBase`, parameterized user-defined-index tests, and randomized user-defined-index stress tests through the end of `table_test.cc`. It is test code rather than production storage code, but it exercises table factory extension points, SST writer/reader behavior, external-file ingestion, iterator/multiscan integration, table properties, file checksums, user-defined index construction/reading, compaction, snapshots, range deletes, reverse comparators, and DB-level persistence behavior.

## Purpose

- Validate `BlockBasedTableOptions::cache_usage_options` override handling when toggling `CacheEntryRoleOptions::charged` for cache roles and when the block cache is disabled.
- Provide a minimal external-table implementation to test `NewExternalTableFactory()`, `ExternalTableBuilder`, `ExternalTableReader`, `ExternalTableIterator`, property-block handoff, checksums, file-system reads, pinned values, `SstFileWriter`, `SstFileReader`, `DB::IngestExternalFile`, DB iterators, and `MultiScan`.
- Provide a synthetic user-defined index implementation that records one index entry per data block and can be injected through `ReadOptions::table_index_factory`.
- Verify user-defined indexes work with plain SST readers, ingested SSTs, DB flush output, merge/delete/single-delete/entity value types, snapshots, compaction output, range deletes, dynamic config strings, partitioned block indexes, reverse comparator ordering, and multiscan prefetch limits.
- Stress compare an ingest-based column family against a normally written column family under randomized ranges, range deletes, atomic replace bulk-load, optional user-defined index use, optional SST partitioning, and both bytewise and reverse-bytewise comparators.

## Important APIs, Types, And Functions

- `ExternalTableTest : DBTestBase` owns the external-table test helpers and uses per-thread DB/file paths to avoid cross-test interference.
- `DummyExternalTableFile` serializes a simple external table format: a 32-bit property-block size, optional property-block bytes, then repeated fixed-size item headers plus key/value payloads. It also accumulates `TableProperties` such as comparator name, raw key/value sizes, entry count, and file size.
- `DummyExternalTableIterator : ExternalTableIterator` implements forward-only iteration, `Seek`, `Next`, `NextAndGetResult`, `PrepareValue`, `UpperBoundCheckResult`, and multiscan `Prepare(const ScanOptions[], size_t)`. It intentionally rejects `SeekToFirst`/`SeekToLast` after scan preparation and returns `NotSupported` for reverse movement.
- `DummyExternalTableReader : ExternalTableReader` implements `NewIterator`, `Get`, `MultiGet`, `GetPropertiesBlock`, and `GetTableProperties`. It deserializes the dummy file into an ordered `std::map`.
- `PinnedDummyExternalTableReader` overrides `Get` to return values pinned from an internal map via `PinnableSlice::PinSlice()` and a cleanup callback, exercising zero-copy `ExternalTableReaderAdapter::Get()` behavior.
- `DummyExternalTableBuilder : ExternalTableBuilder` enforces strictly increasing keys, serializes accumulated key/value pairs on `Finish`, supports optional `PutPropertiesBlock`, exposes `FileSize`, and reports builder status.
- `DummyExternalTableFactory : ExternalTableFactory` creates the dummy builder/reader. With `read_via_options_fs_`, it verifies `ExternalTableOptions` supplies a usable `FileSystem`, `FileOptions`, and checksum handoff type before constructing a reader.
- `CountingFileReadListener : EventListener` opts into file IO notifications and counts successful read operations/bytes, letting tests assert external table open paths update statistics and listener callbacks.
- `PinnedDummyExternalTableFactory` retains the last pinned reader so tests can install pinned data and inspect cleanup counts after DB `Get`/`MultiGet`.
- `UserDefinedIndexTestBase : BlockBasedTableTestBase` provides `CustomFlushBlockPolicy`, `CustomFlushBlockPolicyFactory`, synthetic key generation helpers, `ValidateMultiScan`, and the nested `TestUserDefinedIndexFactory`.
- `TestUserDefinedIndexFactory : UserDefinedIndexFactory` creates builders/readers, optionally skips fixed key-size assertions, logs every `UserDefinedIndexBuilder::ValueType` seen by builders, and exposes seek/next error counters for failure injection.
- `TestUserDefinedIndexBuilder : UserDefinedIndexBuilder` records `OnKeyAdded` calls, maps internal value categories to UDI value types, counts keys per block, and serializes block-handle metadata with `PutLengthPrefixedSlice`, `PutFixed64`, and `PutFixed32`.
- `TestUserDefinedIndexReader : UserDefinedIndexReader` parses the serialized index block into a comparator-ordered map and creates `TestUserDefinedIndexIterator`.
- `TestUserDefinedIndexIterator : UserDefinedIndexIterator` implements `SeekAndGetResult`, `NextAndGetResult`, `Prepare`, block-handle `value()`, scan-range validation, count-limited scan behavior through the `property_bag["count"]`, and injected IO errors.
- `DataRange` models randomized stress-test ranges, including start/end numeric bounds, value, delete-range flag, skipped flag, scan count limit, and formatted start/end keys.
- `UserDefinedIndexStressTest` builds two CFs (`regular_cf`, `ingest_cf`) and helper flows: `SetupDB`, `GenerateKeyRanges`, `CreateSstFileWithRanges`, `RangeScan`, `AddDataToRegularCF`, `ValidateQueryResult`, `IngestFilesInOneLevel`, `IngestDataToCF`, and `CompactIngestedCF`.

## Control Flow

The cache-option tail constructs invalid or unsupported `BlockBasedTableOptions`, installs them with `NewBlockBasedTableFactory`, calls `TryReopen`, and asserts exact status classes and diagnostic text for unsupported data-block charge toggling and invalid filter-construction charging when `no_block_cache` is true.

External-table tests use a consistent flow. A dummy factory creates an SST-like external file through `SstFileWriter` or a direct `ExternalTableBuilder`; a reader is opened either through the factory, `SstFileReader`, or DB ingestion; then iterators, point lookups, batched lookups, file checksums, file-read accounting, pinned-value cleanup, and range scans are verified. `DBMultiScanTest` prepares multiple ranges through `MultiScanArgs`, iterates range-by-range, checks inclusive start/exclusive limit behavior, handles overlapping and open-ended ranges, and injects iterator-construction failure through `SyncPoint`.

External-file ingestion tests open a DB and CF, ingest the generated external table, then read through normal DB iterators. The ingestion test also replaces overlapping key ranges with `snapshot_consistency=false` and an atomic replace descriptor, then verifies non-atomic ingestion of overlapping generated-sequence external data is rejected as `NotSupported`.

User-defined-index basic tests configure a block-based table with a UDI factory and a custom flush policy that starts a new data block every three keys. They write 100 ordered keys with `SstFileWriter`, use `FindMetaBlockInFile` to verify the UDI meta block exists, read all keys with the native index, then set `ReadOptions::table_index_factory` to exercise seek, upper-bound iteration, injected index seek/next errors, and a count-limited multiscan path. The same basic path runs with and without partitioned indexes and with bytewise and reverse-bytewise comparators.

Additional UDI tests cover specific flows: invalid parallel compression with UDI returns `InvalidArgument`; merge-only SSTs remain readable; DB flush sends put/merge/delete/single-delete operations through the UDI builder; value-type mapping is verified by inspecting the factory's shared log; compaction with a held snapshot keeps multiple versions/tombstones and logs them to UDI builders; external-file ingestion with UDI preserves seek/upper-bound behavior; empty-range multiscan behavior is validated across gaps; ingest failure is controlled by `fail_if_no_udi_on_open`; an empty UDI from a dummy file is tolerated during multi-file ingestion; and dynamic `ObjectLibrary` registration lets a UDI factory be loaded from a config string.

`MultiScanFailureTest` exercises validation and error paths: max prefetch size returning `Incomplete`, empty `MultiScanArgs`, missing seek key after `Prepare`, out-of-order seek, start equal to limit, overlapping ranges, upper-bound mismatch, too many seek calls after prepared ranges are exhausted, missing upper bound when a limit exists, and no-limit scans without an upper bound.

Range-delete and cross-file tests create ingested data files, delete-range-only files, and replacement data files, then verify prepared range scans still return the expected count and current values. `QueryCrossTwoFiles` forces SST partitioning through `NewSstPartitionerFixedPrefixFactory(4)` so scanned ranges cross files before and after a range-delete plus new-data ingestion sequence.

The stress fixture randomly generates level-like batches of `DataRange` entries, writes equivalent logical data through two mechanisms, and compares range-scan results. The regular CF receives point puts/deletes and flushes once. The ingest CF receives generated SST files one level at a time, optionally compacts through a partitioner, and optionally uses UDI-backed multiscan. `ValidateQueryResult` runs 200 random range-query iterations and compares regular CF iteration, ingest CF iteration, and ingest CF prepared multiscan results.

## State And Persistence Behavior

- Dummy external tables persist a deliberately simple binary format to filesystem paths. Although only used in tests, the format includes enough state to exercise property-block offsets, table properties, and external table size/checksum accounting.
- External table ingestion flows persist SST/external-table files, open DB directories, create column families, ingest files into RocksDB metadata, and validate that normal DB reads see the ingested contents.
- `ExternalFileChecksumTest` compares `ExternalSstFileInfo::file_checksum` from `SstFileWriter::Finish()` against an independently computed CRC32c over the written file bytes.
- `ReaderFileReadsUpdateStatistics` asserts that opening an external table through `SstFileReader` updates `NON_LAST_LEVEL_READ_COUNT`, `NON_LAST_LEVEL_READ_BYTES`, `SST_READ_MICROS`, and file IO listener counters when the factory reads through `ExternalTableOptions::fs`.
- Pinned external reads preserve zero-copy value lifetime through `PinnableSlice` cleanup callbacks. Tests reset `PinnableSlice` objects and verify cleanup counts, guarding pin ownership and cleanup propagation through DB `Get` and `MultiGet`.
- User-defined index metadata is persisted as a block-based table meta block named with `kUserDefinedIndexPrefix + "test_index"`. Tests locate that block with `FindMetaBlockInFile` and later read it through UDI readers.
- DB flush, compaction, snapshot, and ingest tests intentionally create real LSM state. Snapshot-held compaction is expected to keep multiple versions and tombstones; range-delete tests expect upper-level deletes and replacement files to mask older persisted data correctly.
- Stress tests maintain two logical representations of the same randomized history: persisted ingest files in one CF and normal writes in another CF. The comparison is the persistence oracle for ingestion, range-delete masking, compaction, and multiscan behavior.

## Dependencies And Integration Points

- Test framework dependencies include GoogleTest macros, `DBTestBase`, `BlockBasedTableTestBase`, `SyncPoint`, `Random`, and per-thread test path helpers.
- Table extension APIs include `ExternalTableFactory`, `ExternalTableBuilder`, `ExternalTableReader`, `ExternalTableIterator`, `ExternalTableOptions`, `ExternalTableBuilderOptions`, `NewExternalTableFactory`, `UserDefinedIndexFactory`, `UserDefinedIndexBuilder`, `UserDefinedIndexReader`, `UserDefinedIndexIterator`, `IndexEntryContext`, `ScanOptions`, `IterateResult`, and `IterBoundCheck`.
- SST and DB APIs under test include `SstFileWriter`, `SstFileReader`, `DB::Open`, `CreateColumnFamily`, `DestroyColumnFamilyHandle`, `IngestExternalFile`, `IngestExternalFiles`, `NewIterator`, `NewMultiScan`, `MultiGet`, `Flush`, `CompactRange`, `GetSnapshot`, and `ReleaseSnapshot`.
- Block-table integration uses `BlockBasedTableOptions`, `NewBlockBasedTableFactory`, `FlushBlockPolicyFactory`, `FlushBlockPolicy`, partitioned indexes, filter partitioning flags, `fail_if_no_udi_on_open`, and `FindMetaBlockInFile`.
- Comparator integration is explicit: the UDI tests are parameterized over `BytewiseComparator()` and `ReverseBytewiseComparator()`, and helper code reverses generated keys/ranges/count expectations when using the reverse comparator.
- Filesystem/statistics integration uses `Env`, `FileSystem`, `FSWritableFile`, `FSRandomAccessFile`, `RandomAccessFileReader`, `FileOptions`, `IOOptions`, `ReadFileToString`, `WriteStringToFile`, `EventListener::OnFileReadFinish`, DB statistics tickers, and histograms.
- Merge/entity/range-delete integration uses `MergeOperators::CreateStringAppendOperator()`, `DB::Merge`, `SstFileWriter::Merge`, `DB::PutEntity`, `WideColumns`, `Delete`, `SingleDelete`, and `DeleteRange`.
- Config integration uses `ObjectLibrary::Default()->AddFactory<UserDefinedIndexFactory>()` and `GetColumnFamilyOptionsFromString()` to resolve a UDI factory by name from a block-based-table option string.

## Risks And Edge Cases

- `DummyExternalTableFile` serializes native structs by appending raw bytes for `uint32_t` sizes and item headers. It is suitable for same-process tests but not portable across endian/layout changes; corruption checks are intentionally minimal.
- `DummyExternalTableIterator::Seek()` uses exact `std::map::find()` rather than lower-bound semantics, so it is a test double for exact-key and prepared-range paths, not a general external table iterator.
- The external iterator's prepared-scan state is order-sensitive: each `Seek` must match the next prepared range start, and `Next` uses the last prepared range's limit. This intentionally exposes multiscan protocol violations but can hide bugs that depend on more flexible seek behavior.
- `DummyExternalTableReader::GetTableProperties()` returns fixed small table properties rather than those deserialized from the file, while the builder tracks real properties. Tests depending on exact table properties should account for this simplified reader behavior.
- The pinned reader stores pinned data separately from deserialized file contents, so the test validates pin propagation rather than file/data consistency.
- UDI builder assertions assume five-byte keys unless `skip_key_size_check_` is enabled. DB flush and variable-key tests must set that flag or avoid variable key lengths.
- The UDI index stores both per-key dummy entries and block-level entries for fixed-key tests. The reader must skip entries with zero key counts to find real block entries; regressions in that filtering can change seek counts.
- UDI multiscan relies on the optional `property_bag["count"]`; malformed or missing count properties would throw or produce undefined test behavior because the test iterator calls `std::stoi` without defensive validation.
- Error counters in `TestUserDefinedIndexFactory` are copied into iterators at construction. Changing counters after iterator construction does not affect that iterator, which is useful for deterministic tests but differs from shared mutable fault injection.
- Reverse comparator support requires many manual reversals of generated keys, ranges, and expected counts. Future additions can easily become bytewise-only by accident.
- Randomized stress tests seed from current time and print the seed, so failures may be non-reproducible unless the printed seed and generated ranges are captured.
- `PartialDeleteRange` skips the UDI-enabled path due to a known limitation: a count-limited UDI prepare can under-prepare lower-level keys when upper-level range deletes mask the first prepared keys.
- Several tests skip encrypted environments because direct file checksums, external file reads, or test file formats assume non-encrypted byte visibility.

## Test Signals

- Cache-role option validation should return `NotSupported` for unsupported data-block charge toggling and `InvalidArgument` when enabling charged filter construction while `no_block_cache` is true; status text should mention the relevant role and reason.
- External table basic tests should pass point iteration, `Get`, `MultiGet`, not-found handling, property-block optional support, and strict key ordering in the builder.
- `SstReaderTest` and `PinnedGetTest` should show external tables integrate with `SstFileReader`, DB `Get`, DB `MultiGet`, and the simple `GetContext::SaveValue` path rather than the parsed-internal-key overload.
- File-read statistics tests should observe increased RocksDB read tickers/histograms and `EventListener` counters after reader open through the factory's filesystem read path.
- Ingestion tests should prove external tables can be bulk-loaded into a DB CF, overwritten with atomic replacement, and rejected when overlapping ingestion would require unsupported nonzero sequence-number assignment.
- UDI basic tests should find the `test_index` meta block, read all 100 keys without UDI, produce expected key counts with UDI seek and upper bounds, surface injected seek/next errors, and prepare count-limited multiscan ranges.
- UDI operation-type tests should verify `Put -> kValue`, `Merge -> kMerge`, `Delete -> kDelete`, `SingleDelete -> kDelete`, and wide-column entity writes map to `kOther`.
- Snapshot compaction tests should show UDI builders receive multiple versions/tombstones while current and snapshot DB iterators expose the correct user-visible views.
- Ingest failure tests should enforce `fail_if_no_udi_on_open=true` and then allow ingestion after toggling the option off through `SetOptions`.
- Multiscan failure tests provide strong guardrails around prepared-range protocol, upper-bound requirements, range ordering, overlap detection, max-prefetch behavior, and no-limit scans.
- Range-delete, cross-file, and randomized stress tests are broad integration signals for prepared scans over ingested files, delete-range masking, compaction with optional SST partitioning, atomic replace bulk load, and reverse-comparator behavior.
