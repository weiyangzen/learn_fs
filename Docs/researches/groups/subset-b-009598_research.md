# subset-b-009598 grouped research

This grouped report covers GCSFuse integration tests for negative stat caching, baseline filesystem operations, rapid appends, and read cache behavior. Each section is wrapped for deterministic reconciliation into the mapped per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/infinite_negative_stat_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/infinite_negative_stat_cache_test.go

Purpose: Defines the testify suite for infinite negative metadata stat cache behavior, specifically `--metadata-cache-negative-ttl-secs=-1`. It verifies that a path negatively cached as absent remains hidden from gcsfuse even after external creation in GCS, and that externally created directories can provoke `EEXIST` on later mkdir.

Important APIs/types/functions: `infiniteNegativeStatCacheTest` embeds `suite.Suite` and carries the active flag set plus randomized test directory. `SetupSuite` mounts using `testEnv.mountFunc`; `SetupTest` creates a unique `NegativeStatCacheTest...` directory; `TestInfiniteNegativeStatCache` uses `os.OpenFile`, `client.CreateObjectInGCSTestDir`, and error-string assertions; `TestAlreadyExistFolder` uses `os.Stat`, `client.CreateFolderInBucket` or `client.CreateObjectOnGCS`, and `os.Mkdir`; `TestInfiniteNegativeStatCacheTest` iterates config-built flag sets.

Control flow: each suite run mounts once, creates a fresh directory per test, exercises POSIX calls through the mount, mutates the bucket out of band, then asserts stale negative state. The runner short-circuits for pre-mounted GKE directories or loops over compatible config items otherwise.

State/persistence: test state is split between mounted filesystem paths and direct GCS objects/folders. Infinite negative cache is intentionally persistent across operations within the same mount. Teardown saves logs on failure and unmounts in suite teardown.

Dependencies/integration: Uses shared `setup`, `operations`, `client`, storage-control client support for hierarchical buckets, and testify. It depends on the package-level `testEnv` initialized by `setup_test.go`.

Risks/test signals: Error-string matching in the first test is path-format sensitive. The second test branches on bucket type, making HNS/flat behavior explicit. A passing run signals correct negative-cache TTL semantics and EEXIST behavior under out-of-band mutations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/infinite_negative_stat_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/setup_test.go

Purpose: Provides package-wide setup for negative stat cache tests, including fallback config generation, global clients, mount-mode selection, and cleanup.

Important APIs/types/functions: constants `testDirName` and `onlyDirMounted`; `env` centralizes mount function, mount/root paths, storage clients, context, config, bucket type, and active test directory; `TestMain` orchestrates the full package lifecycle. Fallback config defines disabled, finite, and infinite negative TTL runs via `test_suite.ConfigItem.Run`.

Control flow: `TestMain` parses flags, reads config, synthesizes config if absent, initializes `context.Background`, discovers bucket type via `setup.TestEnvironment`, creates data and control storage clients, handles GKE mounted-directory mode, then runs static, dynamic, and only-dir mount passes sequentially. It stops on first nonzero test code and exits with the final code.

State/persistence: `testEnv` is shared by all package test files. Static and dynamic mount modes reuse root directories differently; only-dir mode sets `setup.OnlyDirMounted` and later removes the only-dir prefix from GCS. Storage clients are closed with deferred callbacks.

Dependencies/integration: Integrates with Google Cloud Storage data/control APIs, `static_mounting`, `dynamic_mounting`, `only_dir_mounting`, and common setup/config helpers.

Risks/test signals: Sequential `m.Run()` calls rely on test packages being written to tolerate repeated runs with different mount state. Cleanup must include both normal and only-dir prefixes or later package passes may observe stale objects. The config compatibility matrix is the key signal that all bucket types are intended for these tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/copy_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/copy_dir_test.go

Purpose: Exercises recursive directory copy behavior through a mounted GCSFuse filesystem for populated and empty source directories copied into nonexistent, empty, and non-empty destinations.

Important APIs/types/functions: `createSrcDirectoryWithObjects` builds `srcCopyDir` with one file and one subdir; `checkIfCopiedDirectoryHasCorrectData` validates entry count, entry names/types, and copied file content; `createDestNonEmptyDirectory` creates a destination with a pre-existing subdirectory; `checkIfCopiedEmptyDirectoryHasNoData` verifies empty copies. Test functions call `operations.CopyDir`, `os.ReadDir`, `os.Mkdir`, `operations.WriteFile`, and `operations.ReadFile`.

Control flow: each test creates an isolated operations test directory, prepares source/destination layouts, invokes `CopyDir`, then validates exact resulting directory shape. When copying into an existing directory, the source directory itself becomes a child; when copying into a nonexistent path, the destination path is created as the copied tree.

State/persistence: Files and explicit directory marker behavior are observed via the mounted filesystem. Existing destination entries are expected to survive unchanged. Test data persists in the shared operations test prefix until package cleanup.

Dependencies/integration: Relies on constants from `operations_test.go` and helper functions from `util/operations` and `util/setup`.

Risks/test signals: The tests assume `os.ReadDir` ordering matches lexical ordering of expected names. A passing run signals that copy preserves file contents, explicit empty directories, and existing destination contents across all configured mount modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/copy_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/copy_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/copy_file_test.go

Purpose: Verifies single-file copy semantics through GCSFuse: the copied file is created at a new path, content matches the source, and the source remains unchanged.

Important APIs/types/functions: `TestCopyFile` uses `setup.SetupTestDirectory`, `operations.CreateFileWithContent`, `operations.ReadFile`, `os.Stat`, `operations.CopyFile`, and `setup.CompareFileContents`.

Control flow: the test creates a randomized temp file under `dirForOperationsTest`, reads its original content, asserts the destination does not already exist, copies the file, then validates both destination and source contents. Defers remove source and destination files.

State/persistence: State lives in the mounted operations test directory and maps to GCS objects. The test depends on close/flush behavior inside `CreateFileWithContent` and `CopyFile` so the subsequent reads see durable content.

Dependencies/integration: Shares `tempFileName` and `Content` constants with `write_test.go`/`operations_test.go`; uses common operations/setup helpers.

Risks/test signals: The destination name is derived by appending `Copy`, so stale objects from failed cleanup could cause a precondition failure. Passing indicates basic object copy and read-after-copy consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/copy_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/create_three_level_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/create_three_level_dir_test.go

Purpose: Validates creation, listing, walking, and file-content behavior for a three-level explicit directory hierarchy under the operations test prefix.

Important APIs/types/functions: `TestCreateThreeLevelDirectories` uses `operations.CreateDirectoryWithNFiles`, `operations.WriteFileInAppendMode`, `filepath.WalkDir`, `os.ReadDir`, and `operations.ReadFile`.

Control flow: the test creates `dirOne/dirTwo/dirThree`, creates one file inside the deepest directory, appends known content, then recursively walks from the test directory. For each directory level it validates object count, child name, child type, and for the deepest file validates content.

State/persistence: The test persists a nested explicit-directory structure and a file object through the mounted filesystem. It checks that parent listings reflect child directories and that the deepest file content is readable after append.

Dependencies/integration: Uses structure constants from `operations_test.go`, setup helpers, and file operation helpers.

Risks/test signals: It assumes deterministic `ReadDir` order for single-entry directories. It logs fatal on read-directory failures inside the walk callback, which exits the process rather than only failing the test. Passing signals correct recursive visibility of explicit directories and nested object reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/create_three_level_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/delete_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/delete_dir_test.go

Purpose: Tests recursive deletion of empty and non-empty explicit directories through `os.RemoveAll`.

Important APIs/types/functions: `TestDeleteEmptyExplicitDir` and `TestDeleteNonEmptyExplicitDir` use `setup.SetupTestDirectory`, `operations.CreateDirectoryWithNFiles`, `os.RemoveAll`, and `os.Stat`.

Control flow: each test creates a target directory under `dirForOperationsTest`; the non-empty case also creates files and a populated subdirectory. After `RemoveAll`, each test stats the removed path and fails if it still exists as a directory.

State/persistence: The non-empty case validates that deleting a directory removes descendant file objects and subdirectory markers from the bucket-backed namespace. No explicit per-test cleanup is needed beyond `RemoveAll`.

Dependencies/integration: Depends on shared operation constants and helper creation utilities.

Risks/test signals: The final stat check does not assert that the returned error is specifically not-exist, only that a valid directory no longer remains. Passing signals recursive directory deletion across explicit directory marker and object descendants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/delete_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/delete_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/delete_file_test.go

Purpose: Validates file deletion both directly under the test bucket prefix and inside an explicit directory.

Important APIs/types/functions: constants define `A`, `A.txt`, and `a.txt`; `createFile` wraps `os.Create` and close; `checkIfFileDeletionSucceeded` uses `os.Remove` followed by `os.Stat`; `TestDeleteFileFromBucket` and `TestDeleteFileFromBucketDirectory` set up the two layouts.

Control flow: tests create a file, call the shared deletion helper, and fail if deletion errors or the file is still stat-able as a non-directory. The directory case creates parent `A` before creating `A/a.txt`.

State/persistence: The operations act through the mount and should delete the corresponding GCS object while leaving parent directories intact.

Dependencies/integration: Uses `operations.CloseFileShouldNotThrowError` and setup permissions.

Risks/test signals: The post-delete check only flags the case where `os.Stat` returns a non-directory file; unusual errors are not inspected. Passing confirms simple object deletion and deletion within explicit directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/delete_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/file_and_dir_attributes_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/file_and_dir_attributes_test.go

Purpose: Verifies stat attributes for files, empty directories, and non-empty directories, focusing on name, size, and modification-time windows.

Important APIs/types/functions: constants define retry timing, byte expectations, and directory/file counts. `checkIfObjectAttrIsCorrect` wraps `os.Stat` and validates mounted path name, modtime range, and size. `TestFileAttributes`, `TestEmptyDirAttributes`, and `TestNonEmptyDirAttributes` run the check inside `operations.RetryUntil`.

Control flow: each test creates a randomized object/directory while capturing pre/post timestamps adjusted by `operations.TimeSlop`, then retries until stat attributes match or timeout.

State/persistence: Created objects/directories persist in the mounted test prefix. Directory size is expected to be zero regardless of contained files; file size is expected to match the known content length.

Dependencies/integration: Uses `context`, time handling, setup and operation helpers, and shared `DirForOperationTests`.

Risks/test signals: Attribute timing is sensitive to kernel/GCS clock differences, mitigated by slop and retry. Passing signals stable stat metadata projection for both object and directory inodes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/file_and_dir_attributes_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/list_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/list_dir_test.go

Purpose: Tests recursive directory listing shape and confirms direct I/O reads still work after listing a directory.

Important APIs/types/functions: `createDirectoryStructureForTest` builds a fixed tree with files, subdirectories, and an empty subdir. `TestListDirectoryRecursively` walks the tree with `filepath.WalkDir` and validates `os.ReadDir` entries at each level. `TestReadFileWorksAfterListDir` creates a GCS object directly with `client.SetupFileInTestDirectory`, lists the mounted directory, then opens the file with `syscall.O_DIRECT` and reads via `operations.ReadFileSequentially`.

Control flow: listing test validates root, parent, child, and empty-directory counts and names. The read-after-list test ensures directory listing/cache activity does not poison later file open/read.

State/persistence: Directory fixtures are created in the bucket-backed test prefix. The second test writes through the storage client and reads through gcsfuse, exercising cross-client visibility.

Dependencies/integration: Uses internal `util.MiB`, storage client globals from `operations_test.go`, setup/client/operations helpers, and testify `require`.

Risks/test signals: ReadDir ordering is assumed. The second test is a regression signal for interactions between list cache/prefetch and direct file reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/list_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/move_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/move_file_test.go

Purpose: Verifies move/rename-like file relocation within the same directory tree, across directories, and over an existing destination file.

Important APIs/types/functions: `createSrcDirectoryAndFile` creates a source directory and writes `MoveFileContent`; `checkIfFileMoveOperationSucceeded` calls `operations.Move` and validates destination content; tests use `os.Mkdir`, `operations.CreateFileWithContent`, `setup.CompareFileContents`, and testify assertions.

Control flow: same-directory and different-directory tests create source file and destination directory, invoke the shared move helper, and read the moved file. The existing-destination test creates both source and destination files, moves source onto destination, checks overwritten content, then asserts the source path is gone.

State/persistence: Moves modify GCS object names through the mount. The overwrite case validates replacement semantics and removal of the old object.

Dependencies/integration: Uses operation constants from `operations_test.go`, setup permissions, helper operation wrappers, and testify.

Risks/test signals: The source-removed check uses string matching for "no such file or directory". Passing signals file rename/copy-delete semantics are consistent for normal and overwrite moves.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/move_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/operations_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/operations_test.go

Purpose: Provides package-level configuration, constants, shared clients, and `TestMain` orchestration for the operations integration tests.

Important APIs/types/functions: Numerous constants define fixture names and expected object counts for copy/list/delete/create tests. `overrideFilePathsInFlagSet` rewrites `/gcsfuse-tmp` to the actual GCE temp root. `RunTestOnTPCEndPoint` synthesizes a TPC-specific config. `TestMain` handles normal and TPC execution, config fallback, bucket environment setup, storage client creation, mount runs, and auth-variant testing.

Control flow: after parsing flags and config, the package either runs TPC-specific static tests or builds/uses operations config. It initializes GCS test environment and storage client, runs mounted-directory mode if requested, rewrites temp paths for GCE, builds compatible flag sets, then runs static, only-dir, persistent, dynamic, and credential/auth permutations in sequence.

State/persistence: Global `storageClient` and `ctx` are shared by tests. Mount mode and test directory setup are controlled by common setup state. Tests persist objects under `dirForOperationsTest` and mode-specific only-dir prefixes until cleanup by framework helpers.

Dependencies/integration: Integrates with Cloud Storage, static/dynamic/only-dir/persistent mounting packages, credential test runner, and test-suite config structures.

Risks/test signals: Repeated `m.Run()` invocations reuse the same package process and global state, so individual tests must be mount-mode agnostic. The fallback config includes cache, JSON read, gRPC, atomic rename, implicit-dirs, metadata prefetch, and streaming-write variants, making failures useful for regression localization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/operations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/parallel_dirops_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/parallel_dirops_test.go

Purpose: Stress-tests concurrent directory operations, lookup, readdir, delete, rename, and mkdir paths when parallel directory operations are allowed.

Important APIs/types/functions: `testDirStrucure` records randomized fixture names. `createDirStructure` creates two explicit dirs and several files with fixed sizes. `deleteDirStructure` calls `setup.CleanUpDir`. `lookUpFileStat` wraps `os.Stat` for goroutines. Tests use `sync.WaitGroup`, `os.ReadDir`, `filepath.WalkDir`, `os.RemoveAll`, `os.Remove`, `os.Rename`, `os.Mkdir`, and testify assertions.

Control flow: each test creates a fresh randomized tree, launches concurrent operations, waits, then validates either deterministic success for independent operations or accepted race outcomes for lookup versus mutation. Race tests allow lookup to succeed before mutation or fail with not-exist after mutation.

State/persistence: Fixture state is mounted-directory state backed by GCS objects. Cleanup removes the entire randomized test directory. Concurrent tests intentionally create transitional states and then assert final persisted state.

Dependencies/integration: Uses common setup/operations helpers and standard filesystem calls.

Risks/test signals: Some assertions assume lexical order of directory entries. Shared local variables are written by goroutines but each variable is assigned by one goroutine before `Wait`, limiting data-race risk. Passing signals directory operation concurrency preserves correctness and tolerates expected races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/parallel_dirops_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/read_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/read_test.go

Purpose: Verifies read-after-write consistency for newly created temp files.

Important APIs/types/functions: `TestReadAfterWrite` uses `os.MkdirTemp`, `os.CreateTemp`, `operations.WriteFileInAppendMode`, `operations.ReadFile`, and `operations.CloseFileShouldNotThrowError`.

Control flow: the test creates a temp directory under the operations prefix, then loops ten times creating a temp file, closing it, appending `"line 1\n"`, reading it back, and comparing exact content.

State/persistence: Each temp file is persisted through the mount as a GCS object. The test depends on append-mode write durability and immediate read visibility from the same mount.

Dependencies/integration: Uses shared constants and setup utilities from the operations package.

Risks/test signals: Temp files are not explicitly removed in the test, relying on broader test cleanup. Passing is a simple but repeated signal for create, append, close, and read consistency.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/rename_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/rename_dir_test.go

Purpose: Regression test for renaming a source directory onto a non-empty destination directory and preserving filesystem health after the failed operation.

Important APIs/types/functions: `TestRenameDirToNonEmptyDestDirectory` uses `os.Mkdir`, `operations.CreateFileWithContent`, `os.Rename`, `os.Stat`, `os.Remove`, and testify assertions.

Control flow: the test creates empty `srcDir`, non-empty `destDir/file.txt`, attempts `os.Rename(srcDir, destDir)`, asserts an error mentioning file-exists/not-empty, stats both source and destination to verify they remain usable, then deletes the destination file and both directories.

State/persistence: The failed rename should leave both directory markers and destination file intact. Cleanup validates that no poisoned local/mounted state prevents subsequent remove operations.

Dependencies/integration: Uses operations/setup helpers and standard POSIX calls through the mount.

Risks/test signals: Error message matching allows several platform-specific substrings but is still string-dependent. Passing signals failed directory rename cleanup is correct and addresses the linked regression context in comments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/rename_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/rename_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/rename_file_test.go

Purpose: Tests normal file rename, error behavior for missing sources, and symlink rename behavior.

Important APIs/types/functions: `TestRenameFile` uses `operations.RenameFile` and content comparison. `TestRenameFileWithSrcFileDoesNoExist` checks missing-source errors. `TestRenameSymlinkToFile` uses `os.WriteFile`, `os.Symlink`, `os.Rename`, `os.Lstat`, `os.Readlink`, and `operations.ReadFile`.

Control flow: the normal test creates a file, reads content, renames, and validates content at the new path. The missing-source test expects an error containing no-such-file. The symlink test creates a target file and symlink, renames the symlink path, verifies the old symlink is gone, the new path remains a symlink to the same target, and reading through it returns target content.

State/persistence: File object, symlink inode representation, and rename metadata are all exercised through the mount.

Dependencies/integration: Uses operation/setup helpers and testify `assert`/`require`.

Risks/test signals: Symlink support must be enabled/available in the tested mount configuration. Passing signals rename preserves file content and symlink identity while surfacing expected errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/rename_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/stat_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/stat_file_test.go

Purpose: Validates that statting a path with a trailing newline fails with `ENOENT`.

Important APIs/types/functions: `TestStatWithTrailingNewline` uses `setup.SetupTestDirectory`, `os.Stat`, and asserts `err.(*os.PathError).Err == syscall.ENOENT`.

Control flow: the test creates the base operations test directory, appends `"/\n"` to the path, stats it, requires an error, and checks the underlying syscall error.

State/persistence: No new object state beyond the test directory. It tests path parsing/lookup behavior in the mount layer.

Dependencies/integration: Uses setup helpers and testify.

Risks/test signals: The type assertion to `*os.PathError` assumes Go's `os.Stat` error shape. Passing signals gcsfuse does not normalize or ignore newline path components.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/stat_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/write_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/operations/write_test.go

Purpose: Exercises file write modes and validates GCS object attributes remain meaningful across append and overwrite operations.

Important APIs/types/functions: constants define temp names and content. `validateExtendedObjectAttributesNonEmpty` creates a storage client, stats the object, converts attributes to internal extended attributes, and rejects nil/empty results. `validateObjectAttributes` compares content type, component count, names, bucket, holds, sizes, hashes, media link, storage class, and mtime ordering. Tests cover append at EOF, write at start, `WriteAt` with `O_DIRECT`, create, append attribute changes, and truncate/write attribute changes.

Control flow: tests create a file under the operations prefix, perform one write variant, compare file contents, then fetch direct GCS attributes. Attribute tests snapshot attrs before and after mutation and validate expected size growth and stable metadata fields.

State/persistence: Writes persist to GCS; direct storage-client stat validates backend metadata rather than only mounted view. Zonal buckets expect `RAPID` storage class and tolerate missing media link.

Dependencies/integration: Uses Cloud Storage client, internal `gcs` and `storageutil` conversions, setup/client/operations helpers, and syscall flags.

Risks/test signals: Object name passed to storage stat omits randomized test directory suffixes, so it relies on shared package naming. Passing signals file writes flush content and preserve extended object metadata invariants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/operations/write_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/appends_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/appends_test.go

Purpose: Tests append behavior for zonal-bucket unfinalized/finalized objects, including dual-mount takeover, visibility before/after close, concurrent append and `r+` handles, random-write fallback, stat-size refresh, and repeated reopen appends.

Important APIs/types/functions: Methods on `DualMountAppendsTestSuite` and `SingleMountAppendsTestSuite` use `createUnfinalizedObject`, `deleteUnfinalizedObject`, `operations.OpenFileInMode`, `appendToFile`, direct `client.ReadObjectFromGCS`, `operations.ValidateESTALEError`, `os.Stat`, and `syscall.O_DIRECT`.

Control flow: tests create an object, open append and sometimes `r+` handles, perform writes, then validate either immediate backend visibility for append-session behavior or delayed visibility until close for fallback writes. Dual-mount takeover verifies old handle sync/close becomes stale after a secondary mount writes. Stat tests validate kernel-visible size before and after metadata-cache expiry.

State/persistence: Maintains `t.fileName` and `t.fileContent` as suite state. Direct GCS reads are the durable source of truth. Open file handles intentionally hold unfinalized append sessions.

Dependencies/integration: Depends on rapid-appends suite setup, zonal bucket support, GCS client helpers, and operation helpers.

Risks/test signals: Timing around stat cache expiry and flush duration can be slow/flaky. Passing signals append-session invalidation, close-time persistence, fallback semantics, and kernel stat refresh work for zonal rapid appends.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/appends_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/reads_after_appends_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/reads_after_appends_test.go

Purpose: Verifies sequential and random reads after rapid appends for single-mount and dual-mount setups, with and without metadata cache.

Important APIs/types/functions: `readAndVerifyFunc` abstracts read validation. `readSequentiallyAndVerify` reads whole content with `operations.ReadFileSequentially`. `readRandomlyAndVerify` performs up to ten random `ReadAt` calls and compares slices. Suite methods `runAppendAndReadTest` implement single and dual mount loops. Runner functions instantiate suites with metadata-cache flags.

Control flow: single-mount tests append twice through one handle and immediately verify the current full content after each append. Dual-mount tests append through `getAppendPath` and read through primary mount; with metadata cache enabled, subsequent reads first see cached old size, wait for TTL/flush, then see updated size.

State/persistence: Suite `fileContent` is the expected byte source. File handles are opened with append plus direct I/O. Dual-mount cases intentionally expose stale metadata state until cache expiry.

Dependencies/integration: Uses rapid-appends base suite, setup random data, operation read helpers, `math/rand/v2`, and testify suite.

Risks/test signals: Random reads are nondeterministic but bounded. Time sleeps depend on `metadataCacheTTLSecs` and `operations.WaitDurationAfterFlushZB`. Passing signals read paths respect append updates and metadata-cache staleness rules.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/reads_after_appends_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/setup_test.go

Purpose: Provides rapid-appends package setup, fallback config, zonal-bucket gating, primary/secondary mount paths, storage client, and global constants.

Important APIs/types/functions: constants define test directory, file prefixes, sizes, block size, open modes, metadata TTL, and append counts. `env` stores storage client, context, config, and bucket type. `TestMain` builds fallback config for single/dual appends and reads under multiple cache/kernel-reader combinations.

Control flow: `TestMain` parses setup flags, reads config, synthesizes config if absent, initializes environment, aborts if not a zonal bucket, creates a storage client, handles GKE mounted-directory mode, sets up the GCE test dir, rewrites temp paths, creates a secondary mount directory, runs tests, and finally cleans the rapid-appends prefix.

State/persistence: Global `testEnv` is shared by suites. The secondary mount directory is created under the test temp root. Cleanup removes GCS test objects after `m.Run`.

Dependencies/integration: Uses Cloud Storage, setup/test-suite helpers, client helpers, and operation constants.

Risks/test signals: The package hard-fails outside zonal bucket runs. Fallback config is extensive and must keep primary/secondary flags aligned by index. Passing package setup indicates zonal rapid-append feature coverage is being run with valid mount/cache combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/suites_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/suites_test.go

Purpose: Defines reusable testify suite types and mount lifecycle helpers for rapid appends tests.

Important APIs/types/functions: `mountPoint` stores root, mount, test directory, and log file paths. `BaseSuite` stores flags, mount points, file name/content, and metadata-cache setting. Suite structs embed `BaseSuite`. `SetupTest`, `TearDownTest`, `setupTestDir`, `mountGcsfuse`, `unmountAndCleanupMount`, `createUnfinalizedObject`, `deleteUnfinalizedObject`, `getAppendPath`, `appendToFile`, `getNewEmptyCacheDir`, `isMetadataCacheEnabled`, and `RunTests` provide shared behavior.

Control flow: In GKE mode, setup records already-mounted paths. In GCE mode, it mounts primary and optional secondary static gcsfuse mounts. Teardown saves primary/secondary logs on failure, then either cleans GCS objects for GKE or unmounts each mount and cleans. `RunTests` filters config items by run name and expands flag strings into per-suite runs.

State/persistence: Suite state tracks current object name/content and mount paths. `appendToFile` updates expected content and syncs dual-mount writes so the other mount can observe them.

Dependencies/integration: Uses static mounting, setup artifact/log helpers, GCS client creation of unfinalized objects, and testify suite/require.

Risks/test signals: `mountGcsfuse` receives `mountPoint` by value, so updates to `mnt.testDirPath` inside it do not mutate the caller beyond initial fields already set by `setupTestDir`; tests rely on those pre-set paths. Passing suites indicate lifecycle isolation, failure log capture, and config expansion work.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rapid_appends/suites_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_exclude_regex_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_exclude_regex_test.go

Purpose: Verifies that file-cache exclude regex rules prevent caching even when range reads are enabled.

Important APIs/types/functions: `cacheFileForExcludeRegexTest` carries flags, storage client, context, and base test name. Setup helpers configure log/cache dir and mount. `TestReadsForExcludedFile` uses `setupFileInTestDir`, `readChunkAndValidateObjectContentsFromGCS`, structured read logs, `validate`, and `validateFileIsNotCached`.

Control flow: each test run truncates the log, removes cache dir, creates a unique test directory and file, performs two range reads at different offsets, then checks both logs are cache misses and no cached file exists. The runner uses config flag sets and adds only-dir-specific exclude-regex variants.

State/persistence: Cache directory state is deliberately cleared per test and inspected after reads. GCS content is created through the storage client, read through the mount, and compared with backend chunks.

Dependencies/integration: Uses read-cache package globals, setup/client/operations helpers, structured read-log parser, and testify suite.

Risks/test signals: Regex construction differs for only-dir mount and dynamic bucket paths. Passing signals exclude regex takes precedence over range-read caching.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_exclude_regex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_include_regex_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_include_regex_test.go

Purpose: Tests include-regex behavior for file cache: matching files cache and hit on second read, nonmatching files remain uncached, and include/exclude no-overlap behaves as expected.

Important APIs/types/functions: `cacheFileForIncludeRegexTest` mirrors the common suite pattern. Tests use `setupFileInTestDir`, `client.SetupFileInTestDirectory`, `readFileAndGetExpectedOutcome`, `read_logs.GetStructuredLogsSortedByTimestamp`, `validateFileIsCached`, and `validateFileIsNotCached`.

Control flow: setup truncates logs and clears cache. The included-file test reads the same matching file twice and expects miss then hit. The non-included test does the same for a nonmatching name and expects two misses. The mixed test reads included twice and excluded twice, validating ordered log entries and cache presence.

State/persistence: Cache files are keyed under the configured cache dir and validated by path. Created GCS objects live in a unique test directory.

Dependencies/integration: Uses read-cache setup config, include regex flags from package setup, and structured logs.

Risks/test signals: The include regex in config assumes generated included filenames start with `foo`. Passing signals regex filtering controls cache admission without interfering with read correctness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_include_regex_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_range_read_false_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_range_read_false_test.go

Purpose: Validates behavior when `file-cache-cache-file-for-range-read` is false, including range-read cache misses and sequentiality after cache eviction.

Important APIs/types/functions: `cacheFileForRangeReadFalseTest` includes booleans for parallel downloads and RAM cache. `readFileBetweenOffset` records expected log metadata while reading byte ranges. Tests use file handles, `operations.OpenFile`, structured read logs, cache validation, and RAM cache path override.

Control flow: `TestRangeReadsWithCacheMiss` performs two random/range reads and expects no cached file. `TestReadIsTreatedNonSequentialAfterFileIsRemovedFromCache` partially reads two cache-capacity-sized files to evict the first, resumes reads, merges expected outcomes, validates two structured read logs, and asserts the evicted file's later chunk is non-sequential/cache-miss while the second remains sequential.

State/persistence: Cache capacity and optional `/dev/shm` cache path determine eviction behavior. Open handles are kept across partial reads, intentionally testing cache-handler lifecycle.

Dependencies/integration: Uses read-cache helpers, structured logs, setup flag builder, and testify.

Risks/test signals: Parallel downloads relax cache-hit expectations for the second file. Byte offsets use `+1` for resumed reads, so expected content merging should be interpreted as log-range validation rather than exact whole-file reconstruction. Passing signals range reads do not populate file cache unless configured and eviction resets sequentiality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_range_read_false_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_range_read_true_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_range_read_true_test.go

Purpose: Verifies that range reads can populate the file cache when range-read caching is enabled, including RAM-cache variants.

Important APIs/types/functions: `cacheFileForRangeReadTrueTest` stores flags, clients, base test name, and RAM-cache option. `TestRangeReadsWithCacheHit` uses `readChunkAndValidateObjectContentsFromGCS`, structured read logs, job logs, `operations.RetryUntil`, cache file validation, and cache-size validation.

Control flow: the test creates an 8 MiB file, performs an initial random read at offset 5000 and expects cache miss, waits until a background file-cache job has downloaded through the full file size, then performs a second range read at offset 1000 and expects a cache hit. It then validates cached content and capacity.

State/persistence: Cache dir is cleared per test, optionally placed under `/dev/shm`. Background download job state is inferred from logs and cached file contents.

Dependencies/integration: Uses read-cache shared constants/helpers, structured read/job log parser, and setup flag sets.

Risks/test signals: Determinism depends on retrying until async job logs show sufficient offset. Passing signals range-read cache admission, background fill, and later range cache hits work.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/cache_file_for_range_read_true_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_disabled_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_disabled_test.go

Purpose: Ensures normal file-cache downloads are used when experimental chunk cache is explicitly disabled.

Important APIs/types/functions: `chunkCacheDisabledTest` follows the common suite pattern. `TestNormalFileCacheWithChunkCacheDisabled` creates a 10 MiB file, reads a chunk, validates structured read logs, then inspects job logs for chunk versus normal file-cache downloads.

Control flow: after setup clears logs/cache and creates a unique directory, the test performs one chunk read, validates a sequential cache miss in read logs, requires exactly one job log, asserts `ChunkCacheDownloads` is empty, and asserts normal `JobEntries` are present.

State/persistence: Cache artifacts and log entries are the primary observed state. The file is created in GCS and read through the mount.

Dependencies/integration: Uses internal cache `util.MiB`, read-cache helpers, structured logs, and setup/client/operations helpers.

Risks/test signals: It assumes exactly one job log for the read. Passing distinguishes disabled chunk-cache behavior from chunk-cache download telemetry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_disabled_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_eviction_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_eviction_test.go

Purpose: Tests LRU-like eviction for experimental chunk cache under a constrained cache size.

Important APIs/types/functions: `chunkCacheEvictionTest` uses common suite lifecycle. `TestEviction` creates two 20 MiB files, reads file 1 fully, file 2 fully, then reads file 1 again, and validates structured logs plus aggregate chunk download ranges.

Control flow: the first full read downloads two 10 MiB chunks for file 1. Reading file 2 forces eviction of file 1 when inserting file 2. Reading file 1 again forces file 2 eviction and redownloads file 1's first chunk. The test aggregates `ChunkCacheDownloads` from all job logs and compares expected ranges.

State/persistence: Cache size is 15 MiB per setup config, so each 20 MiB file exceeds capacity and eviction occurs on insertion. Content validation is skipped in `validateDownloads` because ranges span multiple files.

Dependencies/integration: Uses internal cache data/util types, read-cache helpers, log parser, and storage setup.

Risks/test signals: Expected ranges are value-only and not tied to object name in final comparison. Passing signals chunk-cache eviction and redownload behavior under capacity pressure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_eviction_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_test.go

Purpose: Provides broad coverage for experimental chunk cache: random reads, full sequential reads, reuse of cached chunks, reads spanning chunks, concurrent deduplication, deleted-object fallback errors, and sparse-file allocation.

Important APIs/types/functions: `chunkCacheTest` uses common setup/teardown. Tests use `readChunkAndValidateObjectContentsFromGCS`, `readFileAndValidateCacheWithGCS`, `validateDownloads`, `validateAllocatedFileSize`, `operations.ReadChunkFromFile`, direct GCS deletion, structured job/read logs, and `sync.WaitGroup`.

Control flow: individual tests create files sized around 10 MiB chunk boundaries, perform reads at strategic offsets, assert read-log sequential/cache-hit flags, and compare chunk download ranges. Concurrent dedup launches eight goroutines reading the same chunk and expects one download. Deleted-file test reads one chunk, deletes the source object, then expects second chunk read to return ESTALE and log fallback messages.

State/persistence: Chunk cache stores sparse files under cache dir; tests inspect both logical content and allocated block size. Deletion test intentionally desynchronizes mounted metadata from backend object existence.

Dependencies/integration: Uses internal cache data/util packages, client operations, read logs, and filesystem syscalls.

Risks/test signals: Some tests assume a single job log contains all downloads. The deleted-file test checks log text substrings. Passing signals chunk-cache correctness, deduplication, sparse allocation, and stale-source error handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/chunk_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/disabled_cache_ttl_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/disabled_cache_ttl_test.go

Purpose: Validates that disabling stat/cache TTL causes reads after backend object updates to miss cache and fetch fresh content, while subsequent reads can hit the refreshed cache.

Important APIs/types/functions: `disabledCacheTTLTest` follows common suite lifecycle. `TestReadAfterObjectUpdateIsCacheMiss` uses `setupFileInTestDir`, `readFileAndValidateCacheWithGCS`, `modifyFile`, structured logs, and `validate`.

Control flow: the test creates a file, reads it once to populate cache, modifies the object directly through the storage client, reads immediately again expecting a miss and smaller updated file, then reads a third time expecting a hit for the updated object. It validates all three structured read logs.

State/persistence: Direct GCS mutation changes object generation outside gcsfuse. Cache directory is cleared before test and then refreshed after miss.

Dependencies/integration: Uses setup flag variants with `--stat-cache-ttl=0s`, read-cache helpers, storage client, and structured log parser.

Risks/test signals: Assumes object update is immediately visible with stat TTL zero. Passing signals stale cached file contents are invalidated by object generation/metadata changes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/disabled_cache_ttl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/helpers_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/helpers_test.go

Purpose: Central helper library for read-cache tests, covering expected log metadata, mounted reads, GCS content validation, cache path lookup, cache file validation, remounting, mutation, capacity checks, sparse allocation checks, chunk download validation, and content verification.

Important APIs/types/functions: `Expected` stores log validation data and served content. `readFileAndGetExpectedOutcome`, `validate`, `getCachedFilePath`, `validateFileSizeInCacheDirectory`, `validateFileInCacheDirectory`, `validateFileIsNotCached`, `validateFileIsCached`, `remountGCSFuse`, `readFileAndValidateCacheWithGCS`, `readChunkAndValidateObjectContentsFromGCS`, `readFileAndValidateFileIsNotCached`, `modifyFile`, `validateCacheSizeWithinLimit`, `setupFileInTestDir`, `runTestsOnlyForDynamicMount`, `validateAllocatedFileSize`, `validateDownloads`, and `validateContent` are reused across suites.

Control flow: helpers usually perform a mounted read, capture timestamps, compare served bytes against GCS via CRC or chunk validation, then inspect cache files and structured logs. Retry loops handle asynchronous cache materialization and CRC availability.

State/persistence: Computes cache paths from cache dir, bucket name, test directory basename, and file name. It mutates object content directly through GCS for invalidation tests and remounts gcsfuse by unmounting root and mounting with saved config.

Dependencies/integration: Uses Cloud Storage, internal cache range types, read log parser, setup/client/operations utilities, syscalls, CRC helpers, and testify.

Risks/test signals: Many suites depend on exact structured-log ordering and cache path layout. Helpers deliberately validate both data correctness and telemetry, making failures high-signal for cache implementation regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/helpers_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/job_chunk_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/job_chunk_test.go

Purpose: Validates file-cache download job chunk sizing for single-file and concurrent multi-file reads, both with and without parallel downloads.

Important APIs/types/functions: constant `cacheSizeMB`; `jobChunkTest` stores chunk size expectation. `TestJobChunkSizeForSingleFileReads` and `TestJobChunkSizeForMultipleFileReads` use `setupFileInTestDir`, `readFileAndValidateCacheWithGCS`, `read_logs.GetJobLogsSortedByTimestamp`, `sync.WaitGroup`, and offset-difference assertions.

Control flow: single-file test reads a 16 MiB file, then checks job log bucket/object identity, monotonic increasing offsets, offsets advancing by multiples of expected chunk size, and final offset equal to file size. Multi-file test reads two files concurrently, accounts for nondeterministic log order by swapping expected outcomes, then applies the same offset checks to both jobs.

State/persistence: Download progress is inferred entirely from structured job logs. Cache dir is cleared per test.

Dependencies/integration: Uses internal cache `util.MiB`, read-cache helpers, setup flag sets with 8 MiB or 4 MiB chunk expectations, and structured logs.

Risks/test signals: Uses `setup.LogFile()` rather than `testEnv.cfg.LogFile`; this assumes setup global log file was updated consistently. Passing signals configured chunk sizes are reflected in download job telemetry.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/job_chunk_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/local_modification_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/local_modification_test.go

Purpose: Tests cache behavior after a file is modified locally through the gcsfuse mount.

Important APIs/types/functions: `localModificationTest` uses common suite setup. `TestReadAfterLocalGCSFuseWriteIsCacheMiss` creates a mounted file, reads it to populate cache, appends random data through the mount, then validates behavior with separate branches for zonal and non-zonal buckets.

Control flow: non-zonal path expects the second full read after append to miss cache and read `fileSize + smallContentSize`, with structured logs showing miss and increased chunk count. Zonal path expects unfinalized-object semantics: no new download job for appends, cache file remains original size, cache size remains within limit, and the second log is treated as cache hit while fallback serves newer bytes.

State/persistence: The test mutates the object through the mount, so local write state and cache generation tracking are central. Cache file size is inspected directly for zonal behavior.

Dependencies/integration: Uses read-cache helpers, storage client, operations random data and append helpers, setup bucket-type check, and structured read logs.

Risks/test signals: The zonal branch encodes specialized behavior for unfinalized objects and may diverge from non-zonal assumptions. Passing signals local writes invalidate or bypass stale cache appropriately.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/local_modification_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/range_read_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/range_read_test.go

Purpose: Tests cache hit behavior for range reads within an already downloaded chunk and beyond the initial chunk after background download completion.

Important APIs/types/functions: `rangeReadTest` tracks whether parallel downloads are enabled. `TestRangeReadsWithinReadChunkSize` validates second read within an 8 MiB download window. `TestRangeReadsBeyondReadChunkSizeWithFileCached` waits for background job completion before reading at 10 MiB. `runTests` expands flag sets.

Control flow: the within-chunk test skips when parallel downloads are enabled, then reads offset 0 and 4 MiB and expects miss then hit. The beyond-chunk test reads at 0, polls job logs until offset reaches the large file size, then reads at 10 MiB and expects hit, cache file presence, and capacity compliance.

State/persistence: Cache directory stores a 15 MiB file. Background job progress is monitored through structured job logs.

Dependencies/integration: Uses read-cache helpers, setup/client/operations utilities, structured logs, and testify suite.

Risks/test signals: Async job polling is required for deterministic hits beyond the first chunk. Passing signals background cache fill can satisfy later random reads outside the initially requested range.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/range_read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/read_only_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/read_only_test.go

Purpose: Covers read-only file-cache behavior for repeated sequential reads, oversized files, random reads, and cache capacity across multiple files.

Important APIs/types/functions: `readOnlyTest` uses the common suite. Helpers `readMultipleFiles` and `validateCacheOfMultipleObjectsUsingStructuredLogs` batch reads and log validation. Tests call `readFileAndValidateCacheWithGCS`, `readFileAndValidateFileIsNotCached`, `client.CreateNFilesInDir`, and structured read-log validation.

Control flow: second-read test expects miss then hit for a cacheable file. Oversized sequential and random tests use a file larger than cache capacity and expect no cached file and repeated misses. Multi-file tests create enough 3 MiB files to fit within or exceed the 9 MiB cache capacity, read all files twice, and validate second-pass hit/miss behavior based on capacity.

State/persistence: Cache contents are directly tied to configured 9 MiB capacity. Files are created in a unique test directory via storage client and read through the mount.

Dependencies/integration: Uses read-cache helpers, setup/client/operations, structured logs, and suite runner.

Risks/test signals: Tests assume LRU/capacity behavior is deterministic across sequential reads. Passing signals cache admission and eviction policy for common read-only workloads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/read_only_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/remount_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/remount_test.go

Purpose: Verifies that file-cache state is not reused incorrectly across remounts, including dynamic mount path handling.

Important APIs/types/functions: `remountTest` follows the common suite lifecycle. `readFileAndValidateCacheWithGCSForDynamicMount` temporarily sets dynamic bucket state and adjusts `testEnv.testDirPath`. Tests use `remountGCSFuse`, `readFileAndValidateCacheWithGCS`, and structured read logs.

Control flow: normal remount test reads a file twice before remount and expects miss then hit, remounts, then reads twice again and expects miss then hit from the new mount/log. Dynamic remount test runs only for dynamic mounting, reads once, remounts, then expects the first read after remount to miss and the next to hit.

State/persistence: Remount clears in-memory cache/log context while the cache directory and GCS object may persist. Dynamic test manipulates package setup state to represent bucket-mounted path layout.

Dependencies/integration: Uses read-cache helpers, setup dynamic-bucket markers, storage client, and structured logs.

Risks/test signals: `readFileAndValidateCacheWithGCSForDynamicMount` mutates `testEnv.testDirPath`, so ordering and defer cleanup matter. Passing signals remount invalidates cache reuse boundaries while preserving later per-mount caching.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/remount_test.go -->
