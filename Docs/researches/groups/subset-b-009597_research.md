# Research Group subset-b-009597

This grouped report covers gcsfuse integration tests for inactive stream timeouts, interrupts, kernel list cache, large directory listing, local-file writeback semantics, log rotation, managed folders, monitoring metrics, mount timing/access, mount helpers, and negative stat cache behavior. Each source section is delimited for reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/without_timeout_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/without_timeout_test.go

## Purpose

This suite verifies that the inactive stream timeout feature does not close a reader when the timeout is disabled. It mounts gcsfuse using the package's inactive-stream test harness, opens a file through the mount, performs a small read, waits longer than the default timeout window, and asserts that the gcsfuse log does not contain the inactive-reader close line for that object.

## Important APIs, Types, and Functions

`timeoutDisabledSuite` embeds `suite.Suite` and carries mount flags, a `storage.Client`, `context.Context`, and test metadata. `SetupSuite` calls `setup.SetUpLogFilePath` and `mountGCSFuseAndSetupTestDir`; `TearDownSuite` unmounts through `setup.UnmountGCSFuseWithConfig`; `TearDownTest` saves logs on failure. `TestNoReaderCloser` uses `client.SetupFileInTestDirectory`, `operations.OpenFileAsReadonly`, `ReadAt`, and `doesNotHaveInactiveReaderClosedLogLineInLogFile`. `TestTimeoutDisabledSuite` chooses mounted-directory execution or iterates `setup.BuildFlagSets`.

## Control Flow

For each flag set, the suite configures log paths, mounts, creates a random object under `kTestDirName`, opens it read-only, reads `kChunkSizeToRead` at offset zero, records the time, sleeps for twice `kDefaultInactiveReadTimeoutInSeconds` plus a buffer, then scans logs between the read and wait end time. The expected path is the object path relative to the test directory.

## State and Persistence Behavior

State persists in the mounted filesystem, the backing GCS object created before the read, and the gcsfuse log file. The file handle remains open until deferred close. The test intentionally depends on the absence of background reader cleanup log state after a long idle period.

## Dependencies and Integration Points

It depends on the package-level inactive stream timeout setup variables and helpers, Cloud Storage client APIs, shared setup/mounting utilities, and Testify suite/require. It integrates with GKE mounted-directory mode and normal test-bucket flag-set mode.

## Risks and Test Signals

The test is time-sensitive and log-string-sensitive. A slow system is acceptable because the assertion is negative over a recorded interval, but log format changes or helper timestamp parsing changes can cause false failures. Passing signal is no inactive reader close log while the handle remains idle past the default timeout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/inactive_stream_timeout/without_timeout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/interrupt/git_clone_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/interrupt/git_clone_test.go

## Purpose

This file tests whether common Git workflows can run on a gcsfuse mount under the interrupt test configuration, including `--ignore-interrupts` variants and streaming write settings chosen by package setup. The scenarios cover clone, checkout, empty commit, and committing a newly created 1 MiB file.

## Important APIs, Types, and Functions

`ignoreInterruptsTest` is a Testify suite with `SetupTest` creating `testDirPath` through `setup.SetupTestDirectory`. `cloneRepository` executes `git clone` via `operations.ExecuteToolCommandfInDirectory` with retry handling for transient GitHub/network errors. Helpers `checkoutBranch`, `emptyCommit`, `gitAdd`, `nonEmptyCommit`, and `setGithubUserConfig` run Git subcommands inside the cloned repository.

## Control Flow

Each test starts from a fresh mount test directory. Clone retries up to five times, sleeping a randomized 1 to 2000 ms on DNS, remote-read, or GitHub connection errors. Checkout clones first and switches to `test-branch`. Empty commit clones, configures local author identity, and runs `commit --allow-empty`. Commit-with-changes clones, configures identity, creates a 1 MiB file with `operations.CreateFileOfSize`, runs `git add`, then commits.

## State and Persistence Behavior

The main state is the cloned Git repository tree under the mounted test directory, including `.git`, working tree files, index updates, and commit objects written through gcsfuse. `testDirPath` is package global and reset per test. No explicit teardown removes the repository in this file; the broader package setup handles mount/test directory cleanup.

## Dependencies and Integration Points

The test depends on network access to `https://github.com/gcsfuse-github-machine-user-bot/test-repository.git`, the host `git` binary, shared operations/setup utilities, and `internal/cache/util.MiB`. It is driven by `interrupt_test.go`, which mounts with ignore-interrupt and streaming-write flag combinations.

## Risks and Test Signals

Network flakiness is partially mitigated but GitHub availability, credentials policy, and repository contents remain external dependencies. Git output is surfaced in failures. Strong signals are successful clone, branch checkout, and repository mutations without interrupted syscalls or write-path corruption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/interrupt/git_clone_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/interrupt/interrupt_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/interrupt/interrupt_test.go

## Purpose

This package-level `TestMain` configures and runs the interrupt integration tests. It builds default flag combinations when no config file section is provided, creates shared Cloud Storage clients, mounts gcsfuse through the static mounting harness, and cleans the backing GCS test prefix afterward.

## Important APIs, Types, and Functions

The file defines `testDirName`, package globals `storageClient` and `ctx`, and `TestMain`. It uses `setup.ParseSetUpFlags`, `test_suite.ReadConfigFile`, `setup.TestEnvironment`, `client.CreateStorageClientWithCancel`, `setup.BuildFlagSets`, `setup.SetUpTestDirForTestBucket`, `static_mounting.RunTestsWithConfigFile`, and `setup.CleanupDirectoryOnGCS`.

## Control Flow

`TestMain` loads config and, if absent, creates one `Interrupt` test config. The default flags include implicit dirs with streaming writes disabled, ignore interrupts true/false with streaming writes disabled, and a streaming-writes enabled case compatible with flat and HNS buckets but not zonal. It initializes environment and storage client, handles mounted-directory mode when both mounted directory and bucket are provided, otherwise builds compatible flag sets, sets up the test bucket directory, runs tests under static mounting, cleans `TestBucket/InterruptTest`, and exits with the suite code.

## State and Persistence Behavior

The file owns the package-wide storage client/context and controls lifecycle for bucket prefixes and mounts. It persists no data beyond test-created GCS objects, which are removed on normal completion. Mounted-directory mode delegates cleanup to `setup.RunTestsForMountedDirectory`.

## Dependencies and Integration Points

It integrates with the shared test-suite config schema and static mounting utility. The tests in `git_clone_test.go` rely on this file for `testDirName`, `ctx`, `storageClient`, and the selected flag sets.

## Risks and Test Signals

Configuration compatibility is central: flag strings include both comma-free space-separated flags and protocol/write settings. Cleanup runs only after `RunTestsWithConfigFile` returns. Success is the package test process exiting with the static mounting result and no storage client close fatal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/interrupt/interrupt_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/disabled_kernel_list_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/disabled_kernel_list_cache_test.go

## Purpose

This suite verifies disabled kernel list cache behavior. With `--kernel-list-cache-ttl-secs=0`, a directory listing should always be refreshed from gcsfuse/GCS rather than reused from the kernel list cache.

## Important APIs, Types, and Functions

`disabledKernelListCacheTest` embeds `suite.Suite` and stores current mount flags. Setup mounts via `setup.MountGCSFuseWithGivenMountWithConfigFunc` using the package `mountFunc` and sets the mount directory. `TestKernelListCache_AlwaysCacheMiss` uses `operations.CreateDirectory`, `operations.CreateFile`, `os.Open`, `Readdirnames`, and `client.CreateObjectInGCSTestDir`.

## Control Flow

The test creates an explicit directory with two mounted files, opens and lists it to populate any kernel-side directory data, closes the directory handle, then creates a third object directly in GCS. It reopens the directory and expects the second listing to contain all three names in order, proving the second read was not served from stale kernel cache.

## State and Persistence Behavior

State spans mounted filesystem entries, a direct GCS object injection, and kernel directory entry cache behavior. `SetupTest` resets `testEnv.testDirPath` for `KernelListCacheTest`; suite teardown unmounts. The test intentionally mutates backing storage outside the mount to observe cache coherency.

## Dependencies and Integration Points

The file depends on package setup for `testEnv`, `mountFunc`, `mountDir`, bucket type, and generated flag sets. It integrates with static, dynamic, only-dir, and mounted-directory modes selected in `setup_test.go`.

## Risks and Test Signals

The assertions assume deterministic listing order from gcsfuse for the created names. If ordering changes, behavior may be correct but test failures would occur. Passing signal is immediate visibility of the third GCS-created object under disabled kernel list cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/disabled_kernel_list_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/finite_kernel_list_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/finite_kernel_list_cache_test.go

## Purpose

This suite validates finite kernel list cache TTL behavior. With a 5-second kernel list cache TTL, the first post-mutation listing should remain stale inside the TTL and a later listing should refresh after the TTL expires.

## Important APIs, Types, and Functions

`finiteKernelListCacheTest` mirrors the disabled/infinite suite shape with mount setup and teardown. `TestKernelListCache_CacheHitWithinLimit_CacheMissAfterLimit` uses `operations.SkipKLCTestForUnsupportedKernelVersion`, filesystem directory creation/listing, direct GCS object creation, and `time.Sleep` to bracket the TTL.

## Control Flow

The test creates two files under an explicit directory, lists the directory once, then creates `file3.txt` directly in GCS. After sleeping 2 seconds, it reopens and lists the directory and expects only the original two entries, demonstrating a kernel cache hit. After sleeping 3 more seconds, it lists again and expects all three entries, demonstrating cache expiry and refresh from gcsfuse/GCS.

## State and Persistence Behavior

The important state is kernel-held directory list data and the backing GCS object set. The file uses a single test directory per test and does not modify global configuration beyond the suite's mount flags.

## Dependencies and Integration Points

It depends on kernel support for the list-cache feature, package `setup_test.go` providing `--kernel-list-cache-ttl-secs=5 --rename-dir-limit=10`, and shared client/operations utilities. It participates in the same mounting matrix as the other kernel list cache suites.

## Risks and Test Signals

Timing is the main risk: sleeps assume TTL starts around the first listing and that 2+3 seconds crosses the 5-second boundary reliably. Passing signal is stale listing inside TTL followed by fresh listing after TTL.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/finite_kernel_list_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_delete_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_delete_dir_test.go

## Purpose

This suite checks delete-directory behavior when kernel list cache TTL is infinite and metadata caches are disabled for delete-dir consistency. It ensures cached directory listings do not prevent `RemoveAll` from deleting stale or recreated directory contents.

## Important APIs, Types, and Functions

`infiniteKernelListCacheDeleteDirTest` uses the standard mount suite hooks plus `operations.SkipKLCTestForUnsupportedKernelVersion`. Test cases use `operations.CreateDirectory`, `operations.CreateFile`, `os.Open`, `Readdirnames`, `client.CreateObjectInGCSTestDir`, `client.CreateObjectOnGCS`, and `os.RemoveAll`.

## Control Flow

`TestKernelListCache_ListAndDeleteDirectory` lists a two-file directory to seed the kernel cache, injects a third object directly into GCS, and expects `os.RemoveAll` on the directory to succeed. `TestKernelListCache_DeleteAndListDirectory` deletes a directory, recreates it on GCS with a marker and file, lists it to prove the delete invalidated cache state, then calls `RemoveAll` again successfully.

## State and Persistence Behavior

The suite mutates both mounted state and backing GCS state. The default config for this suite disables metadata positive and negative caches to avoid gcsfuse metadata cache masking kernel cache invalidation after deletes.

## Dependencies and Integration Points

It depends on package setup assigning the delete-dir run to flags `--kernel-list-cache-ttl-secs=-1 --metadata-cache-ttl-secs=0 --metadata-cache-negative-ttl-secs=0`. It integrates with GCS explicit directory objects and the kernel list cache invalidation path.

## Risks and Test Signals

The tests are sensitive to directory marker semantics and bucket type behavior. Passing signals are no errors from `RemoveAll`, fresh visibility after delete/recreate, and no stale cache entry preventing a second deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_delete_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_test.go

## Purpose

This is the broad infinite kernel list cache behavior suite. It validates that infinite TTL preserves stale listings when no local mutation invalidates the cache, and that direct parent directory entries are invalidated by file/directory create, delete, and rename operations made through the mounted filesystem.

## Important APIs, Types, and Functions

`infiniteKernelListCacheTest` owns standard suite setup and teardown. Tests exercise `os.Open`, `Readdirnames`, `os.Create`, `os.Remove`, `os.Mkdir`, `os.Rename`, `operations.CreateDirectory`, `operations.CreateFile`, and direct GCS mutation through `client.CreateObjectInGCSTestDir`.

## Control Flow

`TestKernelListCache_AlwaysCacheHit` seeds a listing, adds a GCS-only object, waits, and expects the cached two-entry listing. File mutation tests seed two entries, add a hidden GCS third entry, then create/delete/rename a mounted file and expect the next listing to refresh. `TestKernelListCache_EvictCacheEntryOfOnlyDirectParent` separately seeds parent and child directory caches, mutates only the child through the mount, injects GCS-only objects in both parent and child, then expects the parent cache to remain stale while the child cache refreshes. Directory add/delete/rename tests follow the same invalidation pattern for subdirectories.

## State and Persistence Behavior

The file is explicitly about kernel list cache state. Direct GCS writes create divergence; mounted filesystem mutations are expected to invalidate exactly the affected parent directory. Random suffixes avoid cross-test name reuse.

## Dependencies and Integration Points

It depends on the package default infinite TTL config, shared setup/client/operations helpers, and kernel support for cache behavior. It is run across configured static, dynamic, only-dir, or mounted-directory modes.

## Risks and Test Signals

The suite assumes stable lexical listing order. It also encodes precise cache invalidation semantics: over-invalidation would fail the direct-parent test, while under-invalidation would fail create/delete/rename tests. Passing signal is stale cache without local mutation and fresh cache for only the direct parent after local mutation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/infinite_kernel_list_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/setup_test.go

## Purpose

This package setup file orchestrates all kernel list cache integration suites. It defines default configs for infinite, delete-dir, finite, and disabled list cache modes, initializes shared clients/environment, and runs the package over static, dynamic, and only-dir mounting modes.

## Important APIs, Types, and Functions

It defines constants `testDirName`, `onlyDirMounted`, and `GKETempDir`; globals `mountFunc`, `mountDir`, `rootDir`, and `testEnv`; struct `env`; `TestMain`; and `overrideFilePathsInFlagSet`. `TestMain` uses setup/test-suite config readers, Cloud Storage client creation, static/dynamic/only-dir mounting utilities, and cleanup helpers.

## Control Flow

When config lacks a `KernelListCache` section, four `ConfigItem`s are created with explicit flags and `Run` selectors. The environment and storage client are initialized, mounted-directory mode is handled early, otherwise the test bucket dir is set up and GKE temp paths are rewritten for GCE. The tests first run with static mounting. If successful, dynamic mounting runs with `mountDir` pointing to `<mount>/<bucket>`. If still successful, only-dir mounting runs with `OnlyDirMountKernelListCache/` and then cleans that prefix. Final cleanup removes the main test directory.

## State and Persistence Behavior

This file owns package-global mutable mount function and mount directory state, which changes between the three execution phases. It also owns shared context, storage client, config pointer, bucket type, and current test directory path.

## Dependencies and Integration Points

It is the integration point for `test_suite.TestConfig`, bucket-type compatibility filtering, static/dynamic/only-dir mounting implementations, and all kernel list cache suite files.

## Risks and Test Signals

Because `m.Run()` is invoked multiple times in one process, package globals must be correctly reset before each phase. Path rewriting must keep log/cache/temp paths valid outside GKE. Success is all selected sub-suites passing in each mounting mode and GCS prefixes being cleaned.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/kernel_list_cache/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_dir_with_twelve_thousand_files_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_dir_with_twelve_thousand_files_test.go

## Purpose

This file stress-tests listing a directory containing 12,000 files and optional explicit and implicit subdirectories. It also checks that kernel list cache improves repeated listing latency when enabled.

## Important APIs, Types, and Functions

`listLargeDir` is a Testify suite with `flags` and `isKernelListCacheEnabled`. Helpers include `validateDirectory`, `checkIfObjNameIsCorrect`, `testdataUploadFilesToBucket`, `createFilesAndUpload`, `listDirTime`, `testdataCreateImplicitDir`, `testdataCreateExplicitDir`, and `prepareTestDirectory`. Tests cover files only, files plus explicit dirs, and files plus explicit and implicit dirs.

## Control Flow

Setup deletes any existing objects under the test name and mounts with current flags. `prepareTestDirectory` creates the mounted directory, generates 12,000 local files under `$HOME`, uploads them in batch, and optionally creates 100 explicit managed directory markers and 100 implicit directories via nested object copies. `listDirTime` records the first `os.ReadDir`, validates entry names/counts, then performs five more reads and returns the fastest repeated listing. Tests assert repeated reads are less than half the first read when kernel list cache is enabled.

## State and Persistence Behavior

Large temporary local file trees are created and removed under `$HOME`. Backing GCS state contains thousands of objects and directory markers. Kernel list cache state is inferred from repeated listing time, not direct counters.

## Dependencies and Integration Points

It uses Cloud Storage batch upload/copy/create-dir helpers, `errgroup` for explicit dir creation, goroutines with a semaphore for implicit dirs, and the package setup's static mount config. It skips implicit-dir coverage for zonal buckets.

## Risks and Test Signals

This is resource and timing heavy. Performance assertions can be noisy on busy systems, and validation assumes prefixes encode numeric ranges. Passing signals are exact entry counts/names and a clear cached-listing speedup when the kernel list cache variant runs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_dir_with_twelve_thousand_files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_large_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_large_dir_test.go

## Purpose

This package setup file configures the list-large-directory integration tests. It defines the object-name prefixes and scale constants, initializes the shared environment, and runs static-mount test suites for both kernel-list-cache and metadata-prefetch configurations.

## Important APIs, Types, and Functions

The file defines constants for file, explicit dir, and implicit dir prefixes plus counts of 12,000 files, 100 implicit dirs, and 100 explicit dirs. It defines package globals `directoryWithTwelveThousandFiles`, `mountFunc`, and `testEnv`, plus `env` and `TestMain`.

## Control Flow

`TestMain` parses setup flags, reads config, and creates a default `ListLargeDir` config when needed. The default config has one run selector for `TestListLargeDirWithKernelListCache` with `--kernel-list-cache-ttl-secs=-1` and one for `TestListLargeDirWithoutKernelListCache` with metadata prefetch. It initializes context, storage client, bucket type, and config pointer; delegates mounted-directory runs when requested; sets up the test bucket directory; sets `mountFunc` to static mounting; runs `m.Run`; and exits with the result.

## State and Persistence Behavior

Package state includes a randomized local directory name, shared storage client/context, bucket type, and selected mount function. The test bucket prefix persists only for the test run and is managed by setup utilities and suite-level delete calls.

## Dependencies and Integration Points

It integrates `test_suite` config compatibility, static mounting, Cloud Storage client lifecycle, and the list stress tests in `list_dir_with_twelve_thousand_files_test.go`.

## Risks and Test Signals

The default flag strings include comma-separated flags in the first config entries, so compatibility with `BuildFlagSets` parsing is important. Success is the test package running selected suites against a mounted test bucket without leaking the storage client.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/list_large_dir/list_large_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/create_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/create_file_test.go

## Purpose

This file tests creation and close-time synchronization of local files on a gcsfuse mount. It focuses on files that exist locally before they are uploaded to GCS and conflict behavior when the same object appears remotely.

## Important APIs, Types, and Functions

Tests are methods on `LocalFileTestSuite`. They use helper `NewFileShouldGetSyncedToGCSAtClose`, `CreateLocalFileInTestDir`, `WritingToLocalFileShouldNotWriteToGCS`, `CloseFileAndValidateContentFromGCS`, `CreateObjectInGCSTestDir`, and `operations.ValidateESTALEError`.

## Control Flow

The first two tests create new local files in the test directory and inside an explicit directory, write content without closing, verify no GCS object exists, then close and verify object contents. `TestCreateNewFileWhenSameFileExistsOnGCS` opens a local file, creates a same-name GCS object before close, writes local content, and expects close to fail with ESTALE while preserving the GCS content. `TestEmptyFileCreation` validates empty close creates an empty GCS object.

## State and Persistence Behavior

Unsynced local file handles are the main state. Data is not persisted to GCS until close, and concurrent remote creation introduces generation conflict semantics. `testDirPath` is reset per test through `setup.SetupTestDirectory`.

## Dependencies and Integration Points

This file depends on `local_file_helper.go` and shared client/operations/setup utilities. It runs under the local-file package's static, only-dir, and dynamic mounting modes and write-buffer flag variants.

## Risks and Test Signals

The conflict test assumes close detects stale remote state and does not overwrite. Passing signals are absent GCS objects before close, exact content after close, and ESTALE with preserved remote content on conflict.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/create_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/edit_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/edit_file_test.go

## Purpose

This file verifies editing and appending behavior after a newly created local file has been synchronized to GCS. It ensures subsequent open/write/append operations update remote object content correctly on close.

## Important APIs, Types, and Functions

`TestEditsToNewlyCreatedFile` and `TestAppendsToNewlyCreatedFile` use `CreateLocalFileInTestDir`, `operations.WriteWithoutClose`, `CloseFileAndValidateContentFromGCS`, `operations.OpenFile`, `WriteAt`, and `os.OpenFile` with `os.O_RDWR|os.O_APPEND`.

## Control Flow

Both tests create a local file, write `FileContents` three times, close it, and validate the concatenated object in GCS. The edit test reopens the file, writes `newContent` at offset zero, closes, and expects the prefix to be replaced while the trailing two original chunks remain. The append test reopens with append mode, writes `appendedContent`, closes, and expects the original content plus appended bytes.

## State and Persistence Behavior

The file transitions from local-only state to synced GCS object state, then back to a locally modified open handle whose final content is persisted on close. Append mode depends on current file size being correctly observed from the synced object.

## Dependencies and Integration Points

It depends on the local-file suite globals and helper utilities. It exercises writeback/edit paths under all mount modes and write buffer configurations selected by `setup_test.go`.

## Risks and Test Signals

Potential risks are sparse/truncated writes, incorrect append offset, or stale cached size after first close. Passing signals are exact GCS contents after edit and append close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/edit_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/local_file_helper.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/local_file_helper.go

## Purpose

This helper file centralizes shared state and local-file helper assertions for the local file integration package. It expresses the core contract that writes to a still-open local file are not visible in GCS until the file is closed.

## Important APIs, Types, and Functions

It defines constants `onlyDirMounted` and `testDirLocalFileTest`, package globals `testDirName`, `testDirPath`, `storageClient`, and `ctx`, plus helpers `WritingToLocalFileShouldNotWriteToGCS` and `NewFileShouldGetSyncedToGCSAtClose`.

## Control Flow

`WritingToLocalFileShouldNotWriteToGCS` writes `client.FileContents` to an open file handle without closing and immediately validates the corresponding GCS object is not found. `NewFileShouldGetSyncedToGCSAtClose` creates a local file, derives the directory name, calls the no-GCS-before-close helper, then closes and validates GCS content.

## State and Persistence Behavior

The helpers make unsynced local file-handle state explicit: write buffers are durable locally but not persisted to GCS until close. Package globals are assigned by `setup_test.go` and individual tests.

## Dependencies and Integration Points

It depends on Cloud Storage client types, shared client helpers, operations write helpers, and the local-file test suite. Nearly every local file test imports or relies on these package globals.

## Risks and Test Signals

The helpers assume object non-existence is the correct pre-close signal and that `client.GetDirName` maps mounted paths to the expected GCS test directory. Failures here usually indicate core local-file writeback contract regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/local_file_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/read_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/read_dir_test.go

## Purpose

This file tests directory listing behavior when local unsynced files, synced GCS files, explicit directories, unlinked files, and concurrent local creations coexist on a gcsfuse mount.

## Important APIs, Types, and Functions

Helpers `creatingNLocalFilesShouldNotThrowError` and `readingDirNTimesShouldNotThrowError` drive concurrent creation/listing. Tests use `os.ReadDir`, `filepath.WalkDir`, local file creation helpers, `operations.ReadDirectory`, `VerifyFileEntry`, `VerifyDirectoryEntry`, and `VerifyCountOfDirectoryEntries`.

## Control Flow

`TestReadDir` builds a mixed directory with an explicit dir containing a local file, empty local file, non-empty local file, and GCS-backed file, then validates listing sizes and types before closing local handles. `TestRecursiveListingWithLocalFiles` walks nested directories and validates local entries. `TestReadDirWithSameNameLocalAndGCSFile` creates a local file then a same-name GCS object and expects close ESTALE after listing. `TestConcurrentReadDirAndCreationOfLocalFiles_DoesNotThrowError` races 100 local file creations against 200 root listings. `TestStatLocalFileAfterRecreatingItWithSameName` validates stat after remove/recreate.

## State and Persistence Behavior

The tests exercise directory entry merging between local unsynced inode state and remote GCS object listings. Unclosed local files appear in listings with local sizes; close persists them or returns ESTALE when a remote conflict exists.

## Dependencies and Integration Points

It depends on local-file globals/helpers plus shared operations/client constants such as `ExplicitDirName`, `FileName1`, and size constants. It exercises the list/stat surfaces used by recursive filesystem clients.

## Risks and Test Signals

Directory entry order is assumed in several assertions. Concurrent test failures would signal locking/race problems. Passing signals are correct merged entries, conflict detection, no concurrent listing errors, and correct stat after recreate.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/read_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/read_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/read_file_test.go

## Purpose

This file verifies that data written to a still-open local file can be read back through the same handle before it is synchronized to GCS.

## Important APIs, Types, and Functions

`TestReadLocalFile` uses `CreateLocalFileInTestDir`, `WritingToLocalFileShouldNotWriteToGCS`, `ReadAt`, and `CloseFileAndValidateContentFromGCS`.

## Control Flow

The test creates a local file, writes `FileContents` twice without closing, constructs the expected concatenated content, reads from offset zero into a buffer of exact length, compares byte count and content, then closes and validates the combined content in GCS.

## State and Persistence Behavior

The key state is local write buffer data available through the open file handle even though the backing GCS object does not yet exist. Close is the persistence boundary.

## Dependencies and Integration Points

It depends on the local-file helper that validates no pre-close GCS object and on client constants for content and storage validation. It complements write tests by checking read-your-writes behavior before upload.

## Risks and Test Signals

The test uses same-handle `ReadAt`, so it does not cover reopening before close. Passing signal is exact local buffer readability and exact persisted content after close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/read_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/remove_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/remove_dir_test.go

## Purpose

This file tests removing directories that contain unsynced local files, alone or mixed with already synced GCS files. It verifies unlinked open files do not upload after their parent directory is removed.

## Important APIs, Types, and Functions

Tests use `operations.CreateDirectory`, `CreateLocalFileInTestDir`, `CloseFileAndValidateContentFromGCS`, `operations.RemoveDir`, `operations.ValidateNoFileOrDirError`, `operations.WriteWithoutClose`, and GCS object-not-found validators.

## Control Flow

`TestRmDirOfDirectoryContainingGCSAndLocalFiles` creates an explicit directory with one synced file and one open local file, removes the directory, verifies the path disappears, writes to the unlinked open handle, closes it successfully, and checks neither local nor synced objects remain in GCS. `TestRmDirOfDirectoryContainingOnlyLocalFiles` removes a directory with two open local files and validates closing both handles does not create GCS objects.

## State and Persistence Behavior

Directory removal unlinks open local files from namespace state. Their handles can still be written/closed, but close must not persist deleted entries. Synced entries and directory markers are deleted from GCS.

## Dependencies and Integration Points

It relies on local file helpers and shared operations for POSIX remove and validation. It covers behavior important for applications that delete trees while files are still open.

## Risks and Test Signals

The tests assume `operations.RemoveDir` handles non-empty directory semantics for this mounted filesystem. Passing signals are namespace removal, safe writes to unlinked handles, no post-close GCS creation, and deletion of synced contents.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/remove_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/rename_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/rename_test.go

## Purpose

This file tests rename behavior for local unsynced files and directories containing local files. It distinguishes supported file rename from unsupported directory rename while unsynced files are present, and verifies directory rename succeeds after sync.

## Important APIs, Types, and Functions

`verifyRenameOperationNotSupported` checks for `operation not supported`. Tests use `os.Rename`, local creation/write helpers, GCS validators, and `operations.Copy/Move`-adjacent constants such as `NewDirName`.

## Control Flow

`TestRenameOfLocalFile` creates and writes an unsynced local file, renames it, and expects the new GCS object to contain the data and the old name to disappear. `TestRenameOfDirectoryWithLocalFileFails` creates a directory with one GCS file and one unsynced local file, attempts directory rename, expects unsupported, writes more, then closes and validates the local file under its original directory. `TestRenameOfLocalFileSucceedsAfterSync` syncs first then renames the file. `TestRenameOfDirectoryWithLocalFileSucceedsAfterSync` reuses the failing setup, then renames after sync and validates both objects under the new directory.

## State and Persistence Behavior

Local file rename can force persistence under the new name. Directory rename is blocked while local unsynced children exist, then becomes a remote object move after children are synced.

## Dependencies and Integration Points

It depends on local-file package state and shared client/operations helpers. It exercises rename-dir-limit configurations from package setup.

## Risks and Test Signals

The expected unsupported error string is platform/path dependent. Passing signals are correct object movement, no overwrite of old names, and protection against renaming directories with unsynced children.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/rename_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/setup_test.go

## Purpose

This package setup file configures and runs all local file integration tests. It defines default flag matrices for local-file write behavior and runs the same suite under static, only-dir, and dynamic mounting.

## Important APIs, Types, and Functions

`TestMain` sets `testDirName`, reads or builds `cfg.LocalFile`, creates the shared storage client/context, handles mounted-directory mode, builds flag sets, sets up the test bucket directory, and invokes `static_mounting.RunTestsWithConfigFile`, `only_dir_mounting.RunTestsWithConfigFile`, and `dynamic_mounting.RunTestsWithConfigFile`. It also defines `LocalFileTestSuite` and `TestLocalFileTestSuite`.

## Control Flow

Default configs include implicit-dirs true/false, rename-dir-limit, streaming writes disabled, grpc protocol, and write block/global block limits. After environment setup, mounted-directory runs are delegated. Otherwise static mounting runs first; only-dir mounting runs if static passes; dynamic mounting runs if only-dir passes.

## State and Persistence Behavior

The file owns package-level `ctx`, `storageClient`, `testDirName`, and mount mode state consumed by all local file tests. It does not itself clean GCS after dynamic mode in this snippet, relying on mounting utilities and per-test setup helpers.

## Dependencies and Integration Points

It integrates shared setup/test-suite config, static/dynamic/only-dir mounting utilities, and Testify suite execution. It is the root lifecycle for all `local_file` test files.

## Risks and Test Signals

Multiple mount modes in one process require globals to remain coherent. Flag compatibility excludes zonal for some global-block cases. Success is all suite methods passing across selected mount variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/stat_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/stat_file_test.go

## Purpose

This file tests stat and truncate semantics for unsynced local files, including lookup through the conflicting-file-name suffix used by gcsfuse internals.

## Important APIs, Types, and Functions

Tests use `operations.VerifyStatFile`, `WritingToLocalFileShouldNotWriteToGCS`, `CloseFileAndValidateContentFromGCS`, `os.Truncate`, and `inode.ConflictingFileNameSuffix`.

## Control Flow

`TestStatOnLocalFile` creates a local file, stats size zero and permissions, writes content, stats the updated local size, then closes and validates GCS content. `TestStatOnLocalFileWithConflictingFileNameSuffix` stats `filePath + inode.ConflictingFileNameSuffix` and expects it to resolve to the local file metadata. `TestTruncateLocalFileToSmallerSize` writes content, verifies full size, truncates to `SmallerSizeTruncate`, verifies the smaller size, and validates truncated GCS content after close.

## State and Persistence Behavior

Stat observes local unsynced metadata before GCS persistence. Truncation mutates local buffered content and only persists the shortened content on close.

## Dependencies and Integration Points

It depends on gcsfuse inode conflict naming behavior, shared local file helpers, and operation validators. It covers metadata surfaces used by editors and tools that stat before close.

## Risks and Test Signals

The conflict suffix behavior is internal and can change with inode implementation. Passing signals are correct local size/permission metadata, suffix lookup support, and exact truncated persisted bytes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/stat_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/sym_link_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/sym_link_test.go

## Purpose

This file tests symlink interactions with local unsynced files: creating and reading symlinks, behavior after deleting the target, and renaming symlinks.

## Important APIs, Types, and Functions

`createAndVerifySymLink` creates a local file, writes unsynced content, creates a symlink via `operations.CreateSymLink`, validates `ReadLink`, and reads through the symlink. Tests use `os.Stat`, `os.Lstat`, `os.Rename`, and GCS validators.

## Control Flow

`TestCreateSymlinkForLocalFile` creates the symlink and closes the target, validating GCS content. `TestReadSymlinkForDeletedLocalFile` removes the target path, closes the unlinked handle without upload, then expects `os.Stat` on the symlink to return not-exist. `TestRenameSymlinkForLocalFile` renames the symlink, verifies the old symlink is gone, verifies the new symlink points to the target and reads content, then closes the target.

## State and Persistence Behavior

Symlink entries are namespace state pointing at local file paths. Removing the target unlinks the local file and prevents later GCS sync; renaming the symlink changes only link path state, not target file state.

## Dependencies and Integration Points

It depends on local-file helpers and shared symlink/readlink/readfile operation validators. It covers POSIX clients that use symlinks to open or move references to in-progress local files.

## Risks and Test Signals

Symlink support can vary by platform/mount configuration. Passing signals are successful read-through before target close, dangling symlink failure after target delete, and preserved link target after symlink rename.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/sym_link_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/unlinked_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/unlinked_file_test.go

## Purpose

This file validates behavior for unlinked local files: stat/listing exclusion, writes and sync after unlink, and reusing the same file name after deletion before or after sync.

## Important APIs, Types, and Functions

Tests use `CreateLocalFileInTestDir`, `operations.RemoveFile`, `ValidateNoFileOrDirError`, `operations.WriteWithoutClose`, `operations.SyncFile`, `CloseFileAndValidateContentFromGCS`, and GCS not-found/content validators.

## Control Flow

The first tests remove open local files and verify stat fails, listings omit unlinked entries, writes to the open handle still succeed, sync does not upload, and close does not create GCS objects. `TestFileWithSameNameCanBeCreatedWhenDeletedBeforeSync` removes and closes an unsynced file, validates no upload, then creates a same-name file and persists new content. `TestFileWithSameNameCanBeCreatedAfterDelete` syncs a file, deletes it from mount/GCS, then recreates the same name and persists new content.

## State and Persistence Behavior

Unlink separates open file handle state from directory namespace state. Once unlinked, sync/close must not persist old content. Name reuse must allocate clean new local state without stale GCS or inode conflicts.

## Dependencies and Integration Points

It depends on local file package globals and shared operation/client helpers. It covers POSIX unlink semantics critical for temp-file workflows.

## Risks and Test Signals

The test intentionally ignores one close error after deleting before sync because flush currently returns error if unlinked. Passing signals are no GCS upload for unlinked handles and correct content for recreated names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/unlinked_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/write_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/write_file_test.go

## Purpose

This file tests write ordering semantics for newly created local files, including sequential writes, random overwrites, out-of-order writes, sparse writes, and writes starting at non-zero offsets.

## Important APIs, Types, and Functions

Tests use `CreateLocalFileInTestDir`, `operations.WriteWithoutClose`, `operations.WriteAt`, `ValidateObjectNotFoundErrOnGCS`, and `CloseFileAndValidateContentFromGCS`.

## Control Flow

`TestMultipleWritesToLocalFile` writes `FileContents` three times and verifies no pre-close GCS object. `TestRandomWritesToLocalFile` writes overlapping strings at offsets 0, 2, and 3, expecting final content `stsstring3`. `TestOutOfOrderWritesToNewFile` writes two chunks then overwrites offset zero with `hello`. `TestMultipleOutOfOrderWritesToNewFile` writes at offsets 15 and 30, expecting zero-filled sparse bytes between. `TestWritesToNewFileStartingAtNonZeroOffset` writes at offset 15 before offset zero, expecting zero fill.

## State and Persistence Behavior

The local write buffer must support overwrite and sparse regions before upload. GCS persistence happens only at close and should reflect the final byte layout, including zero-filled gaps.

## Dependencies and Integration Points

It depends on local helper state and operation write helpers. It exercises local-file writeback buffering under the package's write-block-size and max-block flag variants.

## Risks and Test Signals

Expected strings encode exact sparse-byte behavior. Passing signals are absent pre-close objects and exact final GCS bytes for sequential, overlapping, out-of-order, and sparse writes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/write_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/log_rotation_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/log_rotation_test.go

## Purpose

This package setup file configures gcsfuse log rotation integration tests. It creates a log directory, rewrites GKE-style paths for GCE, builds default log rotation flag sets, and runs the package under static mounting.

## Important APIs, Types, and Functions

It defines constants for test directory, maximum file size, expected active/backup/stderr log counts, temp directory, retry timing, and shared globals `storageClient`, `ctx`, and `cfg`. `setupLogFilePath` sets the concrete log path. `TestMain` owns config, client, mount, and cleanup lifecycle.

## Control Flow

When no `LogRotation` config exists, default flags set `--log-file`, `--log-rotate-max-file-size-mb=2`, `--log-rotate-backup-file-count=2`, compression true/false, and trace severity. Mounted-directory mode is explicitly skipped. GCE setup creates the temp log directory, overrides `/gcsfuse-tmp`, builds compatible flags, points `cfg.LogFile` to the current test log path, runs static mounting tests, cleans the GCS test directory, and exits.

## State and Persistence Behavior

The setup persists active and rotated log files under `setup.TestDir()/gcsfuse-tmp`. It also creates/cleans a GCS prefix for file operations used to generate logs.

## Dependencies and Integration Points

It depends on test-suite config, Cloud Storage client creation, static mounting, path override helpers, and cleanup utilities. `logrotate_logfile_test.go` relies on `cfg.LogFile` and log count constants.

## Risks and Test Signals

The test is disabled for mounted-directory runs and assumes local access to log paths. Success is the package mounting with rotation flags and later tests observing expected rotated files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/log_rotation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/logrotate_logfile_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/logrotate_logfile_test.go

## Purpose

This file drives filesystem operations until gcsfuse rotates its log, then validates the expected active, backup, compressed/uncompressed, and stderr log file set and size limits.

## Important APIs, Types, and Functions

Helpers include `runOperationsOnFileTillLogRotation`, `runParallelOperationsInMountedDirectoryTillLogRotation`, and `validateLogFileSize`. The test uses `operations.GenerateRandomData`, `CreateFileWithContent`, `ReadFile`, `StatFile`, `ReadDirectory`, and `operations.RetryUntil`.

## Control Flow

Each worker creates a 5 MiB file and repeatedly reads it to generate trace logs. It watches `cfg.LogFile` size and exits when the active file size drops, indicating rotation. Five workers run in parallel; the outer test repeats this four times. It then reads the log directory with retry, counts the active `.log`, rotated `.log.gz` or uncompressed files, and stderr files, and validates total counts and size caps for active and uncompressed rotated logs.

## State and Persistence Behavior

State includes large test files under the mount, active log file growth, rotated backup files, and optional compressed backups. Rotation is inferred from active log size decreasing, not from a rotation API.

## Dependencies and Integration Points

It relies on constants and `cfg.LogFile` from `log_rotation_test.go`, setup mount directory state, and retry utilities. It exercises gcsfuse's internal lumberjack-style rotation behavior through real file operations.

## Risks and Test Signals

The loop can run long if logs are not generated or stat intermittently fails; one stat retry is allowed. Directory count includes stderr logs and assumes no unrelated files in the log directory. Passing signals are exactly expected log counts and size-bounded active/uncompressed logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/log_rotation/logrotate_logfile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/admin_permissions_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/admin_permissions_test.go

## Purpose

This suite tests managed-folder operations when effective permissions include admin rights at the managed-folder level or bucket level. It covers create, delete, copy, move, and listing behavior across several bucket/managed-folder permission combinations.

## Important APIs, Types, and Functions

`managedFoldersAdminPermission` tracks `bucketPermission`, `managedFoldersPermission`, and flags. Setup mounts, creates the non-empty managed-folder structure, optionally grants managed-folder IAM roles, and waits for propagation. Tests use `os.Create`, `os.Remove`, `os.RemoveAll`, `operations.CopyFile`, `operations.CopyDir`, `operations.Move`, `operations.StatFile`, and `listNonEmptyManagedFolders`.

## Control Flow

For each flag set, `TestManagedFolders_FolderAdminPermission` first grants bucket admin permission, then iterates permission cases: bucket admin with nil/view/admin managed-folder roles and bucket view with managed-folder admin. It adjusts bucket IAM when needed, sets bucket/testDir path for the mount mode, and runs the suite. Test methods validate object creation/deletion, managed-folder deletion hiding empty folders, copy/move of objects and directories, and listing. Directory copy/move is expected to fail read-only when bucket permission is view despite managed-folder admin.

## State and Persistence Behavior

State includes IAM bindings on buckets and managed folders, managed folder resources created through the Storage Control API, copied test objects, and mounted namespace mutations. Cleanup revokes bindings and removes resources, with special handling when bucket view permission prevents broad cleanup.

## Dependencies and Integration Points

It depends on `test_helper.go`, credentials helpers, Cloud Storage/Storage Control clients, and package mount setup. It only runs static mount via `setup.RunTestsOnlyForStaticMount`.

## Risks and Test Signals

IAM propagation is handled by a fixed 60-second sleep and can still be flaky. Permission union semantics are central. Passing signals are successful admin operations where allowed and read-only failures where bucket-level view blocks broader directory operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/admin_permissions_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/list_empty_managed_folders_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/list_empty_managed_folders_test.go

## Purpose

This suite verifies that empty managed folders are visible when gcsfuse is mounted with `--enable-empty-managed-folders`. It checks managed folders, simulated folders, and files in one directory tree.

## Important APIs, Types, and Functions

`enableEmptyManagedFoldersTrue` is a Testify suite. Helper `createDirectoryStructureForEmptyManagedFoldersTest` creates two Storage Control managed folders, a simulated folder through the mount, and a file. `TestListDirectoryForEmptyManagedFolders` uses `filepath.WalkDir` and `os.ReadDir` to validate entries.

## Control Flow

Each test sets up `EmptyManagedFoldersTest`, creates two empty managed folder resources, creates an empty simulated folder and a file through the mounted filesystem, then walks the root test directory. At the root it expects four entries: the two empty managed folders as directories, simulated folder as directory, and file as non-directory. Inside each folder it expects zero entries.

## State and Persistence Behavior

The test creates managed-folder control-plane resources and mounted filesystem objects. Teardown deletes managed folders and cleans the GCS test directory. Empty managed folders have no object children but should persist as visible directory entries due to the mount flag.

## Dependencies and Integration Points

It depends on `testEnv.controlClient`, `testEnv.storageClient`, setup bucket/mount path translation, and shared client/operations helpers. It is selected by the managed-folder package default config run `TestEnableEmptyManagedFoldersTrue`.

## Risks and Test Signals

Listing order is assumed by index-based assertions. The test also assumes empty managed folder support is enabled and not hidden by bucket type behavior. Passing signal is root visibility of empty managed folders and empty listings inside them.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/list_empty_managed_folders_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/managed_folders_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/managed_folders_test.go

## Purpose

This package setup file orchestrates managed-folder integration tests. It creates storage and control clients, temporary service-account credentials, default flag configurations for view/admin/empty-managed-folder suites, and runs tests across static, dynamic, and only-dir mounting modes.

## Important APIs, Types, and Functions

It defines `env` with context, clients, bucket type, config, mount function/directories, service account/key path, bucket/testDir, and testDirPath. `TestMain` uses setup/test-suite config, credentials helpers, static/dynamic/only-dir mounting utilities, and cleanup.

## Control Flow

Default configs include key-file-based view-permission flags, `--enable-empty-managed-folders`, and key-file/stat-cache-disabled admin-permission flags. `TestMain` initializes clients, creates credentials, substitutes `${KEY_FILE}` in flags, skips mounted-directory mode, sets up test bucket dir, then runs static tests. If successful, it runs dynamic mount with mountDir pointing to the bucket under the mount root. If still successful, it runs only-dir mount and cleans that prefix. Finally it cleans the main managed-folder test prefix and exits.

## State and Persistence Behavior

This file owns service-account credential file lifecycle, shared clients, mount mode globals, and bucket cleanup. Managed-folder resources and IAM bindings are mostly created/removed in helper and suite files.

## Dependencies and Integration Points

It integrates Cloud Storage data APIs, Storage Control managed-folder APIs, credential generation, key-file flag substitution, and all managed-folder suites.

## Risks and Test Signals

Temporary credentials must be removed and IAM changes cleaned even on failures. Multiple `m.Run()` phases mutate global mount state. Success is all selected suites passing in each mount mode and cleanup of GCS/control-plane resources.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/managed_folders_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/test_helper.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/test_helper.go

## Purpose

This helper file provides common managed-folder IAM, directory creation, cleanup, listing, and read-only error assertion utilities used by the managed-folder suites.

## Important APIs, Types, and Functions

It defines managed-folder constants, `FileInNonEmptyManagedFoldersTest`, `IAMPolicy`, and helpers `providePermissionToManagedFolder`, `revokePermissionToManagedFolder`, `createDirectoryStructureForNonEmptyManagedFolders`, `cleanup`, `listNonEmptyManagedFolders`, `copyDirAndCheckErrForViewPermission`, `copyObjectAndCheckErrForViewPermission`, `moveAndCheckErrForViewPermission`, and `createFileForTest`.

## Control Flow

IAM grant writes a temporary JSON policy and runs `gcloud storage managed-folders set-iam-policy`; revoke uses `gcloud storage managed-folders remove-iam-policy-binding` and tolerates missing binding/folder errors. Directory creation deletes any prior test prefix, creates a temp source file, creates two managed folders with Storage Control, copies one file into each, creates a simulated folder with a copied file, and copies one root file. Listing walks the mounted tree and validates the root has two managed folders, one simulated folder, and one file, with each child folder containing one file.

## State and Persistence Behavior

Helpers create IAM policy files, managed-folder resources, GCS objects, and mounted namespace state. Cleanup revokes IAM bindings, deletes managed folders, and removes GCS prefixes.

## Dependencies and Integration Points

It depends on `gcloud`, Cloud Storage and Storage Control clients, setup path translation, and shared operations. View-permission helpers normalize expected read-only filesystem errors for copy/move operations.

## Risks and Test Signals

The listing helper has index-based assumptions and a few error messages reference `objs[3]` even in child contexts, which could obscure diagnostics. IAM relies on external gcloud behavior. Passing signals are correct managed-folder visibility and read-only failures where expected.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/test_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/view_permissions_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/view_permissions_test.go

## Purpose

This suite validates managed-folder behavior when the effective permission is view-only. It ensures listing succeeds while create, delete, copy, and move operations fail with read-only filesystem errors.

## Important APIs, Types, and Functions

`managedFoldersViewPermission` embeds Testify suite and stores flags. Test methods use `listNonEmptyManagedFolders`, `os.Create`, `os.Remove`, `os.RemoveAll`, `moveAndCheckErrForViewPermission`, `copyDirAndCheckErrForViewPermission`, and `copyObjectAndCheckErrForViewPermission`. The suite function applies and revokes IAM roles using `creds_tests`.

## Control Flow

`TestManagedFolders_FolderViewPermission` grants objectViewer on the bucket, creates the non-empty managed-folder structure, runs the suite with nil managed-folder permissions, grants objectViewer on each managed folder, waits 60 seconds, then runs the suite again. Tests list non-empty managed folders and attempt object creation, object deletion, non-empty managed-folder deletion, moving/copying folders, moving/copying objects within a managed folder, and moving/copying objects out of managed folders; all writes are expected to fail read-only.

## State and Persistence Behavior

State includes bucket and managed-folder IAM bindings, managed-folder resources, GCS files, and mounted namespace attempts. View permission should permit reads/lists but not persist namespace mutations.

## Dependencies and Integration Points

It depends on helpers in `test_helper.go`, credential utilities, and package setup for key-file mounting. It exercises authorization through the service account key passed to gcsfuse.

## Risks and Test Signals

Fixed IAM propagation sleep can be flaky. If gcsfuse maps authorization failures to different errors, read-only checks may fail. Passing signals are successful listing and consistent read-only errors for all mutating operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/managed_folders/view_permissions_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/buffered_read_prom_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/buffered_read_prom_test.go

## Purpose

This skipped-by-default suite is intended to verify Prometheus metrics for buffered read behavior, including buffered read byte/latency metrics and fallback reasons for random-read detection and insufficient memory.

## Important APIs, Types, and Functions

`PromBufferedReadTest` embeds `PromTestBase`. Tests use `operations.ReadFile`, `operations.CreateFileOfSize`, `operations.OpenFileAsReadonly`, `io.ReadAll`, and the shared metric assertions `assertNonZeroCountMetric` and `assertNonZeroHistogramMetric`.

## Control Flow

`TestBufferedReadMetrics` reads `hello.txt` and expects GCS read/download byte counters and `buffered_read/read_latency`. `TestRandomReadFallback` creates a 16 MiB file and performs three decreasing-offset `ReadAt` calls so the third exceeds `--read-random-seek-threshold=2`, then expects `buffered_read_fallback_trigger_count{reason=random_read_detected}`. `TestInsufficientMemoryFallback` creates a 40 MiB file, opens two handles, reads all from the first to exhaust global blocks, then reads from the second and expects fallback reason `insufficient_memory`. `TestPromBufferedReadSuite` currently calls `t.SkipNow()` before running flag sets.

## State and Persistence Behavior

The tests create large files under the mounted test directory and inspect in-process Prometheus counters/histograms exposed by the mounted gcsfuse process. Buffered reader memory pool state is part of the behavior under test.

## Dependencies and Integration Points

It depends on monitoring setup flags enabling buffered read with specific block and memory limits, shared Prometheus parser/assertions, and static mounting.

## Risks and Test Signals

Because the suite is unconditionally skipped, it does not currently provide CI signal. If enabled, memory/fallback behavior may be sensitive to read scheduling and block accounting. Expected signal is non-zero buffered read and fallback metrics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/buffered_read_prom_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/kernel_reader_prom_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/kernel_reader_prom_test.go

## Purpose

This suite verifies Prometheus metrics emitted by the kernel reader / multi-range downloader path for zonal buckets.

## Important APIs, Types, and Functions

`PromKernelReaderTest` embeds `PromTestBase`. `TestKernelReaderMetrics` uses `client.SetupFileInTestDirectory`, `os.ReadFile`, and shared Prometheus metric assertion helpers.

## Control Flow

The test creates a 10 MiB file in a per-test GCS directory, reads it through the mount, then asserts non-zero filesystem read count, parallel GCS download/read byte and read counters, and GCS request count/latency for `MultiRangeDownloader::Add`. `TestPromKernelReaderSuite` builds matching flag sets, parses the Prometheus port from flags, and runs the suite.

## State and Persistence Behavior

State includes a large GCS object and Prometheus counters/histograms exposed by the mounted gcsfuse process. Each test uses a sanitized per-test directory name.

## Dependencies and Integration Points

It depends on monitoring setup config entry `--prometheus-port=9193` for zonal buckets and default kernel reader behavior. It uses shared setup/client and metric parsing utilities.

## Risks and Test Signals

The suite is compatible only with zonal bucket runs in default config. If file size or reader thresholds change, the read may not use the parallel path. Passing signal is non-zero parallel read and MultiRangeDownloader metrics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/kernel_reader_prom_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_test.go

## Purpose

This suite validates general gcsfuse Prometheus/OTel metrics for stat, list, xattr error, read, file-cache, GCS request, and reader counters.

## Important APIs, Types, and Functions

`PromTest` embeds `PromTestBase`. Tests call `os.Stat`, `os.ReadDir`, `xattr.Set`, `os.ReadFile`, and shared `assertNonZeroCountMetric`/`assertNonZeroHistogramMetric`.

## Control Flow

`TestStatMetrics` stats `hello.txt` and expects `LookUpInode`, `StatObject`, and latency metrics. `TestFsOpsErrorMetrics` stats a missing file and expects filesystem error and latency metrics. `TestListMetrics` lists the test directory and expects `ReadDir`, `OpenDir`, and `ListObjects` metrics. `TestSetXAttrMetrics` attempts unsupported xattr set and expects an `Others` fs error. `TestReadMetrics` reads `hello.txt` and expects file-cache sequential read, cache miss, open/read fs ops, NewReader request, reader open/close, download bytes, and latency metrics. The suite runner iterates flag sets and parses ports.

## State and Persistence Behavior

Metrics are cumulative process state exposed on `/metrics`. Each test starts with a prepared `hello.txt`, but counters may include prior tests; assertions only require non-zero matching samples.

## Dependencies and Integration Points

It depends on monitoring setup, Prometheus text parser, xattr package, and static mounting with file cache enabled. It exercises both flat and HNS/zonal port variants through config.

## Risks and Test Signals

Metric names/labels are tightly coupled to instrumentation. Counters being cumulative can mask per-test missing increments if earlier tests set the same labels. Passing signal is presence of non-zero expected metric families and labels after operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_w_grpc_metrics_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_w_grpc_metrics_test.go

## Purpose

This suite verifies gRPC client metrics are exported when gcsfuse is mounted with gRPC protocol and experimental gRPC metrics enabled.

## Important APIs, Types, and Functions

`PromGrpcMetricsTest` embeds `PromTestBase`. `TestStorageClientGrpcMetrics` reads `hello.txt` and checks gRPC metric families with shared count/histogram assertion helpers. `TestPromGrpcMetricsSuite` skips when not running in a mounted-directory/GKE environment.

## Control Flow

The test reads the prepared file, then asserts `grpc_client_attempt_started` for the expected storage method: `BidiReadObject` for zonal buckets and `ReadObject` otherwise. It also asserts generic attempt started plus attempt duration, call duration, received compressed message size, and sent compressed message size histograms.

## State and Persistence Behavior

State is Prometheus metric state in the mounted gcsfuse process and the GCS object read. No test-specific persistence beyond the prepared file is introduced.

## Dependencies and Integration Points

It depends on monitoring setup flags with `--client-protocol=grpc --experimental-enable-grpc-metrics=true`, gRPC storage client instrumentation, and mounted-directory mode. Default suite skips on GCE VM static runs.

## Risks and Test Signals

Metric names are from gRPC instrumentation and can change. The environment skip means local/static test runs do not validate this path. Passing signal is non-zero gRPC attempt and histogram metrics after a read.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_w_grpc_metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/setup_test.go

## Purpose

This package setup file provides the shared Prometheus monitoring test harness. It configures default monitoring flag sets, mounts gcsfuse with log/cache path rewriting, prepares per-test files, fetches `/metrics`, and provides metric assertion helpers.

## Important APIs, Types, and Functions

It defines `env`, `testEnv`, `mountFunc`, and `PromTestBase`. Shared helpers include `mountGCSFuseAndSetupTestDir`, `parsePortFromFlags`, `parsePromFormat`, `assertNonZeroCountMetric`, and `assertNonZeroHistogramMetric`. `TestMain` configures seven default monitoring entries.

## Control Flow

`PromTestBase.SetupSuite` sets per-suite log path and mounts. `SetupTest` sanitizes the test name, creates a GCS directory, and writes `hello.txt`. Metric parsing performs HTTP GET against `localhost:<port>/metrics` and parses Prometheus text format. Assertions scan metric families for matching type, label, and non-zero values. `TestMain` builds defaults for OTel/file cache, buffered read, gRPC metrics, and kernel reader with distinct ports, initializes storage, delegates mounted-directory runs, otherwise sets up test bucket, rewrites temp paths, runs static mounting tests, cleans the monitoring prefix, and exits.

## State and Persistence Behavior

It owns the mounted gcsfuse process exposing Prometheus state, test GCS objects under `monitoring`, log/cache directories, and shared storage client/context. Metrics are cumulative across suite lifetime.

## Dependencies and Integration Points

It depends on Cloud Storage clients, static mounting, setup/test-suite config, Prometheus `expfmt`, client model types, and Testify suite/require. All monitoring test files use this harness.

## Risks and Test Signals

Port collisions, stale metrics, and cumulative counters can affect assertions. Path override is required for GCE. Success is mount startup with metrics endpoint reachable and expected metric families non-zero after filesystem actions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/gcsfuse_mount_timeout_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/gcsfuse_mount_timeout_test.go

## Purpose

This file implements mount latency tests across bucket locations and client protocols. It measures repeated gcsfuse mount/unmount cycles and asserts the best observed mount time is below environment-specific thresholds.

## Important APIs, Types, and Functions

Types include `RegionWiseTimeouts`, `ZBMountTimeoutTestCaseConfig`, `MountTimeoutTest`, `NonZBMountTimeoutTest`, and `ZBMountTimeoutTest`. Core helpers are `SetupTest`, `TearDownTest`, `mountOrTimeout`, and `unmountAndWait`. Tests cover multi-region, dual-region, single-region, same-zone zonal, and cross-zone zonal buckets.

## Control Flow

`TestMountTimeout` chooses zonal or non-zonal suites based on `setup.IsZonalBucketRun()` and the `TEST_ENV` value set by package setup. Non-zonal GCE us-central uses strict region thresholds; other GCE regions use relaxed thresholds; non-GCE skips. `mountOrTimeout` constructs gcsfuse args with client protocol, trace logging, and log file, mounts/unmounts ten times, tracks the minimum duration, saves the log artifact on error, and fails if the minimum exceeds expected. `unmountAndWait` calls util unmount and polls `/proc/mounts` for up to five seconds.

## State and Persistence Behavior

Each test creates a temporary mount directory and log file path. It repeatedly mounts real buckets and immediately unmounts, leaving no intended bucket data. Timing state is in-memory, while logs persist as artifacts on failure.

## Dependencies and Integration Points

It depends on the built or installed gcsfuse binary, fusermount on Linux, bucket accessibility checks, cfg protocol constants, and package globals from `mount_timeout_test.go`.

## Risks and Test Signals

Latency tests are inherently environment-sensitive; they mitigate variance by using the minimum of ten attempts. Bucket accessibility, network, and `/proc/mounts` polling can affect results. Passing signal is all accessible buckets mounting under thresholds for selected protocols.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/gcsfuse_mount_timeout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_access_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_access_test.go

## Purpose

This suite verifies that gcsfuse can mount a bucket using a service account that has only minimal list permission on the bucket, validating the mount-time permission requirement.

## Important APIs, Types, and Functions

`MountAccessTest` mirrors the mount-timeout binary harness with `gcsfusePath` and temp `dir`. `mountWithKeyFile` mounts with `--key-file`, trace log, and configured log file, then unmounts via `unmountAndWait`. `TestMountingWithMinimalAccessSucceeds` creates credentials and applies a custom role.

## Control Flow

The test checks bucket access with the default storage client, creates a temporary service account/key, grants custom role `storage.objects.list` on the bucket, mounts using the key file, unmounts, then revokes the role and removes the key. `TestMountAccess` sets a log file and runs the suite.

## State and Persistence Behavior

State includes temporary credentials, an IAM binding for the custom role, a temp mount directory, and logs saved as artifacts on mount failure. No object data is intentionally created.

## Dependencies and Integration Points

It depends on credentials helpers, custom-role IAM helpers, the gcsfuse binary built by package setup, and the shared `unmountAndWait` helper from `gcsfuse_mount_timeout_test.go`.

## Risks and Test Signals

IAM propagation and custom role existence are external prerequisites. The test only checks mount success, not later file operations. Passing signal is mount/unmount success with list-only credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_access_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_timeout_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_timeout_test.go

## Purpose

This package setup file initializes mount-timeout and mount-access tests. It builds or locates gcsfuse, detects the execution environment, creates a storage client, and skips unsupported mounted-directory/GKE scenarios.

## Important APIs, Types, and Functions

Globals include `gBuildDir`, `gFusermountPath`, `gStorageClient`, `gCtx`, and `testBucket`. Constants define environment labels, bucket names, expected timeout thresholds, zonal bucket names, relaxed timeout, and log prefix. `findTestExecutionEnvironment` uses OpenTelemetry GCP resource detection. `TestMain` owns binary/client lifecycle.

## Control Flow

`findTestExecutionEnvironment` detects cloudtop/non-GCE via hostname, non-zonal GCE region via `cloud.region`, and zonal GCE via `cloud.availability_zone`, returning labels consumed by `TestMountTimeout`. `TestMain` parses flags, finds `fusermount` on Linux, reads config, skips mounted-directory runs, creates storage client, sets `TEST_ENV`, and either uses installed gcsfuse by setting `gBuildDir="/"` or builds gcsfuse into a temp directory via `util.BuildGcsfuse`. It runs tests, removes the build dir, and exits.

## State and Persistence Behavior

The file persists a temporary build directory and process environment variable `TEST_ENV` for the package. It owns the shared storage client and test bucket name.

## Dependencies and Integration Points

It depends on setup/test-suite config, `exec.LookPath`, OpenTelemetry GCP resource detector, Cloud Storage client helpers, and gcsfuse build utilities. Other mount_timeout files rely on its globals.

## Risks and Test Signals

Environment detection controls whether latency tests run or skip; detector failures can skip or relax coverage. Installed-package mode assumes binary layout rooted at `/`. Success is successful setup, binary availability, and correct environment label for downstream tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mount_timeout/mount_timeout_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_darwin_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_darwin_test.go

## Purpose

This Darwin-specific mounting test verifies `statfs` values exposed by a mounted canned gcsfuse filesystem on macOS.

## Important APIs, Types, and Functions

`convertStatfsString` converts NUL-terminated `[]int8` mount source bytes into a Go string. `GcsfuseTest.Statfs` mounts the canned bucket, calls `syscall.Statfs`, and checks block, inode, IO size, and mount source fields.

## Control Flow

The test mounts `canned.FakeBucketName` at the suite temp dir using `runGcsfuse`, defers unmount, then performs `syscall.Statfs`. It verifies available byte calculations do not overflow, total bytes are at least 1 TiB, blocks/free/available are equal, inode count is large and free equals total, IO size is 1 MiB, and the filesystem name matches the fake bucket name.

## State and Persistence Behavior

State is limited to a temporary mount point and kernel statfs data from the mounted FUSE filesystem. No bucket or file mutations are performed.

## Dependencies and Integration Points

It depends on `GcsfuseTest` from `gcsfuse_test.go`, the canned bucket implementation, Darwin `syscall.Statfs_t` fields, and `util.Unmount`.

## Risks and Test Signals

This file is build-target specific and field names differ from Linux. Passing signal is a mounted filesystem reporting reasonable capacity/inode metadata and correct mount source name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_darwin_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_linux_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_linux_test.go

## Purpose

This Linux-specific mounting test verifies `statfs` values exposed by a mounted canned gcsfuse filesystem on Linux.

## Important APIs, Types, and Functions

`GcsfuseTest.Statfs` mounts the canned bucket, calls `syscall.Statfs`, and checks `Frsize`, `Blocks`, `Bfree`, `Bavail`, `Files`, `Ffree`, and `Bsize`.

## Control Flow

The test mounts `canned.FakeBucketName`, defers unmount, calls `syscall.Statfs`, asserts fragment size is non-zero, checks byte-capacity multiplication cannot overflow and represents at least 1 TiB, validates all blocks are free/available, validates a large free inode count, and expects block size/recommended IO size of 1 MiB.

## State and Persistence Behavior

State is only the temporary mount and kernel statfs response. It does not write to the filesystem.

## Dependencies and Integration Points

It depends on the shared `GcsfuseTest` harness, Linux syscall layout, canned bucket, and unmount utility. It complements the Darwin-specific statfs file.

## Risks and Test Signals

Any change to advertised capacity, inode, or block size policy will break assertions. Passing signal is a Linux FUSE mount with sane capacity and IO-size metadata.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_linux_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_test.go

## Purpose

This is the main gcsfuse command integration suite using a canned fake bucket. It validates CLI usage errors, mount preconditions, credential path handling, read/write modes, file/dir modes, uid/gid, implicit and only-dir mounts, foreground behavior, version/help flags, and relative/tilde path expansion for log/key files.

## Important APIs, Types, and Functions

`GcsfuseTest` is an ogletest suite with `gcsfusePath` and temp `dir`. Helpers `gcsfuseCommand`, `runGcsfuseWithEnv`, and `runGcsfuse` execute the built binary with a PATH containing `fusermount`. `createTestFilesForRelativePathTesting` prepares files in cwd and home for path expansion tests.

## Control Flow

Bad usage cases run gcsfuse and match exit errors/output. Mount tests cover nonexistent mount point, mount point as file, missing key file via flag/env, canned contents, read-only write failure, read-write overwrite, custom modes, uid/gid, implicit dirs, only-dir with explicit/implicit/trailing slash paths, relative mount point, foreground process lifecycle, version/help success, and log/key file path variants. Foreground mode reads stderr until a successful mount message, checks the process remains alive, unmounts, and expects clean exit.

## State and Persistence Behavior

The suite creates temp mount directories and temporary key/log path test files. Canned bucket data is in-process fake storage; write tests mutate the mounted view. Mounts are unmounted after each success.

## Dependencies and Integration Points

It depends on `main_test.go` for binary build/fusermount path, `internal/canned` fake bucket data, jacobsa ogletest/matchers, fusetesting directory reads, and `tools/util.Unmount`.

## Risks and Test Signals

Output message regexes and CLI error text are version-sensitive. Path expansion tests use real cwd/home files as dummy key/log files. Passing signal is correct command behavior and mounted canned filesystem semantics across all flag combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/gcsfuse_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/main_test.go

## Purpose

This package setup file initializes the canned mounting integration tests. It parses flags, finds fusermount, reads config, skips mounted-directory runs, and builds or locates the gcsfuse binaries used by `gcsfuse_test.go` and `mount_helper_test.go`.

## Important APIs, Types, and Functions

Globals `gBuildDir` and `gFusermountPath` are shared by the package. `TestMain` uses `setup.ParseSetUpFlags`, `test_suite.ReadConfigFile`, `exec.LookPath`, `setup.TestInstalledPackage`, and `util.BuildGcsfuse`.

## Control Flow

After parsing flags, Linux runs locate `fusermount`. If no `Mounting` config exists, one is synthesized from test bucket and mounted directory flags. Mounted-directory mode exits early because these tests build/mount their own canned bucket. Installed-package mode sets `gBuildDir="/"` and runs tests. Otherwise a temp build directory is created, gcsfuse is built into it, tests run, the directory is removed, and the process exits with the test code.

## State and Persistence Behavior

State includes a temporary build directory containing `bin/gcsfuse` and `sbin/mount.*` helpers, plus the fusermount path. The directory is removed after tests unless installed-package mode is used.

## Dependencies and Integration Points

It is the lifecycle root for the mounting package and provides globals consumed by the command and mount-helper suites. It integrates setup/test-suite config with local binary build utilities.

## Risks and Test Signals

Build failures or missing fusermount abort the package. Installed-package mode assumes helper/binary paths under `/`. Success is a usable binary/helper layout for downstream mounting tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/mount_helper_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/mount_helper_test.go

## Purpose

This suite tests the OS mount helper binaries (`mount_gcsfuse`, `mount.gcsfuse`, and Linux `mount.fuse.gcsfuse`) using a canned bucket. It validates helper argument parsing, option filtering, read-only mode, relative mount points, mode options, implicit dirs, and fuse subtype support.

## Important APIs, Types, and Functions

`MountHelperTest` is an ogletest suite with `helperPath` and temp `dir`. Helpers `mountHelperCommand` and `mount` execute the helper with PATH set to the built gcsfuse binary directory. Tests include `BadUsage`, `NoMtabFlag`, `SuccessfulMount`, `RelativeMountPoint`, `ReadOnlyMode`, `ExtraneousOptions`, `LinuxArgumentOrder`, `FuseSubtype`, `ModeOptions`, and `ImplicitDirs`.

## Control Flow

Setup selects helper path by OS. Bad usage checks too few/many args and trailing `-o`. Mount tests invoke helpers with canned bucket and temp dir, then inspect files or write failures. Option tests ensure `-n` is ignored, mount-style noise options are filtered, Linux `-o ro` at the end works, mode options map to file/dir modes, and implicit dirs are visible when requested.

## State and Persistence Behavior

Each test mounts a canned filesystem at a temp directory and unmounts it after validation. No persistent remote state is used. Helper path changes temporarily for Linux fuse subtype.

## Dependencies and Integration Points

It depends on the build layout from `main_test.go`, canned fake bucket data, `tools/util.Unmount`, ogletest/matchers, and OS-specific mount helper naming conventions.

## Risks and Test Signals

Helper output strings and mount option parsing behavior are tightly asserted. Passing signal is successful helper-mediated mounting and correct translation/filtering of mount-style options into gcsfuse behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/mount_helper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/disabled_negative_stat_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/disabled_negative_stat_cache_test.go

## Purpose

This suite verifies negative stat cache disabled behavior. When negative metadata cache TTL is zero, a file that was missing should become visible immediately after a same-name object is created directly in GCS.

## Important APIs, Types, and Functions

`disabledNegativeStatCacheTest` stores flags and a per-test directory name. Setup mounts with package `testEnv.mountFunc`, sets mount dir, and creates a randomized test directory. The test uses `os.OpenFile`, `operations.CreateDirectory`, and `client.CreateObjectInGCSTestDir`.

## Control Flow

The test creates an explicit directory, attempts to open `file1.txt` read-only and expects a no-such-file error, creates the object in GCS under the same path, then immediately opens the file again through the mount. With negative stat cache disabled, the second open should query GCS and succeed.

## State and Persistence Behavior

State is a previously cached negative lookup candidate plus a direct GCS object insertion. Randomized `s.testDir` avoids cross-test cache contamination. The successful file handle is closed at the end.

## Dependencies and Integration Points

It depends on the negative_stat_cache package setup for mount configuration and flag sets, plus shared setup/client/operations helpers. It runs in mounted-directory or configured GCE mode.

## Risks and Test Signals

The expected error string includes the path and `no such file or directory`. Passing signal is immediate visibility of a GCS-created object after an initial miss.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/disabled_negative_stat_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/finite_int_negative_stat_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/finite_int_negative_stat_cache_test.go

## Purpose

This suite verifies finite negative stat cache behavior. With a finite negative TTL, a missing-file lookup should remain cached briefly after the object appears in GCS, then refresh after the TTL expires.

## Important APIs, Types, and Functions

`finiteNegativeStatCacheTest` mirrors the disabled suite with per-test randomized directory state. `TestFiniteNegativeStatCache` uses `operations.CreateDirectory`, `os.OpenFile`, `client.CreateObjectInGCSTestDir`, and `time.Sleep`.

## Control Flow

The test creates an explicit directory and attempts to open a missing file, expecting no-such-file. It then creates the object directly in GCS, immediately opens the file again and still expects no-such-file because the finite negative cache should answer. After sleeping 5 seconds, it opens again and expects success.

## State and Persistence Behavior

The behavior under test is negative metadata cache state inside gcsfuse. Direct GCS insertion creates divergence from the cached miss. The sleep duration is intended to cross the configured negative cache TTL.

## Dependencies and Integration Points

It depends on package setup selecting a finite negative stat cache TTL and shared mount/client utilities. It complements the disabled-cache test to validate both immediate refresh and stale-negative behavior.

## Risks and Test Signals

Timing is the main risk; the test assumes 5 seconds is enough for expiry. Error-string assertions are path-sensitive. Passing signals are miss, cached miss after remote creation, and successful open after TTL expiry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/finite_int_negative_stat_cache_test.go -->
