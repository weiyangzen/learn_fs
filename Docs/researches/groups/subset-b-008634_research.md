# subset-b-008634 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/env_encryption.cc -->
# sources/storage-engines/rocksdb/env/env_encryption.cc

## Purpose

`env_encryption.cc` implements RocksDB's encrypted file-system adapter and the built-in CTR encryption provider used by that adapter. It wraps `FSSequentialFile`, `FSRandomAccessFile`, `FSWritableFile`, and `FSRandomRWFile` so callers see plaintext bytes at logical file offsets, while the underlying file system stores an optional provider prefix followed by encrypted data. It also registers built-in encryption/cipher factories (`CTR`, `CTR://test`, `1://test`, and `ROT13`) for `CreateFromString`-based configuration.

## Important APIs, types, and functions

- `EncryptionProvider::NewCTRProvider()` constructs a `CTREncryptionProvider` around a supplied `BlockCipher`.
- `EncryptedSequentialFile`, `EncryptedRandomAccessFile`, `EncryptedWritableFile`, and `EncryptedRandomRWFile` implement offset translation and call `BlockAccessCipherStream::Encrypt()` or `Decrypt()` around the wrapped file operations.
- `EncryptedFileSystemImpl` derives from `EncryptedFileSystem` and is the main `FileSystemWrapper` implementation. It owns a `std::shared_ptr<EncryptionProvider>` registered as option `provider`.
- `NewEncryptedFileSystemImpl()`, `NewEncryptedFS()`, and `NewEncryptedEnv()` are the construction entry points used by direct callers and the file-system factory registry.
- `BlockAccessCipherStream::Encrypt()` and `Decrypt()` provide block-granular encryption over arbitrary byte ranges, handling partial leading/trailing blocks by copying through a temporary full-block buffer.
- `ROT13BlockCipher` is a test/sample cipher registered as a `BlockCipher`. It is explicitly not production-safe.
- `CTRCipherStream` and `CTREncryptionProvider` implement CTR mode over an arbitrary `BlockCipher`.
- `BlockCipher::CreateFromString()` and `EncryptionProvider::CreateFromString()` register built-ins once and delegate loading to `LoadSharedObject`.

## Control flow

File wrapper reads add `prefixLength_` to the caller offset before reading encrypted bytes, then decrypt the returned buffer in place. Sequential reads track `offset_`; `Skip()` advances the logical stream position; positioned sequential reads and random access reads translate offsets independently. Writes clone caller data into an `AlignedBuffer`, encrypt the clone at the physical offset, and pass only encrypted data to the wrapped file. The caller's input buffer is not mutated. Size, cache invalidation, allocation, truncation, range sync, and preallocation calls are translated by adding or subtracting the prefix length where they refer to file positions or lengths visible to RocksDB.

`EncryptedFileSystemImpl` handles construction paths separately for write, reopen, random read, sequential read, and random read/write. New writable files create a fresh prefix with `EncryptionProvider::CreateNewPrefix()`, write it to offset zero, then construct a stream from that prefix. Reads read the existing prefix before constructing a stream. Reopening a writable file reads an existing prefix for non-empty files and creates a fresh prefix for empty files. Random-RW files decide between read-prefix and write-prefix paths based on `FileExists()` before opening.

`BlockAccessCipherStream` computes `blockIndex = fileOffset / BlockSize()` and `blockOffset = fileOffset % BlockSize()`, then repeatedly encrypts or decrypts one block at a time. Partial-block ranges are copied into an uninitialized full-block buffer at the correct offset, transformed as a whole block, then copied back for only the requested range.

The CTR provider's prefix stores the initial counter in the first cipher block and the IV in the second cipher block. The remainder of the 4096-byte prefix is provider-specific secret prefix space and is encrypted using a CTR stream derived from the plaintext counter/IV. Opening an existing file decodes the counter/IV, checks that the prefix is at least two cipher blocks, decrypts the encrypted prefix tail, and creates a `CTRCipherStream` for file contents.

## State and persistence behavior

The persistent on-disk layout is `[encryption prefix][encrypted user data]`. `CTREncryptionProvider::defaultPrefixLength` is 4096 bytes to keep the first real data byte page-aligned for direct I/O. Public file sizes exclude this prefix; underlying file sizes include it. Prefix bytes are generated with `Random` seeded from `SystemClock::Default()->NowMicros()`, contain a random counter and IV, and may include encrypted subclass-specific prefix data via `PopulateSecretPrefixPart()`. The prefix is written once when a file is created or an empty file is reopened for writing.

The wrappers are largely stateless beyond the wrapped file pointer, the cipher stream, and prefix length. Sequential file wrappers also maintain the current physical offset. No key material is persisted directly by this file except for provider-defined prefix data; the actual cipher/key lifecycle is delegated to `EncryptionProvider` and `BlockCipher` implementations.

## Dependencies and integration points

This file depends on RocksDB's `FileSystem`/`Env` abstraction, `CompositeEnvWrapper`, `AlignedBuffer`, option registration (`OptionTypeInfo`, `RegisterOptions`), object registry loading (`LoadSharedObject`, `ObjectLibrary`), performance timers (`encrypt_data_nanos`, `decrypt_data_nanos`), and conversion between `Status` and `IOStatus`. It integrates with `file_system.cc` because `EncryptedFileSystem::kClassName()` is registered as a built-in file system there and constructed with `NewEncryptedFileSystemImpl()`. It also integrates with `env_test.cc` factory tests for `CTR`, `ROT13`, and `EncryptedFileSystem` option strings.

## Risks and edge cases

- `CreateSequentialCipherStream()` and `CreateRandomReadCipherStream()` use `provider_` directly rather than `GetReadableProvider()`, so a missing provider would be a crash risk if an improperly prepared `EncryptedFileSystemImpl` were used. Factory tests assert that provider-less encrypted FS configuration fails validation.
- `GetChildrenFileAttributes()` subtracts the provider prefix from every child returned by the underlying FS, but comments note directories are not distinguished. This can underflow or misreport directory sizes if directories are present and smaller than the prefix.
- `EncryptedWritableFile::GetFileSize()` subtracts `prefixLength_` from the underlying size without an explicit runtime guard. Correct construction requires the prefix to have been written first.
- Partial-block encryption/decryption transforms an uninitialized temporary full block except for the requested byte range. CTR mode makes this acceptable because only copied-back bytes matter, but non-CTR `BlockAccessCipherStream` subclasses must tolerate arbitrary bytes in the unrequested part of a partial block.
- CTR security depends entirely on the supplied `BlockCipher` and unique counter/IV per file. `ROT13BlockCipher` is test-only and unsafe.
- mmap reads/writes are rejected for encrypted files because the wrapper must transform bytes in userspace.
- Random-RW `isNewFile` is based on `FileExists()` before opening; unusual file-system races could choose the wrong prefix path.

## Test signals

`env_test.cc` covers the factory and configuration side: `LoadCTRProvider` exercises no-cipher failure, `CTR://test`, `1://test`, and `id=CTR; cipher=ROT13`; `LoadROT13Cipher` checks cipher factory loading; `CreateEncryptedFileSystem` checks the provider requirement, serialization/equivalence, default target wrapping, and wrapping over `TimedFileSystem`. Generic environment/file tests also indirectly exercise wrapper contracts such as size reporting, direct I/O option handling, file-system composition, and `SyncFile` behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/env_encryption.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/env_encryption_ctr.h -->
# sources/storage-engines/rocksdb/env/env_encryption_ctr.h

## Purpose

`env_encryption_ctr.h` declares the CTR-mode encryption stream and provider used by RocksDB's encrypted file-system implementation. It is the public internal header that lets `env_encryption.cc`, factory code, tests, and external custom providers refer to the built-in CTR implementation without exposing its implementation details.

## Important APIs, types, and functions

- `CTRCipherStream final : public BlockAccessCipherStream` adapts a `BlockCipher` to the block-access stream interface using counter mode.
- `CTRCipherStream::BlockSize()` delegates to the wrapped cipher's block size.
- `CTRCipherStream::AllocateScratch()`, `EncryptBlock()`, and `DecryptBlock()` are protected overrides implemented in `env_encryption.cc`.
- `CTREncryptionProvider : public EncryptionProvider` owns the configured `BlockCipher` and creates CTR streams from file prefixes.
- `CTREncryptionProvider::kClassName()` returns `CTR`, the object-registry id.
- `GetPrefixLength()`, `CreateNewPrefix()`, `CreateCipherStream()`, and `AddCipher()` implement the provider contract.
- `PopulateSecretPrefixPart()` and `CreateCipherStreamFromPrefix()` are protected extension hooks for subclasses that want encrypted metadata in the prefix or custom stream construction.
- `NewEncryptedFileSystemImpl()` is declared here so built-in file-system registration can construct an encrypted FS without depending on private implementation classes.

## Control flow

Callers construct `CTREncryptionProvider` with either a cipher or no cipher. A provider without a cipher can later accept one through `AddCipher()`, or fail validation/stream creation if no cipher is configured. Creating a new encrypted file calls `CreateNewPrefix()`, which writes CTR parameters and any protected prefix data; opening an existing encrypted file calls `CreateCipherStream()` with the stored prefix. Both produce `BlockAccessCipherStream` instances, normally `CTRCipherStream`.

`CTRCipherStream` stores the shared cipher, a per-file IV string sized to the cipher block size, and the initial counter. For each block it derives a counter block from IV plus block index, encrypts that counter block with the cipher, and XORs it with file data. Decryption is the same operation as encryption.

## State and persistence behavior

The header defines the provider's default prefix length as 4096 bytes. That constant is part of the persistent layout because encrypted files reserve that many leading bytes before user data. `CTRCipherStream` itself keeps only runtime state: `cipher_`, `iv_`, and `initialCounter_`. The IV and initial counter are loaded from or generated into the prefix by the implementation file.

## Dependencies and integration points

The header depends on `rocksdb/env_encryption.h` for `EncryptionProvider`, `BlockAccessCipherStream`, `BlockCipher`, `EnvOptions`, `Slice`, and `Status`. It is included by `env_encryption.cc`, `file_system.cc`, and `env_test.cc`. `file_system.cc` needs it for `NewEncryptedFileSystemImpl()` during built-in file-system registration. Tests use `CTREncryptionProvider::kClassName()` and factory strings that target this provider.

## Risks and edge cases

- The constructor dereferences `c->BlockSize()` when copying the IV, so callers must never construct `CTRCipherStream` with a null cipher.
- The provider can be constructed without a cipher, which is useful for option loading but unsafe for actual encryption until prepared with a valid cipher.
- The header's comment says the CTR implementation is suitable only when the underlying `BlockCipher` is safe. The built-in test ROT13 cipher does not satisfy that condition.
- The 4096-byte prefix is performance-oriented for direct I/O alignment; changing it would affect on-disk compatibility and size accounting.

## Test signals

`env_test.cc` validates provider registry names and option parsing for `CTR`, `CTR://test`, `1://test`, and `id=CTR; cipher=ROT13`. `CreateEncryptedFileSystem` validates use through `FileSystem::CreateFromString()`. Encryption-specific behavior is otherwise mostly exercised through wrapper integration rather than a standalone CTR-mode unit in this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/env_encryption_ctr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/env_posix.cc -->
# sources/storage-engines/rocksdb/env/env_posix.cc

## Purpose

`env_posix.cc` provides the default non-Windows RocksDB `Env` implementation and default `SystemClock`. It binds the higher-level `Env` API to the default `FileSystem`, POSIX time, dynamic library loading, background thread pools, thread status tracking, hostname/thread-id helpers, and singleton lifetime handling.

## Important APIs, types, and functions

- `PosixDynamicLibrary` wraps a `dlopen()` handle and implements `DynamicLibrary::LoadSymbol()` using `dlsym()`.
- `PosixClock : public SystemClock` implements wall-clock, monotonic, CPU time, sleeping, current Unix time, and formatting.
- `PosixEnv : public CompositeEnv` is the default `Env`, built from `FileSystem::Default()` and `SystemClock::Default()`.
- `PosixEnv::LoadLibrary()` resolves shared-library names, adds platform extensions/prefixes, searches optional colon-separated paths, and returns `PosixDynamicLibrary`.
- `Schedule()`, `UnSchedule()`, `SetBackgroundThreads()`, `IncBackgroundThreadsIfNeeded()`, `ReserveThreads()`, `ReleaseThreads()`, and priority-lowering methods delegate to per-priority `ThreadPoolImpl` instances.
- `StartThread()` creates a raw pthread for one-off tasks and records it for `WaitForJoin()`/shutdown joining.
- `Env::Default()` initializes supporting singletons and returns the static default `PosixEnv`.
- `SystemClock::Default()` returns the static default `PosixClock`.

## Control flow

`Env::Default()` first initializes `ThreadLocalPtr`, `CompressionContextCache`, and sync-point singletons. It then creates a static `PosixEnv` with `STATIC_AVOID_DESTRUCTION` and a static `JoinThreadsOnExit` object that joins raw started threads and thread-pool workers during process shutdown. `PosixEnv` construction initializes a mutex, allocates one `ThreadPoolImpl` for each `Env::Priority`, sets each pool's priority, installs this env as host env, and creates a `ThreadStatusUpdater`.

Background work is scheduled by priority into `thread_pools_[pri]`; queue length, unscheduling, reservation, release, and priority changes are direct `ThreadPoolImpl` operations. `StartThread()` allocates a small state object, starts a pthread that invokes the user function and deletes the state, then records the pthread id under `mu_`. `WaitForJoin()` joins all recorded ids and clears the list.

Dynamic library loading normalizes a requested name: empty name loads the current process, otherwise the platform extension is appended if missing and `lib` is prepended for Unix bare names. If a search path is supplied, each path component is tried as `path/libname`; otherwise `dlopen()` uses the system search path.

`PosixClock` chooses platform-specific APIs for nanosecond and CPU timing: `clock_gettime()` on Linux/BSD/AIX, `gethrtime()` on Solaris, Mach clock APIs on macOS, and `std::chrono::steady_clock` elsewhere.

## State and persistence behavior

`PosixEnv` owns process-lifetime thread pools, a mutex, a vector of joinable pthreads, and `allow_non_owner_access_`. No database data is persisted by this file directly; persistence is delegated to `FileSystem::Default()` through the `CompositeEnv` base. State that affects OS behavior includes background thread counts, reserved worker counts, lower CPU/I/O priority settings, and file access permissions indirectly consumed by POSIX file creation code outside this file.

The singleton lifetime is intentionally unusual: thread status updater is not explicitly deleted to avoid use-after-free during static destruction, and `STATIC_AVOID_DESTRUCTION` keeps the default env available late in process shutdown.

## Dependencies and integration points

The implementation is compiled only when `!OS_WIN`. It depends on POSIX headers (`pthread`, `unistd`, `fcntl`, `dlfcn`, `sys/time`, etc.), optional `liburing` headers, RocksDB `CompositeEnv`, `io_posix`, `ThreadPoolImpl`, `ThreadStatusUpdater`, `CompressionContextCache`, `ThreadLocalPtr`, and sync-point infrastructure. It integrates with `file_system.cc` via `FileSystem::Default()` and with broad tests in `env_test.cc` for thread pools, library loading, default env creation, static destruction, direct/chroot environment parameterization, and CPU priority behavior.

## Risks and edge cases

- `WaitForJoin()` iterates and clears `threads_to_join_` without locking, while `StartThread()` mutates it under `mu_`. It is safe under expected test/application sequencing but not a general concurrent join API.
- `JoinThreadsOnExit` intentionally leaks/avoids deleting the thread status updater. That trades memory cleanup for shutdown safety.
- Dynamic loading error paths depend on `dlerror()` state and platform library naming; path search is simple and does not escape or sanitize components.
- `GetThreadID()` falls back to copying `pthread_t` bytes into a `uint64_t` where `gettid()` is unavailable. This is practical but platform-shape dependent.
- `TimeToString()` returns a fixed-size string buffer that may include trailing NUL bytes because it resizes to `maxsize`.
- On non-Linux platforms, CPU priority and I/O priority hooks either degrade or no-op.

## Test signals

`env_test.cc` exercises `RunEventually`, `StartThread`, `TwoPools`, `DecreaseNumBgThreads`, `ReserveThreads`, `UnSchedule`, `LowerThreadPoolCpuPriority`, dynamic library loading with and without search paths, `MultipleCompositeEnv`, `CreateDefaultEnv`, `StaticDestruction`, and many default-env file operations. Parameterized tests run many cases against both `Env::Default()` and a `ChrootEnv`, with direct I/O enabled and disabled where supported.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/env_posix.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/env_test.cc -->
# sources/storage-engines/rocksdb/env/env_test.cc

## Purpose

`env_test.cc` is a large integration and regression test suite for RocksDB's environment, file-system, file, logger, factory, unique-id, async I/O, and sync helper behavior. Although named for env tests, it validates interactions across `Env`, `FileSystem`, POSIX-specific implementation, composite/chroot/mock/fault-injection wrappers, encryption provider registration, `io_uring`, direct I/O, logging, and helper functions such as `WriteStringToFile`.

## Important APIs, types, and functions

- Test fixtures: `EnvPosixTest`, `EnvPosixTestWithParam`, `EnvFSTestWithParam`, `CreateEnvTest`, `EnvTest`, `TestAsyncRead`, `TestGetFileSize`, and `TestIOActivity`.
- Helpers: `NewAligned()`, `ReadFdExactly()`, `WriteFdExactly()`, `RunDeterministicMappingReuseScenario()`, `IoctlFriendlyTmpdir`, `HasPrefix()`, `GenerateFilesAndRequest()`, and `TestAbortIOWithRequests()`.
- Wrapper/mock types: `TestEnv`, `WrappedEnv`, `ReadAsyncFS`, `ReadAsyncRandomAccessFile`, sync-file wrapper classes, `CloseFailFS`, and `RandomRWFileWithMirrorString`.
- Major test groups cover thread scheduling, dynamic library loading, mmap/direct I/O reads, random access unique ids, fallocate/preallocation, `MultiRead`, `io_uring` failures, TSAN mapping annotations, cache invalidation, logging buffers, wrapper forwarding, random read/write files, `Options::env`/`FileSystem` combinations, object factory creation, unique-id generation, async read/poll/abort, static destruction, `GetFileSize`, IO activity strings, `WriteStringToFile`, and `SyncFile`.

## Control flow

The file starts with platform-conditioned includes and helpers, then defines env fixtures. `EnvPosixTestWithParam` receives `(Env*, direct_io)` pairs and drains thread pools in its destructor. Thread-pool tests schedule sleeping or atomic-update tasks, manipulate pool sizes/reservations, and assert queue/running behavior with sync points where ordering matters.

File I/O tests create per-thread temp paths, write deterministic content, reopen through sequential/random/writable/random-RW APIs, and compare returned bytes or metadata. Direct I/O paths allocate page-aligned buffers with `NewAligned()` and sometimes use sync points to mask unsupported `O_DIRECT` paths on platforms where the logical test is not about the kernel flag itself.

Factory tests use `CreateFromString()` with strict `ConfigOptions` to verify built-in object ids, nested wrapper option strings, serialization, equivalence, required options, default target filling, and guarded versus unguarded `Env` creation. Encryption coverage is through `CTREncryptionProvider`, `ROT13`, and `EncryptedFileSystem` factory strings.

Async I/O tests either use `ReadAsyncFS` to simulate asynchronous completion with worker threads, or use real `io_uring` when compiled in. They submit `ReadAsync` requests, interleave with `MultiRead`, call `Poll()`, inject queue-full and io_uring failure states, and stress `AbortIO()` with overlapping, unaligned, reversed, partial, and direct-I/O request sets.

The tail of the file verifies helper semantics: `WriteStringToFile` must close files and delete on close failure; `Env::SyncFile` and `FileSystem::SyncFile` must reopen, call `Sync` or `Fsync`, close, and return sync errors before close errors.

## State and persistence behavior

Tests create and delete temporary files and directories via `test::PerThreadDBPath()`, `test::TmpDir()`, and custom temp directories. Persistent test data is deterministic or random seeded data written to files, then read back through RocksDB abstractions. `IoctlFriendlyTmpdir` selects storage that supports `FS_IOC_GETVERSION` for unique-id tests and skips/bypasses unsupported container or filesystem cases. Some tests intentionally preserve singleton process state such as `Env::Default()` thread pools, sync-point callbacks, and thread-local io_uring state, so fixtures and tests clear callbacks and drain queues to avoid cross-test contamination.

## Dependencies and integration points

The test suite depends on RocksDB DB APIs, env and file-system wrappers, `env_posix.cc` behavior, `io_posix` internals on Linux, `env_encryption_ctr.h`, `file_system.cc` helpers, `ObjectRegistry`, `MockEnv`, `ChrootEnv`, `ReadOnlyFileSystem`, `TimedFileSystem`, `CountedFileSystem`, fault-injection wrappers, logging utilities, unique-id generators, sync points, and test harness utilities. Several tests are platform-gated with `OS_LINUX`, `OS_WIN`, `ROCKSDB_IOURING_PRESENT`, `ROCKSDB_FALLOCATE_PRESENT`, dynamic-extension flags, and filesystem magic checks.

## Risks and edge cases

- Many tests rely on timing (`SleepForMicroseconds`, fixed timeouts, a 5-second watchdog, and stress iterations). They include retries or bypasses, but remain sensitive to overloaded CI.
- Some tests intentionally reach into implementation details (`Posix_IOHandle`, sync point names, io_uring helpers). Refactors can break tests even when public behavior remains stable.
- The direct I/O and fallocate checks are heavily filesystem dependent; the test contains skip logic for tmpfs, overlayfs, btrfs, zfs, Docker, and unsupported fallocate/ioctl cases.
- Parameterized tests share `Env::Default()` singleton state. The fixture drains queues, but background work from unrelated tests can still affect timing-sensitive assertions.
- Several disabled tests document known flakiness or unclear assumptions, including immediate run ordering and unique-id reuse after deletion.
- Async abort tests intentionally call `_exit(1)` from a watchdog on hang, which is useful for regression detection but abrupt for diagnostics.

## Test signals

This file is itself the test signal for the other files in this work item. Specific signals include `CreateEncryptedFileSystem`, `LoadCTRProvider`, and `LoadROT13Cipher` for encryption registration; `FileSystemSyncFileDefault*`, `WriteStringToFileClosesFile`, and `WriteStringToFileCloseFailureDeletesFile` for `file_system.cc`; `RunEventually`, `TwoPools`, `ReserveThreads`, `DecreaseNumBgThreads`, `LoadRocksDBLibrary*`, `CreateDefaultEnv`, and `StaticDestruction` for `env_posix.cc`; and async/multiread/cache/preallocation/random-RW tests for lower-level POSIX file behavior outside this subset.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/env_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/env/file_system.cc -->
# sources/storage-engines/rocksdb/env/file_system.cc

## Purpose

`file_system.cc` implements core default behavior for the `FileSystem` abstraction: built-in factory registration, string-based construction, convenience helpers for writing and reading whole files, default `SyncFile`, default logger creation, file-option optimization hooks, wrapper option serialization, and `DirFsyncOptions` constructors.

## Important APIs, types, and functions

- `RegisterBuiltinFileSystems()` registers `TimedFileSystem`, `ReadOnlyFileSystem`, `EncryptedFileSystem`, `CountedFileSystem`, `MockFileSystem`, and non-Windows `ChrootFileSystem` with `ObjectLibrary`.
- `FileSystem::CreateFromString()` returns `FileSystem::Default()` when the string names the default; otherwise it registers built-ins once and calls `LoadSharedObject<FileSystem>()`.
- `FileSystem::ReuseWritableFile()` implements the default rename-then-open behavior.
- `FileSystem::SyncFile()` reopens a writable file, calls `Sync()` or `Fsync()`, closes it, and preserves the primary sync/fsync error over a close error.
- `FileSystem::NewLogger()` creates an `EnvLogger` over a new writable file with a default 1 MiB writable-file buffer.
- `OptimizeForLogRead()`, `OptimizeForManifestRead()`, `OptimizeForLogWrite()`, `OptimizeForManifestWrite()`, `OptimizeForCompactionTableWrite()`, `OptimizeForCompactionTableRead()`, and `OptimizeForBlobFileRead()` adjust `FileOptions` based on DB options.
- `WriteStringToFile()` writes a full slice, optionally syncs, explicitly closes, and deletes the file on failure.
- `ReadFileToString()` reads a sequential file in 8192-byte chunks into a `std::string`.
- `FileSystemWrapper::PrepareOptions()` fills a null target with `FileSystem::Default()`.
- `FileSystemWrapper::SerializeOptions()` includes a `target=` option for non-default targets unless shallow serialization is requested.
- `DirFsyncOptions` constructors encode default, rename, and explicit fsync reasons.

## Control flow

`CreateFromString()` first checks whether the default file system already matches the requested value. If not, a `std::once_flag` registers built-in factories in the default object library, then shared-object loading handles registry/config parsing. Built-in wrappers are generally created with null targets; their `PrepareOptions()` later fills in `FileSystem::Default()` through wrapper behavior.

`SyncFile()` opens the file with `ReopenWritableFile()`. A sync point can observe or modify the open status. On success it calls either `Fsync()` or `Sync()`, always attempts `Close()`, and returns the close status only if the sync/fsync path succeeded. If sync/fsync failed, the close error is marked checked and suppressed.

`WriteStringToFile()` opens a writable file, appends all data, syncs if requested, then explicitly closes. This avoids relying on destructors that could hide close/flush errors. Any error after file creation triggers `DeleteFile()` cleanup. `ReadFileToString()` opens a sequential file with default options and loops until a read error or an empty fragment signals EOF.

Option optimization methods copy the input `FileOptions` and change only the relevant fields: log/manifest reads disable direct reads, log writes inherit WAL bytes-per-sync and writable buffer size, compaction/blob reads use direct-read DB options, and compaction table writes use direct-write DB options.

## State and persistence behavior

This file owns no long-lived mutable state other than one-time built-in factory registration. It affects persistent data through helper methods: `ReuseWritableFile()` renames files, `WriteStringToFile()` creates/replaces file content and deletes failed writes, `ReadFileToString()` loads content into memory, and `SyncFile()` flushes existing file data to storage. Wrapper serialization preserves target file-system topology in option strings when the target is non-default.

## Dependencies and integration points

The file integrates with `env_encryption.cc` through `NewEncryptedFileSystemImpl()`, with `Env::Default()` for logger creation and default targets, with object registry/customizable option infrastructure, and with built-in wrappers from `env_chroot`, `fs_readonly`, `mock_env`, `counted_fs`, and `env_timed`. Tests in `env_test.cc` cover factory creation for all registered built-ins, read/write helpers, and `SyncFile` error ordering.

## Risks and edge cases

- `ReadFileToString()` allocates its buffer with `new[]` and deletes it manually; early returns are avoided, but RAII would be safer.
- `ReadFileToString()` wraps `NewSequentialFile()` with `status_to_io_status()` even though it already returns `IOStatus` in this API layer, which is harmless but signals historical API layering.
- `WriteStringToFile()` deletes the destination on any append/sync/close failure. That is appropriate for helper semantics but important for callers that expect partial files to remain for diagnostics.
- `SyncFile()` requires a functioning `ReopenWritableFile()` implementation. File systems that do not support reopening writable files inherit a default that may return errors.
- Factory-created wrappers with null targets depend on `PrepareOptions()` being invoked before operational use.
- `SerializeOptions()` suppresses default targets and shallow targets; tooling that expects fully explicit target chains must request non-shallow serialization.

## Test signals

`env_test.cc` includes `CreateReadOnlyFileSystem`, `CreateTimedFileSystem`, `CreateCountedFileSystem`, `CreateChrootFileSystem`, and `CreateEncryptedFileSystem` for factory/serialization behavior. `WriteStringToFileClosesFile` verifies explicit close, and `WriteStringToFileCloseFailureDeletesFile` verifies cleanup on close error. `FileSystemSyncFileDefaultUsesSyncAndFsync`, `FileSystemSyncFileDefaultReturnsReopenError`, `FileSystemSyncFileDefaultReturnsCloseErrorAfterSuccessfulSync`, and `FileSystemSyncFileDefaultReturnsSyncErrorBeforeCloseError` validate `SyncFile()` call order and error precedence.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/env/file_system.cc -->
