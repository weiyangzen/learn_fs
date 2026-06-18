# subset-b-008588 Research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_dynamic_level_test.cc -->
# sources/storage-engines/rocksdb/db/db_dynamic_level_test.cc

## Purpose

`db_dynamic_level_test.cc` is a RocksDB GoogleTest suite for leveled compaction with `level_compaction_dynamic_level_bytes=true`. It validates how RocksDB computes and changes the base level as data volume grows, how dynamic-level layout interacts with automatic and manual compaction, and whether the DB remains readable while the base level migrates.

The file is not production code, but it acts as a behavioral specification for dynamic LSM level sizing. It checks level metadata, compaction output levels, background error counters, and key visibility after flushes, compactions, reopen, and a disabled migration scenario from static to dynamic level sizing.

## Important APIs, Types, and Helpers

- `DBTestDynamicLevel : public DBTestBase` is the test fixture. It uses the test DB name `db_dynamic_level_test` and enables fsync behavior through `env_do_fsync=true`.
- `Options` fields under test include `level_compaction_dynamic_level_bytes`, `max_bytes_for_level_base`, `max_bytes_for_level_multiplier`, `num_levels`, `target_file_size_base`, `write_buffer_size`, `max_write_buffer_number`, L0 compaction/slowdown/stop triggers, `max_background_compactions`, `max_compaction_bytes`, `compression_per_level`, `disable_auto_compactions`, `db_host_id`, and `table_factory`.
- Public and test DB APIs used include `DestroyAndReopen`, `Reopen`, `Put`, `Delete`, `Get`, `Flush`, `CompactRange`, `SetOptions`, `TEST_WaitForCompact`, `GetIntProperty`, `GetProperty`, `GetColumnFamilyMetaData`, and `NumTableFilesAtLevel`.
- Internal synchronization uses `ROCKSDB_NAMESPACE::SyncPoint`, with dependencies around `CompactionJob::Run():Start`, `CompactionJob::Run():End`, `FlushJob::WriteLevel0Table`, and test-defined sync labels.
- Metadata APIs include `ColumnFamilyMetaData` and its per-level file lists, plus properties such as `rocksdb.base-level`, `rocksdb.background-errors`, and `rocksdb.num-files-at-levelN`.
- Helper utilities include `Random`, `RandomShuffle`, `PutFixed32`, `DecodeFixed32`, compression capability checks (`Snappy_Supported`, `LZ4_Supported`), `NewBlockBasedTableFactory`, `BlockBasedTableOptions`, and `port::Thread`.

## Control Flow and State Behavior

`DynamicLevelMaxBytesBase` runs a broad stress scenario across ordered and shuffled key insertion, and across one and three background compaction threads. It configures five levels, small memtables and target files, dynamic level bytes, and per-level compression. The test writes three key bands, deletes one tenth of the middle band, and sleeps briefly between batches to let background work run. It then asserts no background errors, verifies data before and after reopen, performs a full manual compact range, and confirms all files end up in the last level while the data/deletion contract still holds.

`DynamicLevelMaxBytesBase2` targets base-level transitions with controlled data volumes. It disables auto compaction, writes roughly 28 KiB, re-enables compaction, flushes, waits, and confirms the base level starts at L4. A second roughly 28 KiB batch moves the base to L3 while L1 and L2 remain empty. Another roughly 40 KiB leaves the base at L3. A much larger roughly 650 KiB load uses a sync point so compaction starts before the last flush, preventing a jump directly to L1 and asserting the base becomes L2. The final phase runs a manual `CompactRange` in another thread while more writes and a flush occur, then verifies the base advances to L1.

`DynamicLevelMaxBytesCompactRange` verifies manual compaction behavior when the current base level is not L1. It compacts an empty DB, writes data, flushes and waits for background compaction, ensures L0 is non-empty if automatic work drained it, and expects the base level to be L3 with L1/L2 empty. A `SyncPoint` callback observes `CompactionPicker::CompactRange:Return` and records output levels. A full compact range should emit compactions to both L3 and L4, drain L0 and L3, and keep `rocksdb.base-level` at L3.

`DynamicLevelMaxBytesBaseInc` checks that increasing the base level through dynamic sizing does not schedule non-trivial background compactions unnecessarily. A sync callback counts `DBImpl::BackgroundCompaction:NonTrivial`. After inserting 3000 keys with a random prefix and a fixed suffix encoding the key index, the test flushes, waits for compaction, asserts the non-trivial count is zero, and reads every key back to verify value integrity.

`DISABLED_MigrateToDynamicLevelMaxBytesBase` documents a migration scenario from static level bytes to dynamic level bytes. It first writes and deletes keys under static sizing, reopens with dynamic sizing and auto compaction disabled, verifies data, runs a manual compact range to the last level in a background thread while repeatedly reading, re-enables auto compaction, writes more data, waits for compaction, and asserts L1/L2 are empty. Because the test is disabled, it is guidance and regression documentation rather than a normal test signal.

## State and Persistence Behavior

The suite observes LSM placement rather than durable byte-for-byte file contents. Persistent state under test includes flushed SST files, level assignment metadata, deletion tombstones, compaction outputs, base-level property state, and DB contents across close/reopen.

Dynamic level bytes make the base level depend on accumulated data size. Early data lands in the last level, then as total bytes grow the base level moves upward from L4 to L3, L2, and finally L1. The tests assert that intermediate levels below the base can remain empty and that compaction output chooses the computed base and deeper levels rather than assuming L1 is always the starting non-L0 level.

Manual full compaction is expected to preserve live keys, honor deleted keys, and eventually place data in the deepest level when compacting all ranges. Concurrent manual compaction and flush/automatic compaction must not corrupt data or leave base-level accounting stale.

Reopen checks in `DynamicLevelMaxBytesBase` verify dynamic level metadata and generated table files persist cleanly through DB close/open. The disabled migration test further documents that existing static-level DB state should remain readable when reopened with dynamic-level sizing and then compacted to the last level.

## Dependencies and Integration Points

The file integrates the DB test framework in `db/db_test_util.h` with compaction scheduling, `VersionStorageInfo` base-level computation exposed through properties, `CompactionPicker`, `CompactionJob`, `FlushJob`, block-based table sizing, compression libraries, in-memory or default environments, and background thread pools.

Important integration points are:

- RocksDB public option plumbing for dynamic level bytes and runtime `SetOptions`.
- Background compaction and manual `CompactRange` interaction, including concurrent compaction and flush.
- Property exposure for `rocksdb.base-level`, per-level file counts, and background error counts.
- Table construction and compression effects on file size estimates, especially when `db_host_id` is cleared to avoid perturbing file-size calculation in one test.
- SyncPoint labels inside compaction picker/job and flush job internals.

## Risks and Edge Cases

The tests are sensitive to file-size estimates. Small write buffers, target file sizes, block sizes, compression settings, and random value lengths are chosen to drive specific byte thresholds. Changes in table metadata overhead, compression ratio, block layout, host ID properties, or compaction expansion can shift the expected base level.

The suite relies on internal sync-point names and timing. Refactors that rename `CompactionJob`, `FlushJob`, or `CompactionPicker` sync labels can deadlock or silently reduce coverage unless the tests are updated.

Concurrency coverage is intentionally narrow but high risk. The final phase of `DynamicLevelMaxBytesBase2` verifies manual compaction and flush can overlap while base level changes to L1. Bugs here could produce stale level metadata, missed compaction, write stalls, or data loss.

Compression-gated coverage can be skipped when Snappy or LZ4 is unavailable, so release/test environments without those libraries lose part of the signal.

The disabled migration test contains useful behavior but does not protect normal CI unless explicitly enabled. Migration regressions from static to dynamic level sizing may not be caught by default.

## Test Signals

Strong signals include successful `db_dynamic_level_test` runs with `rocksdb.background-errors == 0`, expected `rocksdb.base-level` transitions from L4 to L3 to L2 to L1, empty L1/L2 properties when the base is L3, expected compaction output levels during compact range, and all point reads/deletions matching expected visibility before and after reopen.

Metadata checks such as `ColumnFamilyMetaData` level file counts and `rocksdb.num-files-at-levelN` properties provide direct evidence that dynamic-level placement is correct. SyncPoint callbacks verify specific internal paths, including non-trivial compaction avoidance and compact-range output-level selection.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_dynamic_level_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_encryption_test.cc -->
# sources/storage-engines/rocksdb/db/db_encryption_test.cc

## Purpose

`db_encryption_test.cc` is a compact RocksDB GoogleTest suite for encrypted environment integration. It verifies that user keys and values are not visible in raw files when the test fixture is running with an encrypted environment, that empty encrypted/plain files can be read safely, and that RocksDB can operate when encrypted random-access files do not implement `GetFileSize()`.

The file is a DB-level integration test rather than encryption algorithm code. Its main purpose is to validate the environment/file-system wrapper contract used by encrypted RocksDB builds.

## Important APIs, Types, and Helpers

- `DBEncryptionTest : public DBTestBase` uses the test DB name `db_encryption_test` with `env_do_fsync=true`.
- `GetNonEncryptedEnv()` returns the underlying target environment when `encrypted_env_` is present by casting it to `CompositeEnvWrapper` and calling `env_target()`. Otherwise it returns the fixture `env_`.
- Tests use DB helpers `Put`, `Close`, `CurrentOptions`, `dbname_`, `env_`, and `encrypted_env_` from `DBTestBase`.
- File APIs include `Env::GetChildren`, `Env::NewSequentialFile`, `Env::GetFileSize`, `SequentialFile::Read`, `EnvOptions`, `WritableFile`, `FileSystem::NewRandomAccessFile`, `FSRandomAccessFile::GetFileSize`, `FileOptions`, and `CreateFile`.
- Status expectations use `ASSERT_OK`, `ASSERT_TRUE(status.IsNotSupported())`, `ASSERT_EQ`, and `ASSERT_GE`.
- The test includes `rocksdb/perf_context.h` and `test_util/sync_point.h`, although the visible tests do not use performance counters or sync points directly.

## Control Flow and State Behavior

`CheckEncrypted` writes two recognizable key/value pairs, closes the DB, enumerates the DB directory, and opens every file except `LOCK` through the non-encrypted target environment. It reads each file's raw bytes and searches for the inserted keys, full values, and one value substring. If the fixture has `encrypted_env_`, no hits are allowed; otherwise at least four hits are expected. This creates a dual-mode test: encrypted builds prove plaintext is hidden in storage files, while non-encrypted builds prove the scan would have detected the markers.

`ReadEmptyFile` creates an empty file through the non-encrypted/default environment, reopens it as a sequential file, and reads 16 bytes into a scratch buffer. The expected behavior is `Status::OK` with an empty `Slice`. The comment documents the regression target: reading from an empty file must not trigger an assertion in the file wrapper.

`NotSupportedGetFileSize` only runs when `encrypted_env_` exists. It obtains the encrypted file system, creates an empty file, opens it as an `FSRandomAccessFile`, calls `GetFileSize()`, and asserts the method returns `NotSupported`. The test documents that RocksDB DB operation should not depend on encrypted `FSRandomAccessFile::GetFileSize()` support because table footer reading can fall back to the file system-level `GetFileSize()`.

## State and Persistence Behavior

Persistent state under test is the DB directory contents after a small write workload and the raw bytes stored in generated files. The key security property is that plaintext keys and values written through the DB are not recoverable by opening the physical files through the underlying non-encrypted environment.

The test deliberately closes the DB before scanning files, ensuring memtable/WAL/table data have reached stable file state visible to `Env::GetChildren`. It skips `LOCK` because that file is not expected to contain user records and may be special to the environment.

For empty files, the state contract is simpler: a zero-byte file must read as an empty slice without assertion, both through regular sequential access and through encrypted filesystem random-access setup. The `NotSupportedGetFileSize` case also verifies a negative capability contract: an encrypted random-access file may reject direct file-size queries while the surrounding DB/table code remains expected to use a fallback path.

## Dependencies and Integration Points

The suite integrates `DBTestBase` encrypted-environment fixture support with RocksDB's `Env` and newer `FileSystem` APIs. It depends on `CompositeEnvWrapper` to expose the target non-encrypted environment for raw-file inspection and on encrypted file wrappers to hide plaintext while still preserving DB readability.

Important integration points are:

- Encrypted environment setup in the broader test harness through `encrypted_env_`.
- Raw file enumeration and sequential reads through the underlying environment.
- `FSRandomAccessFile` capability handling, especially `GetFileSize()` returning `NotSupported`.
- Table footer reading behavior outside this file, where `ReadFooterFromFile()` is expected to fall back to file-system-level size queries.

## Risks and Edge Cases

`CheckEncrypted` is a coarse plaintext scan, not a cryptographic verification. It catches obvious unencrypted leakage of the inserted strings, but it does not prove encryption strength, nonce/key correctness, or absence of all metadata leakage.

The raw read uses `scratch.reserve(fileSize)` and then passes `scratch.data()` as the destination buffer. In modern C++, writing into reserved but not resized string storage is risky because the string size remains zero and writable capacity through `data()` is only well-defined for existing characters. The test then relies on the returned `Slice` for length, but the scratch buffer lifetime and writable range still make this a maintenance hazard if standard/library behavior changes.

The test assumes plaintext markers should appear in non-encrypted mode. Changes to file format, compression, WAL flushing, table encoding, or write path could reduce visible hits and make the non-encrypted sanity branch flaky even though the DB is correct.

The encrypted `GetFileSize()` negative capability is intentional. Production code must continue to tolerate `NotSupported` from `FSRandomAccessFile::GetFileSize()`; adding unconditional direct size calls in table readers would regress encrypted environments.

## Test Signals

Strong signals include zero plaintext marker hits when `encrypted_env_` is active, at least four marker hits without encryption, successful sequential read of an empty file returning an empty slice, and `FSRandomAccessFile::GetFileSize()` returning `NotSupported` for encrypted random-access files.

The file is most useful when run in both encrypted and non-encrypted fixture configurations. The non-encrypted branch validates the detector, while the encrypted branch validates that the environment wrapper actually transforms stored file contents.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/db_encryption_test.cc -->
