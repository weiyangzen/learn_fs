# Research Report: subset-b-008636

This grouped report covers the RocksDB env, example, and file utility sources assigned to `subset-b-008636`. Each file section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/mock_env.cc -->
# sources/storage-engines/rocksdb/env/mock_env.cc

## Purpose
`mock_env.cc` implements RocksDB's in-memory mock environment: a `MockFileSystem` backed by `MemFile` objects, a `MockEnv` wrapper, and an emulated clock configuration path. It is a test-oriented filesystem/environment that lets RocksDB code exercise file creation, reads, writes, renames, locking, logging, corruption of unsynced bytes, and fake sleeping without touching a real filesystem.

## Important APIs and control flow
The core private type is `MemFile`, which owns file bytes, size, modification time, fsynced byte count, a random generator for corruption, lock-file state, and a manual reference count. `MockSequentialFile`, `MockRandomAccessFile`, `MockRandomRWFile`, and `MockWritableFile` adapt `MemFile` to RocksDB `FS*File` interfaces. `TestMemLogger` writes formatted log lines to a mock writable file.

`MockFileSystem` normalizes paths through `NormalizeMockPath()`, keeps `file_map_` under `mutex_`, and implements the main `FileSystem` operations. Reads and opens check for existence, lock-file misuse, and direct-I/O support. `NewWritableFile()` replaces an existing file, `ReopenWritableFile()` appends to or creates a file, `ReuseWritableFile()` renames then opens, and `LinkFile()` shares a `MemFile` with an extra reference. `RenameFileInternal()` recursively moves children. `CorruptBuffer()` mutates bytes after `fsynced_bytes_`.

## State, persistence, and integration
All file data is process memory; persistence is modeled only by `fsynced_bytes_` so corruption can spare synced prefixes. Modification time comes from the configured `SystemClock`, normally an `EmulatedSystemClock` created by `MockEnv::Create()`. `PrepareOptions()` can adopt the environment clock when the filesystem was built with `SystemClock::Default()`. The file registers option metadata for `supports_direct_io`, while the emulated clock registers `time_elapse_only_sleep` and `mock_sleep`.

`MockEnv` is a `CompositeEnvWrapper` combining a base `Env`, the mock filesystem, and the clock. `NewMemEnv()` preserves older in-memory env behavior by returning `MockEnv::Create(base_env)`.

## Risks and test signals
This mock is intentionally partial. `IsDirectory()` is unsupported, directories are represented as `MemFile`s, and `DeleteDir()` uses relative child names from `GetChildrenInternal()` with `DeleteFileInternal()`, which is a risk for nested directory cleanup semantics. `MockWritableFile::use_direct_io()` currently returns `false && use_direct_io_`, so direct-write reporting is suppressed even when options request it. `NewWritableFile()` creates and inserts the file before returning `NotSupported` for direct writes, leaving observable state on failure. The manual refcounting requires every map insertion/open/link to pair with `Unref()`. Test signals include `mock_env_test`, DB tests using `NewMemEnv`, direct-I/O option tests, file lock behavior, corruption-after-sync behavior, and sync point injection around reads and size checks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/mock_env.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/mock_env.h -->
# sources/storage-engines/rocksdb/env/mock_env.h

## Purpose
`mock_env.h` declares the public test-facing in-memory filesystem and environment types used by RocksDB tests. It exposes `MockFileSystem`, which implements the `FileSystem` interface, and `MockEnv`, which wraps a base `Env` with that filesystem and an emulated/system clock.

## Important APIs and types
`MockFileSystem` overrides file creation/opening APIs for sequential, random-access, random-RW, writable, reopened writable, reused writable, directory, logger, lock, and sync operations. It also exposes filesystem metadata operations such as `FileExists`, `GetChildren`, `DeleteFile`, `Truncate`, `CreateDir`, `DeleteDir`, `GetFileSize`, `GetFileModificationTime`, `RenameFile`, `LinkFile`, `GetTestDirectory`, and `GetAbsolutePath`. `CorruptBuffer()` is a test hook for corrupting unsynced in-memory bytes. `PrepareOptions()` lets config parsing rebind the clock.

Private state is a mutex-protected `std::map<std::string, MemFile*>`, a `SystemClock` shared pointer/raw pointer pair, and a `supports_direct_io_` flag. Helper methods perform path normalization, internal rename/delete, and child discovery.

`MockEnv` derives from `CompositeEnvWrapper`, provides two static `Create()` factories, reports class name `MockEnv`, and forwards `CorruptBuffer()` to the underlying `MockFileSystem`.

## State, dependencies, and integration
The header depends on RocksDB's `FileSystem`, `Env`, `Status`, `SystemClock`, `CompositeEnvWrapper`, and port mutex abstractions. It is not a general production filesystem contract; it is a test utility that supplies enough `FileSystem` behavior for DB tests and examples of environment composition.

## Risks and test signals
The API surface is broad while the implementation is partial. Callers that assume all `FileSystem` methods are production-complete can hit `NotSupported`, especially for directory classification. Because the header exposes `MockFileSystem` directly, tests may depend on implementation quirks such as normalized absolute paths, in-memory lock files, and direct-I/O toggles. Test signals are successful compilation of env tests, option parsing for registered mock options, and behavioral tests around file corruption, fake sleeping, locks, children, renames, and unsupported calls.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/mock_env.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/mock_env_test.cc -->
# sources/storage-engines/rocksdb/env/mock_env_test.cc

## Purpose
`mock_env_test.cc` is the focused unit test for `MockEnv`. It validates two mock-environment behaviors: unsynced data corruption and fake sleep advancing emulated time.

## Important APIs and control flow
`MockEnvTest` owns a `MockEnv*` created from `Env::Default()` and deletes it in the fixture destructor. The `Corrupt` test writes a synced prefix and an unsynced suffix to `/dir/f`. It reads the prefix through `RandomAccessFile`, fsyncs the file, calls `MockEnv::CorruptBuffer()`, and verifies the synced prefix is unchanged. It then appends a second string, verifies it is readable, corrupts again, and asserts that the unsynced suffix differs.

The `FakeSleeping` test captures `GetCurrentTime()`, calls `SleepForMicroseconds(3 * 1000 * 1000)`, and checks that the apparent wall time advanced by 3 or 4 seconds.

## State, persistence, and integration
The tests rely on `MockEnv`'s in-memory state, `WritableFile` fsync forwarding to `MemFile::Fsync()`, `RandomAccessFile` reads into scratch memory, and `EmulatedSystemClock` behavior from `MockEnv::Create()`. They integrate with RocksDB's `testharness`, stack trace handler, and standard `ASSERT_OK`/`ASSERT_EQ` macros.

## Risks and test signals
The corruption test only verifies that corruption changes a suffix, not the exact corruption range, and it depends on a random mutation being different from the original bytes. The fake-sleep test tolerates one extra second for runtime delay but can still be sensitive if the emulated clock or real clock backing changes. Passing tests signal that `fsynced_bytes_` boundaries, `CorruptBuffer()`, file read/write wrappers, and fake sleep behavior remain compatible with legacy in-memory-env expectations.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/mock_env_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/unique_id_gen.cc -->
# sources/storage-engines/rocksdb/env/unique_id_gen.cc

## Purpose
`unique_id_gen.cc` implements RocksDB's internal 128-bit unique identifier generation. It combines several entropy or uniqueness sources, hashes them into raw IDs, and provides reusable generator classes for semi-structured and less predictable IDs.

## Important APIs and control flow
`GenerateRawUniqueIdImpl()` fills an `Entropy` struct and passes its bytes to `Hash2x64()`. Entropy tracks include `EntropyTrackRandomDevice` using `std::random_device`, `EntropyTrackEnvDetails` using hostname, process ID, thread ID, current time, and nanoseconds, and `EntropyTrackPortUuid` using `port::GenerateRfcUuid()`. A RocksDB version identifier is included so schema changes can avoid accidental same-byte interpretations. Debug builds expose `TEST_GenerateRawUniqueId()` to disable individual entropy tracks.

`SemiStructuredUniqueIdGen::Reset()` captures a process ID and raw base ID. `GenerateNext()` returns a stable upper half plus `base_lower_ ^ counter_.fetch_add(1)` while still in the same process; after fork/process-ID change it falls back to raw generation.

`UnpredictableUniqueIdGen::Reset()` fills a 256-bit atomic pool from repeated raw IDs. `GenerateNext()` adds timing entropy from `_rdtsc()` when SSE4.2 is available or `SystemClock::NowNanos()` otherwise. `GenerateNextWithEntropy()` hashes a relaxed atomic counter and entropy pool with `BijectiveHash2x64()`, returns the result, and feeds part of it back into the pool.

## State, dependencies, and integration
The file depends on `Env`, `port` process/UUID APIs, RocksDB version macros, hash utilities, atomics, and platform-specific timestamp support. It is used for DB session IDs and fallback generation behind `Env::GenerateUniqueId`/DB `IDENTITY` workflows.

## Risks and test signals
The comments explicitly say the output has not been validated for cryptography. Entropy quality varies by platform, `std::random_device` implementation, system clock resolution, hostname availability, and UUID support. `SemiStructuredUniqueIdGen::Reset()` is not thread safe, and fork detection trades guaranteed continuity for raw fallback. `UnpredictableUniqueIdGen` intentionally allows benign races on entropy-pool writes. Test signals include collision/challenge tests using `TEST_GenerateRawUniqueId`, fork/process tests for `SemiStructuredUniqueIdGen`, multithread sanitizer runs for the atomic pool, and platform builds with and without SSE4.2.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/unique_id_gen.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/unique_id_gen.h -->
# sources/storage-engines/rocksdb/env/unique_id_gen.h

## Purpose
`unique_id_gen.h` declares internal APIs for extracting environment entropy and generating unique identifiers. It distinguishes these utilities from algorithmic pseudorandomness in `random.h` and notes possible future migration to public `Env` APIs.

## Important APIs and types
`GenerateRawUniqueId(uint64_t* a, uint64_t* b, bool exclude_port_uuid=false)` returns a probabilistically globally unique 128-bit value split across two 64-bit words. Debug builds declare `TEST_GenerateRawUniqueId()` with switches for excluding UUID, environment details, and random-device sources.

`SemiStructuredUniqueIdGen` stores `base_upper_`, `base_lower_`, an atomic counter, and a saved process ID. It provides `Reset()`, `GenerateNext(uint64_t*, uint64_t*)`, a templated integral `GenerateNext<T>()`, and `GetBaseUpper()`. It is optimized for many IDs per generator by combining a random base with a guaranteed local counter sequence.

`UnpredictableUniqueIdGen` is cache-line aligned, owns a four-word atomic entropy pool plus counter, and exposes `Reset()`, `GenerateNext()`, and `GenerateNextWithEntropy()`. Debug builds include a zero-initialized constructor and counter accessor.

## State, dependencies, and integration
The header depends on port cache-line alignment, atomics, type traits, and the RocksDB namespace header. It documents expected integration with DB session IDs and DB identity generation fallbacks.

## Risks and test signals
The contract is probabilistic and explicitly non-cryptographic. `Reset()` on both generators is not thread safe, while generation is intended to be thread safe. Smaller templated outputs intentionally cycle through all low-word possibilities only within the semi-structured generator's counter assumptions. Tests should verify API compile behavior, process/fork fallback, no duplicate IDs under multithreaded generation, debug challenge modes, and correct alignment/atomic sanitizer behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/unique_id_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/CMakeLists.txt -->
# sources/storage-engines/rocksdb/examples/CMakeLists.txt

## Purpose
This CMake file declares build targets for the RocksDB example programs. It is a thin integration layer that compiles individual example source files and links them against the configured `${ROCKSDB_LIB}` target.

## Important APIs and control flow
The file calls `add_executable()` and `target_link_libraries()` for `simple_example`, `column_families_example`, `compact_files_example`, `c_simple_example`, `optimistic_transaction_example`, `transaction_example`, `compaction_filter_example`, `options_file_example`, and `multi_processes_example`. `multi_processes_example` is marked `EXCLUDE_FROM_ALL`, so it is available as a target but not built by default.

## State, dependencies, and integration
It depends on the parent CMake configuration defining `${ROCKSDB_LIB}` and include/link settings for the RocksDB library. The file contains no persistent state and no install/export logic; it only wires local examples into the build graph.

## Risks and test signals
The target list does not include `rocksdb_backup_restore_example.cc`, although the Makefile does, which can cause coverage differences between CMake and Make builds. No per-target C/C++ standard, warning, or platform settings are specified here, so correctness depends on inherited parent configuration. Test signals are a successful CMake configure/build for all listed targets and explicit build of the excluded multi-process target when needed.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/Makefile -->
# sources/storage-engines/rocksdb/examples/Makefile

## Purpose
The examples `Makefile` builds RocksDB example binaries against the static library from the parent repository. It supports both C and C++ examples and delegates library construction to `make static_lib` one directory up.

## Important APIs and control flow
The file includes `../make_config.mk`, optionally adds jemalloc flags, disables RTTI unless `USE_RTTI=1`, and sets `CFLAGS += -Wstrict-prototypes`. The `all` target builds the main examples, including `rocksdb_backup_restore_example`. Each C++ binary rule invokes `$(CXX)` with `../librocksdb.a`, `-I../include`, optimization, `-std=c++20`, platform flags, and exec link flags. The C example compiles through `.c.o` and links the object with C++ linkage. `clean` removes generated binaries and `c_simple_example.o`; `librocksdb` runs the parent static library build.

## State, dependencies, and integration
The file is build-system state only. It depends on variables from `make_config.mk`, a compatible compiler, the static RocksDB archive, optional jemalloc libraries/includes, pthread/linker flags, and the example source filenames.

## Risks and test signals
The rules duplicate command lines, so new examples or option changes can drift. Hard-coding `-std=c++20` must stay compatible with the library and toolchain. CMake and Make target coverage differ. `clean` must stay in sync with binary names. Test signals are clean `make -C examples all`, individual target builds, jemalloc/non-jemalloc builds, `USE_RTTI` variants, and `make clean` removing only generated outputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/c_simple_example.c -->
# sources/storage-engines/rocksdb/examples/c_simple_example.c

## Purpose
`c_simple_example.c` demonstrates the RocksDB C API for opening a DB, tuning options, writing and reading a key, creating a backup, restoring from the latest backup, and cleaning up C API resources.

## Important APIs and control flow
The program chooses platform-specific DB and backup paths, creates `rocksdb_options_t`, detects CPU count with `GetSystemInfo()` on Windows or `sysconf(_SC_NPROCESSORS_ONLN)` elsewhere, calls `rocksdb_options_increase_parallelism()`, `rocksdb_options_optimize_level_style_compaction()`, and enables `create_if_missing`. It opens the DB with `rocksdb_open()`, opens a backup engine, writes `"key" -> "value"` with `rocksdb_put()`, reads it with `rocksdb_get()`, validates with `strcmp`, then creates a new backup.

After closing the DB it creates restore options, restores the latest backup into the original DB/WAL paths, reopens the DB, and destroys write/read/options/restore resources before closing the backup engine and DB.

## State, persistence, and integration
The example persists data under `/tmp/rocksdb_c_simple_example` or `C:\Windows\TEMP\...` and backup state under a sibling backup directory. It integrates solely through `rocksdb/c.h` and standard C allocation/error conventions, where returned values must be freed and API objects explicitly destroyed.

## Risks and test signals
The example uses `assert(!err)` and does not free error strings on failure, so it is demonstrative rather than robust. Paths are fixed and can collide with existing local data. It restores into the same live path after close, which is fine for a simple example but not a general backup policy. Test signals are successful compilation with the C API, a zero exit status, value equality before backup, and successful restore/open cycle.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/c_simple_example.c -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/column_families_example.cc -->
# sources/storage-engines/rocksdb/examples/column_families_example.cc

## Purpose
`column_families_example.cc` demonstrates creating, reopening, using, writing atomically across, dropping, and destroying handles for RocksDB column families.

## Important APIs and control flow
The example opens a DB with `Options::create_if_missing`, creates column family `"new_cf"`, destroys its handle, and closes the DB. It then reopens with a `std::vector<ColumnFamilyDescriptor>` containing both `kDefaultColumnFamilyName` and `"new_cf"`, receiving parallel `ColumnFamilyHandle*` entries. It writes and reads a key in the non-default family, then uses `WriteBatch` to put into both families and delete from the default family. Finally it drops the non-default family and destroys every handle before closing.

## State, persistence, and integration
The DB path is a platform-specific temp directory. Persistent state includes the created column family metadata and key/value data. The example integrates with `rocksdb/db.h`, `rocksdb/options.h`, `rocksdb/slice.h`, `DBOptions`, `ColumnFamilyOptions`, `ColumnFamilyDescriptor`, `ColumnFamilyHandle`, and `WriteBatch`.

## Risks and test signals
The fixed temp path can collide with previous runs, and the example does not call `DestroyDB`, so stale DB state can affect repeated execution. It uses raw handles and manual destruction, which is correct for the API but easy to leak in real code. It asserts only status success, not all resulting values. Test signals are successful open with explicit default CF, correct handle count/order, successful `Put`/`Get` on `handles[1]`, successful cross-CF `WriteBatch`, `DropColumnFamily`, and handle destruction without leaks or status failures.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/column_families_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/compact_files_example.cc -->
# sources/storage-engines/rocksdb/examples/compact_files_example.cc

## Purpose
`compact_files_example.cc` demonstrates how external code can implement custom compaction scheduling with RocksDB's `CompactFiles`, `EventListener`, and `GetColumnFamilyMetaData` APIs.

## Important APIs and control flow
The file defines an abstract `Compactor` listener interface with `PickCompaction()` and `ScheduleCompaction()`, a `CompactionTask` struct carrying DB, compactor, column-family name, input files, target level, options, and retry flag, and a `FullCompactor` that compacts all files to the highest level whenever possible.

`FullCompactor::OnFlushCompleted()` picks a task after flush and sets `retry_on_fail` when writes were stopped. `PickCompaction()` gathers all file names from `ColumnFamilyMetaData`, aborting if any file is already being compacted. `ScheduleCompaction()` queues `CompactFiles()` on `options_.env`. The static worker calls `DB::CompactFiles()` and optionally retries non-IO failures.

`main()` disables built-in background compaction, configures small buffers and L0 stall triggers, registers the listener, destroys and opens the DB, writes many keys to force flushes/compactions, verifies values, and closes.

## State, persistence, and integration
Persistent state is the temp DB's SST files and LSM levels. Integration points include flush event callbacks, `Env::Schedule`, compaction metadata, manual compaction options, and DB write/read APIs.

## Risks and test signals
`CompactionTask` stores `const std::string& column_family_name` from callback metadata, which is risky if the referenced string does not outlive scheduled background execution. Retry scheduling does not null-check `new_task` before `ScheduleCompaction(new_task)`. The compactor only calls `GetColumnFamilyMetaData(&cf_meta)` for the default family despite receiving a CF name. Test signals are absence of write stalls with background compaction disabled, correct value reads after many writes, successful scheduled `CompactFiles()` status output, and thread/lifetime sanitizer coverage for listener-scheduled tasks.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/compact_files_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/compaction_filter_example.cc -->
# sources/storage-engines/rocksdb/examples/compaction_filter_example.cc

## Purpose
`compaction_filter_example.cc` demonstrates compaction filtering of merge operands. It shows how a `CompactionFilter` can remove selected operands before a custom `MergeOperator` performs full merge.

## Important APIs and control flow
`MyMerge` implements `MergeOperator::FullMergeV2()`, copies an existing value if present, iterates operands, asserts no operand equals `"bad"`, and assigns the latest operand as the merged value. `MyFilter` implements `CompactionFilter::Filter()` for regular values and `FilterMergeOperand()` for merge operands. It increments counters and returns true for merge operands whose existing value is `"bad"`.

`main()` removes the temp DB directory with a platform-specific shell command, opens a DB with `options.merge_operator` and `options.compaction_filter`, writes several merge operands including `"bad"`, runs full `CompactRange()`, and asserts that regular-value filter count is zero while merge-operand filter count is six.

## State, persistence, and integration
The example persists a DB under `/tmp/rocksmergetest` or Windows temp. It integrates with RocksDB compaction filters, merge operators, merge writes, and manual compaction. Filter state is mutable counters on a stack-owned filter referenced by `Options`.

## Risks and test signals
Using `system("rm -rf ...")` or `rmdir` with string concatenation is acceptable for fixed example paths but unsafe as a general pattern. The filter pointer is non-owning, so the filter must outlive the DB. The example does not close/destroy through RAII beyond `unique_ptr<DB>`. Test signals are `CompactRange()` success, six merge operand filter invocations, zero regular value filter invocations, and no assertion in the merge operator seeing `"bad"`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/compaction_filter_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/multi_processes_example.cc -->
# sources/storage-engines/rocksdb/examples/multi_processes_example.cc

## Purpose
`multi_processes_example.cc` demonstrates RocksDB primary/secondary operation on Linux. One process creates and writes a primary DB, while another opens the same DB as a secondary, periodically catches up, serves reads, and verifies its view against a read-only primary view.

## Important APIs and control flow
The file is Linux-only; non-Linux builds print "Not implemented." It defines two column families, big-endian-sortable 64-bit key encoders/decoders, random value generation, and an atomic signal flag for secondary shutdown.

`CreateDB()` destroys and recreates the DB, then creates non-default column families. `RunPrimary()` repeatedly opens the DB with all column families, writes `kNumKeysPerFlush` keys per family, flushes each family, advances the key counter, and often closes/reopens to exercise manifest/log durability. `RunSecondary()` installs a SIGINT handler, creates a secondary directory, opens `DB::OpenAsSecondary()`, starts range-scan and point-lookup threads, loops on `TryCatchUpWithPrimary()`, reports observed max keys, and on shutdown verifies key/value equality against `DB::OpenForReadOnly()` on the primary path.

## State, persistence, and integration
The program uses fixed paths under `/tmp` for primary DB, secondary state, and a declared but unused primary-status file. It integrates with Linux directory/signal APIs, RocksDB secondary instances, flushing, iterators, read options with checksum verification and total-order seek, and column family descriptors.

## Risks and test signals
The secondary verification opens only default iterators despite defining multiple column families, so it does not fully verify every CF. The key decoder treats `char` values as signed in the non-little-endian branch, which is a portability risk, though the example is Linux-focused. Threads share one secondary `DB` for reads, which RocksDB supports, but iterator status is not checked after scans. Fixed paths can collide. Test signals are successful two-terminal execution, secondary catch-up progress, concurrent range/point reads without errors, SIGINT shutdown, and final verification success.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/multi_processes_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/optimistic_transaction_example.cc -->
# sources/storage-engines/rocksdb/examples/optimistic_transaction_example.cc

## Purpose
`optimistic_transaction_example.cc` demonstrates RocksDB's `OptimisticTransactionDB` API, including read-committed behavior, snapshot isolation, conflict detection at commit time, and multiple-snapshot transaction patterns.

## Important APIs and control flow
The example opens an `OptimisticTransactionDB`, obtains the base `DB`, and runs three scenarios. The first starts a transaction, writes `"abc"`, writes conflicting `"abc"` outside the transaction, and shows `Commit()` returning `Busy` while unrelated outside write `"xyz"` succeeds. The second starts a transaction with `set_snapshot=true`, writes `"abc"` outside the transaction, reads the old snapshot value via `GetForUpdate()`, and shows commit conflict. The third advances snapshots within one transaction, writes `"x"`, observes outside write `"y"`, calls `SetSnapshot()`, reads `"y"` for update, updates it, and commits successfully.

## State, persistence, and integration
The DB is under a temp path and is destroyed at the end. The example integrates with `OptimisticTransactionOptions`, `Transaction`, `Snapshot`, base DB reads/writes, and transaction `Get`, `GetForUpdate`, `Put`, `SetSnapshot`, and `Commit`.

## Risks and test signals
The example manually deletes transactions and `txn_db`, so early exits would leak. Snapshot pointers must be cleared from `ReadOptions` after transaction deletion, which the example does. Unlike pessimistic transactions, outside conflicting writes are not locked out and conflicts surface at commit. Test signals are expected `IsBusy()` statuses for conflicts, successful read of committed outside values, successful final commit after snapshot advancement, and clean `DestroyDB()`.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/optimistic_transaction_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/options_file_example.cc -->
# sources/storage-engines/rocksdb/examples/options_file_example.cc

## Purpose
`options_file_example.cc` demonstrates using `rocksdb/utilities/options_util.h` to load persisted RocksDB options from a DB directory and reopen without manually reconstructing all scalar options.

## Important APIs and control flow
The example builds `DBOptions` with `create_if_missing`, two `ColumnFamilyDescriptor`s, a shared LRU cache, `BlockBasedTableOptions`, and a dummy compaction filter. It installs table factories and a non-owning compaction-filter pointer, destroys and opens the DB, creates `"new_cf"` so options are persisted, closes, then calls `LoadLatestOptions()` into `loaded_db_opt` and `loaded_cf_descs`.

After loading, it validates `create_if_missing`, obtains loaded `BlockBasedTableOptions` from the table factory, checks `block_size`, manually restores `block_cache`, confirms the compaction filter pointer is null after load, manually restores it, and reopens with the loaded descriptors. Handles are deleted before close.

## State, persistence, and integration
The DB path holds RocksDB's generated options file. Integration points include `ConfigOptions`, `LoadLatestOptions`, block-based table factories, cache ownership through `shared_ptr`, and pointer-valued option repair before `DB::Open()`.

## Risks and test signals
The loop over loaded column families always uses `loaded_cf_descs[0]` when fetching table options, likely a copy/paste issue that does not validate all CFs. Pointer-valued options are not serialized as live objects and must be restored manually; forgetting this can silently alter behavior. The example uses raw CF handles and fixed temp paths. Test signals are successful load, scalar option equality, table factory option preservation, explicit restoration of cache/filter pointers, and successful reopen with loaded options.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/options_file_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/rocksdb_backup_restore_example.cc -->
# sources/storage-engines/rocksdb/examples/rocksdb_backup_restore_example.cc

## Purpose
`rocksdb_backup_restore_example.cc` demonstrates the C++ backup engine APIs for creating, listing, verifying, and restoring a RocksDB backup.

## Important APIs and control flow
The program opens a temp DB with optimized options and `create_if_missing`, writes `"key1"`, opens `BackupEngine` with `BackupEngineOptions("/tmp/rocksdb_example_backup")`, creates a new backup, retrieves backup metadata with `GetBackupInfo()`, and verifies backup ID 1. It then writes `"key2"`, closes the DB, opens `BackupEngineReadOnly`, restores backup ID 1 into the DB/WAL paths, reopens the DB, and verifies `"key1"` exists while `"key2"` is not found. It deletes both backup engine objects and closes the DB.

## State, persistence, and integration
Persistent state lives under `/tmp/rocksdb_example` or Windows temp for the DB, but the backup path is hard-coded to `/tmp/rocksdb_example_backup` even on Windows. The example integrates with `BackupEngine`, `BackupEngineReadOnly`, `BackupInfo`, `Env::Default()`, and standard DB read/write APIs.

## Risks and test signals
Several calls ignore their returned `Status` while asserting an older `s`, notably `db->Put()` and `CreateNewBackup()`, so failures could be missed in the example. The backup path is not platform-adjusted. Fixed backup IDs assume an empty/new backup directory; stale backups can change semantics. Test signals are backup creation success, `VerifyBackup(1)`, restore success, reopened DB containing only pre-backup data, and no stale backup directory interference.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/rocksdb_backup_restore_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/rocksdb_option_file_example.ini -->
# sources/storage-engines/rocksdb/examples/rocksdb_option_file_example.ini

## Purpose
`rocksdb_option_file_example.ini` is a sample RocksDB options file. It documents the options-file format and provides example `Version`, `DBOptions`, `CFOptions`, and `TableOptions/BlockBasedTable` sections.

## Important content and structure
The header comments describe RocksDB's INI-like extensions: escaped characters, hash comments, single-line `option_name = value` statements, section syntax with optional arguments, and colon-separated lists. The `[Version]` section records `rocksdb_version=4.3.0` and `options_file_version=1.1`.

`[DBOptions]` enumerates database-wide settings such as WAL TTL/size, background compactions/flushes, file opening, mmap/direct I/O toggles, log settings, manifest limits, and create/error flags. `[CFOptions "default"]` sets level compaction, six levels, block-based table factory, bytewise comparator, memtable settings, level triggers, compression and per-level compression, merge operator, write buffer size, dynamic level bytes, and other column-family controls. `[TableOptions/BlockBasedTable "default"]` configures block format, checksum, filter policy, block sizing, index type, and cache flags.

## State, persistence, and integration
This file is static example configuration consumed by RocksDB option parsing utilities rather than compiled code. It mirrors options persisted in DB directories and can be used with examples or tests that load options from files.

## Risks and test signals
The example version is old relative to current RocksDB and may contain deprecated, renamed, or behaviorally changed options. Typo-like comments such as "SecitonTitle" are harmless but signal sample age. Pointer-like options such as filters, factories, and comparators depend on registered names and may need application-side reconstruction. Test signals are successful parsing by `LoadOptionsFromFile`/`LoadLatestOptions`, expected defaults for omitted options, and validation that listed option names still exist.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/rocksdb_option_file_example.ini -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/simple_example.cc -->
# sources/storage-engines/rocksdb/examples/simple_example.cc

## Purpose
`simple_example.cc` is the basic C++ RocksDB API example. It demonstrates opening a DB, writing, reading, atomic batch updates, `PinnableSlice` reads, and closing through RAII.

## Important APIs and control flow
The program configures `Options` with `IncreaseParallelism()`, `OptimizeLevelStyleCompaction()`, and `create_if_missing=true`, opens a temp DB into `std::unique_ptr<DB>`, writes `"key1" -> "value"`, reads it into `std::string`, and applies a `WriteBatch` that deletes `"key1"` and puts `"key2"`. It then verifies `"key1"` is not found and `"key2"` has the expected value.

The final part demonstrates three `PinnableSlice` patterns: default construction, construction with an external string fallback buffer, and reuse with explicit `Reset()` between reads. It notes that the slice is invalid after reset.

## State, persistence, and integration
The DB path is fixed under temp and persists across runs unless externally destroyed. The example integrates with `DB`, `Options`, `ReadOptions`, `WriteOptions`, `WriteBatch`, `Status`, and `PinnableSlice`.

## Risks and test signals
The example does not call `DestroyDB`, so prior contents may exist but the exercised keys are overwritten/deleted. One `db->Get()` status for `"key2"` is not checked before asserting value. `PinnableSlice` lifetime rules are easy to misuse in application code; reset before reuse is the key signal. Test signals are all assertions passing, successful batch atomicity, not-found status for deleted key, and correct pinned/fallback value behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/simple_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/transaction_example.cc -->
# sources/storage-engines/rocksdb/examples/transaction_example.cc

## Purpose
`transaction_example.cc` demonstrates RocksDB's pessimistic `TransactionDB` API, including lock-based conflict prevention, snapshot reads, `GetForUpdate`, savepoints, rollback, and commit behavior.

## Important APIs and control flow
The example opens `TransactionDB` with `TransactionDBOptions` and runs three scenarios. The first starts a transaction, writes `"abc"`, shows outside reads cannot see the uncommitted value, writes unrelated `"xyz"` outside, then attempts an outside write to `"abc"` that fails with `Status::kLockTimeout` because the transaction holds the key lock. Commit succeeds and `"abc"` becomes visible.

The second starts with `set_snapshot=true`, writes `"abc"` outside, reads latest committed value without snapshot, reads old value with snapshot, then `GetForUpdate()` on the snapshotted key returns `Busy`, after which the transaction rolls back. The third uses multiple snapshots and a savepoint: it writes `"x"`, observes outside `"y"`, advances the transaction snapshot, updates `"y"`, rolls back to the savepoint, commits, and verifies `"x"` is committed while `"y"` remains at the outside value.

## State, persistence, and integration
The DB is a fixed temp path and is destroyed at the end. Integration points are `TransactionDB`, `Transaction`, `TransactionOptions`, `Snapshot`, savepoint APIs, and standard read/write options.

## Risks and test signals
Manual transaction and DB deletion can leak on assertion failure. Snapshot pointers in `ReadOptions` are explicitly cleared after transaction deletion, which is required. The example depends on default lock timeout behavior for `kLockTimeout`. Test signals are expected lock timeout for outside conflicting write, expected busy status for snapshot `GetForUpdate`, rollback to savepoint preserving outside `"y"`, and clean destroy.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/examples/transaction_example.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/delete_scheduler.cc -->
# sources/storage-engines/rocksdb/file/delete_scheduler.cc

## Purpose
`delete_scheduler.cc` implements rate-limited file deletion for RocksDB. Instead of immediately removing every file, it can rename files to a `.trash` path, account for trash size, and delete them on a background thread with pacing, chunked truncation, directory fsync, and bucket-level wait support.

## Important APIs and control flow
`DeleteFile()` handles accounted files tracked by `SstFileManagerImpl`. It deletes immediately when rate limiting is disabled or trash size exceeds `max_trash_db_ratio`; otherwise it queues the file. `DeleteUnaccountedFile()` handles untracked files and deletes immediately when slow deletion is disabled or hard-link count is greater than one unless forced to background.

`AddFileToDeletionQueue()` calls `MarkAsTrash()`, updates `total_trash_size_` for accounted files, records stats, pushes a `FileAndDir` into `queue_`, updates pending counts and bucket counts, and signals the background thread. `MarkAsTrash()` appends `.trash`, resolves name conflicts under `file_move_mu_`, renames the file, and informs `SstFileManagerImpl` for accounted moves.

`BackgroundEmptyTrash()` waits on `cv_`, pops queued files, calls `DeleteTrashFile()` without holding `mu_`, records errors, applies a time penalty proportional to deleted bytes/rate, decrements pending and bucket counts, and signals waiters. `DeleteTrashFile()` can partially delete large single-link files with `Truncate()`/`Fsync()` chunks before full delete. `CleanupDirectory()` discovers existing trash files and either schedules them through an SFM or deletes immediately.

## State, persistence, and integration
State includes atomic rate/trash size/ratio, pending queues and buckets under `InstrumentedMutex`, background errors, stats pointer, and a lazily created `port::Thread`. Filesystem persistence changes are real renames/deletes/truncates through `FileSystem`, with optional directory fsync after final delete. Accounted file lifecycle is integrated with `SstFileManagerImpl::OnMoveFile`, `OnDeleteFile`, and `ScheduleFileDeletion`.

## Risks and test signals
Correctness depends on lock ordering across `mu_`, `file_move_mu_`, filesystem calls, and SFM callbacks. Destructor stops the background thread without guaranteeing all trash is emptied, leaving `.trash` files by design. Partial deletion is disabled for hard-linked files and depends on `NumFileLinks`, `ReopenWritableFile`, `Truncate`, and `Fsync` support. `CleanupDirectory()` must not double-account files if `OnAddFile()` succeeds but scheduling fails. Test signals include rate penalty timing, stats tick counts, conflict-name trash creation, background error collection, hard-link behavior, immediate deletion threshold, bucket wait signaling, and cleanup of existing trash files.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/delete_scheduler.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/delete_scheduler.h -->
# sources/storage-engines/rocksdb/file/delete_scheduler.h

## Purpose
`delete_scheduler.h` declares the `DeleteScheduler` class, RocksDB's internal mechanism for optionally slowing file deletion through a trash queue and background worker. It documents the distinction between accounted files managed by `SstFileManager` and unaccounted files outside its size accounting.

## Important APIs and types
The constructor receives a `SystemClock`, `FileSystem`, byte-per-second rate, info log, `SstFileManagerImpl`, maximum trash/DB ratio, and maximum delete chunk size. Public methods include `GetRateBytesPerSecond()`, `SetRateBytesPerSecond()`, `DeleteFile()`, `DeleteUnaccountedFile()`, `WaitForEmptyTrash()`, `NewTrashBucket()`, `WaitForEmptyTrashBucket()`, `GetBackgroundErrors()`, `GetTotalTrashSize()`, ratio getters/setters, `IsTrashFile()`, `CleanupDirectory()`, and `SetStatisticsPtr()`.

Private helpers perform immediate deletion, queueing, trash renaming, trash-file deletion, SFM callbacks, background draining, and lazy thread creation. `FileAndDir` captures queued filename, directory to sync, accounted flag, and optional bucket.

## State, dependencies, and integration
The class depends on RocksDB `FileSystem`, `Env`, `Logger`, `SystemClock`, statistics, `InstrumentedMutex`/`InstrumentedCondVar`, and `SstFileManagerImpl`. Queue state, bucket counters, background errors, closing flag, and stats pointer are protected by `mu_`; name-conflict avoidance uses `file_move_mu_`. Atomic fields expose rate, trash size, and ratio.

## Risks and test signals
The header defines a concurrent class with strong lifecycle expectations: callers must handle remaining trash on destructor, bucket users must wait on created buckets, and SFM must outlive the scheduler. The API mixes foreground and background deletion based on rate, ratio, hard links, and force flags, so tests must cover every branch. Signals include successful wait semantics, no deadlocks, accurate stats, correct `IsTrashFile()` suffix detection, and stable behavior when rate changes from disabled to enabled.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/delete_scheduler.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/delete_scheduler_test.cc -->
# sources/storage-engines/rocksdb/file/delete_scheduler_test.cc

## Purpose
`delete_scheduler_test.cc` verifies `DeleteScheduler` behavior across rate limiting, concurrency, trash naming, background failures, partial deletion, hard links, foreground fallback, accounted/unaccounted files, and bucket waits.

## Important APIs and control flow
The fixture creates three per-thread test directories, owns an `SstFileManagerImpl`, obtains its `DeleteScheduler`, and has helpers for creating tracked/untracked dummy files and counting normal/trash files. Sync points are used extensively to hold the background thread, inspect penalties, inject ordering, and count delete/ftruncate/fsync paths.

Tests cover basic rate limiting with expected cumulative penalties and directory fsync, multi-directory scheduling, multithreaded queueing, disabled rate limiting with immediate delete, trash-name conflicts, externally deleted trash files producing background errors, repeated queue draining, chunked partial deletion, hard-link fallback, destructor with non-empty queue, immediate delete when trash exceeds a configured DB-size ratio, suffix classification, mixed accounted/unaccounted file deletion, concurrent unaccounted bucket deletion, immediate unaccounted deletion with remaining links, and a regression ensuring `WaitForEmptyTrashBucket()` is signaled when a single-file bucket empties while global pending work remains.

## State, persistence, and integration
The tests operate on real default `Env` filesystem directories and use SFM accounting/statistics. They integrate with RocksDB `SyncPoint`, `Statistics` tickers (`FILES_MARKED_TRASH`, `FILES_DELETED_FROM_TRASH_QUEUE`, `FILES_DELETED_IMMEDIATELY`), hard-link APIs, and background thread timing.

## Risks and test signals
Timing-based assertions can be sensitive to slow systems, though sync points reduce nondeterminism. Some tests are Linux-conditional or disabled. The bucket-signal regression is important because a missed condition-variable signal can hang callers indefinitely. Passing this suite signals queue accounting, rate calculations, bucket counters, partial deletion, stats, hard-link policy, foreground fallback, and background error paths are working.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/delete_scheduler_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/file_prefetch_buffer.cc -->
# sources/storage-engines/rocksdb/file/file_prefetch_buffer.cc

## Purpose
`file_prefetch_buffer.cc` implements `FilePrefetchBuffer`, the reusable buffering and readahead engine used for table reads, user scans, compaction reads, and explicit/implicit prefetch. It supports synchronous reads, asynchronous reads with polling/abort, overlap buffers, filesystem-owned buffer reuse, readahead-size tuning, and statistics.

## Important APIs and control flow
`Prefetch()` is the simple single-buffer synchronous path. `TryReadFromCache()` delegates to `TryReadFromCacheUntracked()`, which checks min-offset tracking, explicit async request state, buffer coverage, implicit sequential-read eligibility, and calls `PrefetchInternal()` on misses or partial hits. `PrefetchAsync()` submits explicit async reads, optionally fills `result` immediately from existing data, resets stale async work, and returns `TryAgain` when the caller should poll via a later read.

`PrefetchInternal()` is the central path. It aborts outdated IO, clears outdated buffers, handles overlapping data across async buffers or filesystem-owned sync buffers, polls completed async reads, determines read spans via `ReadAheadSizeTuning()`, schedules remaining async buffers with `PrefetchRemBuffers()`, performs a synchronous `Read()` when necessary, and copies partial data into `overlap_buf_`.

`ReadAsync()` uses `RandomAccessFileReader::ReadAsync()` with `PrefetchAsyncCallback()` and falls back to synchronous read on `NotSupported`. `PollIfNeeded()`, `AbortOutdatedIO()`, and `AbortAllIOs()` manage filesystem async handles. `ReadAheadSizeTuning()` aligns offsets, invokes the optional cache-aware callback, trims already-prefetched ranges, prepares buffers, and records trimming stats.

## State, persistence, and integration
The implementation has no persistent state beyond in-memory buffers. It integrates with `RandomAccessFileReader`, `FileSystem::Poll`/`AbortIO`, direct-I/O alignment, optional `FSSupportedOps::kFSBuffer`, `IOOptions`, `Statistics` histograms/tickers, `StopWatch`, and sync points for fault injection.

## Risks and test signals
The code is sensitive to offset arithmetic, alignment, EOF/truncated reads, async callback races, stale handles, and overlap-buffer sizing. `async_read_in_progress_` is used as a main-thread coordination flag rather than a general mutex. `FSBufferDirectRead()` reuses filesystem buffers only for single-buffer non-direct reads, and prefetch explicitly disables that optimization in one path due to overflow risk. Test signals should include direct/non-direct IO, mmap exclusion, async supported/unsupported, Poll failure injection, non-sequential reads aborting stale IO, overlap across two buffers, cache-tuned trimming, stat counters, and sanitizer runs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/file_prefetch_buffer.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/file_prefetch_buffer.h -->
# sources/storage-engines/rocksdb/file/file_prefetch_buffer.h

## Purpose
`file_prefetch_buffer.h` declares RocksDB's `FilePrefetchBuffer`, `ReadaheadParams`, `BufferInfo`, and usage enum. Together they define the in-memory state machine used to serve file reads from prefetched buffers and to drive synchronous/asynchronous readahead.

## Important APIs and types
`ReadaheadParams` carries initial and maximum readahead sizes, implicit-auto-readahead flags and counters, and `num_buffers`. `BufferInfo` owns an `AlignedBuffer`, offset, async request length, async in-progress flag, filesystem IO handle/deleter, and initial end offset. It provides predicates for whether data or pending async ranges cover an offset, whether buffers are outdated, and current size.

`FilePrefetchBufferUsage` classifies stat attribution for table-open tail prefetch, user scan prefetch, compaction prefetch, and unknown use.

`FilePrefetchBuffer` exposes `Prefetch()`, `PrefetchAsync()`, `TryReadFromCache()`, `min_offset_read()`, `GetPrefetchOffset()`, read-pattern updates, readahead state export, readahead decrement, async callback, and test buffer-inspection methods. Private methods handle buffer preparation, abort/poll, outdated data clearing, internal prefetch, sync/async reads, overlap copying, eligibility logic, FS-buffer use, read-ahead tuning, stats, and active/free buffer queue management.

## State, dependencies, and integration
State is a deque of active buffers, a deque of free buffers, an optional overlap buffer, readahead sizing/counters, previous read pattern, explicit-prefetch state, filesystem/clock/stats pointers, usage, callback, and buffer count. The destructor aborts pending IO, destroys IO handles, records discarded bytes, and deletes all buffers.

## Risks and test signals
The header reveals complex ownership: raw `BufferInfo*` objects move between deques and must be deleted exactly once, async handles must be destroyed through provider deleters, and overlap buffers are allocated only for multi-buffer or FS-buffer cases. `GetPrefetchOffset()` assumes at least one active buffer. Implicit auto-readahead depends on sequential access accounting. Tests should validate constructor/destructor lifecycle, zero/one/multi-buffer cases, min-offset tracking when disabled, buffer queue transitions, and stats for discarded/useful/prefetched bytes.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/file_prefetch_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/file/file_util.cc -->
# sources/storage-engines/rocksdb/file/file_util.cc

## Purpose
`file_util.cc` implements shared RocksDB file utilities for copying files, creating files, deleting DB files through optional `SstFileManager`, generating checksums, and recursively destroying directories.

## Important APIs and control flow
The first `CopyFile()` overload copies from a `FileSystem` source into an existing `WritableFileWriter`. It opens a `SequentialFileReader`, determines size when zero means "copy all", allocates a read buffer at least 4 KiB and at least `max_read_buffer_size`, then loops reading, checking for unexpected EOF, appending to the destination writer, and finally syncing with `use_fsync`. The second overload opens a destination `FSWritableFile`, wraps it in `WritableFileWriter`, and delegates.

`CreateFile()` opens a writable file, appends provided contents, and syncs. `DeleteDBFile()` and `DeleteUnaccountedDBFile()` route through `SstFileManagerImpl` scheduling unless forced foreground or no SFM exists, otherwise they call `Env::DeleteFile()`.

`GenerateOneFileChecksum()` validates and creates a checksum generator, verifies requested generator name when provided, opens a `RandomAccessFileReader`, computes file size, chooses a readahead buffer size with direct-I/O alignment, prepares `IOOptions`, reads the whole file in chunks, updates/finalizes the generator, and returns checksum plus function name. `DestroyDir()` recursively deletes children when `IsDirectory()` is supported and tolerates concurrent external deletion.

## State, persistence, and integration
These utilities perform real filesystem writes, syncs, deletes, and recursive removals. They integrate with `FileSystem`, `Env`, `SequentialFileReader`, `RandomAccessFileReader`, `WritableFileWriter`, `SstFileManagerImpl`, `IOTracer`, checksum factories, `RateLimiter`, statistics, and `ReadOptions`.

## Risks and test signals
The read buffer expression uses `max(4096, max_read_buffer_size)`, so a value named "max" actually acts as a minimum if larger than 4 KiB. Copy and checksum treat short reads before requested size as corruption. `DeleteDBFile()` assumes `sst_file_manager` is an `SstFileManagerImpl` when present. `DestroyDir()` ignores `IsDirectory()` unsupported, which can leave nested contents for filesystems without directory classification. Test signals are successful full/partial copy, checksum name mismatch failures, direct-I/O alignment coverage, read error/short-file corruption, SFM deletion routing, and recursive destroy under races.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/file/file_util.cc -->
