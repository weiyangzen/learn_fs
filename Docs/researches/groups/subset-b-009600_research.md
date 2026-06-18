# subset-b-009600 research

Grouped research for gcsfuse integration tests and shared test utilities under `sources/user-network-fs/gcsfuse/tools/integration_tests`. Each section is source-tree-aligned and delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/setup_test.go

## Purpose

Bootstraps the stale file handle integration package. It loads the stale-handle test configuration, supplies fallback flag sets for streaming-writes enabled and disabled modes, creates the shared GCS storage client, decides whether the package is running against an already mounted directory or a statically mounted test bucket, and wires the package-global mount function and mount paths used by the suites.

## Important APIs, control flow, and dependencies

`TestMain` calls `setup.ParseSetUpFlags`, `test_suite.ReadConfigFile`, `setup.TestEnvironment`, `client.CreateStorageClient`, `setup.RunTestsForMountedDirectory`, `setup.SetUpTestDirForTestBucket`, and `static_mounting.MountGcsfuseWithStaticMountingWithConfigFile`. The fallback configuration creates two `ConfigItem`s keyed by `Run`: `TestStaleHandleStreamingWritesEnabled` uses zero metadata TTL plus one MiB write blocks, and `TestStaleHandleStreamingWritesDisabled` forces `--enable-streaming-writes=false`; each includes HTTP and gRPC flag variants and compatibility for flat, HNS, and zonal buckets.

## State, persistence, dependencies, and integration points

The package-global `testEnv` stores `context.Context`, `*storage.Client`, selected `*test_suite.TestConfig`, bucket type, and the current test directory. `mountDir`, `rootDir`, and `mountFunc` are shared with the stale-handle suites. Mounted-directory mode is intentionally restricted to cases where both mounted directory and bucket are known, because tests validate remote bucket contents as well as local file-handle behavior.

## Risks and test signals

Risk is concentrated in global setup: an absent config causes mounted-directory tests to exit early, stale globals affect all suites in the package, and a mismatch between bucket type and flags can hide stale-handle regressions. The main test signal is successful package initialization across dynamic config, fallback flags, GKE mounted directory mode, and static mount mode with the storage client closed after `m.Run`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/stale_file_handle_common_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/stale_file_handle_common_test.go

## Purpose

Defines the common stale-file-handle suite shared by local-file and empty-GCS-file scenarios. It verifies that gcsfuse reports ESTALE-like errors when an open file handle loses ownership because the backing object was clobbered or the path was renamed, while local unlink of an open file behaves like POSIX and does not upload stale content.

## Important APIs, control flow, and dependencies

`staleFileHandleCommon` embeds `suite.Suite` and carries flags, the active `*os.File`, generated file name, random 5 MiB payload, and booleans for streaming-writes and local-file modes. `SetupSuite` mounts gcsfuse with `setup.MountGCSFuseWithGivenMountWithConfigFunc`, sets the mounted directory, creates the GCS test directory with `client.SetupTestDirectory`, and generates test data. Tests use `operations.WriteWithoutClose`, `operations.SyncFile`, `operations.RenameFile`, `operations.ValidateESTALEError`, `operations.ValidateSyncGivenThatFileIsClobbered`, and GCS helpers from `util/client`.

## State, persistence, dependencies, and integration points

The suite explicitly maintains an open file handle while changing the namespace or backing object. `TestClobberedFileSyncAndCloseThrowsStaleFileHandleError` writes dirty local data, overwrites the GCS object generation, then expects sync/close to surface stale-handle behavior and preserve the clobbering GCS contents. `TestFileDeletedLocallySyncAndCloseDoNotThrowError` removes the path through the mount and verifies continued writes to the unlinked handle do not recreate the object. `TestRenamedFileSyncAndCloseThrowsStaleFileHandleError` renames the local path, expects further writes on the old handle to fail, and expects sync/close to be no-ops because no further data was accepted.

## Risks and test signals

The tests encode subtle differences between remote clobber, local unlink, and local rename. Zonal streaming-write takeover is skipped because unfinalized zonal object overwrite support is not ready. Strong signals are exact ESTALE validation, no-error validation for unlink, and final GCS content or not-found checks after each handle is closed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/stale_file_handle_common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/stale_file_handle_local_and_synced_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/stale_file_handle_local_and_synced_file_test.go

## Purpose

Adds concrete stale-handle suites for two starting states: a purely local file created through the mount and an empty object that already exists in GCS. It also provides the package entry points that run those suites under streaming-writes enabled and disabled flag configurations.

## Important APIs, control flow, and dependencies

`staleFileHandleLocalFile.SetupTest` creates a unique local file with `operations.OpenFileWithODirect`. `staleFileHandleEmptyGcsFile.SetupTest` creates an empty GCS object with `client.CreateObjectOnGCS`, validates it, and opens it through the mount. Additional empty-GCS tests cover read after remote clobber, first write after remote clobber, and remote delete while the file handle is dirty. `TestStaleHandleStreamingWritesEnabled` and `TestStaleHandleStreamingWritesDisabled` either run directly for mounted-directory mode or iterate over `setup.BuildFlagSets` for the configured bucket type.

## State, persistence, dependencies, and integration points

The tests coordinate three state sources: the open local file descriptor, the mounted namespace, and the underlying object generation in GCS. Remote clobber uses `WriteToObject` without matching the handle generation; remote delete uses `DeleteObjectOnGCS`. Each suite saves gcsfuse logs on failure and relies on the common suite for mount lifecycle.

## Risks and test signals

The riskiest paths are generation takeover and flushing dirty data after the remote object disappears. Zonal streaming-write cases are skipped for known takeover and client bugs. Signals include ESTALE on reads or close after clobber, successful writes before stale detection where the implementation accepts buffering, unchanged clobbering contents in GCS, and object-not-found validation after remote delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/stale_file_handle_local_and_synced_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/buffer_size_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/buffer_size_test.go

## Purpose

Tests streaming-write behavior under different write buffer configurations by mounting a separate gcsfuse instance and writing files whose sizes are smaller than, equal to, or larger than the configured block pool capacity.

## Important APIs, control flow, and dependencies

`TestWritesWithDifferentConfig` skips mounted-directory mode, creates a private mount directory, temporarily swaps `testEnv.cfg.GCSFuseMountedDirectory`, and runs subtests with `static_mounting.MountGcsfuseWithStaticMountingWithConfigFile`. Cases vary `--write-block-size-mb` and `--write-max-blocks-per-file`, then create a local file, generate data with `operations.GenerateRandomData`, write through `operations.WriteAt`, and validate close-time upload through `CloseFileAndValidateContentFromGCS`.

## State, persistence, dependencies, and integration points

The test manipulates package config state and restores it with `defer`. Each subtest mounts and unmounts independently, creates a fresh test directory, and validates the object lifecycle differs for zonal buckets, where file creation may create an empty object earlier, versus non-zonal buckets, where the object is not expected until upload.

## Risks and test signals

Risks include global config mutation, resource leaks from nested mounts, and boundary bugs when `blockSize * maxBlocks` is less than file size. Signals are successful stateless remount, correct pre-upload object state, and exact GCS content after closing the file for all buffer-size combinations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/buffer_size_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/common_streaming_writes_suite_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/common_streaming_writes_suite_test.go

## Purpose

Defines shared suite state and helper assertions for streaming-write tests. The common suite supplies a unique test directory, a reusable 5 MiB payload, and a `ReadAt` validation helper used by local-file and empty-GCS-file test suites.

## Important APIs, control flow, and dependencies

`StreamingWritesSuite` stores the active file handle, file name, mounted file path, payload, and a `test_suite.TestifySuite` bridge. `SetupSuite` calls `setup.SetupTestDirectory` and generates data with `setup.GenerateRandomString`. `TearDownSuite` saves the gcsfuse log on failure. `validateReadCall` performs `ReadAt` at offset zero and asserts byte count and content with testify `require` and `assert`.

## State, persistence, dependencies, and integration points

This suite relies on package-level `testEnv` from streaming-writes setup and is embedded by the local-file and empty-GCS-file suites. The payload size crosses multiple one MiB streaming blocks, so read/write tests exercise buffered state before and after upload.

## Risks and test signals

Because the same embedded suite is reused by many test files, stale `f1`, `fileName`, or `filePath` state would cross-contaminate tests if concrete suites failed to recreate files in `SetupTest` and `SetupSubTest`. The direct signal is exact in-handle readback before GCS validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/common_streaming_writes_suite_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/empty_gcs_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/empty_gcs_file_test.go

## Purpose

Defines the streaming-writes suite variant where the file already exists as an empty GCS object before it is opened through the mount. This exercises takeover and write buffering for synced-but-empty objects.

## Important APIs, control flow, and dependencies

`streamingWritesEmptyGCSFileTestSuite` embeds `StreamingWritesSuite` and `suite.Suite`. `SetupTest` and `SetupSubTest` both call `createEmptyGCSFile`, which generates a unique name, creates an empty object with `CreateObjectInGCSTestDir`, validates it with `ValidateObjectContentsFromGCS`, records `filePath`, and opens with `operations.OpenFileWithODirect`. `TestEmptyGCSFileTestSuiteTest` wires the embedded testify suite and runs all inherited test methods.

## State, persistence, dependencies, and integration points

The suite starts every test from a durable empty GCS object, not just a local inode. This matters for read-after-write, rename, truncate, symlink, and out-of-order write methods inherited from `StreamingWritesSuite`, because gcsfuse must preserve object-generation correctness while streaming data into an existing object.

## Risks and test signals

Risks include setup reuse across subtests, precondition failures when the object already exists, and O_DIRECT alignment assumptions in the operation helper. Signals come from the inherited tests: exact readback, GCS content validation after close, rename/delete semantics, and no unexpected object-not-found errors for the initial empty object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/empty_gcs_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/local_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/local_file_test.go

## Purpose

Defines the streaming-writes suite variant for files created locally through the mounted filesystem. It verifies streaming writes for files with no preexisting GCS object.

## Important APIs, control flow, and dependencies

`streamingWritesLocalFileTestSuite` embeds the common streaming suite. `SetupTest` and `SetupSubTest` call `createLocalFile`, which generates a unique name, builds the mounted path, and opens an O_DIRECT file through `operations.OpenFileWithODirect`. `TestStreamingWritesLocalFileTestSuite` attaches the testify suite and runs all shared streaming-write test methods.

## State, persistence, dependencies, and integration points

The initial state is local-only until streaming upload behavior creates or finalizes an object. Inherited tests check that pre-flush reads come from local streaming buffers, close uploads data to GCS, out-of-order writes synchronize correctly, and deletes prevent unwanted object persistence.

## Risks and test signals

The important risk is confusing local-only file state with already-synced object state, especially on zonal buckets where empty appendable objects may appear earlier. Signals are inherited content checks and object-not-found expectations before close or after deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/local_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/read_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/read_file_test.go

## Purpose

Exercises reads from streaming-write files before sync, after sync, after additional writes, and after close/reopen. It proves gcsfuse can satisfy reads from in-flight streaming buffers and from the finalized object.

## Important APIs, control flow, and dependencies

The methods are attached to `StreamingWritesSuite`: `TestReadFileAfterSync`, `TestReadBeforeFileIsFlushed`, `TestReadBeforeSyncThenWriteAgainAndRead`, and `TestReadAfterFlush`. They use `WriteAt`, `operations.WriteAt`, `operations.SyncFile`, `validateReadCall`, `CloseFileAndValidateContentFromGCS`, and `operations.OpenFileAsReadonly`.

## State, persistence, dependencies, and integration points

The control flow intentionally alternates local dirty state, explicit sync, second append-style write, close-time upload, and readonly reopen. It integrates with both local-file and empty-GCS-file suite variants, so the same behavior must hold whether the object was absent or empty before the test.

## Risks and test signals

Risks include stale read buffers after sync, incorrect file size after appending, and close/reopen differences between local cache and GCS object state. Signals are exact `ReadAt` byte counts, no read errors, and final GCS content matching either one or two copies of the payload.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/read_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/rename_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/rename_file_test.go

## Purpose

Validates rename interactions with streaming writes, including renaming after data has been synced but before close and syncing an already-open handle after its path has moved.

## Important APIs, control flow, and dependencies

`TestRenameBeforeFileIsFlushed` writes twice, verifies stat size, calls `Sync`, renames the path, validates new GCS object contents, closes the original handle, and verifies the old object is gone. `TestSyncAfterRenameSucceeds` writes once, syncs, renames, calls `Sync` again on the old handle, validates the renamed object, and closes. Dependencies are `operations.WriteWithoutClose`, `operations.VerifyStatFile`, `operations.RenameFile`, GCS validation helpers, and testify `require`.

## State, persistence, dependencies, and integration points

The tests keep the file descriptor open across namespace moves. They require gcsfuse to bind the streaming upload state to the file content while updating object names and deleting old names in GCS.

## Risks and test signals

Risks include data being uploaded under the old object name, stale file handle errors on benign post-rename sync, and premature close failures. Signals are no rename/sync errors, exact content under the new name, successful close, and object-not-found for the original name.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/rename_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/setup_test.go

## Purpose

Bootstraps the streaming-writes integration package. It loads configuration, supplies fallback streaming-write flags, creates the shared storage client, handles mounted-directory mode, and runs the package tests once for each compatible static mount flag set.

## Important APIs, control flow, and dependencies

`TestMain` uses `setup.ParseSetUpFlags`, `test_suite.ReadConfigFile`, `setup.TestEnvironment`, `client.CreateStorageClient`, `setup.RunTestsForMountedDirectory`, `setup.BuildFlagSets`, `setup.SetUpTestDirForTestBucket`, and `static_mounting.RunTestsWithConfigFile`. The fallback config uses `--rename-dir-limit=3`, one MiB write blocks, max two blocks per file, unlimited global blocks, and both HTTP and gRPC client protocol variants, compatible with flat, HNS, and zonal buckets.

## State, persistence, dependencies, and integration points

The package-global `testEnv` stores the config, context, storage client, and per-suite test directory. Static mounting is delegated to the mounting utility, which remounts per flag set and invokes the package's Go tests against the same storage client.

## Risks and test signals

Global setup risk includes missing config, stale mount directories, and cross-flag leakage if cleanup fails. The strongest signals are successful execution under all generated flag sets, log preservation on failure, and correct behavior in both mounted-directory and self-managed static mount modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/symlink_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/symlink_file_test.go

## Purpose

Tests symlink behavior for files with in-flight streaming writes. It verifies reads through a symlink see unflushed local data and that deleting the target local file invalidates the symlink without uploading data.

## Important APIs, control flow, and dependencies

`TestCreateSymlinkForLocalFileAndReadFromSymlink` creates a symlink to the active file, writes data, validates `readlink`, opens the symlink, reads through it, and validates GCS content after close. `TestReadingFromSymlinkForDeletedLocalFile` follows the same setup, deletes the target file path, closes the original file handle without error, confirms no GCS object exists, and expects `os.Stat` on the symlink to fail.

## State, persistence, dependencies, and integration points

The tests combine symlink namespace entries with streaming buffer state. Reads through the symlink must resolve to the same open file data even before upload, while removing the target must prevent close from resurrecting the object.

## Risks and test signals

Risks include dereferencing symlinks through stale metadata, leaking content to GCS after target deletion, and inconsistent behavior between local and empty-GCS suite variants. Signals are successful `VerifyReadLink`, exact symlink readback, final content validation for the live-target case, object-not-found for the deleted-target case, and stat failure for the dangling link.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/symlink_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/truncate_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/truncate_file_test.go

## Purpose

Provides detailed streaming-write coverage for truncate operations, including pure truncate, invalid negative truncate, write-after-truncate at different offsets, write-then-truncate up and down, write-truncate-write with preserved file offset semantics, and truncate followed by delete.

## Important APIs, control flow, and dependencies

The suite methods call `t.f1.Truncate`, `operations.WriteWithoutClose`, `WriteAt`, `operations.VerifyStatFile`, `CloseFileAndValidateContentFromGCS`, `ValidateObjectContentsFromGCS`, `ValidateObjectNotFoundErrOnGCS`, and `os.Remove`. Test tables encode expected final content with zero-filled holes when truncate extends file size or when subsequent writes occur after the old file offset.

## State, persistence, dependencies, and integration points

The tests are stateful at the file-handle level: truncate changes size but not necessarily the file pointer, stat must reflect local size before upload, and close must materialize zero padding in GCS. `TestTruncateDownAndDeleteFile` also checks that deleting a locally truncated file removes the remote object instead of uploading the truncated content.

## Risks and test signals

Risks include off-by-one zero padding, forgetting that truncate does not move the write pointer, uploading stale pre-truncate data, and inconsistent deletion semantics. Signals are exact stat sizes before upload, exact final strings including `\x00` bytes, expected error on negative truncate, and remote deletion after `os.Remove`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/truncate_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/write_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/write_file_test.go

## Purpose

Tests out-of-order writes against streaming-write files. The goal is to ensure random writes cause the file to synchronize correctly and that deletion after such synchronization removes the remote object.

## Important APIs, control flow, and dependencies

`TestOutOfOrderWriteSyncsFileToGcs` writes `foobar`, verifies local size, writes `foo` at offset 3, validates the preexisting GCS content is still `foobar`, then closes and validates final `foofoo`. `TestOutOfOrderWriteSyncsFileToGcsAndDeletingFileDeletesFileFromGcs` performs the same out-of-order write but removes the file and expects the object to be absent. Dependencies are operation helpers, GCS content/not-found helpers, and `os.Remove`.

## State, persistence, dependencies, and integration points

Out-of-order writes force reconciliation between streamed sequential data and random overwrite data. The tests rely on inherited setup for both local and empty-GCS starting states and inspect remote state before final close/delete.

## Risks and test signals

Risks include losing the first three bytes, prematurely uploading random-write content, or failing to delete the remote object after local removal. Signals are local stat size, pre-close GCS content, final close content, and object-not-found after delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/write_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_handling_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_handling_test.go

## Purpose

Bootstraps the symlink-handling integration package and defines metadata constants for the standard and legacy GCS symlink representations. It runs both standard and legacy symlink suites against configured or fallback mounts.

## Important APIs, control flow, and dependencies

`TestMain` loads `cfg.SymlinkHandling`, creates fallback `ConfigItem`s for `TestStandardSymlinksTestSuite` with `--enable-standard-symlinks=true` and `TestLegacySymlinksTestSuite` with `--enable-standard-symlinks=false`, initializes the environment with `setup.TestEnvironment`, creates a storage client, and handles GKE mounted-directory versus static mount setup. Constants are `TestDirName`, `SymlinkMetadataKey` (`gcsfuse_symlink_target`), and `StandardSymlinkMetadataKey` (`goog-reserved-file-is-symlink`).

## State, persistence, dependencies, and integration points

The shared `testEnv` holds the storage client, context, and config pointer. Static mount mode calls `setup.SetUpTestDirForTestBucket` and `setup.OverrideFilePathsInFlagSet` so paths embedded in flags point at local test directories. Cleanup removes the symlink test directory from GCS after the package run.

## Risks and test signals

Risks include wrong metadata-key interpretation, config `Run` names not matching suite dispatch, and cleanup deleting the wrong prefix for only-dir mounts. Test signals come from the downstream suite tests plus successful initialization in both standard and legacy modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_handling_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_operations_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_operations_test.go

## Purpose

Contains the symlink operation test cases shared by standard and legacy suites. It covers symlink creation, readlink, reading and writing through file symlinks, listing through directory symlinks, renaming symlinks, copying symlinks without dereferencing, and reading a standard symlink while mounted in legacy mode.

## Important APIs, control flow, and dependencies

Tests use `os.Symlink`, `os.Readlink`, `os.ReadFile`, `os.WriteFile`, `os.ReadDir`, `os.Rename`, `os.Lstat`, `os.Stat`, and `exec.Command("cp", "-P", ...)`. They rely on suite helpers `createSymlink`, `createGCSSymlinkObject`, and `validateBackingGCSObjectForSymlink` to create either local symlinks through the mount or synthetic GCS symlink objects.

## State, persistence, dependencies, and integration points

Each test starts from the suite's unique `linkName` and `targetPath`. Standard symlinks store the target in object contents plus metadata; legacy symlinks store target in metadata with empty contents. Operation tests inspect both filesystem behavior and underlying GCS object representation where appropriate.

## Risks and test signals

Risks include dereferencing symlinks during copy, damaging target files during rename, inability to read standard symlinks in legacy mode, and divergent semantics for file versus directory targets. Signals are exact target path readback, content propagated through symlink writes, directory entry expectations, `ModeSymlink` bits from `Lstat`, and target existence after symlink rename/copy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_operations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_suites_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_suites_test.go

## Purpose

Defines the reusable symlink suite infrastructure and the standard/legacy suite types. It handles per-test mounting, directory setup, synthetic GCS symlink object creation, backing-object validation, and config-driven suite dispatch.

## Important APIs, control flow, and dependencies

`BaseSymlinkSuite` stores flags, mount directory, test directory, representation mode, link name, and target path. `SetupTest` mounts gcsfuse for non-GKE runs and creates unique names. `TearDownTest` unmounts, saves logs, and cleans the GCS prefix. Helpers include `createSymlink`, `createTempFile`, `validateBackingGCSObjectForSymlink`, and `createGCSSymlinkObject`, the latter using `client.NewWriter`. `RunTests` selects config items by `Run` name and splits flag strings with `strings.Fields`.

## State, persistence, dependencies, and integration points

The backing-object validator reads object attrs and contents from GCS to enforce representation details: standard symlinks must contain the target and both metadata keys, while legacy symlinks must have size zero, the old metadata key, and no standard marker. Synthetic object creation waits for size updates on zonal buckets.

## Risks and test signals

Risks include per-test mount overhead, flag parsing that depends on whitespace rather than comma splitting, and cleanup interactions with GKE mounted directories. Signals are no-error mount/setup, exact metadata/content assertions, and successful suite selection for both `TestStandardSymlinksTestSuite` and `TestLegacySymlinksTestSuite`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/symlink_handling/symlink_suites_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/test_config.yaml -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/test_config.yaml

## Purpose

Central YAML manifest for gcsfuse integration test suites. It maps suite names to mounted-directory placeholders, bucket placeholders, optional only-dir or secondary mount placeholders, flag matrices, bucket-type compatibility, optional `run` filters, and whether the case runs on GKE.

## Important APIs, control flow, and dependencies

The file is consumed by `test_suite.ReadConfigFile` and `setup.BuildFlagSets`. Top-level suites include directory behavior, operations, streaming writes, stale handles, unfinalized objects, unsupported paths, symlink handling, buffered/read cache, credential and mounting tests, flag optimizations, monitoring, managed folders, rapid appends, and concurrent operations. Relevant entries for this subset include `streaming_writes` flags with one MiB write blocks and unlimited global blocks, `stale_handle` split by streaming enabled/disabled `Run` names, `unfinalized_object` split by read/operation/tailing read runs and metadata TTLs, `unsupported_path` with `--enable-unsupported-path-support`, and `symlink_handling` split by standard-symlink enablement.

## State, persistence, dependencies, and integration points

The YAML is not executable but it controls runtime coverage and mount persistence behavior. Placeholder expansion injects bucket names, mounted directories, key files, billing projects, log files, cache paths, and profiler labels. Compatibility maps determine whether flat, HNS, or zonal buckets execute each flag set, and `run` names allow a package `TestMain` to run only the intended suite method.

## Risks and test signals

Risks include config drift from fallback configs embedded in Go files, comma-versus-space flag syntax differences, missing compatibility coverage, and stale `run` names silently skipping tests. Test signals are indirect: package `TestMain` functions should build non-empty compatible flag sets, run only matching suites when `run` is set, and skip incompatible bucket types as declared.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/test_config.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/setup_test.go

## Purpose

Bootstraps integration tests for unfinalized and appendable zonal objects. It restricts the package to zonal bucket runs, builds fallback configs for read, operation, and tailing-read suites, and wires static mounting for each compatible flag set.

## Important APIs, control flow, and dependencies

`TestMain` loads `cfg.UnfinalizedObject`, supplies fallback config items for `TestUnfinalizedObjectReadTest`, `TestUnfinalizedObjectOperationTest`, and `TestUnfinalizedObjectTailingReadTest`, calls `setup.TestEnvironment`, exits early when `setup.IsZonalBucketRun` is false, creates a storage client, handles mounted-directory mode, sets up the test bucket directory, and stores `mountFunc` as `static_mounting.MountGcsfuseWithStaticMountingWithConfigFile`.

## State, persistence, dependencies, and integration points

The package globals mirror stale-handle setup: `testEnv`, `mountFunc`, `mountDir`, and `rootDir`. Fallback flags vary metadata cache TTL and `--enable-kernel-reader=false` because these tests depend on fresh or cached stat/read behavior after remote appends to an unfinalized object.

## Risks and test signals

Primary risks are accidentally running against non-zonal buckets, where appendable object semantics are unavailable, and stale metadata cache hiding size or generation changes. Signals are early skip for non-zonal environments, successful setup of zonal static or mounted-directory runs, and downstream read/operation/tailing tests observing unfinalized object behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/tailing_reads_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/tailing_reads_test.go

## Purpose

Tests tailing reads from an open handle while an unfinalized zonal object is remotely appended at the same generation. It validates that file size and sequential reads advance as appendable object content grows.

## Important APIs, control flow, and dependencies

`unfinalizedObjectTailingReads` sets up a mounted suite, creates a per-test directory and file name, and uses `client.CreateUnfinalizedObject`, `os.OpenFile`, `readFile.Stat`, `client.AppendableWriter`, and `operations.CloseFileShouldNotThrowError`. `TestTailingRead` reads initial content, then loops twice: fetch object attrs and generation, open an appendable writer for that generation, write random data, close, sleep past the two-second metadata TTL, stat the open handle, and read the newly appended bytes.

## State, persistence, dependencies, and integration points

The object generation should remain stable across appends. The read handle remains open, so the test probes whether gcsfuse refreshes size for an existing handle after metadata TTL expiry and can continue reading from the current file offset.

## Risks and test signals

Risks include fixed sleeps causing flakiness, metadata cache not expiring, remote append changing generation unexpectedly, and kernel-reader differences. Signals are exact initial read content, updated `Stat` size after each append, exact appended data read from the same handle, and successful close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/tailing_reads_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/unfinalized_object_operations_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/unfinalized_object_operations_test.go

## Purpose

Covers non-read operations and metadata behavior for unfinalized zonal objects: visible nonzero sizes, same-mount creation and finalization, rename semantics, inode preservation on remote append, and inode change on remote overwrite.

## Important APIs, control flow, and dependencies

`unfinalizedObjectOperations` manages suite mount lifecycle and per-test setup. Helper `setupUnfinalizedObjectAndGetInitialInode` creates an unfinalized object and stats it with `operations.StatFileOrFatal`. Tests use `client.CreateUnfinalizedObject`, `operations.CreateFile`, `WriteWithoutClose`, `SyncFile`, `StatFile`, `RenameFile`, `AppendableWriter`, object attrs, and GCS validation helpers.

## State, persistence, dependencies, and integration points

Tests distinguish same-generation append from generation-changing overwrite. A remote append should update size while preserving inode ID; a remote overwrite should change the inode. Same-mount unfinalized creation writes and syncs without final close, then additional writes and close finalize the object. Rename tests verify object movement and stale-handle behavior for old file descriptors.

## Risks and test signals

Risks include known skipped overwrite behavior (`b/411333280`), incorrect inode identity when generation does not change, and rename of unfinalized objects from different mounts. Signals are nonzero stat sizes, final size doubling after close, object-not-found for renamed source, exact content at destination, ESTALE after writing through a stale handle, preserved generation on append, and changed inode on overwrite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/unfinalized_object_operations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/unfinalized_read_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/unfinalized_read_test.go

## Purpose

Tests read behavior for unfinalized zonal objects created through the mount or modified remotely. It focuses on O_DIRECT versus non-O_DIRECT reads after remote append, EOF behavior, and content visibility beyond the cached object size.

## Important APIs, control flow, and dependencies

Constants define one MiB initial and append sizes plus read flags. `setupAndAppend` creates an unfinalized object, opens it with requested flags, reads initial content to cache state, appends remotely with `client.AppendableWriter` at the current generation, and verifies generation stability. `TestUnfinalizedObjectsCanBeRead` reads an unfinalized same-mount file through an O_DIRECT readonly handle. `TestReadRemotelyModifiedUnfinalizedObject` table-drives offsets, read sizes, expected byte counts, EOF expectations, and expected content stitching.

## State, persistence, dependencies, and integration points

The key state distinction is cached size versus actual size after append. O_DIRECT reads are expected to bypass or refresh enough state to read appended bytes, including partial ranges crossing the original end; non-O_DIRECT reads beyond cached size currently return EOF. The suite runs under metadata cache and kernel-reader flag variants from config.

## Risks and test signals

Risks include stale cached size, kernel read path differences, wrong EOF semantics, and generation mismatch after append. Signals are exact initial content, preserved generation, byte count and error equality for each subcase, and expected content slices combining original and appended data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/unfinalized_read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unsupported_path/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/unsupported_path/setup_test.go

## Purpose

Bootstraps integration tests for GCS object names that cannot be represented cleanly as POSIX paths. It loads or supplies config with unsupported-path support enabled and runs the package over compatible static mount flag sets or a provided mounted directory.

## Important APIs, control flow, and dependencies

`TestMain` defines `DirForUnsupportedPathTests`, parses setup flags, reads `cfg.UnsupportedPath`, supplies fallback flags with `--implicit-dirs`, `--enable-unsupported-path-support=true`, high rename-dir limit, negative metadata cache disabled, and gRPC/non-gRPC variants. It initializes `ctx`, `bucketType`, `storageClient`, builds flag sets, sets up the test directory, and calls `static_mounting.RunTestsWithConfigFile`.

## State, persistence, dependencies, and integration points

The globals `storageClient`, `ctx`, and `bucketType` are consumed by the test suite. Bucket-type knowledge matters because zonal tests create finalized objects while flat/HNS use normal object creation.

## Risks and test signals

Risks include unsupported-path support not actually enabled, incompatible gRPC zonal coverage, and globals being unset if setup exits early. Signals are successful mount initialization and downstream tests observing unsupported object filtering, copying, rename, and deletion behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unsupported_path/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unsupported_path/unsupported_path_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/unsupported_path/unsupported_path_test.go

## Purpose

Verifies filesystem behavior when a GCS prefix contains object names with unsupported path components such as double slashes, `/.`, `/..`, terminal `.`, terminal `..`, and nested unsupported segments.

## Important APIs, control flow, and dependencies

`UnsupportedPathSuite` sets up a mounted test directory and bucket prefix, populates unsupported and supported objects in `createTestObjects`, and tests `os.ReadDir`, `operations.CopyDir`, `operations.RenameDir`, and `os.RemoveAll`. It uses `client.CreateObjectOnGCS` or `client.CreateFinalizedObjectOnGCS` depending on bucket type, and `client.ListDirectory` to inspect raw GCS entries after operations.

## State, persistence, dependencies, and integration points

The suite deliberately creates objects that may be hidden or normalized by POSIX path handling. List and copy operations are expected to expose/copy only supported entries plus representable parent directories, while rename and delete are expected to operate on all GCS objects under the prefix, including unsupported names.

## Risks and test signals

Risks include path normalization accidentally escaping the test prefix, copy losing representable parent directories, rename omitting hidden unsupported children, and remove-all leaving raw GCS objects behind. Signals are exact local entry names for list, exact copied object names for copy, thirteen expected raw object names after rename, stat failure after delete, and empty raw GCS listing after removal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/unsupported_path/unsupported_path_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/benchmark_setup/benchmark_setup.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/benchmark_setup/benchmark_setup.go

## Purpose

Provides a small reflection-based benchmark runner for integration benchmark suites. It discovers methods named `Benchmark*` on a struct, runs each as a sub-benchmark, and wraps each benchmark with setup and teardown hooks.

## Important APIs, control flow, and dependencies

`Benchmark` requires `SetupB(*testing.B)` and `TeardownB(*testing.B)`. `getBenchmarkFunc` looks up a named method on a reflected value and verifies it has signature `func(*testing.B)`, failing the benchmark immediately if not. `RunBenchmarks` iterates `reflect.TypeOf(x).NumMethod`, filters names with `strings.HasPrefix("Benchmark")`, and calls `b.Run` with `b.Cleanup` registered before `x.SetupB` and benchmark execution.

## State, persistence, dependencies, and integration points

No persistent state is owned by this utility. It coordinates suite-local benchmark resources by guaranteeing teardown registration even if setup or the benchmark body fails. Benchmarks using this helper can keep their own state on the receiver.

## Risks and test signals

Risks include reflection method-set surprises for pointer versus value receivers, non-deterministic method ordering, and accidentally running helper methods prefixed with `Benchmark`. Signals are sub-benchmark execution and teardown counts covered by the companion test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/benchmark_setup/benchmark_setup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/benchmark_setup/benchmark_setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/benchmark_setup/benchmark_setup_test.go

## Purpose

Verifies the reflection benchmark runner invokes setup, benchmark methods, and teardown exactly once per discovered benchmark method in the tested scenario.

## Important APIs, control flow, and dependencies

`benchmarkStructure` records counters for setup, teardown, and two benchmark methods. `BenchmarkRunBenchmarks` creates the struct, calls `benchmark_setup.RunBenchmarks`, and asserts the counters: two setup calls, one call to each benchmark method, and two teardown calls. The benchmark methods sleep for one second to reduce repeated invocations from benchmark calibration.

## State, persistence, dependencies, and integration points

The only state is in-memory counters on the benchmark struct. The test depends on Go benchmark execution behavior and testify assertions.

## Risks and test signals

Risk comes from benchmarking semantics: `b.N` and calibration can call benchmark bodies multiple times, so this test intentionally makes methods slow to stabilize counts. Signals are exact counter assertions showing per-sub-benchmark setup and cleanup execution.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/benchmark_setup/benchmark_setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/control_client.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/control_client.go

## Purpose

Provides integration-test helpers around the GCS Storage Control API for managed folders and HNS folder creation. This client is used for test data setup, not application runtime behavior.

## Important APIs, control flow, and dependencies

`storageControlClientRetryOptions` configures gax timeout and retries for transient gRPC codes, including a temporary unauthenticated retry. `CreateControlClient` creates a `StorageControlClient` and sets create/delete managed folder call options. `CreateControlClientWithCancel` creates a cancelable context and close function. `DeleteManagedFoldersInBucket`, `CreateManagedFoldersInBucket`, and `CreateFolderInBucket` build Storage Control resource names and issue API requests.

## State, persistence, dependencies, and integration points

The helpers persist managed folder or HNS folder resources in the target bucket. They integrate with `setup.GetBucketAndObjectBasedOnTypeOfMount` and `internal/storage.FullBucketPathHNS` to respect only-dir mounts and HNS naming.

## Risks and test signals

Risks include fatal exits on setup failures, broad string matching for already-exists/not-found style errors, and a formatting bug in the `CreateControlClient` error string that uses `#{err}` instead of formatting `%v`. Signals are successful client creation, idempotent create/delete behavior for managed folders, and returned folder objects for HNS folder creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/control_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/gcs_helper.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/gcs_helper.go

## Purpose

Collects high-level GCS helper functions and constants used throughout integration tests for object creation, validation, test directory setup, unfinalized object creation, requester-pays toggling, and common file names/content.

## Important APIs, control flow, and dependencies

Constants define common file and directory names, contents, sizes, and permissions. Helpers wrap lower-level storage-client operations: `CreateImplicitDir`, `ValidateObjectNotFoundErrOnGCS`, `ValidateObjectContentsFromGCS`, `ValidateObjectChunkFromGCS`, `CloseFileAndValidateContentFromGCS`, `CreateLocalFileInTestDir`, `CreateObjectInGCSTestDir`, `CreateFinalizedObjectInGCSTestDir`, `SetupFileInTestDirectory`, `SetupTestDirectory`, `SetupUniqueTestDirectory`, `CreateNFilesInDir`, `GetCRCFromGCS`, `CreateUnfinalizedObject`, and requester-pays helpers.

## State, persistence, dependencies, and integration points

Most helpers create, delete, or inspect real GCS objects through `storage.Client`. `SetupTestDirectory` deletes existing objects with the target prefix and creates a directory marker object, using `setup.MntDir` and `setup.OnlyDirMounted` to map between mounted paths and bucket objects. `CreateUnfinalizedObject` uses appendable writer setup, writes content, closes without finalizing for zonal behavior, and sleeps for size visibility.

## Risks and test signals

Risks include fatal test termination on validation mismatches, string-matching object-not-found errors, sleeps for eventual size visibility, and helpers that assume object content fits in memory. Signals are direct content equality, expected not-found errors, CRC availability, requester-pays state changes, and clean test directories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/gcs_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/storage_client.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/storage_client.go

## Purpose

Implements the lower-level GCS storage client layer for integration tests. It selects HTTP/1, gRPC, zonal, TPC endpoint, and key-file authentication modes; centralizes retry behavior; and provides object, bucket, upload, download, appendable writer, listing, and cleanup helpers.

## Important APIs, control flow, and dependencies

Client construction includes `ShouldRetryForTest`, `CreateHttp1StorageClient`, `CreateStorageClient`, `getTokenSrc`, and `CreateStorageClientWithCancel`. Object IO helpers include `ReadObjectFromGCS`, `ReadChunkFromGCS`, `NewWriter`, `WriteToObject`, `CreateObjectOnGCS`, `CreateFinalizedObjectOnGCS`, `DownloadObjectFromGCS`, `DeleteObjectOnGCS`, `DeleteAllObjectsWithPrefix`, `StatObject`, `UploadGcsObjectWithPreconditions`, `UploadGcsObject`, `CopyFileInBucket`, `CopyFileInBucketWithPreconditions`, `NewWriterWithPreconditionsSet`, `AppendableWriter`, `CreateGcsDir`, `BatchUploadFilesWithoutIntermediateDelays`, `ListDirectory`, and `CheckBucketAccess`.

## State, persistence, dependencies, and integration points

The helpers persist and mutate real GCS objects and bucket state. `CreateStorageClient` uses gRPC with bidi reads for zonal buckets, HTTP/1 with HTTP/2 disabled otherwise, optional service account key files, optional billing project through `getBucketHandle`, and `RetryAlways` with custom retry filtering. `NewWriter` detects RAPID storage class and configures appendable writer behavior for zonal runs; non-zonal tests encountering a RAPID bucket return an error.

## Risks and test signals

Risks include broad retries masking real failures, fatal exits in bucket deletion/copy helpers, in-memory reads for large objects, wait/sleep assumptions for zonal size visibility, duplicate entries in combined object/folder listings, and a suspicious no-op `ClearCacheControlOnGcsObject` that mutates fetched attrs without issuing an update. Signals are successful object reads/writes with preconditions, appendable writes at a generation, concurrent prefix deletion/upload without joined errors, and bucket access/listing checks that respect requester-pays and only-dir mount mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/client/storage_client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/creds_tests/creds.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/creds_tests/creds.go

## Purpose

Provides shared credential-test setup for gcsfuse integration suites that need to verify `--key-file` and `GOOGLE_APPLICATION_CREDENTIALS` authentication behavior with controlled service-account permissions.

## Important APIs, control flow, and dependencies

`projectID` reads metadata server project ID, maps cloudtop environments to a whitelisted test project, and logs when the project is not whitelisted. `CreateCredentials` and `CreateCredentialsForSA` fetch a service account key from Secret Manager and write it to a temp JSON file. IAM helpers add and remove storage roles or custom roles on a bucket. `RunTestsForDifferentAuthMethods` creates credentials, grants the requested permission, runs tests with `GOOGLE_APPLICATION_CREDENTIALS`, then with both env var and `--key-file`, then with `--key-file` only. A deprecated wrapper builds a config from setup flags.

## State, persistence, dependencies, and integration points

The utility mutates bucket IAM policy and local process environment, writes a temporary credential file, and depends on metadata, Secret Manager, IAM, storage client, static mounting, and test-suite config. It deliberately sleeps two minutes after IAM changes for propagation before running mounts.

## Risks and test signals

Risks include long IAM propagation delays, fatal exits on secret/IAM failures, leaked credentials or environment variables if execution aborts, and tests running in non-whitelisted projects with only a log warning. Signals are successful mount/test runs under all three credential combinations and deferred role revocation and temp-file cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/creds_tests/creds.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/buffered_read_log_parser.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/buffered_read_log_parser.go

## Purpose

Parses JSON-formatted gcsfuse buffered-read trace logs into structured per-file-handle entries with chunk reads, request IDs, execution times, fallback status, random seek count, and restart status.

## Important APIs, control flow, and dependencies

The parser defines regexes for `ReadFile`, buffered `ReadAt` requests, simple `ReadAt` responses, fallback messages, and restart messages. `ParseBufferedReadLogsFromLogReader` loads lines, calls `filterAndParseLogLineForBufferedRead`, and drops handles that never produced buffered chunks. Parsing functions create `BufferedReadLogEntry` on `ReadFile`, append `BufferedReadChunkData` on `ReadAt` requests, map request ID back to handle/chunk in `opReverseMap`, fill execution time on responses, and mark fallback or restart events.

## State, persistence, dependencies, and integration points

Parser state is held in maps keyed by file handle and request ID. It depends on log message ordering: a `ReadFile` must precede `ReadAt`, and a request must precede its response. Non-JSON lines are ignored, while malformed JSON logs with expected fields missing produce errors.

## Risks and test signals

Risks include brittle regexes tied to exact log strings, JSON type assertions that can panic on malformed timestamp/message shapes, and fallback logs for unknown handles being treated as errors. Signals are structured maps with expected common read fields, chunks, execution time, fallback/random seek count, restarted flag, and expected errors for missing prerequisite logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/buffered_read_log_parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/buffered_read_log_parser_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/buffered_read_log_parser_test.go

## Purpose

Unit-tests the buffered read JSON log parser for successful parsing, ignored noise, fallback detection, restart detection, and key malformed-order errors.

## Important APIs, control flow, and dependencies

`TestParseBufferedReadLogsFromLogReaderSuccessful` builds in-memory log streams with `bytes.NewReader` and expected `map[int64]*read_logs.BufferedReadLogEntry` values. Cases cover one chunk, multiple chunks on the same handle, no fallback, no parsable logs, fallback with random seek count, generic fallback, non-JSON logs, and restart. `TestBufferedReadLogsFromLogReaderUnsuccessful` asserts errors for missing `ReadFile`, response without request, invalid read-file fields, and fallback for unknown handle.

## State, persistence, dependencies, and integration points

The tests are pure unit tests and call `setup.IgnoreTestIfIntegrationTestFlagIsSet` to avoid running during integration-only invocations. They validate parser state transitions across multiple JSON lines and request-ID reverse mapping.

## Risks and test signals

Risks include equality fragility when parser structs gain fields, hard-coded log formats drifting from gcsfuse trace output, and incomplete malformed JSON coverage for panics. Signals are exact struct equality for successful cases and substring matching for expected parser errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/buffered_read_log_parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/helpers.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/helpers.go

## Purpose

Contains shared parsing helpers for read-cache and job-log JSON parsers, including integer conversion, log line loading, tokenized file-cache read parsing, and job/chunk download message parsing.

## Important APIs, control flow, and dependencies

`parseToInt64` wraps decimal parsing with contextual errors. `loadLogLines` reads an entire `io.Reader` and splits by newline. `parseReadFileLog`, `parseFileCacheRequestLog`, and `parseFileCacheResponseLog` parse older tokenized file-cache messages into `StructuredReadLogEntry` and `ReadChunkData`, maintaining an operation reverse map. `parseJobFileLog` and `parseChunkDownloadLog` use regexes to populate `Job`, `JobData`, and `ChunkDownloadLogEntry`.

## State, persistence, dependencies, and integration points

All parser state is in caller-provided maps keyed by file handle, operation ID, or job ID. The helpers assume a specific token order and punctuation from gcsfuse logs, including trailing commas and `bucket:/object` formatting.

## Risks and test signals

Risks include index panics on short token arrays, regexes that do not support unusual object characters, whole-file log loading for large logs, and silent boolean parse errors in file-cache responses. Signals are downstream parser tests that validate exact job offsets, chunk ranges, file-cache chunks, and clear errors when expected patterns are absent.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/helpers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_job_log_parser.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_job_log_parser.go

## Purpose

Parses JSON gcsfuse job download logs for read-cache tests and exposes a helper that returns structured job log entries from a log file.

## Important APIs, control flow, and dependencies

`parseJobLogsFromLogFile` loads lines and delegates each JSON line to `filterAndParseJobLogLine`. The filter unmarshals JSON, extracts timestamp and message, normalizes whitespace with a regexp, and dispatches to `parseJobFileLog` for `downloaded till` messages or `parseChunkDownloadLog` for sparse-file range downloads. `GetJobLogsSortedByTimestamp` opens a log file, parses it, and converts the resulting map to a slice.

## State, persistence, dependencies, and integration points

The parser reads log files from disk but maintains only in-memory maps. Despite the function name, `GetJobLogsSortedByTimestamp` does not sort; it iterates over a map, so ordering is nondeterministic. It depends on shared helper structs and setup log path reporting.

## Risks and test signals

Risks include panic on JSON logs missing timestamp or message, nondeterministic output order, and regex limitations for bucket/object names. Signals are successful parsing of repeated job entries and chunk download ranges in the companion unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_job_log_parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_job_log_parser_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_job_log_parser_test.go

## Purpose

Unit-tests job log parsing for file-cache progress logs and sparse chunk download logs.

## Important APIs, control flow, and dependencies

`TestParseJobLogsSuccessful` defines table cases with in-memory JSON logs and expected `map[string]*Job` values. It verifies a single job entry, repeated entries for the same job plus a second job with hyphenated bucket and nested object path, and a chunk download range entry with start/end offsets and bytes added.

## State, persistence, dependencies, and integration points

The test is pure and skipped when integration-test flags are set. It validates accumulation into existing map entries and construction of `ChunkCacheDownloads` separately from regular `JobEntries`.

## Risks and test signals

Risks include exact struct equality failing when new fields are added, lack of negative tests for malformed job logs, and not checking the advertised sorted order of `GetJobLogsSortedByTimestamp`. Signals are exact expected maps for all successful parser scenarios.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_job_log_parser_test.go -->
