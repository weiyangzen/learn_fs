# subset-b-009601 research

Grouped research report for selected gcsfuse integration utilities, test suites, operational tools, proxy helpers, package tools, and tracing files. Each section preserves the exact source path and is wrapped for reconciliation into the required source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_read_log_parser.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_read_log_parser.go

Purpose: parses JSON-formatted gcsfuse read/cache trace logs into structured entries keyed by file handle, and exposes helpers for tests that need logs sorted by read start timestamp.

Important APIs/types/functions: `filterAndParseLogLine`, `ParseReadLogsFromLogFile`, `GetStructuredLogsSortedByTimestamp`, and `ParseJsonLogLineIntoLogEntryStruct`. It depends on helper parsers in the same package for read-file, file-cache request, and file-cache response messages.

Control flow: each input line is JSON-decoded; non-JSON lines are ignored. Timestamp and message fields are extracted with direct type assertions, whitespace is normalized, and message substrings route the line to one of the specialized parsers. File-cache requests populate a reverse operation-id map so later response logs can update the matching chunk.

State/persistence behavior: all state is in memory: a handle-to-read-entry map and operation-id-to-chunk-index map. The package reads from an `io.Reader` or opened log file but does not persist parser output.

Dependencies/integration: integrates with gcsfuse trace log format, `setup.LogFile()` for error context, and Go tests that inspect read-cache behavior.

Risks/test signals: malformed JSON is ignored, but malformed structured JSON with missing or mistyped fields can panic because of unchecked type assertions. Tests cover expected log sequences, ignored non-JSON logs, and parser errors for missing prerequisite log records.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_read_log_parser.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_read_log_parser_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_read_log_parser_test.go

Purpose: unit-tests the JSON read-log parser used by integration tests for read cache and file cache behavior.

Important APIs/types/functions: `TestParseLogFileSuccessful`, `TestParseLogFileUnsuccessful`, shared constants for timestamps, object metadata, handle ids, and `chunkData` expected output. Tests use `ParseReadLogsFromLogFile` and compare maps of `StructuredReadLogEntry`.

Control flow: successful cases feed in-memory multiline log streams covering a single chunk, repeated chunks, irrelevant JSON logs, and non-JSON input. Failure cases omit the preceding read or file-cache request logs or corrupt numeric tokens to ensure parser errors contain expected fragments.

State/persistence behavior: tests are pure in-memory `bytes.Reader` cases and call `setup.IgnoreTestIfIntegrationTestFlagIsSet`, so they are intended for normal unit-test runs rather than integration-test executions.

Dependencies/integration: depends on `testify/assert`, `testify/require`, and exact gcsfuse trace-message shapes.

Risks/test signals: tests validate happy paths and several parser-level errors, but they do not cover JSON records with missing `timestamp` or `message` fields that could panic in production parser code.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/json_read_log_parser_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/structure.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/structure.go

Purpose: defines shared structured log data models for read-cache, chunk-cache, job, and buffered-read log parsers.

Important APIs/types/functions: `CommonReadLog`, `StructuredReadLogEntry`, `ReadChunkData`, `Job`, `JobData`, `ChunkCacheReadLogEntry`, `ChunkDownloadLogEntry`, internal `handleAndChunkIndex`, `LogEntry`, `BufferedReadLogEntry`, and `BufferedReadChunkData`.

Control flow: there is no executable flow; the file supplies DTO-style structs embedded or populated by parser files. `StructuredReadLogEntry` embeds `CommonReadLog` and appends chunk details; `BufferedReadLogEntry` extends the same common read fields with fallback/restart flags.

State/persistence behavior: these structs represent in-memory parsed logs only. Timestamps are stored as seconds/nanos fields for parser comparison, while generic `LogEntry` stores a `time.Time`.

Dependencies/integration: consumed by JSON read parser, buffered read parser, job parser, and integration tests that assert read/cache behavior.

Risks/test signals: the models assume parser ordering means chunks are timestamp-sorted; if log files are not pre-sorted, downstream tests may infer incorrect chronology.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/log_parser/json_parser/read_logs/structure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/dynamic_mounting/dynamic_mounting.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/dynamic_mounting/dynamic_mounting.go

Purpose: provides integration-test orchestration for dynamic bucket mounting, where the root mount exposes accessible buckets and tests run inside the selected test bucket subdirectory.

Important APIs/types/functions: `MountGcsfuseWithDynamicMountingWithConfig`, deprecated `MountGcsfuseWithDynamicMounting`, `runTestsOnGivenMountedTestBucket`, `executeTestsForDynamicMounting`, and `RunTestsWithConfigFile`.

Control flow: default log flags and the root mount directory are appended to each flag set, gcsfuse is mounted, the effective test mount path is changed to `<root>/<bucket>`, tests run, then global and config mount paths are restored before unmounting.

State/persistence behavior: mutates `setup` globals via `SetMntDir` and `SetDynamicBucketMounted`, and mutates `TestConfig.GCSFuseMountedDirectory` during each iteration. Persistent effects are the gcsfuse mount and log file.

Dependencies/integration: wraps `mounting.MountGcsfuse`, `setup.ExecuteTest`, `setup.UnMountAndThrowErrorInFailure`, and the common `test_suite.TestConfig`.

Risks/test signals: failures can leave global mount state inconsistent if cleanup paths are interrupted. The deprecated signature ignores its `context` and storage client parameters, signaling ongoing migration to config-file driven tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/dynamic_mounting/dynamic_mounting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/mounting.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/mounting.go

Purpose: central low-level helper for invoking a gcsfuse or mount.gcsfuse binary from integration-test mounting packages.

Important APIs/types/functions: `MountGcsfuse(binaryFile string, flags []string) error`.

Control flow: constructs `exec.Command(binaryFile, flags...)`, ensures the integration log directory exists, appends the command line to `setup.LogFile()`, runs the mount command via `CombinedOutput`, and wraps any mount failure.

State/persistence behavior: writes the command invocation to the configured log file and creates its parent directory. The actual mount is external process state controlled by gcsfuse/fusermount.

Dependencies/integration: used by static, dynamic, only-dir, and persistent mounting helpers. It depends on `setup.LogFile()` and `operations.CloseFile`.

Risks/test signals: if opening the log file fails, the code still defers `operations.CloseFile(file)` on a possibly nil file, which can panic. Errors are surfaced primarily through mount command output and wrapped process failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/mounting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/only_dir_mounting/only_dir_mounting.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/only_dir_mounting/only_dir_mounting.go

Purpose: orchestrates integration tests for `--only-dir` mounts, including cases where the mounted prefix exists and does not exist in the bucket.

Important APIs/types/functions: `MountGcsfuseWithOnlyDirWithConfigFile`, deprecated `MountGcsfuseWithOnlyDir`, `executeTestsForOnlyDirMounting`, `mountGcsFuseForFlagsAndExecuteTests`, and `RunTestsWithConfigFile`.

Control flow: sets `setup.OnlyDirMounted`, deletes objects under the target prefix, runs each flag set, creates the prefix using storage-client helpers, runs the flag sets again, deletes the prefix, and resets only-dir state.

State/persistence behavior: mutates global only-dir state in `setup`, creates/deletes GCS objects under the test directory, mounts/unmounts gcsfuse, and writes trace logs.

Dependencies/integration: depends on `client.CreateStorageClient`, `client.DeleteAllObjectsWithPrefix`, `client.SetupTestDirectory`, and `mounting.MountGcsfuse`.

Risks/test signals: cleanup errors are logged with `%w` but through `log.Println`, so wrapping is ineffective. Because each flag set mounts and runs tests twice, failures can be sensitive to leftover bucket state or unmount failures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/only_dir_mounting/only_dir_mounting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/persistent_mounting/perisistent_mounting.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/persistent_mounting/perisistent_mounting.go

Purpose: supports integration tests through the persistent mount helper path, translating CLI-style gcsfuse flags into `-o` options for `mount.gcsfuse`.

Important APIs/types/functions: `makePersistentMountingArgs`, `mountGcsfuseWithPersistentMountingWithConfigFile`, `executeTestsForPersistentMountingWithConfigFile`, and `RunTestsWithConfigFile`.

Control flow: transforms flags by removing `--o=`, changing hyphens to underscores, stripping doubled underscores, and restoring `_1` to `-1`; appends each as separate `-o` option after bucket, mount point, trace severity, and log file; mounts through `setup.SbinFile`; then runs tests for each flag set.

State/persistence behavior: creates persistent mount process state and writes logs through gcsfuse. It does not create its own durable files beyond the configured log.

Dependencies/integration: consumes `test_suite.TestConfig`, `mounting.MountGcsfuse`, `setup.ExecuteTestForFlagsSet`, and the mount helper built or installed by setup.

Risks/test signals: flag rewriting is string-based and can corrupt values containing hyphens or `_1` sequences unrelated to negative values. Tests using persistent mounting validate whether translated options still behave as intended.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/persistent_mounting/perisistent_mounting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/static_mounting/static_mounting.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/static_mounting/static_mounting.go

Purpose: standard static bucket mounting harness for integration tests.

Important APIs/types/functions: `MountGcsfuseWithStaticMountingWithConfigFile`, deprecated `MountGcsfuseWithStaticMounting`, `executeTestsForStaticMounting`, and `RunTestsWithConfigFile`.

Control flow: optional TPC endpoint key-file flag is added, default trace log flags plus bucket and mount directory are appended, gcsfuse is mounted with `setup.BinFile`, and each flag set runs through `setup.ExecuteTestForFlagsSet`.

State/persistence behavior: establishes one gcsfuse mount per flag set and writes to the configured gcsfuse log file. It relies on setup globals for binary and endpoint mode.

Dependencies/integration: common entry point for packages such as write-large-files and implicit/explicit directory tests.

Risks/test signals: mutates the supplied `flags` slice by append, so callers reusing backing arrays could see unexpected changes. Failures are detected by mount errors or nonzero test exit codes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/static_mounting/static_mounting.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/dir_operations.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/dir_operations.go

Purpose: directory and bucket-management helpers for integration tests.

Important APIs/types/functions: permission constants, `CopyDir`, `CopyObject`, `Move`, `RenameDir`, `CreateDirectoryWithNFiles`, `RemoveDir`, `ReadDirectory`, verification helpers, `CreateDirectory`, `DirSizeMiB`, managed-folder helpers, and `CopyFileInBucket`.

Control flow: simple operations use OS commands or filesystem calls; `CreateDirectoryWithNFiles` creates many files concurrently with a bounded 1024-goroutine semaphore and reports the first create error through a buffered channel.

State/persistence behavior: creates, renames, removes, and lists local or mounted directories, and invokes `gcloud alpha storage` commands for managed folders and bucket file copy. These calls modify local filesystem, mounted gcsfuse view, and remote GCS bucket state.

Dependencies/integration: used by integration test packages that need large directory structures or managed folders. Uses `ExecuteGcloudCommand` from the same package.

Risks/test signals: shelling out to `cp`, `mv`, and `gcloud` makes behavior platform/tool dependent. `DirSizeMiB` assumes non-nil `info` in `filepath.Walk` even when an error is passed to the callback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/dir_operations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/file_operations.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/file_operations.go

Purpose: broad file-operation helper library for integration tests, including direct I/O reads/writes, content comparison, stat validation, checksum helpers, temp-file creation, GCS object utilities, and sync/error assertions.

Important APIs/types/functions: `CopyFile`, `WriteFileInAppendMode`, `WriteFile`, `ReadFileSequentially`, `WriteChunkOfRandomBytesToFiles`, `WriteFilesSequentially`, `ReadChunkFromFile`, `AreFilesIdentical`, `GetGcsObjectSize`, `CreateFile`, `OpenFiles`, `VerifyStatFile`, `CreateFileOfSize`, `CalculateFileCRC32`, `CreateLocalTempFile`, `ReadAndCompare`, `CreateLocalFile`, `ValidateSyncGivenThatFileIsClobbered`, and `StatFileOrFatal`.

Control flow: most helpers fail tests directly through `testing.TB` or return wrapped errors. Large-write helpers open matching local and mounted files, write identical random chunks at offsets, optionally sync, and compare byte-for-byte using fixed-size buffers.

State/persistence behavior: heavily mutates local files, mounted gcsfuse files, temp files under `/tmp`, and GCS objects through `gcloud`. It also waits after close/sync for zonal buckets to observe size updates.

Dependencies/integration: used across write, read, local-file, gzip, streaming-writes, and stale-handle tests. Depends on `setup`, internal GCS storage abstractions, `testify`, gzip, CRC32, and Linux `O_DIRECT`.

Risks/test signals: direct I/O imposes alignment constraints, and some helpers call fatal logging or exit indirectly via `CloseFile`. `CreateFileOfSize` converts random bytes to string, which can be memory-heavy for large files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/file_operations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/operations.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/operations.go

Purpose: miscellaneous operation helpers for random data generation, shelling out to external tools, and zonal bucket timing.

Important APIs/types/functions: `GenerateRandomData`, `ExecuteToolCommandfInDirectory`, `ExecuteGcloudCommandf`, `ExecuteGcloudCommand`, `runCommand`, and `WaitForSizeUpdate`.

Control flow: commands are executed through `/bin/bash -c`, stdout/stderr are captured, and failures return stdout plus a formatted error with stderr. Random data uses a time-seeded `math/rand` source.

State/persistence behavior: no direct persistent state beyond invoked commands. Command helpers can change remote GCS state depending on the gcloud command supplied.

Dependencies/integration: supports directory/file helpers and integration suites that need gcloud or other CLI tools.

Risks/test signals: command construction is shell-based, so callers must avoid untrusted input or unsafe quoting. Random bytes are not cryptographic, which is fine for test content but not for security-sensitive generation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/operations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/string_operations.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/string_operations.go

Purpose: small string and naming helpers for integration tests.

Important APIs/types/functions: `VerifyExpectedSubstrings`, `VerifyUnexpectedSubstrings`, `GetRandomName`, and `SplitBucketNameAndDirPath`.

Control flow: substring helpers iterate expected or unexpected fragments and record `t.Errorf`; random names use `uuid.NewRandom`; bucket splitting requires the form `<bucket>/<object-name>` and fails tests if no slash is present.

State/persistence behavior: no persistent state. The only state produced is a random UUID string.

Dependencies/integration: used by tests that verify command output, logs, or bucket/object path parsing.

Risks/test signals: substring checks continue after failures because they use `Errorf`, while split parsing uses `Fatalf`. `SplitBucketNameAndDirPath` only splits once, preserving deeper object paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/string_operations.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/validation_helper.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/validation_helper.go

Purpose: shared validation and retry helpers for integration tests.

Important APIs/types/functions: `ValidateNoFileOrDirError`, `ValidateObjectNotFoundErr`, `ValidateESTALEError`, `ValidateEIOError`, `CheckErrorForReadOnlyFileSystem`, `SkipKLCTestForUnsupportedKernelVersion`, and generic `RetryUntil[T]`.

Control flow: validators assert expected filesystem, syscall, read-only, and GCS not-found errors. `RetryUntil` loops until an operation returns nil error or a context deadline expires, logging attempts and failing the test on timeout.

State/persistence behavior: reads filesystem and GCS state but does not write it. `RetryUntil` creates a deadline context and ticker.

Dependencies/integration: integrates with internal `common`, `gcs`, `storageutil`, syscall errors, and `testify`.

Risks/test signals: error matching uses string/regexp checks around platform text, so behavior can vary by OS or wrapped error wording. `RetryUntil` fatal-exits tests rather than returning the last error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/operations/validation_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/implicit_and_explicit_dir_setup/implicit_and_explicit_dir_setup.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/implicit_and_explicit_dir_setup/implicit_and_explicit_dir_setup.go

Purpose: test setup helpers for explicit-directory objects, implicit-directory objects, and mixed directory structures.

Important APIs/types/functions: exported constants for directory/file names and counts, `RunTestsForExplicitAndImplicitDir`, `RemoveAndCheckIfDirIsDeleted`, `CreateImplicitDirectoryStructureUsingStorageClient`, `CreateImplicitDirectoryStructure`, `CreateExplicitDirectoryStructure`, `CreateImplicitDirectoryInExplicitDirectoryStructure`, and storage-client variant.

Control flow: the runner chooses mounted-directory mode, static mount, then persistent mount. Structure helpers create implicit objects through GCS client or the shell script and explicit files/directories through the mounted filesystem.

State/persistence behavior: creates and deletes local mounted paths and remote GCS objects. It depends on global `setup.TestBucket()` and `setup.MntDir()`.

Dependencies/integration: used by implicit and explicit directory integration suites, static/persistent mounting harnesses, `client` GCS helpers, and `operations` file helpers.

Risks/test signals: the script path is relative and can be sensitive to working directory. Mixed structures intentionally combine gcsfuse-created explicit directories with GCS-client-created implicit children, which is the key integration behavior under test.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/implicit_and_explicit_dir_setup/implicit_and_explicit_dir_setup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/implicit_and_explicit_dir_setup/testdata/create_objects.sh -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/implicit_and_explicit_dir_setup/testdata/create_objects.sh

Purpose: shell testdata creator for implicit directory objects in a GCS bucket or bucket prefix.

Important APIs/types/functions: no functions; the script creates a temporary directory, writes two local files, uploads them using `gcloud storage cp`, and removes the temp directory.

Control flow: `mktemp -d`, `cd`, write `fileInImplicitDir1`, upload to `gs://$1/implicitDirectory/`, write `fileInImplicitDir2`, upload to `gs://$1/implicitDirectory/implicitSubDirectory/`, return and delete the temp directory.

State/persistence behavior: creates transient local files and durable GCS objects under the supplied argument. It assumes `$1` is a bucket or bucket/prefix without shell-unsafe characters.

Dependencies/integration: equivalent to the Go `testdataCreateObjects` helper but uses the `gcloud` CLI.

Risks/test signals: no `set -euo pipefail`, no argument validation, and unquoted `gs://$1/...` arguments make it fragile for unusual bucket strings.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/implicit_and_explicit_dir_setup/testdata/create_objects.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/setup.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/setup.go

Purpose: central integration-test setup package for flags, global test state, gcsfuse build/install selection, mount directories, log artifacts, bucket type detection, config-derived flag sets, and mount/unmount helpers.

Important APIs/types/functions: flag accessors, global setters/getters, `SetUpTestDir`, `UnMount`, `ExecuteTestForFlagsSet`, skip helpers, `SetUpTestDirForTestBucket`, `SetupTestDirectory`, `CleanupDirectoryOnGCS`, `BucketType`, `BuildFlagSets`, `SetGlobalVars`, `GetBucketAndObjectBasedOnTypeOfMount`, mount wrappers, proxy-log helpers, GCE zone/region helpers, profiler flag parsers, and log-file path setup.

Control flow: tests parse flags, choose installed/prebuilt/source-built gcsfuse, create temp mount/log paths, derive bucket type through the storage API, build compatible flag sets from YAML config, mount if needed, execute tests, unmount, and save logs on failure.

State/persistence behavior: package-level globals hold binary paths, log path, mount dir, test dir, bucket, only-dir/dynamic mount context, billing project, and key file. It creates temp directories, writes artifact logs, deletes local directories, and deletes GCS objects during cleanup.

Dependencies/integration: integrates with Google Cloud Storage clients, experimental gRPC bidi reads, auth credentials, OpenTelemetry GCP resource detection, internal build utility, `test_suite` config models, and system `fusermount`.

Risks/test signals: global mutable state makes tests order-sensitive and migration-sensitive. Several helpers call `os.Exit` or `log.Fatal`, so failures can bypass defers. Bucket cleanup splits bucket/path with a simple two-element assumption.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/setup.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/yaml-config.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/yaml-config.go

Purpose: writes YAML configuration files into the current integration test directory.

Important APIs/types/functions: `YAMLConfigFile(yamlContent any, fileName string) string`.

Control flow: marshals arbitrary content with `yaml.Marshal`, joins the target name under `TestDir()`, writes the file with mode `0644`, and exits the process through `LogAndExit` on marshal or write failure.

State/persistence behavior: persists config files inside the integration test temp directory, often for generated gcsfuse mount config flags.

Dependencies/integration: used by setup helpers such as HNS flag injection and tests that need config files at runtime.

Risks/test signals: fatal process exit on write failures prevents local test recovery. It assumes `TestDir()` has already been initialized.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/yaml-config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/test_suite/config.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/test_suite/config.go

Purpose: defines YAML-backed integration-test configuration schemas and loader.

Important APIs/types/functions: `BucketType`, `TestConfig`, `ConfigItem`, top-level `Config`, and `ReadConfigFile`.

Control flow: `ReadConfigFile` reads a file path if non-empty, expands environment variables in the YAML content, unmarshals into `Config`, and returns an empty config when no path is supplied.

State/persistence behavior: reads config from disk but does not write. The resulting structs drive mount paths, buckets, log paths, compatibility, and flag sets across many test packages.

Dependencies/integration: consumed by `setup.BuildFlagSets`, mounting harnesses, and test `TestMain` functions. Uses `gopkg.in/yaml.v3`.

Risks/test signals: load and parse errors call `log.Fatalf`, terminating the process. `GCSFuseMountedDirectory` and log fields are not YAML-tagged, so they are runtime-populated rather than config-file fields.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/test_suite/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/test_suite/testify_interface.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/util/test_suite/testify_interface.go

Purpose: small interface adapter for testify suite types.

Important APIs/types/functions: `TestifySuite`, embedding `suite.TestingSuite` and requiring `Run(name string, subtest func()) bool`.

Control flow: no executable flow; it allows helpers to accept suite values that can run subtests.

State/persistence behavior: no state or persistence.

Dependencies/integration: depends on `github.com/stretchr/testify/suite`.

Risks/test signals: interface is narrow and useful for compile-time abstraction; no direct tests are present in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/util/test_suite/testify_interface.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/concurrent_write_files_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/concurrent_write_files_test.go

Purpose: integration test for concurrently writing multiple large files through gcsfuse.

Important APIs/types/functions: `TestWriteMultipleFilesConcurrently`, `DirForConcurrentWrite`, `errgroup.Group`, `operations.WriteFilesSequentially`, and `operations.AreFilesIdentical`.

Control flow: creates a test directory, generates three file names, starts one errgroup task per file, writes identical 500 MiB content to a local temp file and mounted file, then compares them.

State/persistence behavior: writes large local temp files under `/tmp` and large objects through the mounted gcsfuse directory; temp local files are removed via `t.Cleanup`.

Dependencies/integration: relies on `write_large_files_test.go` setup, static mounting, direct I/O helpers, and the bucket backend.

Risks/test signals: the errgroup wait result is ignored, so goroutine-returned errors would not fail the test except where helper assertions fail inside goroutines. It stresses global write-block limits and parallel object creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/concurrent_write_files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/concurrent_write_to_same_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/concurrent_write_to_same_file_test.go

Purpose: integration test for concurrent writes to disjoint offsets in the same mounted file.

Important APIs/types/functions: `TestWriteToSameFileConcurrently` and helper `writeToFileSequentially`.

Control flow: creates local and mounted files, starts five goroutines, assigns each a non-overlapping 10 MiB range within a 50 MiB region, writes matching random 1 MiB chunks to both files, waits for all writers, and compares mounted content with local content.

State/persistence behavior: mutates one local temp file and one mounted gcsfuse file concurrently. On zonal buckets, files are explicitly synced after each writer completes.

Dependencies/integration: depends on `operations.OpenFiles`, `WriteChunkOfRandomBytesToFiles`, `SyncFiles`, and the package-level setup/mount state.

Risks/test signals: concurrent writes to the same local file and mounted file assume disjoint offsets avoid racey content conflicts. The main test checks errgroup errors and byte equality.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/concurrent_write_to_same_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/random_write_large_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/random_write_large_file_test.go

Purpose: integration test for random offset writes into a large sparse file through gcsfuse.

Important APIs/types/functions: `TestWriteLargeFileRandomly`, `NumberOfRandomWriteCalls`, `DirForRandomWrite`, and `MaxFileOffset`.

Control flow: opens a local and mounted file, performs 20 random writes of `ChunkSize` bytes below 500 MiB, aligns offsets to 4 KiB for `O_DIRECT`, writes identical chunks to both files, closes them, and compares content.

State/persistence behavior: creates local temp state and a mounted object with random sparse writes. Content is persisted through close/sync behavior in helpers.

Dependencies/integration: uses `internal/cache/util.KiB` for alignment and shared write-large-file constants.

Risks/test signals: randomness means coverage varies by run; it validates final content equivalence rather than specific offsets. Sparse-file semantics and direct I/O alignment are important.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/random_write_large_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/seq_write_large_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/seq_write_large_file_test.go

Purpose: integration test for sequentially writing a 500 MiB file through gcsfuse.

Important APIs/types/functions: constants `FiveHundredMB`, `ChunkSize`, `DirForSeqWrite`, variable `FiveHundredMBFile`, and `TestWriteLargeFileSequentially`.

Control flow: creates a mounted test directory, builds matching local and mounted paths, writes both sequentially in 20 MiB chunks, then compares file content.

State/persistence behavior: writes a large local temp file and a large mounted object; removes only the local temp file in cleanup.

Dependencies/integration: core test for write-large-files package setup and operations helpers.

Risks/test signals: the generated `FiveHundredMBFile` is package-global, so all tests in the process share that name. Signal is byte-for-byte equality after sequential write completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/seq_write_large_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/slow_file_write_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/slow_file_write_test.go

Purpose: integration test for slow large writes with long pauses between synced chunks.

Important APIs/types/functions: `TestSlowWriteToFile` and `DirForSlowWrite`.

Control flow: opens a mounted file with `O_DIRECT`, generates a 33 MiB string, writes it twice, syncs after each write, asserts byte counts, and sleeps 40 seconds between writes to exceed the referenced 32 second chunk retry deadline.

State/persistence behavior: creates and syncs a mounted gcsfuse file. No local oracle file is used.

Dependencies/integration: uses `operations.OpenFileWithODirect`, `operations.SyncFile`, and setup random-string generation.

Risks/test signals: expensive and timing-sensitive by design. It checks write/sync success but not final file content or size explicitly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/slow_file_write_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/write_large_files_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/write_large_files_test.go

Purpose: package-level `TestMain` and shared constants/state for large-file write integration tests.

Important APIs/types/functions: constants `TmpDir`, `OneMiB`, `WritePermission_0200`, package globals `storageClient` and `ctx`, and `TestMain`.

Control flow: parses setup flags, loads common YAML config or synthesizes default write-large-files configs, creates a storage client, determines bucket type, supports mounted-directory mode, builds compatible flag sets, sets up test dirs, mounts statically, and exits with the test result.

State/persistence behavior: initializes package storage client and setup globals, creates build/mount temp directories, and mounts/unmounts through static mounting.

Dependencies/integration: ties together `client`, `setup`, `test_suite`, and `static_mounting`.

Risks/test signals: falls back to hard-coded flags when config is absent, including streaming-writes disabled and write block limits. Mounted-directory mode requires both bucket and mount path because tests compare mounted data with bucket-visible content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/write_large_files/write_large_files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/log_rotate/install_script.sh -->
# sources/user-network-fs/gcsfuse/tools/log_rotate/install_script.sh

Purpose: installs hourly logrotate and rsyslog configuration for gcsfuse logs on Linux hosts.

Important APIs/types/functions: shell writes to `/etc/logrotate.hourly.conf`, `/etc/cron.hourly/gcsfuse-logrotate`, `/etc/logrotate.hourly.d/gcsfuse`, and `/etc/rsyslog.d/08-gcsfuse.conf`.

Control flow: creates hourly config directory, writes logrotate include config, writes an hourly cron script invoking `/usr/sbin/logrotate`, installs rotation policy for `/var/log/gcsfuse.log`, writes rsyslog filter for program name `gcsfuse`, then restarts rsyslog through `service` or `systemctl`.

State/persistence behavior: mutates system `/etc` configuration, cron hourly jobs, logrotate policy, rsyslog policy, and service state.

Dependencies/integration: requires root privileges and installed cron/logrotate/rsyslog tooling.

Risks/test signals: no `set -e`, so some earlier failures may not stop the script. It checks only the exit status of the immediately preceding `tee` or redirect blocks at a few points.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/log_rotate/install_script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/metrics-gen/main.go -->
# sources/user-network-fs/gcsfuse/tools/metrics-gen/main.go

Purpose: code generator that reads `metrics.yaml` and emits metric handle, noop metrics, OpenTelemetry metrics, and OTel metric tests from templates.

Important APIs/types/functions: schema structs `Metric`, `Attribute`, `AttrValuePair`, `AttrCombination`, `DistinctAttr`, `TemplateData`; name/unit helpers; `generateCombinations`; validators; `buildSwitches`; `findDistinctAttributes`; `main`; and `createFile`.

Control flow: reads YAML, validates uniqueness, sort order, metric fields, attribute fields, and constant-name collisions; normalizes attributes and values for deterministic generation; derives distinct string attribute types and all attribute combinations; executes four templates into the output directory.

State/persistence behavior: reads an input YAML file, creates the output directory, and writes generated Go files. It has no long-lived runtime state.

Dependencies/integration: depends on `text/template`, `gopkg.in/yaml.v3`, and local template files expected in the working directory.

Risks/test signals: templates are loaded by relative name, so the generator must run from the template directory or equivalent. Validators enforce sorted input before later sorting for output, making source YAML ordering part of the contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/metrics-gen/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/find.go -->
# sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/find.go

Purpose: locates `fusermount` and `gcsfuse` executables for the mount helper.

Important APIs/types/functions: `findFusermount` and `findGcsfuse`.

Control flow: `findFusermount` returns empty on non-Linux; on Linux it checks hard-coded absolute candidates. `findGcsfuse` checks `gcsfuse` via PATH first and then several absolute locations.

State/persistence behavior: no persistent state; it only probes executable availability.

Dependencies/integration: used by `mount_gcsfuse/main.go` before invoking gcsfuse. Uses `exec.LookPath` and `runtime.GOOS`.

Risks/test signals: hard-coded paths can miss distro-specific locations. On non-Linux, `findFusermount` returns nil error and empty path, which leads to an empty PATH directory in the caller.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/find.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/main.go -->
# sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/main.go

Purpose: mount(8) helper that translates fstab or mount command invocations into `gcsfuse` CLI arguments and executes gcsfuse.

Important APIs/types/functions: `flagTypes`, `isEquiv`, `findEquivFlag`, `makeGcsfuseArgs`, `parseArgs`, `run`, and `main`.

Control flow: parses mount-helper arguments, maps known gcsfuse boolean/non-boolean options from `-o` strings, ignores mount-only no-op options, passes unknown options through as `-o`, normalizes path-like device values to base bucket names, locates gcsfuse and fusermount, then runs gcsfuse with a restricted environment containing PATH, HOME, and proxy variables.

State/persistence behavior: does not persist files, but starts the real gcsfuse mount process and writes diagnostic output to stderr/stdout.

Dependencies/integration: depends on `cfg.BuildFlagSet`, `internal/mount.ParseOptions`, `pflag`, and the executable finders.

Risks/test signals: option map iteration order is nondeterministic, so tests use element matching. Unknown options are intentionally passed to FUSE, which can fail at runtime if unsupported.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/main_test.go

Purpose: unit tests for mount-helper option translation and device parsing.

Important APIs/types/functions: `TestMakeGcsfuseArgs` and `TestParseArgs_DeviceIsParsedCorrectly`.

Control flow: table-driven tests check boolean flags with underscores/hyphens, string flags, debug flags, ignored mount options, pass-through regular options, mixed options, and `o` as a literal option. Device tests ensure path-like bucket names are reduced to their base name.

State/persistence behavior: pure unit tests; no mount process is started.

Dependencies/integration: depends on `testify/assert` and current gcsfuse flag definitions from `cfg.BuildFlagSet`.

Risks/test signals: uses `assert.ElementsMatch` for generated flags because option map order is not stable; this does not validate exact argument ordering before bucket/mount point.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/mount_gcsfuse/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/build.go -->
# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/build.go

Purpose: builds a gcsfuse release tree from a requested git commit/tag and version for packaging.

Important APIs/types/functions: `build(commit, version)`.

Control flow: creates temp GOCACHE, output, and git clone directories; clones `GoogleCloudPlatform/gcsfuse` at the commit; builds `tools/build_gcsfuse`; runs it with source dir, output dir, and version; then renames `bin` to `usr/bin` for Linux package layout.

State/persistence behavior: creates temp directories and returns a build output directory that caller later deletes. Network clone and local build outputs are key side effects.

Dependencies/integration: used by `package_gcsfuse/main.go`; requires `git`, `go`, and reachable GitHub repository.

Risks/test signals: cloning from a fixed remote makes builds network-dependent. Error cleanup removes output only when returning an error; successful cleanup is caller-owned.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/build.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/main.go -->
# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/main.go

Purpose: CLI entry point for building release packages from a version and optional commit.

Important APIs/types/functions: `run(args []string)` and `main`.

Control flow: validates `dst_dir version [commit]`, defaults commit to `v<version>`, checks required tools, builds the release tree, and on Linux emits both deb and rpm packages.

State/persistence behavior: writes package artifacts to the destination directory and deletes the temporary build directory after packaging.

Dependencies/integration: dispatches to platform-specific `checkForTools`, `build`, `packageDeb`, and `packageRpm`.

Risks/test signals: only Linux packaging is implemented; non-Linux runs can build but do not package. The rpm error is wrapped as `packageDeb`, a copy/paste message issue.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/package.go -->
# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/package.go

Purpose: wraps `fpm` to create deb and rpm packages from a prepared filesystem tree.

Important APIs/types/functions: `packageFpm`, `packageDeb`, and `packageRpm`.

Control flow: constructs an `fpm -s dir` command with package type, name, version, dependency on `fuse`, maintainer, URL, and description; runs it in the output directory; package-specific functions only choose `deb` or `rpm`.

State/persistence behavior: writes package files through the external `fpm` process into the output directory.

Dependencies/integration: called by package CLI after `build`; requires Ruby fpm installed.

Risks/test signals: function parameters `osys` and `arch` are unused. Package metadata is static and minimal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/package.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/tools_darwin.go -->
# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/tools_darwin.go

Purpose: Darwin-specific prerequisite checker for the packaging CLI.

Important APIs/types/functions: `checkForTools`.

Control flow: checks `git`, `fpm`, and `go` with `exec.LookPath`, returning an install-instruction error on the first missing tool.

State/persistence behavior: no persistent state.

Dependencies/integration: selected by Go build tags through filename suffix on macOS.

Risks/test signals: the fpm instruction includes installing gnu-tar and fpm through gem; no version pinning is enforced.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/tools_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/tools_linux.go -->
# sources/user-network-fs/gcsfuse/tools/package_gcsfuse/tools_linux.go

Purpose: Linux-specific prerequisite checker for the packaging CLI.

Important APIs/types/functions: `checkForTools`.

Control flow: checks `git`, `fpm`, and `go` with `exec.LookPath`, returning distro-oriented install instructions on the first missing tool.

State/persistence behavior: no persistent state.

Dependencies/integration: selected by Go build tags through filename suffix on Linux.

Risks/test signals: checks availability only, not compatible versions of fpm, Go, or build tooling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse/tools_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse_docker/Dockerfile -->
# sources/user-network-fs/gcsfuse/tools/package_gcsfuse_docker/Dockerfile

Purpose: Docker build environment for producing gcsfuse deb and rpm packages for amd64 or arm64 Linux.

Important APIs/types/functions: build args `GCSFUSE_VERSION`, `BRANCH_NAME`, `ARCHITECTURE`, `GCSFUSE_REPO`, package build steps using `build_gcsfuse`, `dpkg-deb`, and `fpm`.

Control flow: starts from Go image, installs Ruby/fpm dependencies, validates architecture, clones and checks out gcsfuse, installs the repository's `.go-version`, builds gcsfuse into a package tree, moves binaries to `/usr/bin`, prepares Debian metadata/docs, updates version/architecture fields, gzips changelog, strips binaries, builds deb and rpm outputs under `/packages`.

State/persistence behavior: image layers contain the cloned repo, downloaded Go toolchain, built binaries, package tree, and final packages.

Dependencies/integration: used by release/package automation where host tooling is encapsulated in Docker.

Risks/test signals: `RUN PATH=$PATH:/usr/local/go/bin` does not persist as an `ENV`, though later `go version` may still find Go if base image paths remain valid. The rpm URL is built as `https://$GCSFUSE_REPO`, which can duplicate scheme when default repo already includes `https://`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/package_gcsfuse_docker/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/prefetch_cache_gcsfuse/main.go -->
# sources/user-network-fs/gcsfuse/tools/prefetch_cache_gcsfuse/main.go

Purpose: CLI wrapper for prefetching GCS objects into gcsfuse's persistent cache directory.

Important APIs/types/functions: `run(args []string)` and `main`.

Control flow: validates `cache_dir bucket_name [prefix]`, logs resolved settings, calls `prefetchCache`, and wraps failures with CLI context.

State/persistence behavior: delegates cache file creation to `prefetch.go`; this file itself only logs and exits with status 1 on error.

Dependencies/integration: paired with `prefetch.go` and standard `flag` parsing.

Risks/test signals: usage message uses `os.Args[0]` even when `run` is unit-tested with synthetic args. No explicit validation checks that cache dir exists or is writable before delegation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/prefetch_cache_gcsfuse/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/prefetch_cache_gcsfuse/prefetch.go -->
# sources/user-network-fs/gcsfuse/tools/prefetch_cache_gcsfuse/prefetch.go

Purpose: downloads objects from a GCS bucket into the local content cache format used by gcsfuse.

Important APIs/types/functions: `NUM_WORKERS`, `downloadFile`, and `prefetchCache`.

Control flow: `prefetchCache` creates a storage client and 10-minute context, lists objects with optional prefix, sends object attrs through a channel, and runs 10 worker goroutines. Each worker creates a temp cache file, streams object bytes into it, and writes adjacent JSON metadata containing cache file name, bucket, object, generation, and metageneration.

State/persistence behavior: creates cache data files and `.json` metadata files in the cache directory. It reads object data and metadata from GCS.

Dependencies/integration: depends on `cloud.google.com/go/storage` and internal `contentcache.CacheFileObjectMetadata`/prefix conventions.

Risks/test signals: partial data files are not removed on copy or metadata failure, matching TODO comments. Listing errors only log and stop the producer; `prefetchCache` still returns nil after worker completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/prefetch_cache_gcsfuse/prefetch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/config.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/config.go

Purpose: configuration schema and loader for the HTTP/gRPC proxy server used to inject retry behavior and validate headers.

Important APIs/types/functions: `RetryConfig`, `HeaderValidation`, `Config`, `printConfig`, and `parseConfigFile`.

Control flow: Viper reads the YAML config file and unmarshals into `Config`; `printConfig` logs target, retry configs, and header validation entries.

State/persistence behavior: reads configuration from disk; no writes. Runtime state is passed to `OperationManager` and proxy startup.

Dependencies/integration: used by `main.go`, operation manager, and gRPC metadata validation.

Risks/test signals: unknown YAML keys are ignored, so "invalid" config content can parse successfully into zero-valued fields. Tests explicitly reflect this permissive behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/config_test.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/config_test.go

Purpose: tests config parsing behavior for valid, empty, and unknown-key YAML files.

Important APIs/types/functions: `TestParseConfigFile`.

Control flow: creates temp YAML files, writes content, calls `parseConfigFile`, and asserts target host and retry config fields for valid input while expecting nil retry configs for empty or unknown-key input.

State/persistence behavior: creates and removes temp files.

Dependencies/integration: depends on `testify/assert`.

Risks/test signals: the invalid-config case asserts no error, documenting that schema validation is not enforced by the loader.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/emulator.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/emulator.go

Purpose: client helper for creating retry-test resources in a storage emulator/proxy target.

Important APIs/types/functions: `emulatorTest`, `RetryTestClient`, `(*emulatorTest).GetRetryID`, and `CreateRetryTest`.

Control flow: encodes retry instructions and transport to JSON, posts to `<host>/retry_test`, requires HTTP 200, decodes returned `id`, and returns it. Empty instruction maps return an empty id without a request.

State/persistence behavior: mutates the `host.Path` field during the request and resets it afterward. Remote emulator state is created by the POST.

Dependencies/integration: called by `AddRetryID` to plant emulator behavior and add `x-retry-test-id` to proxied requests.

Risks/test signals: response body close errors are ineffectively assigned to the local `err` in a defer after return values are fixed. Mutating a shared `url.URL` would not be safe across concurrent calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/emulator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/emulator_test.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/emulator_test.go

Purpose: unit tests for retry-test creation client behavior.

Important APIs/types/functions: `TestGetRetryID` and `TestCreateRetryTest`.

Control flow: mock HTTP servers assert `/retry_test`, return JSON id values, and tests assert expected ids. Empty instruction input is checked for no-op behavior.

State/persistence behavior: starts temporary HTTP servers; no durable state.

Dependencies/integration: uses `httptest` and `testify/assert`.

Risks/test signals: tests do not cover non-200 responses, malformed JSON responses, or invalid host URLs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/emulator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/grpc_proxy.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/grpc_proxy.go

Purpose: transparent gRPC proxy that forwards raw protobuf bytes to a target while optionally validating incoming metadata.

Important APIs/types/functions: `rawCodec`, `validateGRPCMetadata`, and `startGRPCProxy`.

Control flow: registers a raw byte codec, creates a target client connection with insecure credentials and raw codec, installs an unknown-service handler, extracts method and metadata, validates configured headers, opens a matching target stream, then proxies messages in both directions with goroutines and returns the first directional error.

State/persistence behavior: maintains target gRPC connection and listener/server state for process lifetime. No files are written.

Dependencies/integration: started by `GRPCProxyServer.Start` in `main.go`; uses `google.golang.org/grpc` metadata/status APIs.

Risks/test signals: target connection is not explicitly closed. Metadata validation only treats non-empty expected patterns as matchable, so empty-pattern validations effectively check presence only when fail-on-missing is set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/grpc_proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/main.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/main.go

Purpose: executable proxy server for integration tests, supporting HTTP forwarding with retry injection and gRPC forwarding with metadata validation.

Important APIs/types/functions: flags `config-path`, `debug`, `log-file`; globals `gConfig`, `gOpManager`, `gPort`; `ProxyHandler.ServeHTTP`; `AddRetryID`; `ProxyServer.Start`; `main`; `GRPCProxyServer.Start`.

Control flow: main parses config, opens log file, initializes operation manager, and starts HTTP or gRPC based on `proxyType`. HTTP handler copies request headers/body to target, deduces request type, optionally creates a retry test and header, forwards, rewrites redirect `Location` hosts to the proxy port, copies response headers/body, and logs timing. Servers listen on random ports and block until SIGINT/SIGTERM.

State/persistence behavior: global config/operation manager/port state is shared across handlers. Operation manager retry counts mutate across requests. Logs are appended to the supplied log file.

Dependencies/integration: used by integration tests as a custom endpoint. Depends on request mapper, emulator helper, operation manager, and gRPC proxy.

Risks/test signals: global mutable state complicates parallel tests. `http.Client{}` has no timeout, so stalled target requests can hang. Typos in log text do not affect behavior but reduce polish.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/main_test.go

Purpose: unit test for injecting retry ids into proxied HTTP requests.

Important APIs/types/functions: `TestAddRetryID`.

Control flow: starts a mock server returning a retry test id, sets package globals `gConfig` and `gOpManager`, builds a request and request-type instruction, calls `AddRetryID`, and asserts the request header was populated.

State/persistence behavior: mutates package globals for the duration of the test and starts a temporary HTTP server.

Dependencies/integration: covers interaction among operation manager, emulator helper, and request mutation.

Risks/test signals: does not restore globals after the test; safe only if tests do not depend on pristine global state.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/main_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/operation_manager.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/operation_manager.go

Purpose: tracks retry instructions by request type and dispenses them according to skip and retry counts.

Important APIs/types/functions: `OperationManager`, `NewOperationManager`, `retrieveOperation`, and `addRetryConfig`.

Control flow: configs are grouped by `RequestType`. On retrieval, a mutex protects the slice; the first config either consumes skip count and returns empty, consumes retry count and returns its instruction, or is removed when exhausted before checking the next config.

State/persistence behavior: in-memory mutable retry counters are process state. No persistent files are written.

Dependencies/integration: called by `AddRetryID` for every HTTP request.

Risks/test signals: slice elements are copied into local `configs`; the code updates map only when dropping exhausted configs, but count mutations on `configs[0]` modify the shared underlying array, so behavior works but is subtle. Mutex makes per-process access safe.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/operation_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/operation_manager_test.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/operation_manager_test.go

Purpose: unit tests for retry configuration grouping and retrieval semantics.

Important APIs/types/functions: `TestNewOperationManager`, `TestRetrieveOperation`, and `TestAddRetryConfig`.

Control flow: tests initialize configs with different methods, skip counts, retry counts, and repeated methods, then assert returned instruction sequences and internal map shape.

State/persistence behavior: pure in-memory tests, aside from package debug flag reads in constructors.

Dependencies/integration: uses `testify/assert`.

Risks/test signals: tests cover sequential retrieval but not concurrent access. They validate the intended stateful consumption behavior used by the proxy.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/operation_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/request_mapper.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/request_mapper.go

Purpose: maps incoming HTTP requests to proxy retry request types and emulator instruction names.

Important APIs/types/functions: `RequestType` constants, `RequestTypeAndInstruction`, `deduceRequestTypeAndInstruction`, and `isJsonAPI`.

Control flow: JSON API paths containing `/storage/v1` are classified by HTTP method and path shape: GET ending `/o` lists, GET containing `/o/` stats, POST creates, DELETE deletes, PUT updates. Non-JSON GET requests are XML reads. Unknown methods map to `Unknown` with empty instruction.

State/persistence behavior: stateless classification only.

Dependencies/integration: feeds `AddRetryID` and `OperationManager`.

Risks/test signals: JSON read requests are explicitly TODO and currently indistinguishable from stat GETs. Path matching is substring/suffix based and may misclassify unusual encoded paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/request_mapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/request_mappper_test.go -->
# sources/user-network-fs/gcsfuse/tools/proxy_server/request_mappper_test.go

Purpose: unit tests for HTTP request type and instruction mapping.

Important APIs/types/functions: `TestDeduceRequestTypeAndInstruction`.

Control flow: table-driven tests construct minimal `http.Request` values for JSON stat/list/create/delete/update/unknown and XML read/unknown cases, then assert request type and instruction strings.

State/persistence behavior: pure in-memory tests.

Dependencies/integration: uses `testify/assert`.

Risks/test signals: filename contains a typo (`mappper`). Tests do not cover encoded object names, query strings, copy/compose requests, or JSON read TODO behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/proxy_server/request_mappper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/scripts/skip_tests/main.go -->
# sources/user-network-fs/gcsfuse/tools/scripts/skip_tests/main.go

Purpose: converts a newline-separated skip-test list into a single regex alternation.

Important APIs/types/functions: `main`.

Control flow: scans stdin line by line, trims whitespace, ignores empty lines and comments beginning with `#`, appends remaining lines to a slice, and prints them joined by `|`.

State/persistence behavior: stateless filter; reads stdin and writes stdout only.

Dependencies/integration: useful in scripts that pass skip lists to Go test regex flags.

Risks/test signals: it does not regexp-escape entries, so skip list lines are interpreted as regex syntax by downstream consumers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/scripts/skip_tests/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/util/build_gcsfuse.go -->
# sources/user-network-fs/gcsfuse/tools/util/build_gcsfuse.go

Purpose: helper library for integration tests to build gcsfuse and mount helper binaries into a destination directory.

Important APIs/types/functions: `BuildGcsfuse` and internal `buildBuildGcsfuse`.

Control flow: builds the `tools/build_gcsfuse` helper into a temp path using isolated GOPATH/GOCACHE, locates the gcsfuse module source via `go/build.Import`, then runs the helper with source dir, destination dir, and version `0.0.0`.

State/persistence behavior: creates temporary build directories and writes binaries/layout into the supplied destination directory.

Dependencies/integration: used by integration setup when tests do not use installed or prebuilt gcsfuse. Requires Go toolchain and module source to be discoverable.

Risks/test signals: `go/build.Import` reflects GOPATH-era lookup behavior and can be fragile under unusual module/workspace setups. Build errors include combined command output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/util/build_gcsfuse.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/util/unmount.go -->
# sources/user-network-fs/gcsfuse/tools/util/unmount.go

Purpose: retrying unmount helper for FUSE mount points.

Important APIs/types/functions: `Unmount(dir string) error`.

Control flow: calls `fuse.Unmount`; on success returns nil. If the error text contains `resource busy`, it logs, sleeps with exponential backoff factor 1.3 starting at 10 ms, and retries indefinitely. Other errors are wrapped and returned.

State/persistence behavior: mutates OS mount state by unmounting the target. No files are written.

Dependencies/integration: used by tools and tests that need robust cleanup, especially on OS X per comments.

Risks/test signals: indefinite retry on persistent resource-busy errors can hang callers. Matching is string-based rather than typed.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/util/unmount.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/benchmark_test.go -->
# sources/user-network-fs/gcsfuse/tracing/benchmark_test.go

Purpose: benchmarks tracing operations for both OpenTelemetry and noop tracer implementations.

Important APIs/types/functions: `BenchmarkTrace` with sub-benchmarks for span start/end, server span start/end, record error, trace upload with/without errors and bytes, set cache/upload attributes, and context propagation.

Control flow: iterates over `NewOTELTracer()` and `NewNoopTracer()`, runs `b.Run` sub-benchmarks, and loops with `b.Loop()` to exercise each tracing method.

State/persistence behavior: benchmark-only in-memory span operations; no persistent output except Go benchmark results.

Dependencies/integration: validates relative cost of the `TraceHandle` interface implementations.

Risks/test signals: recording errors repeatedly on one span in the benchmark differs from typical one-error-per-span usage but gives a stable microbenchmark target.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/noop_tracer.go -->
# sources/user-network-fs/gcsfuse/tracing/noop_tracer.go

Purpose: no-op implementation of the tracing interface for deployments or tests without active tracing.

Important APIs/types/functions: `noopTracer`, `emptyFinisher`, methods implementing span start/end, server span, error recording, cache/read attributes, upload attributes, `TraceUpload`, `PropagateTraceContext`, and `NewNoopTracer`.

Control flow: every method returns the input context, noop span, empty finisher, or no-op side effect. Context propagation deliberately returns the new context unchanged.

State/persistence behavior: no state or persistence.

Dependencies/integration: implements `TraceHandle` using OpenTelemetry `noop.Span`.

Risks/test signals: no direct tests in this file, but benchmarks include noop behavior. It should remain allocation-light and semantically inert.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/noop_tracer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/otel_tracer.go -->
# sources/user-network-fs/gcsfuse/tracing/otel_tracer.go

Purpose: OpenTelemetry-backed implementation of the gcsfuse tracing interface.

Important APIs/types/functions: `otelTracer`, attribute key globals, `StartSpan`, `StartServerSpan`, `EndSpan`, `RecordError`, `SetCacheReadAttributes`, `SetUploadAttributes`, `TraceUpload`, `PropagateTraceContext`, and `NewOTELTracer`.

Control flow: starts spans from the global OTel tracer, records errors and status, sets cache/upload attributes using a two-element `sync.Pool` slice, returns upload finishers that attach bytes/error attributes before ending the span, and copies a span from one context to another for propagation.

State/persistence behavior: holds a tracer and attribute slice pool in memory. Emitted spans are exported according to the global OpenTelemetry provider outside this file.

Dependencies/integration: implements `TraceHandle`; uses constants from `span_attributes.go` and tracer name from the package.

Risks/test signals: pooled slices are reused after `SetAttributes`, relying on OTel copying key-values synchronously. Tests cover span creation, server kind, error status, cache attributes, and context propagation; upload attributes are benchmarked but not unit-tested here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/otel_tracer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/otel_tracer_test.go -->
# sources/user-network-fs/gcsfuse/tracing/otel_tracer_test.go

Purpose: unit tests for the OpenTelemetry tracer implementation.

Important APIs/types/functions: `TestOtelTracer_StartEndSpan`, `TestOtelTracer_StartServerSpan`, `TestOtelTracer_RecordError`, `TestOtelTracer_SetCacheReadAttributes`, and `TestOtelTracer_PropagateTraceContext`.

Control flow: each test installs an SDK tracer provider with a span recorder, creates `NewOTELTracer`, performs a tracing operation, ends spans where needed, and asserts recorder contents.

State/persistence behavior: mutates the global OTel tracer provider for each test; all span data is in-memory.

Dependencies/integration: uses `tracetest.SpanRecorder`, `sdktrace.TracerProvider`, OTel attributes/codes, and `testify/assert`.

Risks/test signals: tests do not reset the global provider to its previous value, so package-level parallelism would need care. Upload-specific attributes and `TraceUpload` finisher behavior are not directly asserted.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/otel_tracer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/span_attributes.go -->
# sources/user-network-fs/gcsfuse/tracing/span_attributes.go

Purpose: centralizes tracing span attribute key strings.

Important APIs/types/functions: constants `IS_CACHE_HIT`, `BYTES_READ`, `BYTES_UPLOADED`, and `OBJECT_NAME`.

Control flow: no executable flow.

State/persistence behavior: no state; constants define exported instrumentation key names.

Dependencies/integration: consumed by `otel_tracer.go` and tests to set/assert attributes.

Risks/test signals: changing these constants changes telemetry schema and test expectations, so they are integration-facing API surface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tracing/span_attributes.go -->
