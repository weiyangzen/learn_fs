# sources/storage-engines/rocksdb/table/table_test.cc lines 1-6732

## Scope

This chunk covers the first 6,732 lines of RocksDB's `table_test.cc`. It starts with shared test scaffolding for blocks, SST table readers/builders, memtables, and DB-backed iterators, then covers table-property and unique-id tests, block-based table format and cache tests, plain-table checks, generic approximate-offset tests, randomized harness tests, footer/format-version validation, prefix-filter behavior, block alignment and file checksum regression tests, tail-prefetch helpers, data-block hash index tests, iterator upper-bound behavior, large-entry handling, compression-dictionary cache charging, and the start of `CacheUsageOptionsOverridesTest::SanitizeAndValidateOptions`. Tests for external tables and user-defined indexes begin after this chunk and are out of scope.

## Purpose

- Provide broad regression coverage for RocksDB table abstractions independent of a full DB where possible: `Block`, `BlockBasedTable`, `PlainTable`, `MemTable`, and real `DB` iterators are exercised through a common harness.
- Verify that table builders persist correct data, metadata, checksums, unique IDs, block handles, footers, filter/index blocks, file checksums, and table properties.
- Validate iterator semantics across forward scan, backward scan, seek, `SeekForPrev`, total-order seek, prefix seek, upper-bound checks, async IO, lazy value preparation, and large values.
- Exercise block-cache integration, including data/index/filter cache hits and misses, cache key reuse across table reopen, cache allocator ownership, cache tracing records, cache charging policies, and readahead trimming.
- Lock down compatibility-sensitive schemas such as SST unique IDs, built-in checksum outputs, footer encodings, unsupported legacy format rejection, Crc32c file checksum values, and format-version option sanitization.
- Cover option validation for block-based tables, especially block alignment, compression constraints, cache usage options, block restart intervals, invalid block size deviations, and unsupported format versions.

## Important APIs, Types, And Functions

- `Constructor` is the common fixture interface. It stores user-provided key/value pairs in comparator order, then delegates `FinishImpl()` to concrete implementations and exposes `NewIterator()`, `db()`, arena-mode hints, and deletion semantics.
- `KeyConvertingIterator` wraps an `InternalIterator` that yields internal keys and exposes only user keys. It encodes seek targets as `ParsedInternalKey(target, kMaxSequenceNumber, kTypeValue)` and converts returned keys with `ParseInternalKey()`.
- `BlockConstructor`, `TableConstructor`, `MemTableConstructor`, and `DBConstructor` adapt the same harness to raw data blocks, table files in a `test::StringSink`, in-memory memtables, and a real DB opened under `test::PerThreadDBPath("table_testdb")`.
- `TableConstructor::FinishImpl()` builds a table through `moptions.table_factory->NewTableBuilder()`, optionally encodes user keys into internal-key format, flushes the `WritableFileWriter`, and reopens the result with `NewTableReader()`. It is the central helper for most tests in this chunk.
- `TableConstructor::Reopen()` constructs a `RandomAccessFileReader` over the in-memory SST contents and calls `TableFactory::NewTableReader()` with `TableReaderOptions`, including prefix extractor, compression manager, block cache tracer, file number, unique ID, level, and optional external-file largest sequence number.
- `HarnessTest` parameterizes the shared iterator tests over block-based tables, plain tables with prefix modes, raw blocks, memtables, and DBs. `GenerateArgList()` combines table type, bytewise or reverse comparator, restart interval, supported compression, compression parallelism, format versions, and mmap reads.
- `ReverseKeyComparator`, `Reverse()`, and `Increment()` allow the harness to test non-lexicographic ordering and key successor behavior.
- `BlockBasedTableTest` is parameterized by footer/table format version, super-block alignment size, alignment overhead ratio, and `separate_key_value_in_data_block`. `GetBlockBasedTableOptions()` injects those parameters into each test.
- `FileChecksumTestHelper` wraps table-builder creation, random KV generation, table flushing, file checksum generator attachment, and independent checksum recalculation over `RandomAccessFileReader`.
- `BlockCacheTraceWriter`, `BlockCacheTraceReader`, `BlockCacheTracer`, `BlockCacheTraceRecord`, and `VerifyBlockAccessTrace()` validate block cache access records for `Get`, `MultiGet`, iterator, and approximate-size paths.
- `BlockCachePropertiesSnapshot` captures statistics tickers for cache hits/misses and cache bytes read/write, making cache behavior assertions less dependent on global counter deltas.
- `HitMissCountingCache` is a `CacheWrapper` that counts synchronous and async cache lookup hits/misses and cross-checks those counts against expected trace records.
- `CustomFlushBlockPolicy` and `FlushBlockEveryKeyPolicyFactory` force specific data-block boundaries for index and cache-laziness tests.
- `NoBufferAlignmenttWritableFile` and `NoBufferAlignmenttWritableFileFileSystem` force writable-file buffer alignment to one byte, making block-align checksum regressions reproducible with small writer buffers.

## Control Flow

Most table tests follow the same flow: populate a constructor with sorted or randomized keys, create `Options`, `ImmutableOptions`, `MutableCFOptions`, and table-specific options, call `Constructor::Finish()`, then compare iterator/table-reader behavior against the saved `KVMap`. For table-backed tests, finishing writes a complete table into memory, flushes it, and immediately reopens it as a `TableReader`; tests can then reset and reopen readers with modified options while preserving the same SST bytes.

The parameterized harness calls `TestForwardScan()`, `TestBackwardScan()` where supported, and `TestRandomAccess()`. Random access repeatedly selects `Next`, `SeekToFirst`, `Seek`, `Prev`, or `SeekToLast`, updates an STL-map model iterator, and compares the model string with the real iterator. Plain-table variants disable reverse iteration and restrict random seeks to prefix-compatible cases.

Block-based property tests build small tables and read `TableProperties` from the reader. They compare number of entries, raw key/value size, data size, data block count, comparator/merge/prefix/collector/filter names, compression name encodings, and range deletion iterators. Unique-id tests derive public and internal table IDs from `db_id`, `db_session_id`, and file number, then verify stable expected values, conversion round trips, zero-ID handling, and failure when required fields are missing.

Index tests construct multi-block files with controlled prefixes and verify binary-search, interpolation-search, hash-search, two-level, and binary-with-first-key indexes. They seek existing and non-existing prefixes, exercise `SeekForPrev()`, and check partitioned-index reseek optimizations. `BinaryIndexWithFirstKey2` and `BinaryIndexWithFirstKeyGlobalSeqno` also verify lazy value preparation: index entries can return a valid key without immediately reading the data block, but `PrepareValue()` must fetch the correct value and sequence number.

Cache and readahead tests warm specific blocks, perform seek/scan operations, then inspect cache membership, cache statistics, trace files, `FilePrefetchBuffer` offsets/sizes, `READAHEAD_TRIMMED`, and async `TryAgain` behavior. Tracing tests start a block cache trace before constructing the table, perform user reads twice to distinguish misses from hits, then read the trace file back and compare block type, caller, cache-hit state, `get_id`, referenced key, data-size estimates, and snapshot flags.

Footer and format tests build synthetic footers through `FooterBuilder`, decode them with `Footer::DecodeFrom()`, and validate block handles, checksum type, magic number, format version, context checksum behavior, and plain-table zero block-trailer size. Separate tests construct fake legacy footers to ensure old magic numbers and format versions 0/1 are rejected unless unsupported-format testing is explicitly allowed.

Block-alignment tests use real table builders over `test::StringSink`, confirm aligned data blocks are exactly 4096 bytes in table properties, reopen the same file with `block_align=false`, and scan all 10,000 keys. The DB-level checksum regressions open a real DB with `block_align=true`, Crc32c file checksums, and in one case a tiny writer buffer with no alignment requirement; `VerifyFileChecksums()` must succeed after flush.

The chunk ends while `CacheUsageOptionsOverridesTest::SanitizeAndValidateOptions` is checking that sanitized `BlockBasedTableOptions::cache_usage_options.options_overrides` contains one entry for every `CacheEntryRole` and defaults to `cache_usage_options.options` when no per-role override was supplied. The unsupported-role validation branch continues after line 6732 and is outside this chunk.

## State And Persistence Behavior

This test file mostly writes ephemeral state to in-memory `test::StringSink`/`StringSource` objects, but the bytes are complete table files with real footers, metadata blocks, data blocks, checksums, index/filter blocks, and table properties. The same in-memory SST bytes are reopened under different options in tests for block cache reuse, prefix extractor mismatch, filter policy changes, block alignment, and cache behavior.

Some tests create real DB directories under `test::PerThreadDBPath()`. `DBConstructor` destroys and recreates `table_testdb`; `DBHarnessTest` inserts enough keys to force flush/compaction files; `PrefixAndWholeKeyTest`, block-align checksum tests, bad-option tests, and cache-usage option tests open real DB instances to verify table options as DB open/flush/compaction would consume them.

Persistent schema invariants are explicitly tested. Unique ID generation from DB ID, session ID, and original file number must remain stable; built-in checksums must continue returning the encoded 32-bit values asserted here; footer encodings must remain decodable across supported block-based and plain-table format versions; legacy formats must remain rejected; and Crc32c file checksum output for fixed data must not drift.

Cache state is treated as observable system state. Tests verify when index/filter blocks are preloaded rather than cached, when cache entries survive table reader reopen because table file unique IDs are stable, when changing block cache instances isolates cached data, when custom cache allocators deallocate everything, and when temporary compression-dictionary-building buffers reserve and release pinned cache usage.

## Dependencies And Integration Points

- Core table APIs: `rocksdb/table.h`, `TableBuilder`, `TableReader`, `BlockBasedTableFactory`, `PlainTableFactory`, `Block`, `BlockBuilder`, `BlockFetcher`, `Footer`, `FooterBuilder`, `ReadTableProperties()`, and meta-block helpers.
- DB and internal key APIs: `DB`, `WriteBatch`, `MemTable`, `InternalKey`, `ParsedInternalKey`, `InternalKeyComparator`, `test::PlainInternalKeyComparator`, `RangeTombstone`, and `GetContext`.
- Cache and tracing APIs: `Cache`, `LRUCacheOptions`, `CacheWrapper`, `BlockCacheTraceWriter/Reader`, `BlockCacheTracer`, `BlockBasedTableIterator`, `FilePrefetchBuffer`, `TailPrefetchStats`, and block-cache/perf-context ticker names.
- Compression and checksum APIs: supported compression enumeration helpers, compression managers, built-in checksum computation, `FileChecksumGenerator`, `FileChecksumGenCrc32cFactory`, and table file checksum fields.
- Option objects: `Options`, `ImmutableOptions`, `MutableCFOptions`, `BlockBasedTableOptions`, `PlainTableOptions`, `TableBuilderOptions`, `TableReaderOptions`, cache usage options, compression options, and DB/CF option validation.
- Test infrastructure: GoogleTest parameterization, `test::StringSink`, `test::StringSource`, `test::RandomKey`, `Random`, `DBTestBase`, `SyncPoint` infrastructure includes, and `test::PerThreadDBPath()`.

## Risks And Edge Cases

- Many tests rely on exact byte-level sizes, offsets, checksum strings, ticker counts, or trace-record sequences. Legitimate format or accounting changes can break tests and must be accompanied by careful schema/migration reasoning.
- The harness mixes user keys and internal keys. The `convert_to_internal_key_` flag and `KeyConvertingIterator` wrappers are essential; using the wrong comparator or key format can make a test pass over a different behavior than intended.
- Cache tests can be sensitive to cache capacity, metadata charging, block size, format version, filter policy type, and whether index/filter blocks are pinned, preloaded, or inserted into cache.
- Async IO tests depend on `Status::TryAgain()` sequencing and on the composite environment/file-system path exposing async lookup behavior in the expected way.
- The first-key index tests depend on lazy value preparation semantics. Changes to iterator prefetching or value pinning can alter data-block hit/miss counts without changing visible keys.
- Block alignment interacts with compression, file checksum generation, write-buffer flushing, filesystem-required buffer alignment, and padded bytes. The regressions here specifically guard against checksumming padded bytes inconsistently.
- Tests for unsupported format versions intentionally toggle `TEST_AllowUnsupportedFormatVersion()`. If that global escape hatch leaks, format-version tests can produce misleading results.
- `BlockReadCountTest` contains a branch for `bloom_filter_type == 0` even though the loop starts at 1; that branch documents older block-based-filter behavior but is unreachable in the current loop.
- The line-range boundary cuts `CacheUsageOptionsOverridesTest::SanitizeAndValidateOptions` in the middle, so this chunk can only document the completed sanitization portion and the start of unsupported cache-role validation.

## Test Signals

- `ParameterizedHarnessTest` provides the broadest iterator signal: empty, single, multiple, special-key, and randomized key sets across block-based, plain, raw block, memtable, and DB implementations.
- `DBHarnessTest.RandomizedLongDB` confirms real DB ingestion creates SST files and that DB-backed iteration remains model-equivalent after enough writes to force file creation.
- Table-property tests validate metadata correctness for raw sizes, compression names, collector names, filter names, unique IDs, range deletion blocks, data block counts, index size growth, and plain-table properties.
- Cache/tracing tests validate `Get`, `MultiGet`, iterator, approximate-offset, prefetch, async scan, index/filter/data block caching, cache-byte tickers, trace-file contents, and custom cache hit/miss accounting.
- Format and checksum tests lock down built-in checksum outputs, zero-input checksum behavior, file checksum integration, footer encoding/decoding, legacy format rejection, and unsupported format-version handling.
- Alignment and block-option tests verify block alignment constraints, properties block restart points, meta-block seekability, properties-block ordering, compression ratio threshold behavior, and invalid option normalization.
- Prefix and filter tests cover whole-key plus prefix filters, prefix-extractor mismatch fallback, total-order seek over hash indexes, noop prefix extraction, skipped prefix bloom filters, data-block hash indexes, and upper-bound iterator invalidation.
- Compression-dictionary cache-charge tests assert pinned cache usage is added and released depending on cache role overrides, buffer-limit overflow, and strict cache-capacity overflow.
