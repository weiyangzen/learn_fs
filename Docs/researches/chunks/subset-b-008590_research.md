# sources/storage-engines/rocksdb/db/db_etc2_test.cc lines 7091-8259

## Scope

This chunk is the tail of `db_etc2_test.cc`. It covers DB recovery and reopen behavior for epoch numbers, database directory renaming, SST unique-ID verification, best-efforts recovery, latest-sequence lookup through memtable history, ZSTD checksum corruption detection, non-blocking block-cache-tier reads, file checksum extraction from the current MANIFEST, concurrent point/range tombstone conversion under readers, `fast_sst_open` metadata persistence, and the GoogleTest `main()` entry point.

The code is test-focused but it documents contracts for production RocksDB components around MANIFEST metadata, table open verification, recovery filtering, read-path cache-only behavior, filesystem open metadata, and concurrent delete/iteration semantics.

## Purpose

The tests in this range validate persistence-sensitive and integration-heavy behavior:

- file epoch numbers and next epoch counters must survive reopen across levels, column families, and `allow_ingest_behind` mode;
- a RocksDB directory renamed at the filesystem layer must reopen correctly when `dbname_` is updated and `create_if_missing=false`;
- SST unique IDs in table properties and MANIFEST edits must be verified when requested, skipped for backward-compatible missing IDs, and treated as recoverable by best-efforts recovery;
- `DBImpl::GetLatestSequenceForKey()` must return sequence and timestamp metadata from maintained memtable history without reading SST files, including for blob-backed wide-column entities under a newer merge;
- ZSTD decompression checksum failures must surface as corruption both on read and under paranoid flush-time file checks;
- `kBlockCacheTier` reads must not open files on a table-cache miss;
- `experimental::GetFileChecksumsFromCurrentManifest()` must reconstruct live-file checksum mappings from MANIFEST records after a column family is dropped;
- conversion of contiguous point tombstones into range tombstones must behave correctly with concurrent writers/readers and both concurrent and non-concurrent memtable writes;
- `Options::fast_sst_open` must collect, persist, pass, ignore, and suppress filesystem open metadata according to option state across flush, compaction, ingestion, reopen, and disable-after-persist cases.

## Important APIs, Types, And Helpers

- `DBTest2` is the shared fixture from the beginning of the file, derived from `DBTestBase`, providing helpers such as `DestroyAndReopen`, `Reopen`, `TryReopen`, `CreateAndReopenWithCF`, `ReopenWithColumnFamilies`, `Put`, `Delete`, `Flush`, `MoveFilesToLevel`, `GetLevelFileMetadatas`, `FilesPerLevel`, `Get`, and `GetBlobFileNumbers`.
- `Options` fields exercised here include `allow_ingest_behind`, `num_levels`, `compaction_style`, `disable_auto_compactions`, `level0_file_num_compaction_trigger`, `verify_sst_unique_id_in_manifest`, `best_efforts_recovery`, `max_write_buffer_size_to_maintain`, `comparator`, `enable_blob_files`, `enable_blob_direct_write`, `min_blob_size`, `blob_direct_write_partitions`, `merge_operator`, `compression`, `compression_opts.checksum`, `paranoid_file_checks`, `file_checksum_gen_factory`, `allow_concurrent_memtable_write`, `min_tombstones_for_range_conversion`, `write_buffer_size`, and `fast_sst_open`.
- `VersionSet`, `ColumnFamilySet`, `ColumnFamilyData`, and `FileMetaData` are used directly in `RecoverEpochNumber` to inspect persisted per-file `epoch_number`, `num_entries`, largest keys, and per-CF `GetNextEpochNumber()`.
- `SyncPoint` callbacks tamper with internal table/manifest behavior in deterministic ways: `PropertyBlockBuilder::AddTableProperty:Start` mutates `TableProperties::db_session_id`; `VersionEdit::EncodeTo:UniqueId` clears the manifest unique ID; `BlockBasedTableBuilder::WriteBlock:TamperWithCompressedData` corrupts compressed bytes.
- `UniqueId64x2`, `TableProperties`, `DBImpl::GenerateDbSessionId`, and `Options::verify_sst_unique_id_in_manifest` form the unique-ID verification test surface.
- `ColumnFamilyHandleImpl`, `SuperVersion`, `SequenceNumber`, and `DBImpl::GetLatestSequenceForKey()` provide an internal latest-sequence lookup path that can operate in `cache_only` mode and optionally return a user timestamp.
- `test::BytewiseComparatorWithU64TsWrapper`, `PutFixed64`, and reversed fixed-width keys create timestamped keys whose timestamp bytes are checked after lookup.
- Blob and wide-column APIs include `DB::PutEntity`, `WideColumns`, `kDefaultWideColumnName`, `enable_blob_direct_write`, and the string-append merge operator from `MergeOperators`.
- `ReadOptions::read_tier = kBlockCacheTier`, `TEST_table_cache()->SetCapacity(0)`, and ticker `NO_FILE_OPENS` validate no-file-open behavior on cache-only reads.
- `GetFileChecksumGenCrc32cFactory`, `LiveFileMetaData`, `NewFileChecksumList`, `ReadOnlyFileSystem`, and `experimental::GetFileChecksumsFromCurrentManifest()` validate checksum persistence in MANIFEST metadata.
- `DBTestConcurrentRangeTombstoneConversions` is a parameterized fixture over `(allow_concurrent_memtable_write, min_tombstones_for_range_conversion)`.
- `FastOpenTestRandomAccessFile` wraps `FSRandomAccessFile` and overrides `GetFileOpenMetadata()` to return deterministic metadata while incrementing an atomic retrieval counter.
- `FastOpenTestFS` wraps `FileSystem` and intercepts `NewRandomAccessFile()` to count and record when `FileOptions::file_metadata` is passed to the filesystem, then wraps opened files in `FastOpenTestRandomAccessFile`.
- `CompositeEnvWrapper` installs `FastOpenTestFS` beneath an `Env` so DB opens, table opens, flushes, compactions, and ingestions exercise the metadata path without replacing unrelated environment behavior.
- `SstFileWriter` and `IngestExternalFileOptions` exercise fast-open metadata collection for externally produced SST ingestion.
- The final `main()` installs RocksDB's stack trace handler, initializes GoogleTest, registers custom objects, and runs the test binary.

## Test Coverage And Control Flow

### Epoch numbers and directory reopen

`RecoverEpochNumber` loops over `allow_ingest_behind` true and false. It creates a leveled DB with auto compactions disabled and a second column family. In the default CF it flushes `"key1"`, moves the file to L1, then flushes `"key2"` to L0. In `cf1` it flushes `"cf1_key1"` to L0. The test inspects `FileMetaData` before and after `ReopenWithColumnFamilies({"default", "cf1"}, options)`.

The assertions prove three related contracts:

- file-level epoch metadata is assigned in flush order and survives MANIFEST recovery;
- files in different levels and column families retain their own epoch values and key metadata;
- each `ColumnFamilyData::GetNextEpochNumber()` recovers to the next expected value.

When `allow_ingest_behind` is true, the expected epoch values are offset by `kReservedEpochNumberForFileIngestedBehind`, so the same persistence checks also protect the reserved epoch namespace used by ingest-behind.

`RenameDirectory` writes a key, closes the DB, renames the database directory with `env_->RenameFile(dbname_, new_dbname)`, updates `dbname_`, reopens with `create_if_missing=false`, and confirms the old value is readable. This is a small filesystem/DB-name integration test for reopen after an out-of-band directory rename.

### SST unique-ID verification and recovery

`SstUniqueIdVerifyBackwardCompatible` first opens with `verify_sst_unique_id_in_manifest=false` and creates three flushed SSTs. Sync-point counters confirm table open skipped unique-ID verification. The DB then reopens with verification enabled, and the same files pass verification. The test next clears the unique ID being encoded into a later manifest edit, creates enough files to trigger compaction, waits for compaction, and reopens with verification still enabled. Reopen succeeds but the missing-ID file follows the backward-compatible skip path, proving old manifests without unique IDs are accepted.

`SstUniqueIdVerify` uses a sync point to change each SST's `TableProperties::db_session_id`, which changes the table-derived unique ID after the manifest has recorded its expected ID. Reopen with `verify_sst_unique_id_in_manifest=true` must return corruption. Reopen with verification disabled must still work. The same corruption expectation is repeated for a compaction-generated SST after the L0 trigger fires.

`SstUniqueIdVerifyMultiCFs` creates three column families. It writes good SSTs to the default CF and CF `"two"` while verification is disabled, then enables a bad-session-ID sync point only for SSTs flushed in CF `"one"`. `TryReopenWithColumnFamilies({"default", "one", "two"}, options)` with verification enabled must return corruption, showing a mismatch in any opened CF can fail DB recovery.

`BestEffortsRecoveryWithSstUniqueIdVerification` repeats the mismatch scenario for each possible bad L0 file position out of seven L0 files. Normal reopen with verification returns corruption. Reopen with `best_efforts_recovery=true` succeeds and exposes only the latest complete state before the corrupted file. It then reopens with regular recovery again and expects the same visible state, writes a clean flush, reopens, and verifies the DB can continue from the recovered state. The loop protects ordering semantics: when the first file is bad no keys remain, otherwise the expected value version is `"v" + (k - 1)`.

### Latest sequence lookup and memtable history

`GetLatestSeqAndTsForKey` configures a user timestamp comparator and maintained memtable history via `max_write_buffer_size_to_maintain`. It writes 100 timestamped keys, flushes, obtains the default CF's `SuperVersion`, and calls `dbfull()->GetLatestSequenceForKey()` for each key with `cache_only=true` and `lower_bound_seq=0`. Each call must return OK, set `found_record_for_key`, leave `is_blob_index=false`, and return the expected fixed64 timestamp. The final assertion that `GET_HIT_L0` remains zero proves the operation did not read SST files.

`GetLatestSequenceForKeyFromHistoryWithBlobBackedWideColumnEntity` targets a narrower history path. It enables blob files, direct blob writes, a blob size threshold, one blob-direct-write partition, and the string-append merge operator. It writes a wide-column entity whose default column is large enough to become blob-backed, then merges a suffix. After flush it confirms a blob file exists and there are no immutable memtables. A cache-only `GetLatestSequenceForKey()` must still find the key in maintained history, return the merge's latest sequence number, and report that the result is not merely a blob index. This guards the interaction between flushed memtable history, wide-column entity base values, direct blob write, and merge operands.

### Compression checksum, cache-tier reads, and manifest checksums

`ZSTDChecksum` is compiled only when `ZSTD` is available. It enables ZSTD compression and ZSTD frame checksums, writes one large value, and corrupts the last byte of compressed block output through a sync point. A subsequent `Get()` must return corruption. With `paranoid_file_checks=true`, the same corruption is expected during `Flush()`, proving both read-time and flush-time verification paths can catch decompression checksum failures.

`TableCacheMissDuringReadFromBlockCacheTier` sets the table cache capacity to zero after reopening with statistics enabled, writes and flushes `"foo"`, records `NO_FILE_OPENS`, and performs a `Get()` with `ReadOptions::read_tier = kBlockCacheTier`. The expected status is `Incomplete`, and `NO_FILE_OPENS` must not change. This documents that block-cache-tier reads are strictly non-blocking and do not open SSTs just to satisfy a table-cache miss.

`GetFileChecksumsFromCurrentManifest_CRC32` opens a separate DB with CRC32C file checksum generation enabled and a high L0 trigger to avoid automatic compaction. It flushes four default-CF files, creates a temporary CF, flushes one file in it, then drops that CF. Before close it captures `GetLiveFilesMetaData()` as the source of truth. After close it uses a `ReadOnlyFileSystem` and `experimental::GetFileChecksumsFromCurrentManifest()` to populate a `FileChecksumList` from the current MANIFEST. The test asserts the list size matches live files and that each live file number maps to the exact checksum and checksum function name from `LiveFileMetaData`. Dropped-column-family manifest edits must be interpreted correctly so deleted-CF files are not reported as live.

### Concurrent tombstone conversion

`DBTestConcurrentRangeTombstoneConversions` parameterizes `MixedWritesWithConcurrentReaders` over both `allow_concurrent_memtable_write` values and `min_tombstones_for_range_conversion` values `0` and `4`. The test seeds 100 keys, flushes them, then runs:

- a writer that puts and `SingleDelete`s keys 0-9;
- a deleter that point-deletes contiguous keys 20-29;
- a range deleter that deletes ranges 40-50, 60-70, and 80-90.

After waiting for the point-deleter to finish, it starts eight iterator threads: four forward scans over keys 20-30 and four reverse scans over the same area. These scans intentionally hit the contiguous point tombstones while other write activity may still be present. After joining all threads, if the conversion threshold is enabled, the test asserts that the `READ_PATH_RANGE_TOMBSTONES_INSERTED` plus `READ_PATH_RANGE_TOMBSTONES_DISCARDED` tickers increased.

The final forward and reverse full-DB iterations compare exact expected keys: 10-19, 30-39, 50-59, 70-79, and 90-99 survive; keys 0-9 are covered by put plus `SingleDelete`; keys 20-29 are point-deleted; the three range-deleted intervals are hidden. This provides both concurrency safety and semantic correctness signals for read-path range tombstone conversion.

### Fast SST open metadata

`FastOpenTestRandomAccessFile` and `FastOpenTestFS` create the test harness for `Options::fast_sst_open`. The random-access wrapper's `GetFileOpenMetadata()` returns `"fast_open_metadata:" + fname` and increments a retrieval counter. The filesystem wrapper records when `NewRandomAccessFile()` receives non-null `FileOptions::file_metadata`, stores the last metadata string, and always wraps successfully opened files so future metadata retrieval calls are observable.

`FastSstOpenDefaultFSReturnsNotSupported` creates a small `.sst` file directly through the default filesystem, opens it as a random-access file, and checks the default `GetFileOpenMetadata()` response is `NotSupported` with empty metadata. This establishes the default-filesystem behavior the fast-open path must tolerate.

`FastSstOpenFlushAndReopen` and `FastSstOpenCompactionAndReopen` enable `fast_sst_open` with the default filesystem. They flush, optionally compact via `level0_file_num_compaction_trigger=2`, close, reopen, and read data. These tests do not require metadata support; they verify the feature does not break normal flush/compaction/reopen when the filesystem cannot provide metadata.

`FastSstOpenWithTestFS` opens a DB on `FastOpenTestFS` with `fast_sst_open=true`, flushes one SST, and expects exactly one metadata retrieval during flush and no metadata passed during that initial open. After closing and reopening, reads succeed and exactly one SST open receives persisted metadata beginning with the expected prefix.

`FastSstOpenCompactionWithTestFS` writes two flush files with compaction trigger 2, waits for compaction, and expects at least two metadata retrievals from the flush SSTs. The compaction output may or may not add another retrieval depending on table-cache state, so the assertion is lower-bounded. On reopen, at least one SST open must receive metadata and both keys must read correctly.

`FastSstOpenDisabledNoMetadata` uses the same test filesystem but keeps `fast_sst_open=false`. Flush must retrieve no metadata, reopen must pass no metadata, and the key remains readable.

`FastSstOpenToggleOption` writes the first SST with `fast_sst_open=false`, then reopens with it enabled and writes a second SST while compaction is prevented by a high L0 trigger. Only the second file should retrieve metadata, and on the final reopen only one of the two SST opens should receive metadata. This captures per-file metadata persistence rather than a global option-only behavior.

`FastSstOpenIngestion` writes an external SST using `SstFileWriter`, ingests it with `move_files=false`, and expects the ingestion path to retrieve metadata for the ingested file. After reopen, reads of ingested keys must succeed and at least one SST open must receive metadata.

`FastSstOpenDisableAfterMetadataPersisted` writes and flushes a metadata-bearing SST with `fast_sst_open=true`, closes, then reopens with `fast_sst_open=false`. Even though metadata exists in the MANIFEST, the filesystem must receive no `file_metadata` on open. This is a critical stale-metadata protection case, especially for metadata representing temporary credentials or filesystem open tokens.

## State And Persistence Behavior

This chunk repeatedly verifies that on-disk metadata and DB state survive close/reopen boundaries:

- epoch numbers are stored with file metadata in the MANIFEST and restored into `FileMetaData` and each CF's next epoch counter;
- database content remains readable after an out-of-band directory rename when `dbname_` points to the renamed path;
- SST unique IDs recorded in the MANIFEST are compared to table-derived unique IDs on reopen when verification is enabled;
- missing unique IDs are tolerated as an old-manifest compatibility case, while mismatched IDs become corruption unless best-efforts recovery excludes the affected files;
- best-efforts recovery modifies the recovered visible state by truncating past corrupted file metadata, after which regular reopen and new writes proceed from that state;
- `max_write_buffer_size_to_maintain` keeps enough flushed memtable history for cache-only latest-sequence lookups even after `Flush()`;
- blob-backed wide-column values and merge sequence numbers interact with the history state without requiring immutable memtables to remain;
- file checksums and checksum function names are reconstructed from the current MANIFEST and matched against live-file metadata after DB close;
- fast SST open metadata is persisted per file and later passed to `NewRandomAccessFile()` only when `fast_sst_open` is enabled for that open.

The tests also deliberately confirm cases where state must not be persisted or used: disabled `fast_sst_open` collects no metadata, previously persisted fast-open metadata is ignored after disabling the option, and block-cache-tier reads do not open files or populate table-cache state on a miss.

## Dependencies And Integration Points

The chunk integrates with several RocksDB subsystems:

- MANIFEST/version metadata through `VersionEdit`, `VersionSet`, `ColumnFamilyData`, `FileMetaData`, SST unique IDs, file checksums, dropped-CF edits, and fast-open metadata fields;
- table building/opening through `PropertyBlockBuilder`, `BlockBasedTable::Open`, table property unique IDs, compression checksums, and table-cache behavior;
- DB recovery paths through normal reopen, `TryReopen`, multi-CF reopen, best-efforts recovery, and corruption handling;
- memtable history and read paths through `SuperVersion`, `GetLatestSequenceForKey`, user timestamps, blob direct write, wide columns, and merge operators;
- blob storage through direct blob write, blob file creation, blob-backed wide-column entities, and external SST ingestion;
- filesystem abstractions through `FileSystemWrapper`, `FSRandomAccessFileWrapper`, `FileOptions::file_metadata`, `ReadOnlyFileSystem`, `CompositeEnvWrapper`, and default filesystem unsupported metadata behavior;
- concurrency through `port::Thread`, concurrent memtable write configuration, point tombstone conversion, range tombstone insertion/discarding tickers, and forward/reverse iterators;
- test infrastructure through GoogleTest parameterization, `SyncPoint` callbacks, statistics/tickers, `Random`, and `DBTestBase` lifecycle helpers.

These tests are sensitive integration points for changes in manifest encoding/decoding, table property generation, recovery filtering, table-reader open options, cache-only read behavior, direct blob write semantics, and read-path deletion acceleration.

## Risks And Edge Cases

- The unique-ID tampering tests rely on sync-point names and internal table property encoding points. Refactoring table-property generation or manifest serialization can break the test harness even if the production contract is preserved.
- Backward-compatible missing unique IDs are intentionally skipped, not treated as corruption. Tightening verification must account for old manifests and the `SkippedVerifyUniqueId` path.
- Best-efforts recovery with unique-ID mismatch drops newer files. This is correct for the tested recovery contract but is data-loss-prone by design; changes should be explicit about which files survive and why.
- `GetLatestSequenceForKey()` with `cache_only=true` depends on maintained memtable history. Changes to history retention, flush cleanup, or timestamp comparator handling can accidentally force SST reads or lose timestamp metadata.
- The blob-backed wide-column history test is narrow but important: it checks a V2 entity base value under a newer merge after flush, with no immutable memtables. A simpler value-only implementation could pass other sequence tests while failing this case.
- ZSTD checksum coverage exists only in builds with `ZSTD` defined. Non-ZSTD builds do not exercise that corruption path from this file.
- The block-cache-tier read test forces table cache capacity to zero; production behavior with partial table-cache pressure may involve more paths, but this test asserts the strict no-file-open behavior for a miss.
- Manifest checksum extraction uses a read-only filesystem and compares only live files after a dropped CF. It does not validate deleted-file checksum retention or all historical edits.
- The concurrent tombstone test is schedule-dependent. It creates real reader/writer overlap but does not force all possible interleavings; the ticker assertion for range tombstone conversion is only required when the threshold is non-zero.
- Fast SST open tests use opaque metadata strings derived from filenames. They validate plumbing and option gating, not the semantics of a real filesystem token, credential, or platform-specific fast-open handle.
- Some fast-open assertions are lower-bounded because compaction output metadata retrieval depends on table-cache state. This avoids flakiness but also means the exact compaction-output retrieval count is not specified.
- Disabling `fast_sst_open` after metadata is persisted must override manifest metadata at table open time; forgetting this can make stale credentials or invalid open tokens break future DB opens.

## Test Signals

Primary signals are `ASSERT_OK`, `EXPECT_OK`, status class checks (`IsCorruption`, `IsIncomplete`, `IsNotSupported`), exact value reads, exact `FilesPerLevel()` strings, exact file metadata fields, per-CF next epoch values, sync-point counters, statistics tickers, live-file checksum comparisons, and fast-open metadata counters.

For future RocksDB changes, failures in this chunk usually indicate one of these classes of regression:

- MANIFEST metadata is not encoded, decoded, or filtered consistently across reopen;
- SST unique-ID verification incorrectly rejects old files, misses corrupted files, or fails to interact with best-efforts recovery;
- cache-only read paths accidentally perform disk/table-cache opens;
- memtable-history lookup no longer preserves timestamps, latest sequence numbers, wide-column base values, or blob-backed entity state;
- read-path range tombstone conversion is unsafe under concurrent reads/writes or changes iteration visibility;
- fast SST open metadata is collected at the wrong time, persisted for the wrong files, passed when disabled, or lost across flush/compaction/ingestion/reopen.
