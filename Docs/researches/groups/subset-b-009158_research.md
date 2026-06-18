# subset-b-009158 grouped research

This grouped report covers the exact source files assigned to work item `subset-b-009158`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/archiver_test.go -->
# sources/sync-backup/restic/internal/archiver/archiver_test.go

Purpose: This is the main archiver integration/regression test file. It exercises file saving, directory and tree saving, snapshot creation, parent snapshot reuse, target resolution, filtering, error handling, metadata-only changes, cancellation, and racy filesystem changes against real test repositories and tracked filesystem wrappers.

Important APIs and helpers: `prepareTempdirRepoSrc`, `saveFile`, `blobCountingRepo`, `blobCountingSaver`, `MockFS`, `TrackFS`, `failSaveRepo`, `failSaveSaver`, `snapshot`, `overrideFS`, `overrideFile`, `mockToNoder`, and `missingFS` are test scaffolds around `New`, `Snapshot`, `runWorkers`, `save`, `saveDir`, `saveTree`, `fileChanged`, and `nodeFromFileInfo`. The benchmark functions measure small and large file chunking throughput.

Control flow and state: Tests create temporary source trees with `TestDir`, run archiver workers through `repo.WithBlobUploader`, wait on `futureNode` results, then validate repository trees with `TestEnsureFileContent`, `TestEnsureTree`, `TestEnsureSnapshot`, and `checker.TestCheckRepo`. Incremental tests track saved blob handles to ensure existing blobs and trees are not written again. Parent snapshot tests record bytes read through `MockFS` to prove unchanged files are detected from metadata and previous snapshot content instead of being reread.

Persistence and integration: The tests persist blobs into `repository.TestRepository`, `mem.New`, and wrapped backend variants. They integrate with `internal/data` tree loading, `internal/checker`, feature flags for hardlink/device metadata, `fs.Track`, `fs.NewReader`, and context cancellation. Snapshot summaries are compared against expected `Summary`, `ItemStats`, and `ChangeStats` values.

Risks and edge cases: The suite guards callback ordering, duplicate blob writes, ctime/inode ignore flags, unreadable files, missing parent paths, context-canceled snapshots, early abort when uploads fail, metadata updates without content changes, file-vs-directory races, irregular files, missing files during stat/open, explicit target filter bypass, symlink target handling, and platform differences for Windows and Darwin timestamp granularity.

Test signals: This file is itself the broadest archiver signal. It uses repository consistency checks after successful snapshots and targeted assertions for expected errors, skipped Windows/Darwin-sensitive cases, and deterministic expected tree structures.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/archiver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/archiver_unix_test.go -->
# sources/sync-backup/restic/internal/archiver/archiver_unix_test.go

Purpose: Unix-only regression coverage for hardlink metadata in snapshots. It verifies that hardlinked files can retain device ID, inode, and link count metadata when the `DeviceIDForHardlinks` feature flag is enabled.

Important APIs and functions: `statAndSnapshot` compares metadata from `nodeFromFile` against a node saved through `snapshot`; `TestHardlinkMetadata` builds a source tree containing regular files, a hardlink, and a directory.

Control flow and state: The test enables the feature flag, creates files, snapshots `testlink`, `testfile`, and `testdir`, then compares metadata fields on returned `data.Node` values. Hardlink nodes should preserve device/inode/link count, while ordinary files and directories should have `DeviceID` zeroed.

Dependencies and integration: It depends on Unix hardlink support, `feature.TestSetFlag`, `fs.NewLocal`, the helpers in `archiver_test.go`, and the test repository created by `prepareTempdirRepoSrc`.

Risks and test signals: The file guards against leaking device IDs for ordinary nodes while still preserving the metadata necessary to identify hardlinks. It is excluded from Windows via build tag.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/archiver_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/buffer.go -->
# sources/sync-backup/restic/internal/archiver/buffer.go

Purpose: Provides a small reusable buffer pool used by the archiver file saver when chunking file contents. It reduces allocations for normal chunk buffers while avoiding retention of unexpectedly large slices.

Important APIs and types: `buffer` holds `Data []byte` and a back-pointer to its `bufferPool`. `buffer.Release` returns the buffer to the pool only when it came from a pool and its capacity does not exceed the pool default. `bufferPool` wraps `sync.Pool`; `newBufferPool(defaultSize int)` initializes the pool; `Get` retrieves a `*buffer`.

Control flow and state: `sync.Pool.New` creates buffers with `Data` sized to `defaultSize`. Callers may mutate or reslice `Data`. On release, oversized buffers are discarded by not putting them back, preventing a single large chunk/read from permanently raising memory pressure.

Dependencies and integration: The only dependency is `sync`. The main integration point is `fileSaver.saveFile`, which obtains buffers for `chunker.Next` and releases them from async upload callbacks.

Risks and test signals: Correctness depends on every buffer user calling `Release`, including error paths and async callbacks. Reusing buffers before upload callbacks finish would corrupt data, so release timing is critical. `buffer_test.go` verifies reuse and large-buffer discard behavior despite `sync.Pool` GC nondeterminism.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/buffer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/buffer_test.go -->
# sources/sync-backup/restic/internal/archiver/buffer_test.go

Purpose: Unit tests for the archiver buffer pool.

Important APIs and functions: `TestBufferPoolReuse` obtains a buffer, records its backing slice address, releases it, and checks that a later `Get` can reuse the same slice. `TestBufferPoolLargeBuffers` grows a buffer past the default capacity and checks that a subsequent buffer does not keep that larger capacity.

Control flow and state: Both tests retry up to 100 times because `sync.Pool` may drop entries during garbage collection. The large-buffer test mutates `buf.Data` with `append`, so it covers the exact retention risk handled by `Release`.

Dependencies and integration: Uses Go's `testing` package only and targets `newBufferPool`, `Get`, and `Release` in `buffer.go`.

Risks and test signals: The tests are deliberately tolerant of `sync.Pool` nondeterminism. They signal memory-retention regressions and broken reuse, but do not assert strict pool capacity or lifetime guarantees.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/buffer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/doc.go -->
# sources/sync-backup/restic/internal/archiver/doc.go

Purpose: Package documentation for the `archiver` package. It states that the package is responsible for saving whole directory structures into a restic repository.

Important APIs and functions: The file exports no symbols. Its value is the package comment that appears in generated Go documentation.

Control flow and state: There is no runtime control flow or persistent state.

Dependencies and integration: It only declares `package archiver` and integrates with `go doc`/documentation tooling.

Risks and test signals: No direct tests are needed. The risk is stale documentation if package responsibilities change.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/exclude.go -->
# sources/sync-backup/restic/internal/archiver/exclude.go

Purpose: Implements archiver exclusion predicates for tag files, device boundaries, file size, and online-only cloud files. It adapts user-facing backup options into `SelectByNameFunc` and `SelectFunc` style predicates.

Important APIs and types: `RejectByNameFunc`, `RejectFunc`, `CombineRejectByNames`, and `CombineRejects` convert reject predicates into positive select functions. `RejectIfPresent` parses `filename[:header]` tag-file specs and returns a cached predicate. `RejectByDevice` builds a `deviceMap` for `--one-file-system`; `RejectBySize` rejects files larger than a maximum; `RejectCloudFiles` rejects files whose metadata reports recall-on-data-access. Internal helpers include `rejectionCache`, `isExcludedByFile`, `isDirExcludedByFile`, `newDeviceMap`, and `deviceMap.IsAllowed`.

Control flow and state: Tag-file rejection checks the containing directory, caches the decision by directory, avoids excluding the tag file itself, and optionally validates a required header. Device rejection normalizes sample paths, maps allowed source roots to device IDs, walks parent directories to find the controlling allowed device, rejects files on other devices, and specially keeps mountpoint directories when their parent is allowed. Size and cloud predicates are stateless.

Persistence and dependencies: This code reads filesystem metadata and tag-file content through `internal/fs.FS`; it does not persist data. It depends on `debug`, `errors`, runtime OS checks, and `fs.ExtendedFileInfo` methods such as `RecallOnDataAccess`.

Integration points: These predicates feed archiver and scanner selection. `RejectIfPresent` supports cache-directory and user tag-file exclusions; `RejectByDevice` enforces filesystem boundary behavior; `RejectCloudFiles` protects against hydrating online-only files.

Risks and test signals: Important risks are stale cache decisions if tag files change during traversal, warning-only handling for malformed tag files, panics if `deviceMap.IsAllowed` unexpectedly cannot locate an ancestor, Windows lack of device IDs, and mountpoint directory inclusion semantics. `exclude_test.go` covers tag signatures, multiple tag rules, size rejection, and device-map boundary decisions.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/exclude.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/exclude_test.go -->
# sources/sync-backup/restic/internal/archiver/exclude_test.go

Purpose: Unit tests for archiver exclusion predicates.

Important APIs and functions: `TestIsExcludedByFile` covers `isExcludedByFile`; `TestMultipleIsExcludedByFile` validates multiple `RejectIfPresent` instances together; `TestIsExcludedByFileSize` validates `RejectBySize`; `TestDeviceMap` validates `deviceMap.IsAllowed`.

Control flow and state: Tests create temporary directory trees and tag files, then run predicate logic either directly or through `filepath.Walk`. Inclusion decisions are collected in maps and compared against expected values.

Dependencies and integration: Uses `internal/fs.NewLocal`, `fs.ExtendedStat`, `internal/test`, OS file creation, truncation, and path normalization. The tests are close to backup traversal behavior but do not run the full archiver.

Risks and test signals: These tests protect against tag-file specs canceling each other out, incorrect tag signature interpretation, directories being rejected by size, and accidental crossing of device boundaries. Device tests use synthetic IDs, so they cover logic but not OS stat behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/exclude_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/file_saver.go -->
# sources/sync-backup/restic/internal/archiver/file_saver.go

Purpose: Implements concurrent file content saving for the archiver. It reads files, chunks them, uploads data blobs asynchronously, builds `data.Node` content references, and reports per-file statistics through futures and callbacks.

Important APIs and types: `fileSaver` owns a chunk buffer pool, `restic.BlobSaverAsync`, chunker polynomial, job channel, `CompleteBlob`, and `NodeFromFileInfo`. `newFileSaver` starts worker goroutines. `Save` enqueues a `saveFileJob` and returns a `futureNode`. `saveFile` performs the actual file-to-blobs pipeline. `TriggerShutdown` closes the job channel.

Control flow and state: Each worker reuses one chunker. `saveFile` calls `start`, builds a metadata node, checks that it is a file, resets the chunker, loops through chunks, reserves positions in `node.Content`, and calls `SaveBlobAsync`. A mutex guards shared `futureNodeResult`, stats, remaining upload count, and content assignment. The future completes only after the reader reaches EOF, the file is closed, `completeReading` has run, and all async uploads have returned.

Persistence and dependencies: Persistence is through the repository's blob saver. In-memory state includes buffer pool entries, per-job content arrays, counters, and callback status. Dependencies include `chunker`, `data`, `fs`, `restic`, `errgroup`, and context cancellation.

Integration points: The archiver uses this from `runWorkers` and `save` to save regular files. The returned `futureNode` is consumed by tree saving. Stats flow into snapshot summaries, and `CompleteBlob` supports progress accounting.

Risks and test signals: Risks include callback order, data corruption if buffers are released too early, deadlocks if async callbacks never fire, races around `remaining`, double completion, context cancellation after queueing, file close errors, and non-file metadata. Tests in `file_saver_test.go` and `archiver_test.go` cover concurrent saves, callbacks, stats, cancellation, and upload-failure behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/file_saver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/file_saver_test.go -->
# sources/sync-backup/restic/internal/archiver/file_saver_test.go

Purpose: Focused concurrency test for `fileSaver`.

Important APIs and functions: `createTestFiles` creates temporary files. `startFileSaver` sets up an errgroup, random chunker polynomial, `mockSaver`, and a `NodeFromFileInfo` bridge. `TestFileSaver` queues multiple files through `Save`, waits on all futures, and validates that the mock saver saw every file.

Control flow and state: The test starts one worker per CPU, submits 15 files, consumes `futureNodeResult` values, shuts down the saver, and waits for worker exit.

Dependencies and integration: Uses `chunker.RandomPolynomial`, `fs.NewLocal`, `mockSaver` from `tree_saver_test.go`, `errgroup`, and the real `fileSaver` implementation.

Risks and test signals: It mainly signals queue/worker/future correctness under concurrent use. Broader file content, stats, and failure cases are covered by `archiver_test.go`.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/file_saver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/scanner.go -->
# sources/sync-backup/restic/internal/archiver/scanner.go

Purpose: Implements a lightweight scanner that traverses backup targets and emits cumulative counts for files, directories, other nodes, and bytes without saving data.

Important APIs and types: `Scanner` has `FS`, `SelectByName`, `Select`, `Error`, and `Result` hooks. `NewScanner` installs permissive defaults. `ScanStats` holds counters. `Scan`, `scanTree`, and `scan` drive traversal.

Control flow and state: `Scan` resolves relative targets, builds the same target tree representation as the archiver, and recursively scans leaf nodes. `scan` checks context cancellation, applies name-based selection before `Lstat`, applies metadata-based selection afterward unless the path is explicit, recurses directories in sorted order, updates counters, and calls `Result` after each included item plus once for the final aggregate.

Persistence and dependencies: Scanner is read-only and stores only call-stack counters. It depends on `fs.FS`, sorted directory listing, `debug`, and archiver target-tree helpers.

Integration points: Used by command/UI paths that need pre-backup scan summaries and by selection logic shared with the archiver. Its explicit-target behavior mirrors tree leaf semantics.

Risks and test signals: Risks include divergence from archiver traversal, wrong counts when errors are ignored, and context cancellation returning partial stats. `scanner_test.go` validates include/filter traversal, ignored errors, removed files, and cancellation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/scanner.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/scanner_test.go -->
# sources/sync-backup/restic/internal/archiver/scanner_test.go

Purpose: Tests scanner traversal, filtering, error handling, and cancellation.

Important APIs and functions: `TestScanner` checks cumulative `ScanStats` for include-all and `.txt` selection. `TestScannerError` validates no-error, unreadable-directory, and removed-item cases. `TestScannerCancel` verifies graceful early exit after context cancellation.

Control flow and state: Tests build temporary `TestDir` trees, chdir into them, run `NewScanner(fs.Track{FS: fs.NewLocal()})`, collect `Result` callbacks in maps or final counters, and optionally customize `Select`, `Error`, or `Result` to trigger edge cases.

Dependencies and integration: Uses `TestCreateFiles`, `fs.Track`, `internal/test`, `go-cmp`, and OS chmod/remove behavior. Some unreadable-directory coverage is skipped on Windows.

Risks and test signals: The tests guard deterministic sorted traversal, correct aggregation order, filtering of files while preserving directory traversal, ignored filesystem errors, and partial stats after cancellation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/scanner_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/testing.go -->
# sources/sync-backup/restic/internal/archiver/testing.go

Purpose: Shared test helper library for archiver package tests. It creates synthetic filesystem trees, snapshots them, and validates repository or local filesystem contents against declarative `TestDir` structures.

Important APIs and types: `TestSnapshot`, `TestDir`, `TestFile`, `TestSymlink`, `TestHardlink`, `TestCreateFiles`, `TestWalkFiles`, `TestEnsureFiles`, `TestEnsureFileContent`, `TestEnsureTree`, and `TestEnsureSnapshot` are exported test helpers.

Control flow and state: `TestCreateFiles` sorts names so hardlink targets exist before hardlinks, then recursively creates files, symlinks, hardlinks, and directories. `TestEnsureFiles` walks expected and actual filesystem trees to catch missing, wrong-type, wrong-content, wrong-target, and extra paths. Repository validation loads snapshot and tree blobs, walks nodes, and for file content reconstructs data by loading each content blob into a buffer.

Persistence and dependencies: It writes temporary filesystem content and reads repository blobs. Dependencies include `data.LoadSnapshot`, `data.LoadTree`, `restic.BlobLoader`, `fs`, `debug`, and `internal/test` assertions.

Integration points: This file underpins nearly every archiver test and encodes the expected mapping from local files to restic tree nodes.

Risks and test signals: Helper bugs can mask archiver regressions, especially around path normalization, Windows symlink handling, and exact tree comparison. `testing_test.go` validates helper failure and success behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/testing_test.go -->
# sources/sync-backup/restic/internal/archiver/testing_test.go

Purpose: Tests the archiver test-helper utilities themselves.

Important APIs and types: `MockT` captures helper failures without aborting the outer test. `createFilesAt` creates flat test fixtures. Tests cover `TestCreateFiles`, `TestWalkFiles`, `TestEnsureFiles`, and `TestEnsureSnapshot`.

Control flow and state: The tests create local directory structures, compare observed item types and contents, intentionally pass mismatched expectations through `MockT`, and assert that helpers fail when they should. Snapshot helper tests create a repository, run a real archiver snapshot, and compare expected `TestDir` layouts.

Dependencies and integration: Uses `repository.TestRepository`, `New`, `Snapshot`, `internal/test`, `go-cmp`, `fs.NewLocal`, and temporary directories.

Risks and test signals: These tests protect the reliability of the larger archiver suite by confirming helpers detect missing, extra, wrong-content, wrong-type, wrong-symlink, and snapshot-tree mismatches.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/testing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/tree.go -->
# sources/sync-backup/restic/internal/archiver/tree.go

Purpose: Builds and normalizes the virtual tree that maps user backup targets into snapshot paths. It handles relative paths, absolute roots, Windows volumes, duplicate target elimination, root-name collisions, and target unrolling.

Important APIs and types: `tree` stores child `Nodes`, leaf `Path`, `FileInfoPath`, `Root`, and `Explicit`. `pathComponents`, `rootDirectory`, `tree.Add`, `tree.add`, `Leaf`, `NodeNames`, `formatTree`, `unrollTree`, `backupTarget`, and `newTree` implement the mapping.

Control flow and state: `newTree` cleans each target, skips duplicates, calls `Add`, then `unrollTree`. `Add` converts the path into components, determines the root, resolves top-level name collisions by suffixing names such as `foo-1`, and marks direct leaf targets as explicit. `unrollTree` expands a node that is both a leaf and a parent by reading its directory contents so that only leaves retain `Path`.

Persistence and dependencies: The tree is in-memory. The only filesystem reads occur during `unrollTree` via `fs.Readdirnames`. Dependencies include `fs.FS`, sorted names, `debug`, and restic errors.

Integration points: Both archiver snapshot saving and scanner traversal use this representation. `Explicit` is consumed by scanner/save logic to bypass filters only for user-listed target paths.

Risks and test signals: Risks include unstable snapshot shape, path collision bugs, duplicate handling, relative-parent targets, Windows volume roots, and filters applied to the wrong target. `tree_test.go` and `archiver_test.go` provide extensive coverage.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/tree.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/tree_saver.go -->
# sources/sync-backup/restic/internal/archiver/tree_saver.go

Purpose: Concurrently serializes directory nodes into restic tree blobs after child file/tree futures have completed.

Important APIs and types: `treeSaver` owns a `BlobSaverAsync`, error handler, and job channel. `newTreeSaver`, `TriggerShutdown`, `Save`, `saveTreeJob`, `save`, and `worker` implement the queue and worker lifecycle.

Control flow and state: `Save` enqueues a tree job and returns a future. `save` consumes child `futureNode` values in order, applies error filtering through `errFn`, skips excluded/nil nodes, adds nodes to `data.NewTreeJSONBuilder`, tolerates duplicate identical adjacent nodes by warning, finalizes JSON, uploads it as a `TreeBlob`, updates `ItemStats`, and sets `node.Subtree` to the new tree ID. Workers return fatal errors through the errgroup.

Persistence and dependencies: Tree blobs are persisted through `SaveBlobAsync`; state is otherwise per-job. Dependencies include `data`, `restic`, `errgroup`, context cancellation, and `ErrorFunc`.

Integration points: Directory saving in the main archiver schedules `treeSaver` jobs after file and child directory futures. Its stats are merged into snapshot summaries.

Risks and test signals: Risks include deadlocks waiting on futures, missing context cancellation, duplicate-name ordering errors, ignored errors dropping nodes, and worker termination on upload failures. `tree_saver_test.go` validates success, injected child errors, and duplicate handling.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/tree_saver.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/tree_saver_test.go -->
# sources/sync-backup/restic/internal/archiver/tree_saver_test.go

Purpose: Unit tests for concurrent `treeSaver` behavior.

Important APIs and types: `mockSaver` implements async blob saving by hashing buffers in goroutines. `setupTreeSaver` creates a context, errgroup, tree saver, and shutdown function. Tests include `TestTreeSaver`, `TestTreeSaverError`, and `TestTreeSaverDuplicates`.

Control flow and state: Success tests enqueue many tree nodes and consume futures. Error tests inject a failing child future at different positions and assert shutdown returns that error. Duplicate tests submit two children with the same name and either identical or different metadata, expecting identical duplicates to be tolerated and non-identical duplicates to fail.

Dependencies and integration: Uses `data.Node`, `restic.Hash`, `errgroup`, `runtime.NumCPU`, and package `futureNode` helpers.

Risks and test signals: The tests protect worker shutdown semantics, error propagation from child futures, and the special duplicate-node behavior required during tree construction.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/tree_saver_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/tree_test.go -->
# sources/sync-backup/restic/internal/archiver/tree_test.go

Purpose: Tests virtual target-tree construction and path normalization.

Important APIs and functions: `testBackupTargets` marks paths explicit. `TestPathComponents`, `TestRootDirectory`, and `TestTree` cover `pathComponents`, `rootDirectory`, `newTree`, `Add`, and `unrollTree`.

Control flow and state: Tests build expected `tree` values for simple files, multiple roots, relative parent paths, duplicate/colliding basenames, nested targets, unrolled parent/child target combinations, Windows volumes/UNC roots, and invalid `.`/`..` direct tree inputs. Temporary source trees are created when unroll behavior requires real directory contents.

Dependencies and integration: Uses `fs.NewLocal`, `TestCreateFiles`, `internal/test`, `go-cmp`, OS path normalization, and runtime OS skips.

Risks and test signals: This file is the key signal for stable snapshot path layout. It catches regressions in collision suffixing, duplicate target removal, explicit flags, virtual Windows prefixes, relative root detection, and unroll collision errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/archiver/tree_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/all/all.go -->
# sources/sync-backup/restic/internal/backend/all/all.go

Purpose: Central registration point for all supported repository backend factories.

Important APIs and functions: `Backends()` creates a `location.Registry` and registers Azure, B2, Google Cloud Storage, local, rclone, REST, S3, SFTP, and Swift factories.

Control flow and state: Each call returns a new registry populated in fixed order. No global mutable state is stored in this file.

Dependencies and integration: Depends on backend subpackages and `internal/backend/location`. Higher-level repository location parsing uses this registry to open or create the chosen backend.

Risks and test signals: Adding a backend requires updating this list or the backend will not be available through the aggregate registry. There is no direct test in this subset; coverage is usually through location/backend integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/all/all.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/azure/azure.go -->
# sources/sync-backup/restic/internal/backend/azure/azure.go

Purpose: Implements the restic `backend.Backend` interface for Azure Blob Storage.

Important APIs and types: `Backend` stores config, container client, connection count, default layout, and optional access tier. `NewFactory`, `Open`, `Create`, `Save`, `Load`, `Stat`, `Remove`, `List`, `Delete`, `Hasher`, `Properties`, `IsNotExist`, `IsPermanentError`, `Warmup`, and `WarmupWait` expose backend behavior. Internal helpers include `open`, `supportedAccessTiers`, `useAccessTier`, `saveSingleBlob`, `saveLarge`, and `openReader`.

Control flow and state: `open` builds a container URL using account name, endpoint suffix, and container, then chooses shared-key, SAS, Azure CLI, or default Azure credentials. `Create` probes or creates the container, with special tolerance for authorization failures from restricted tokens. `Save` chooses single `Upload` for files up to 256 MiB or block upload with 100 MiB blocks for larger files. `Load` delegates range validation to `util.DefaultLoad` and `openReader`; `List` pages blobs under the layout prefix.

Persistence and dependencies: Data persists as Azure blobs using the default restic layout. The backend uses MD5 for transactional validation and optional access tier selection. Dependencies include Azure SDK clients, `layout`, `location`, `util`, `backend`, `debug`, and restic errors.

Integration points: Registered by `NewFactory` and `backend/all`. It participates in repository creation/opening, retry wrappers, cache wrappers, and generic backend tests. `AccessTierArchive` is applied only to non-metadata pack files to keep metadata immediately readable.

Risks and test signals: Risks include credential-mode regressions, SAS token quirks, range-read short-file detection, memory usage for single uploads, block ID collisions if block content repeats, access-tier misapplication to metadata, and pagination/cancellation handling. `azure_test.go` runs the generic backend suite when environment variables are available, covers SAS token creation, and optionally tests large upload range reads.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/azure/azure.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/azure/azure_test.go -->
# sources/sync-backup/restic/internal/backend/azure/azure_test.go

Purpose: Integration and benchmark tests for the Azure backend.

Important APIs and functions: `newAzureTestSuite` configures the generic backend test suite. `TestBackendAzure`, `BenchmarkBackendAzure`, `TestBackendAzureAccountToken`, `TestBackendAzureContainerToken`, and `TestUploadLargeFile` exercise account-key, SAS token, and large upload paths.

Control flow and state: Tests read `RESTIC_TEST_AZURE_*` environment variables, parse repository config, apply environment credentials, set a unique prefix, create the backend, and run generic backend tests or benchmarks. Large upload creates 300 MiB of random data, saves it, then reads several offset/length ranges back for byte comparison.

Dependencies and integration: Uses `internal/backend/test`, `backend.Transport`, `azure.Create`, `options.SecretString`, and real Azure Blob Storage credentials. Cleanup calls `Delete` and `Remove` on test data.

Risks and test signals: Tests are skipped without credentials, so CI signal depends on secret availability. When enabled, they validate credential modes, suite compliance, large block uploads, range reads over block boundaries, and cleanup behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/azure/azure_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/azure/config.go -->
# sources/sync-backup/restic/internal/backend/azure/config.go

Purpose: Defines Azure backend configuration parsing and environment application.

Important APIs and types: `Config` stores account name/key/SAS, credential mode, endpoint suffix, container, prefix, connection limit, and access tier. `NewConfig` supplies defaults. `ParseConfig` parses `azure:container:/prefix`. `ApplyEnvironment` fills missing credential fields from environment variables.

Control flow and state: Parsing validates the `azure:` prefix and requires a colon separating container from path. It cleans and trims the prefix. Environment application only overwrites empty fields and parses `AZURE_FORCE_CLI_CREDENTIAL` as a boolean when present.

Dependencies and integration: Uses `options.Register`, `options.SecretString`, `backend.ApplyEnvironmenter`, `os.Getenv`, and path cleaning. The parsed config feeds `azure.open` and factory registration.

Risks and test signals: Risks include ambiguous container/path separators, silently ignored invalid boolean environment values, and missing validation for access-tier names until open-time matching. `config_test.go` covers valid parse cases.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/azure/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/azure/config_test.go -->
# sources/sync-backup/restic/internal/backend/azure/config_test.go

Purpose: Parse tests for Azure backend locations.

Important APIs and functions: `configTests` defines expected `Config` values and `TestParseConfig` delegates to `backend/test.ParseConfigTester`.

Control flow and state: The tests cover root prefix, nested prefix, and trailing slash cleanup for strings of the form `azure:container-name:/...`.

Dependencies and integration: Uses the backend test helper package and `ParseConfig` from `config.go`.

Risks and test signals: Provides basic positive parse coverage. It does not cover invalid Azure config strings or environment application.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/azure/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/b2/b2.go -->
# sources/sync-backup/restic/internal/backend/b2/b2.go

Purpose: Implements the restic backend interface for Backblaze B2 using the `blazer/b2` library.

Important APIs and types: `b2Backend` stores client, bucket, config, layout, and `canDelete`. `NewFactory`, `Open`, `Create`, `Properties`, `Hasher`, `IsNotExist`, `IsPermanentError`, `Load`, `Save`, `Stat`, `Remove`, `List`, `Delete`, `Close`, `Warmup`, and `WarmupWait` provide backend behavior. `sniffingRoundTripper` and `newClient` improve connection error reporting.

Control flow and state: `newClient` requires account ID/key, wraps the HTTP transport to remember connection errors, and applies a one-minute client creation timeout. `Open` locates an existing bucket; `Create` creates a private bucket. `Save` streams through a B2 writer and checks byte count. `Load` wraps range reads and detects too-short files by observing whether the caller consumed the expected limited bytes. `Remove` tries repeated deletes to clear versions, falls back to hide on unauthorized delete, and tracks fallback in `canDelete`.

Persistence and dependencies: Data is persisted as B2 objects using the default layout. Dependencies include `blazer/b2`, `base.Code`, `layout`, `location`, `util`, `backend`, and context cancellation.

Integration points: Registered through `NewFactory` and used by generic backend tests. It reports atomic replace support and no hasher because B2 handles SHA1 internally.

Risks and test signals: Risks include B2 eventual consistency, hidden old versions, authentication retry hangs in the library, fragile too-short detection if consumers do not read, and `canDelete` mutating after authorization errors. `b2_test.go` runs the generic suite with delayed removal allowance; config tests validate parsing and bucket-name errors.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/b2/b2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/b2/b2_test.go -->
# sources/sync-backup/restic/internal/backend/b2/b2_test.go

Purpose: Integration and benchmark harness for the B2 backend.

Important APIs and functions: `newB2TestSuite` builds a generic backend test suite with minimal data and delayed-removal wait. `testVars`, `TestBackendB2`, and `BenchmarkBackendb2` gate execution on `RESTIC_TEST_B2_*` environment variables.

Control flow and state: The suite parses `RESTIC_TEST_B2_REPOSITORY`, applies credentials from the test environment, assigns a unique prefix, and runs generic tests or benchmarks.

Dependencies and integration: Uses `internal/backend/test`, `b2.NewFactory`, and real Backblaze B2 credentials. It calls `rtest.SkipDisallowed` when skipped.

Risks and test signals: Skipped without credentials. When enabled, it validates backend interface compliance under B2's delayed deletion behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/b2/b2_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/b2/config.go -->
# sources/sync-backup/restic/internal/backend/b2/config.go

Purpose: Defines B2 backend configuration parsing, bucket-name validation, default options, and environment credential loading.

Important APIs and types: `Config` stores account ID, key, bucket, prefix, and connections. `NewConfig`, `ParseConfig`, `ApplyEnvironment`, and internal `checkBucketName` implement config behavior.

Control flow and state: `ParseConfig` requires `b2:` prefix, splits bucket and optional prefix at `:`, validates bucket names by length and allowed characters, cleans the prefix, and returns defaults with five connections. `ApplyEnvironment` fills account ID and key only when not already set.

Dependencies and integration: Uses `options.Register`, `options.SecretString`, `backend.ApplyEnvironmenter`, regex validation, and path cleaning. The config feeds `Open`, `Create`, and the location registry.

Risks and test signals: Bucket validation is intentionally stricter than generic paths and treats slash-separated strings without a colon as invalid bucket names. `config_test.go` covers valid forms and representative invalid strings.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/b2/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/b2/config_test.go -->
# sources/sync-backup/restic/internal/backend/b2/config_test.go

Purpose: Parse and validation tests for B2 backend locations.

Important APIs and functions: `configTests` covers valid strings; `invalidConfigTests` covers missing prefix, missing bucket, underscores, and slash-without-colon mistakes. `TestParseConfig` and `TestInvalidConfig` exercise `ParseConfig`.

Control flow and state: Positive tests use `backend/test.ParseConfigTester`. Negative tests assert exact error strings and that invalid configs do not return nil errors.

Dependencies and integration: Uses `internal/backend/test` and package-local parsing.

Risks and test signals: These tests guard the user-facing location grammar and bucket-name constraints. They do not cover environment variable application.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/b2/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/backend.go -->
# sources/sync-backup/restic/internal/backend/backend.go

Purpose: Defines the central backend abstraction used by restic repositories and wrapper layers.

Important APIs and types: `ErrNoRepository`, `Backend`, `Properties`, `Unwrapper`, `AsBackend`, `FreezeBackend`, `FileInfo`, and `ApplyEnvironmenter`. The interface includes save/load/stat/list/remove/delete/close, hashing, not-exist/permanent-error classification, and warmup methods.

Control flow and state: This file has no persistence. The key logic is `AsBackend`, which walks wrapper chains via `Unwrap` until it finds a backend of the requested generic type or returns the zero value.

Dependencies and integration: All concrete backend packages implement this interface. Retry logic relies on permanent error classification; cache/dryrun/limiter/sema/retry wrappers rely on interface composition and optional unwrapping.

Risks and test signals: Interface contract drift affects all storage backends. `Load` requires idempotent callbacks because retry wrappers may call them multiple times. `backend_test.go` validates `AsBackend` through wrapper chains.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/backend_test.go -->
# sources/sync-backup/restic/internal/backend/backend_test.go

Purpose: Tests generic backend unwrapping via `AsBackend`.

Important APIs and types: `testBackend` unwraps to nil; `otherTestBackend` unwraps to its embedded backend. `TestAsBackend` checks direct matches, non-matches, single-level unwrapping, and wrapped non-matches.

Control flow and state: The test constructs small wrapper chains and asserts pointer identity or nil results.

Dependencies and integration: Uses `backend.AsBackend` and `internal/test.Assert`.

Risks and test signals: Guards optional-backend discovery used by higher-level code that needs to recover a concrete backend from wrappers.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/backend.go -->
# sources/sync-backup/restic/internal/backend/cache/backend.go

Purpose: Provides a backend wrapper that transparently caches selected files locally while delegating storage operations to an underlying backend.

Important APIs and types: `cacheBackend` embeds `backend.Backend` and `*Cache`, tracks `inProgress` downloads, and logs cache-cleanup errors. Key methods are `newBackend`, `Remove`, `Save`, `Load`, `Stat`, `List`, `Unwrap`, `Warmup`, and `WarmupWait`. `autoCacheTypes` selects index files, snapshot files, and metadata pack files.

Control flow and state: `Save` stores cacheable files in the backend first, rewinds, then saves them in cache. `Load` waits for any existing download, tries cache load, falls back directly for non-cacheable types, otherwise downloads the complete file once through `cacheFile`, then serves the requested range from cache. `cacheFile` uses a handle-to-channel map so concurrent callers share one download. `List` records backend IDs and clears stale cache entries after successful listing.

Persistence and dependencies: Persistent state lives in `Cache` files. Runtime state includes `inProgress` synchronization and forgotten cache entries in `Cache`. Dependencies include `backend`, `io`, `sync`, and `debug`.

Integration points: `Cache.Wrap` returns this wrapper. It is commonly layered with retry and remote backends; `Unwrap` supports `backend.AsBackend`.

Risks and test signals: Risks include serving stale cached data unless callers use `Forget`, deadlocks if in-progress channels are not closed, cache poisoning after failed downloads, out-of-bounds range behavior, and cache pruning errors. `backend_test.go` covers normal load/save/remove/stat, concurrent load errors, range errors, forget circuit breaker, and automatic clearing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/backend_test.go -->
# sources/sync-backup/restic/internal/backend/cache/backend_test.go

Purpose: Tests the cache backend wrapper around an underlying backend.

Important APIs and helpers: `loadAndCompare`, `save`, `remove`, `randomData`, and `list` drive common operations. `loadCountingBackend` counts backend loads; `loadErrorBackend` injects load errors. Tests include `TestBackend`, `TestOutOfBoundsAccess`, `TestForget`, `TestErrorBackend`, `TestAutomaticCacheClear`, and `TestAutomaticCacheClearInvalidFilename`.

Control flow and state: Tests save data directly and through wrapped backends, observe whether cache files exist, remove backend entries, call `Stat`/`List`, and verify cache cleanup. Concurrent error tests run several goroutines against a backend that fails loads to ensure waiters do not hang and successful fallback states remain valid.

Dependencies and integration: Uses `mem.New`, `backend/test.LoadAll`, `TestNewCache`, `restic.Hash`, and randomized data.

Risks and test signals: The suite guards cache population, stale entry removal on stat/list, no duplicate full downloads for bad ranges, error propagation, and the one-shot `Forget` circuit breaker.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/cache.go -->
# sources/sync-backup/restic/internal/backend/cache/cache.go

Purpose: Manages cache directory creation, layout, versioning, age detection, and backend wrapping.

Important APIs and types: `Cache` stores the repo cache path, base path, creation flag, and `forgotten` circuit-breaker map. `New`, `readVersion`, `writeCachedirTag`, `All`, `OlderThan`, `Old`, `IsOld`, `Wrap`, and `BaseDir` are the main functions. Constants define directory/file modes, cache version, cacheable subpaths, CACHEDIR.TAG signature, and max cache age.

Control flow and state: `New` resolves the base directory, creates it, writes `CACHEDIR.TAG`, opens or creates the repo-specific cache directory, validates/updates the version file, updates directory timestamps, creates data/snapshots/index subdirectories, and returns a `Cache`. Directory listing filters only valid 64-hex IDs and check-cache names.

Persistence and dependencies: Persists `CACHEDIR.TAG`, `version`, and cache subdirectories on disk. Uses `os`, `filepath`, regex validation, timestamps, and `pkg/errors`.

Integration points: Called by command setup and tests to create caches; `Wrap` integrates with `cacheBackend`; `Old`/`OlderThan` support cache cleanup commands.

Risks and test signals: Risks include version incompatibility, missing tag/version recreation, permissions, invalid directory cleanup, and timestamp-based old-cache detection. `cache_test.go` validates creation, tag recreation, and version recreation.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/cache_test.go -->
# sources/sync-backup/restic/internal/backend/cache/cache_test.go

Purpose: Tests cache directory initialization and repair.

Important APIs and functions: `TestNew` exercises `New` with a random repository ID and a temporary base directory.

Control flow and state: The test creates a cache, then removes `CACHEDIR.TAG` and `version` in later iterations. Each call to `New` must recreate missing files, preserve the base path, and report `Created` only for the first creation step.

Dependencies and integration: Uses `restic.NewRandomID`, `internal/test`, `os`, and `filepath`.

Risks and test signals: Guards startup behavior when users delete metadata files or re-open an existing cache. It does not cover newer-version rejection or old-cache listing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/dir.go -->
# sources/sync-backup/restic/internal/backend/cache/dir.go

Purpose: Resolves the base cache directory.

Important APIs and functions: `EnvDir` returns `RESTIC_CACHE_DIR`. `DefaultDir` returns that env value when set, otherwise uses `os.UserCacheDir()` joined with `restic`.

Control flow and state: No persistent state is changed. Errors from `os.UserCacheDir` are wrapped with context.

Dependencies and integration: Used by `Cache.New` when no explicit base directory is provided. Depends on `os`, `filepath`, and `fmt`.

Risks and test signals: Platform-specific user cache lookup can fail. `dir_test.go` verifies environment override behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/dir_test.go -->
# sources/sync-backup/restic/internal/backend/cache/dir_test.go

Purpose: Tests cache directory environment override.

Important APIs and functions: `TestCacheDirEnv` validates `DefaultDir` when `RESTIC_CACHE_DIR` is set or temporarily set by the test.

Control flow and state: The test preserves/restores environment when it has to set the variable, then asserts the returned directory equals the environment value and no error occurs.

Dependencies and integration: Uses `os` environment APIs and `internal/test` assertions.

Risks and test signals: Guards user-configured cache location behavior across platforms.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/file.go -->
# sources/sync-backup/restic/internal/backend/cache/file.go

Purpose: Implements per-file cache persistence, loading, saving, forgetting, clearing, listing, and existence checks.

Important APIs and methods: `Cache.filename`, `canBeCached`, `load`, `save`, `Forget`, `remove`, `Clear`, `list`, `Has`, and `isFile`. Cacheable types are defined in `cache.go`.

Control flow and state: Cached filenames are sharded by the first two handle-name characters under type-specific directories. `load` opens a cache file, validates requested range, seeks, and optionally limits the reader. `save` creates the shard directory, writes to a temp file, closes it, then atomically renames into place; Windows permission errors during rename-over-open are treated as success. `Forget` normalizes metadata handles, removes at most once per process via `forgotten`, and prevents repeated delete/re-cache loops. `Clear` removes cache files not present in a valid ID set. `list` walks cache subdirectories and returns file basenames.

Persistence and dependencies: Persists cached files on local disk and uses temp files plus rename for concurrent-process safety. Depends on `backend`, `util.LimitReadCloser`, `os`, `filepath`, `runtime`, and `pkg/errors`.

Integration points: Used by `cacheBackend` for transparent loading/saving and pruning. It assumes valid restic IDs are long enough for two-character sharding.

Risks and test signals: Risks include panics for too-short names, stale or corrupt cached files, range validation mismatches, concurrent save/load behavior, Windows rename semantics, and damaged cache directories. `file_test.go` covers file operations, range loads, concurrent saves, and damaged-cache save failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/file_test.go -->
# sources/sync-backup/restic/internal/backend/cache/file_test.go

Purpose: Tests low-level cache file operations.

Important APIs and helpers: `generateRandomFiles`, `randomID`, `load`, `listFiles`, and `clearFiles` exercise `Cache.save`, `load`, `Has`, `list`, and `Clear`. Tests include `TestFiles`, `TestFileLoad`, `TestFileSaveConcurrent`, and `TestFileSaveAfterDamage`.

Control flow and state: Tests generate random cache files for snapshot, pack, and index types, validate hashes after reload, compare listed IDs, clear all but selected IDs, and verify range reads with offsets and lengths. Concurrent save/load simulates multiple restic processes writing the same handle and tolerates either temporary not-exist or correct data while writes race.

Dependencies and integration: Uses `restic.Hash`, random data helpers, `errgroup`, OS file removal, runtime Windows skip for concurrency semantics, and `TestNewCache`.

Risks and test signals: Guards cache layout, atomic temp-file save, range slicing, clearing semantics, concurrent writers, and failure after the cache directory is removed.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/testing.go -->
# sources/sync-backup/restic/internal/backend/cache/testing.go

Purpose: Shared cache test helper for constructing isolated cache instances.

Important APIs and constants: `testCacheID` is a stable 64-character hex ID. `TestNewCache` creates a temporary directory and calls `New` with that ID.

Control flow and state: Each call creates a new temp base directory, logs it, initializes the cache, and fails the test on error.

Dependencies and integration: Uses `internal/test.TempDir` and the package's `New` function. It is consumed by cache backend and file tests.

Risks and test signals: The helper reduces duplicated setup but hardcodes a single ID; tests that need multiple cache IDs must not reuse it blindly.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/cache/testing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/doc.go -->
# sources/sync-backup/restic/internal/backend/doc.go

Purpose: Package documentation for backend storage implementations.

Important APIs and functions: The file exports no symbols. Its package comment states that backends provide local and remote storage, implement `Backend`, and that the memory backend stores data in a map for tests.

Control flow and state: No runtime behavior or persistent state.

Dependencies and integration: Integrates with Go documentation generation for `internal/backend`.

Risks and test signals: No direct tests. Documentation should be kept aligned with backend package responsibilities.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/doc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/dryrun/dry_backend.go -->
# sources/sync-backup/restic/internal/backend/dryrun/dry_backend.go

Purpose: Implements a write-suppressing backend wrapper used by `backup --dry-run`.

Important APIs and types: `Backend` wraps an underlying `backend.Backend`. `New` constructs it. `Save`, `Remove`, and `Delete` validate/accept but do not mutate the repository. `Properties`, `Close`, `Hasher`, `IsNotExist`, `IsPermanentError`, `List`, `Load`, and `Stat` delegate. `Warmup` and `WarmupWait` are no-ops.

Control flow and state: Mutating operations return nil without touching the wrapped backend, except `Save` first validates the handle. Read-only operations pass through to the underlying backend. There is no local persistent state.

Dependencies and integration: Depends on `backend` and `debug`. It layers over any real backend for dry-run mode so backup logic can read repository state while avoiding modifications.

Risks and test signals: Risks include accidental mutation leakage, invalid handles being accepted, or warmup causing side effects during dry run. `dry_backend_test.go` verifies that saves/removes/deletes do not affect the underlying memory backend while reads/lists/stats still work.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/dryrun/dry_backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/dryrun/dry_backend_test.go -->
# sources/sync-backup/restic/internal/backend/dryrun/dry_backend_test.go

Purpose: Behavioral tests for the dry-run backend wrapper.

Important APIs and functions: `newBackends` returns dry-run and underlying memory backends. `TestDry` drives a scripted sequence of operations over both backends.

Control flow and state: The test directly saves/removes on the memory backend when it needs real state, then performs dry-run saves/removes/deletes and confirms they do not change that state. It also validates stat/load/list outputs and expected not-found errors.

Dependencies and integration: Uses `mem.New`, `backend.Handle`, `backend.NewByteReader`, sorting for deterministic list comparison, and `IsNotExist` checks.

Risks and test signals: Guards non-mutating dry-run semantics and read delegation. It intentionally avoids the generic backend suite because dry-run writes are not persistent.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/dryrun/dry_backend_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/file.go -->
# sources/sync-backup/restic/internal/backend/file.go

Purpose: Defines backend file type identifiers and handles.

Important APIs and types: `FileType` enumerates `PackFile`, `KeyFile`, `LockFile`, `SnapshotFile`, `IndexFile`, and `ConfigFile`. `FileType.String` returns layout names, with pack files historically named `data`. `Handle` combines type, metadata flag, and name. `Handle.String` formats a shortened display form. `Handle.Valid` validates type and name requirements.

Control flow and state: There is no persistence. Validation permits nameless config handles but requires names for all other valid types.

Dependencies and integration: Concrete backends and layouts use `Handle` to derive storage paths. Cache logic uses `IsMetadata` for pack-file caching and Azure uses it for access-tier decisions.

Risks and test signals: Adding file types requires updating validation and string conversion. `file_test.go` covers display and validation basics.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/file_test.go -->
# sources/sync-backup/restic/internal/backend/file_test.go

Purpose: Tests backend handle formatting and validation.

Important APIs and functions: `TestHandleString` covers compact display strings. `TestHandleValid` covers invalid type, missing name, config-file exception, and valid lock handle cases.

Control flow and state: Table-driven tests call `Handle.Valid` and compare errors against expected validity.

Dependencies and integration: Uses `internal/test.Equals` and package-local `Handle`/`FileType` values.

Risks and test signals: Guards the core handle contract used by every backend and wrapper.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/gs/config.go -->
# sources/sync-backup/restic/internal/backend/gs/config.go

Purpose: Defines Google Cloud Storage backend configuration parsing and environment application.

Important APIs and types: `Config` stores project ID, bucket, prefix, connection count, and creation region. `NewConfig`, `ParseConfig`, and `ApplyEnvironment` implement defaults, location parsing, and environment fill-in.

Control flow and state: `ParseConfig` requires `gs:` and a bucket/path colon, cleans the prefix, and defaults to five connections in region `us`. `ApplyEnvironment` fills `ProjectID` from `GOOGLE_PROJECT_ID` when unset.

Dependencies and integration: Uses `options.Register`, `backend.ApplyEnvironmenter`, path cleaning, and errors. The config feeds `gs.Open` and `gs.Create`.

Risks and test signals: Risks include missing project ID during bucket creation and minimal validation of bucket names. `config_test.go` covers valid parse forms.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/gs/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/gs/config_test.go -->
# sources/sync-backup/restic/internal/backend/gs/config_test.go

Purpose: Parse tests for Google Cloud Storage backend locations.

Important APIs and functions: `configTests` defines expected configs for root, nested, and trailing-slash prefixes. `TestParseConfig` delegates to `backend/test.ParseConfigTester`.

Control flow and state: The tests verify default connections and region along with parsed bucket/prefix fields.

Dependencies and integration: Uses package-local `ParseConfig` and backend test utilities.

Risks and test signals: Provides positive parser coverage but not invalid strings or environment application.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/gs/config_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/gs/gs.go -->
# sources/sync-backup/restic/internal/backend/gs/gs.go

Purpose: Implements the restic backend interface for Google Cloud Storage.

Important APIs and types: `gs` stores the storage client, project ID, connection count, bucket name, region, bucket handle, and layout. `NewFactory`, `Open`, `Create`, `Save`, `Load`, `Stat`, `Remove`, `List`, `Delete`, `Close`, `Warmup`, `WarmupWait`, `Hasher`, `Properties`, `IsNotExist`, and `IsPermanentError` implement backend behavior. Helpers include `getStorageClient`, `bucketExists`, `open`, and `openReader`.

Control flow and state: `getStorageClient` builds an HTTP client using the supplied transport and either `GOOGLE_ACCESS_TOKEN` or Google default credentials. `Create` checks bucket existence, tolerates forbidden bucket-attrs access as possible existing bucket, and creates a bucket when missing. `Save` disables resumable upload chunking, streams data, sets MD5, closes the writer, and checks byte count. `Load` delegates to `util.DefaultLoad` and range reader validation. `List` iterates objects by layout prefix and calls the callback with basename/size.

Persistence and dependencies: Data persists as GCS objects using the default restic layout. Dependencies include `cloud.google.com/go/storage`, OAuth2/google auth, `googleapi`, `layout`, `location`, `util`, and restic backend abstractions.

Integration points: Registered through `NewFactory` and aggregate backend registry. It supports generic backend tests and repository operations. MD5 hasher support enables upload validation.

Risks and test signals: Risks include credential/environment handling, forbidden bucket-existence checks masking missing buckets, range-too-short classification, rate-limit behavior from disabled chunking, and object listing cancellation. `gs_test.go` runs the generic backend suite when GCS credentials are available; config tests cover parsing.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/gs/gs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/gs/gs_test.go -->
# sources/sync-backup/restic/internal/backend/gs/gs_test.go

Purpose: Integration and benchmark harness for the Google Cloud Storage backend.

Important APIs and functions: `newGSTestSuite` creates the generic backend suite. `TestBackendGS` and `BenchmarkBackendGS` gate execution on project, repository, and credential environment variables.

Control flow and state: Tests parse `RESTIC_TEST_GS_REPOSITORY`, set project ID and unique prefix, and run generic backend tests or benchmarks. They require either `GOOGLE_APPLICATION_CREDENTIALS` or `GOOGLE_ACCESS_TOKEN`.

Dependencies and integration: Uses `internal/backend/test`, `gs.NewFactory`, real GCS credentials, and `internal/test.SkipDisallowed` on skips.

Risks and test signals: Skipped without credentials. When enabled, it validates the GCS backend against the shared backend contract and performance benchmarks.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/gs/gs_test.go -->
