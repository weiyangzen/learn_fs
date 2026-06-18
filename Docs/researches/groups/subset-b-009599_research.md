# Research Group subset-b-009599

This grouped report covers selected GCSFuse integration tests and shell harnesses under `sources/user-network-fs/gcsfuse/tools/integration_tests`. Each section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/setup_test.go

## Purpose

`setup_test.go` is the package harness for read-cache integration tests. It centralizes constants, environment state, fallback test configuration, mount selection, log/cache path setup, and cleanup for suites that validate GCSFuse file cache, range read caching, metadata TTL behavior, chunk cache, regex include/exclude rules, remount behavior, and parallel download behavior.

## Important APIs, Types, and Functions

Important constants include cache sizes, file sizes, chunk sizes, offsets, TTLs, cache directory names, and retry timings used by the sibling read-cache tests. The package-level `env` struct stores the `storage.Client`, context, active test directory, `test_suite.TestConfig`, bucket type, and cache directory path. `setupLogFileAndCacheDir` selects a per-suite log and cache directory, with special handling for GKE-mounted-directory mode and legacy GKE paths. `mountGCSFuseAndSetupTestDir` mounts GCSFuse using the current `mountFunc` and creates a unique GCS-backed test directory. `TestMain` is the main orchestrator. `overrideFilePathsInFlagSet` rewrites `/gcsfuse-tmp` placeholders into the actual temp root for non-GKE runs.

## Control Flow

`TestMain` parses setup flags, reads the config file, and if `ReadCache` config is absent synthesizes a large matrix of `ConfigItem` entries. Those entries map run names such as `TestSmallCacheTTLTest`, `TestRangeReadTest`, `TestChunkCacheTest`, and regex/cache variants to explicit GCSFuse flag strings and bucket compatibility maps. It then creates the storage client, handles mounted-directory mode, prepares the test bucket directory, rewrites temp paths, and runs the package three times: static mounting, dynamic mounting, and only-dir mounting. Each phase changes `mountDir` and `mountFunc`, then calls `m.Run`. Cleanup removes both normal and only-dir test prefixes from GCS.

## State and Persistence Behavior

The harness mutates global package state (`testEnv`, `mountDir`, `rootDir`, `mountFunc`) between mounting phases and across suite runs. It creates local cache directories and JSON log files under a GCSFuse temp directory, and it creates/deletes test object prefixes in the target bucket. Cache directories are not automatically cleaned by GCSFuse on mount, so sibling suites explicitly remove them between tests. The fallback config includes duplicate assignment to config index 13 for job chunk parallel-download variants; later assignment overrides the earlier list.

## Dependencies and Integration Points

The file depends on Google Cloud Storage client APIs, GCSFuse internal cache unit constants, integration `client`, `setup`, `test_suite`, and mounting helpers for static, dynamic, and only-dir modes. It integrates with all `read_cache` sibling suites through shared constants and helpers, and with the higher-level mounted-directory runner through `setup.RunTestsForMountedDirectory`.

## Risks and Edge Cases

The harness is sensitive to path rewriting, especially `/gcsfuse-tmp`, GKE-mounted-directory paths, and legacy log paths. Misconfigured run names or compatibility maps can silently skip intended suites. Because `m.Run` is invoked multiple times with mutable global mount state, suites must not assume one-time package state. The generated fallback matrix is large and easy to drift from YAML config. Time-based TTL tests can be flaky under high GCS latency unless their retry wrappers are used.

## Test Signals

Strong signals are successful execution of the read-cache package across static, dynamic, and only-dir mounting with flat, HNS, and zonal compatibility. Logs should be produced in the configured JSON log files, cache directories should be isolated per test name, and cleanup should leave no `ReadCacheTest` or only-dir test prefixes in the bucket.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/small_cache_ttl_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/small_cache_ttl_test.go

## Purpose

`small_cache_ttl_test.go` validates file-cache behavior when metadata cache TTL is finite and the file-cache capacity is small. It verifies both stale-cache serving before metadata expiry and cache hits after metadata refresh when object content has not changed.

## Important APIs, Types, and Functions

`smallCacheTTLTest` is a `testify/suite` suite with per-run flags, storage client, context, and base test name. `SetupSuite` configures log/cache paths and mounts GCSFuse; `SetupTest` truncates logs, removes the cache directory, and creates a fresh test prefix; `TearDownTest` preserves logs on failure; `TearDownSuite` unmounts. `TestReadAfterUpdateAndCacheExpiryIsCacheMiss` and `TestReadForLowMetaDataCacheTTLIsCacheHit` are the behavioral tests. `TestSmallCacheTTLTest` expands config-derived flag sets and runs the suite.

## Control Flow

The update/expiry test uses `operations.RetryUntil` to keep the first read, direct GCS object modification, and immediate second read within the configured metadata TTL. It expects the second read to serve stale cached content, then sleeps for TTL expiry and expects a third read to miss cache and fetch the smaller updated object. The low-TTL cache-hit test reads an object, waits past metadata TTL, reads again, and immediately reads a third time; unchanged content should remain cache-hit eligible.

## State and Persistence Behavior

Each test creates objects in a unique GCS prefix, writes file-cache content to `testEnv.cacheDirPath`, and appends structured read logs to `testEnv.cfg.LogFile`. The first test changes remote object content through the storage client while local cache state persists across reads. Cache validation reads local cache file sizes and JSON log entries.

## Dependencies and Integration Points

The suite relies on shared read-cache helpers (`setupFileInTestDir`, `modifyFile`, `readFileAndValidateCacheWithGCS`, `readFileAndGetExpectedOutcome`, `validate`, and cache-size validators), the JSON read-log parser, `operations.RetryUntil`, and suite flag matrices from `setup_test.go`.

## Risks and Edge Cases

The first scenario is timing-sensitive: if object creation, read, modification, and second read exceed `metadataCacheTTlInSec`, stale serving is no longer expected, so the retry wrapper restarts setup. Log assertions require exactly three structured read logs, so unrelated reads from setup or kernel behavior can break the signal. Cache size expectations depend on configured file sizes and chunk counts.

## Test Signals

Expected logs are miss, hit, miss for the update/expiry path and miss, hit, hit for the unchanged-content path. Content comparison must show stale data before TTL expiry and updated data after expiry. The suite should pass with both serial and parallel downloads, and with HTTP or gRPC client protocol flag variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_cache/small_cache_ttl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/concurrent_read_same_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/concurrent_read_same_file_test.go

## Purpose

This file stress-tests concurrent random reads from the same mounted file and compares every read against a local disk copy. It targets the GCSFuse read algorithm under shared-file-handle-independent workloads.

## Important APIs, Types, and Functions

`TestReadSameFileConcurrently` creates a 30 MiB file, copies it into the mount, and starts three goroutines through `errgroup.Group`. `readAndCompare` opens the mounted file read-only, performs five `ReadAt` calls at a supplied offset and chunk size, reads the same bytes from the local disk file, and compares byte slices with `bytes.Equal`.

## Control Flow

The test creates one source/mounted file pair, chooses a random offset for each goroutine, and has every goroutine call `readAndCompare` with a 5 MiB chunk size. `readAndCompare` treats `io.EOF` as non-fatal because a random offset near EOF may return a short read. It then reads the matching local chunk with `operations.ReadChunkFromFile` and fails the test if content differs.

## State and Persistence Behavior

The test persists a generated file on local disk and in the mounted bucket prefix through helper APIs. It has no explicit cleanup in this file, relying on shared integration helpers and package cleanup. The mounted file is opened separately per goroutine, which isolates file offsets while exercising shared backend/cache behavior.

## Dependencies and Integration Points

It depends on `read_gcs_algo` package constants from `read_gcs_algo_test.go`, `operations.CreateFileAndCopyToMntDir`, `operations.OpenFileAsReadonly`, `operations.ReadChunkFromFile`, and `golang.org/x/sync/errgroup`. It integrates with the package mount harness that supplies the bucket and flags.

## Risks and Edge Cases

Random offsets are chosen with `rand.Int64N(fileSize)` but a 5 MiB chunk may extend beyond EOF; both mounted and local helper behavior must produce comparable buffers for short reads. The goroutines call `t.Fatalf` from worker goroutines, which is common in tests but can make failure reporting abrupt. `errgroup` itself does not receive real errors from the helper because fatal exits happen through `testing.T`.

## Test Signals

Passing signal is byte-for-byte equality across five repeated random reads in each concurrent goroutine. Failures indicate concurrency bugs in read buffering, range handling, cache reuse, or mounted-file consistency against local disk.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/concurrent_read_same_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/read_gcs_algo_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/read_gcs_algo_test.go

## Purpose

`read_gcs_algo_test.go` is the package harness for tests that exercise GCSFuse read algorithm transitions and block-size handling. It prepares storage clients, config fallback, mount flags, and test-bucket setup.

## Important APIs, Types, and Functions

The file defines `OneMB`, `DirForReadAlgoTests`, package globals `storageClient` and `ctx`, and `TestMain`. The fallback `ReadGCSAlgo` config provides an `--implicit-dirs=true` flag set and flat/HNS/zonal compatibility.

## Control Flow

`TestMain` parses flags, loads config, synthesizes a default config if absent, creates context and storage client, handles mounted-directory mode when both mounted directory and test bucket are supplied, builds compatible flag sets, prepares the test directory for the bucket, and invokes `static_mounting.RunTestsWithConfigFile`.

## State and Persistence Behavior

Package-level state contains the storage client and context for helper use. Test files are created under `DirForReadAlgoTests` in the bucket/mount and are compared against local disk copies. There is no multi-mount cycle in this harness, unlike the read-cache harness.

## Dependencies and Integration Points

The file integrates with `test_suite.ReadConfigFile`, `setup.TestEnvironment`, `setup.BuildFlagSets`, `setup.SetUpTestDirForTestBucket`, mounted-directory test execution, and static mounting. Sibling tests use `OneMB` and `DirForReadAlgoTests`.

## Risks and Edge Cases

The fallback log message mentions list-large-dir tests, which is misleading but not behavioral. Since all tests run through static mounting only, it does not cover persistent or dynamic mount differences. Mounted-directory mode requires a test bucket because file contents are validated against bucket-backed state.

## Test Signals

Successful package execution across compatible bucket types indicates that algorithm tests can create local/mounted file pairs and compare data under the configured read path. Setup failures usually point to config, credential, or mount issues rather than algorithm logic.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/read_gcs_algo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/seq_diff_block_size_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/seq_diff_block_size_test.go

## Purpose

This test checks sequential reads with block sizes below, equal to, non-multiple of, and multiple of the typical 1 MiB kernel buffer size. It targets range assembly and sequential-read detection around varied read sizes.

## Important APIs, Types, and Functions

`testCase` stores a subtest name, offset, and chunk size. `TestReadSequentialWithDifferentBlockSizes` creates a 10 MiB local/mounted file pair and runs `operations.ReadAndCompare` for chunk sizes 0.5 MiB, 1 MiB, 1.5 MiB, and 5 MiB.

## Control Flow

The test builds a static table of read sizes at offset zero, then runs a subtest for each case. Each subtest reads the mounted file and local disk file at the same offset and compares bytes through the shared operations helper.

## State and Persistence Behavior

The only persisted state is the generated test file in local disk and in the mounted bucket directory. The subtests share the same file pair, so earlier reads may warm caches or read-ahead state for later subtests depending on mount configuration.

## Dependencies and Integration Points

It depends on `OneMB` and `DirForReadAlgoTests` from the package harness and on `operations.CreateFileAndCopyToMntDir` and `operations.ReadAndCompare`. It runs under the harness-provided GCSFuse flags.

## Risks and Edge Cases

Because subtests share one file and always start at offset zero, caching/read-ahead warmed by earlier subtests can influence later cases. The test validates correctness, not exact algorithm classification or number of backend requests. It will not catch performance-only regressions unless they cause incorrect data or errors.

## Test Signals

Passing subtests show that reads of common and irregular block sizes return byte-identical data to local disk. Failures suggest short-read handling, range boundary, or buffer aggregation problems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/seq_diff_block_size_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/seq_to_ran_to_seq_read_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/seq_to_ran_to_seq_read_test.go

## Purpose

This test exercises a read pattern that begins with reads currently classified as sequential, shifts into random backward reads, then performs a large read expected to re-enter sequential behavior under the existing read algorithm.

## Important APIs, Types, and Functions

`TestSeqReadThenRandomThenSeqRead` creates a 50 MiB test file and calls `operations.ReadAndCompare` at offsets 40 MiB, 35 MiB, 30 MiB, 25 MiB, 20 MiB, and finally 10 MiB with a 40 MiB read size.

## Control Flow

The test intentionally reads backward in 1 MiB chunks. A comment documents that the current algorithm treats the first two reads as sequential. After several random reads, it performs a larger 40 MiB read from 10 MiB, which should be converted to sequential by current logic. Every step validates mounted content against the local disk source.

## State and Persistence Behavior

The mounted file and local disk file persist for the duration of the test. The sequence is stateful with respect to GCSFuse's per-handle or per-reader algorithm heuristics; changing the ordering changes the behavior under test.

## Dependencies and Integration Points

The test uses `operations.CreateFileAndCopyToMntDir`, `operations.ReadAndCompare`, `OneMB`, and `DirForReadAlgoTests`. It is coupled to the read algorithm behavior documented in an inline GitHub URL for an older implementation.

## Risks and Edge Cases

The test checks correctness but not structured evidence that the algorithm actually classified reads as sequential or random. If the algorithm changes but still returns correct bytes, this test may continue passing. Conversely, if future behavior intentionally changes classification, the comments may become stale without affecting assertions.

## Test Signals

The primary signal is byte-for-byte equality through an access pattern that crosses sequential/random/sequential heuristics. Failures indicate stateful reader transition bugs, range handling errors, or large-read fallback problems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_gcs_algo/seq_to_ran_to_seq_read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/concurrent_read_files_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/concurrent_read_files_test.go

## Purpose

This file validates concurrent reads of multiple large files through a mounted GCSFuse directory. It targets large-object throughput and correctness when several 500 MiB objects are created and read at the same time.

## Important APIs, Types, and Functions

The file defines random file names `FileOne`, `FileTwo`, and `FileThree`, plus `NumberOfFilesInLocalDiskForConcurrentRead`. `TestReadFilesConcurrently` creates a package test directory, concurrently creates/copies three local files to the mount, registers local-file cleanup, and concurrently reads each mounted file with `operations.ReadAndCompare`.

## Control Flow

An `errgroup.Group` first starts three creation goroutines, each selecting a local path under `$HOME`, a mount path under the test directory, and creating/copying a 500 MiB file. After creation succeeds, a cleanup closure is registered for each local file. A second errgroup runs one full-file read comparison per file.

## State and Persistence Behavior

The test creates three large local files and three mounted bucket objects. Local files are removed via `t.Cleanup`; mounted content is handled by package-level test-directory cleanup. Arrays of paths are shared across goroutines with distinct indices.

## Dependencies and Integration Points

It depends on package constants from `read_large_files_test.go`, `setup.SetupTestDirectory`, `setup.GenerateRandomString`, `operations.CreateFileOnDiskAndCopyToMntDir`, and `operations.ReadAndCompare`. It runs under the read-large-files mount matrix, including file-cache variants.

## Risks and Edge Cases

The test is resource-intensive: it writes and reads roughly 1.5 GiB of test data. It depends on available disk, mount bandwidth, and timeout budget. Although index capture is handled explicitly, calls into `testing.T` from goroutines can produce abrupt failure behavior. Parallel creation and read may expose cache capacity pressure under file-cache configurations.

## Test Signals

Passing signal is full byte equality for all three 500 MiB mounted files against their local sources under concurrent reads. Failures may indicate race conditions, large-range read bugs, cache eviction problems, or environment resource exhaustion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/concurrent_read_files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/random_read_large_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/random_read_large_file_test.go

## Purpose

This test validates random reads from a 500 MiB mounted object by comparing many 1 MiB chunks against the local source file.

## Important APIs, Types, and Functions

`TestReadLargeFileRandomly` creates and copies a 500 MiB file, loops `NumberOfRandomReadCalls` times, chooses a random offset with `rand.Int63n`, and calls `operations.ReadAndCompare` with `RandomReadChunkSize`. It removes the local file at the end.

## Control Flow

After setup, each iteration picks an offset between `MinReadableByteFromFile` and `MaxReadableByteFromFile`, then reads the mounted and local files at that offset. The helper handles the actual content comparison.

## State and Persistence Behavior

The test creates one large local file and one mounted object. The local file is explicitly removed after the loop; bucket cleanup is package-level. Reads may warm GCSFuse file cache or range cache depending on flags.

## Dependencies and Integration Points

It depends on package constants, `operations.CreateFileAndCopyToMntDir`, `operations.ReadAndCompare`, and the read-large-files harness. It runs under plain, gRPC, file-cache, and zonal-specific flag sets.

## Risks and Edge Cases

Offsets can be near EOF while read size is 1 MiB, so helper behavior must handle short reads consistently. The old `math/rand` package is used without explicit seeding, which gives repeatable pseudo-random sequences in many Go versions. The test validates correctness but not request count or performance.

## Test Signals

Success means all random chunks match the local source. Failures point to offset handling, short-read handling, range-read correctness, or cache-file-for-range-read interactions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/random_read_large_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/read_large_files_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/read_large_files_test.go

## Purpose

This is the package harness for large-file read tests. It defines size constants and configures GCSFuse runs that exercise normal reads, gRPC, file cache with range caching, unlimited file cache, and a zonal-bucket-specific kernel-reader-disabled path.

## Important APIs, Types, and Functions

Constants define `FiveHundredMB`, sequential `ChunkSize`, random chunk size, number of random reads, offset bounds, and `DirForReadLargeFilesTests`. Package globals store `storageClient`, `ctx`, and a random file name. `TestMain` controls config loading, storage client lifecycle, mounted-directory mode, path rewriting, flag-set generation, and static mount execution.

## Control Flow

`TestMain` parses flags, synthesizes `ReadLargeFiles` config if needed, sets up environment and storage client, optionally delegates to mounted-directory mode, prepares the bucket test directory, rewrites `/gcsfuse-tmp` cache paths, builds compatible flag sets, and runs the tests via `static_mounting.RunTestsWithConfigFile`.

## State and Persistence Behavior

The harness creates bucket prefixes and local cache directories under the test temp root. It maintains a storage client for the package lifetime and relies on helper cleanup for generated large files and bucket directories. It does not run dynamic or persistent mounts.

## Dependencies and Integration Points

It depends on Google Cloud Storage client setup, `operations.MiB`, setup/test-suite helpers, and static mounting. Sibling tests consume the size and directory constants.

## Risks and Edge Cases

The default flag matrix includes expensive 500 MiB workloads with a 700 MiB file-cache limit, so tests can stress disk and runtime. Zonal bucket compatibility differs from flat/HNS for one config item. Cache path rewriting must occur before flag-set expansion. Mounted-directory mode requires both bucket and mount so local-vs-mounted validation remains meaningful.

## Test Signals

Package-level success across the flag matrix proves large sequential, random, and concurrent reads return correct content under multiple read/cache configurations. Setup failures usually indicate bucket, build, mount, or local resource problems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/read_large_files_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/seq_read_large_file_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/seq_read_large_file_test.go

## Purpose

This test validates sequential full-file reads of a 500 MiB mounted object, including an `O_DIRECT` open path.

## Important APIs, Types, and Functions

`TestReadLargeFileSequentially` creates and copies a 500 MiB local file, opens the mounted file with `os.O_RDONLY|syscall.O_DIRECT`, reads it sequentially using `operations.ReadFileSequentially` with a 200 MiB chunk size, reads the local source with `operations.ReadFile`, and compares byte slices.

## Control Flow

The test creates the file pair, opens the mounted file, reads sequentially into memory, reads the entire local file, compares content with `bytes.Equal`, and removes the local file.

## State and Persistence Behavior

It creates a large local file and mounted object. It loads the full 500 MiB contents into memory for comparison, which creates high memory pressure. The local file is explicitly removed; bucket object cleanup is handled by package setup.

## Dependencies and Integration Points

It depends on `operations.CreateFileAndCopyToMntDir`, `operations.ReadFileSequentially`, `operations.ReadFile`, package constants, and setup file permissions. It exercises the kernel/direct-read path as controlled by mount flags.

## Risks and Edge Cases

`O_DIRECT` has platform and alignment constraints, so helper implementations must respect direct I/O requirements. Reading the entire file into memory can be expensive. The test catches content errors but not partial performance regressions.

## Test Signals

Passing signal is exact equality between sequentially read mounted content and the local source. Failures suggest direct I/O, sequential buffering, large chunk, or EOF handling bugs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/read_large_files/seq_read_large_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/readdirplus_with_dentry_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/readdirplus_with_dentry_cache_test.go

## Purpose

This suite verifies that when readdirplus and dentry cache are enabled, GCSFuse serves `ReadDirPlus` directory listing correctly and avoids extra `LookUpInode` calls during the measured directory read.

## Important APIs, Types, and Functions

`ReaddirplusWithDentryCacheTest` is a `testify/suite` suite with flags, storage client, context, and base name. `SetupSuite` configures the log file and mounts, `SetupTest` creates a per-test directory, teardown preserves logs and unmounts. `TestReaddirplusWithDentryCache` creates a target directory with one file, one empty subdirectory, and one non-empty subdirectory, then calls `fusetesting.ReadDirPlusPicky`.

## Control Flow

The test builds a known directory tree, records start/end timestamps around `ReadDirPlusPicky`, checks the returned entries count, names, directory flags, and modes, then calls `validateLogsForReaddirplus` with `dentryCacheEnabled=true`. That validator requires `ReadDirPlus` logs, rejects `ReadDir` logs, and rejects `LookUpInode` logs in the measured window.

## State and Persistence Behavior

The suite creates GCS-backed objects and directories under `dirForReaddirplusTest/<test name>`. It writes trace JSON logs to a per-suite log file. Directory and inode cache state is intentionally warmed during setup and object creation, and this is part of the expected no-lookup behavior.

## Dependencies and Integration Points

It uses shared `readdirplus` harness state and helpers, `operations` directory/file helpers, `setup.SetUpLogFilePath`, `fusetesting.ReadDirPlusPicky`, and `testify` assertions. It depends on mount flags `--experimental-enable-readdirplus` and `--experimental-enable-dentry-cache`.

## Risks and Edge Cases

The test assumes stable listing order (`emptySubDirectory`, `file`, `subDirectory`) and specific modes. Log-based assertions depend on trace JSON formatting and timestamp windows. If setup no longer warms parent inode cache, `LookUpInode` expectations may need adjustment.

## Test Signals

Success requires correct readdirplus entry metadata and logs showing `ReadDirPlus` but not `ReadDir` or `LookUpInode`. Failures separate data-plane listing issues from control-plane/cache behavior through the log validator.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/readdirplus_with_dentry_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/readdirplus_without_dentry_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/readdirplus_without_dentry_cache_test.go

## Purpose

This suite verifies readdirplus behavior when dentry cache is not enabled. It expects `ReadDirPlus` listing correctness and confirms lookup calls occur for parent and entries.

## Important APIs, Types, and Functions

`ReaddirplusWithoutDentryCacheTest` mirrors the dentry-cache-enabled suite. Its core test creates the same directory structure and calls `fusetesting.ReadDirPlusPicky`, then validates entries and log behavior through `validateLogsForReaddirplus` with `dentryCacheEnabled=false`.

## Control Flow

Setup configures logging and mounting. The test creates `target_dir`, a file, an empty subdirectory, and a subdirectory containing one file. It records the `ReadDirPlusPicky` time window, verifies the three direct entries, and validates logs. With dentry cache disabled, the validator requires `ReadDirPlus`, rejects plain `ReadDir`, and requires `LookUpInode`.

## State and Persistence Behavior

State is a GCS-backed test tree and trace log file. Unlike the cache-enabled case, lookup behavior is expected during the measured read because dentries are not cached.

## Dependencies and Integration Points

It depends on the shared readdirplus setup, GCS client helpers, operations helpers, `fusetesting`, and the package config item that enables readdirplus without enabling dentry cache.

## Risks and Edge Cases

The same ordering, mode, and log-format assumptions apply as in the cache-enabled suite. The required `LookUpInode` signal can be sensitive to implementation changes that prefetch or cache dentries through another path even when the explicit dentry cache flag is absent.

## Test Signals

Passing signal is correct entry metadata plus logs that show `ReadDirPlus`, do not show `ReadDir`, and do show `LookUpInode`. This distinguishes readdirplus correctness from dentry-cache optimization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/readdirplus_without_dentry_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/setup_test.go

## Purpose

`setup_test.go` is the harness for readdirplus integration tests. It prepares config, mounting, storage clients, log parsing helpers, and log validation that differentiates readdirplus from plain readdir and dentry-cache behavior.

## Important APIs, Types, and Functions

Constants define test directory names and GKE temp/log paths. `env` stores storage client, context, test directory, config, and bucket type. `loadLogLines` reads a log stream into lines. `validateLogsForReaddirplus` parses JSON log lines and searches message text for `ReadDirPlus (`, `ReadDir (`, and `LookUpInode (` within a timestamp window. `mountGCSFuseAndSetupTestDir` mounts and creates the test directory. `TestMain` loads config and runs the package.

## Control Flow

`TestMain` parses flags, synthesizes two fallback config items if needed, initializes environment and storage client, handles mounted-directory mode, prepares the test bucket directory, rewrites temp paths, sets static mounting as the only mount mode, runs tests, cleans the test prefix from GCS, and exits with the package result.

## State and Persistence Behavior

The harness stores mutable global `testEnv`, `mountFunc`, `mountDir`, and `rootDir`. It writes trace logs to configured JSON files and creates/deletes `dirForReaddirplusTest` objects in the bucket. Log validation reads the persisted log file after each test action.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, JSON log parsing in `read_logs`, static mounting, setup/test-suite helpers, and `testify/require`. Sibling suites use `validateLogsForReaddirplus` as the behavioral oracle for FUSE operation selection.

## Risks and Edge Cases

`validateLogsForReaddirplus` ignores lines that fail JSON parsing, so non-JSON logs can hide expected signals. Timestamp filtering requires clock consistency and accurate log timestamps. The fallback config only covers static mounting. The `OldGKElogFilePath` compatibility path is a migration accommodation that may become stale.

## Test Signals

Success means both readdirplus suites can create directories, call `ReadDirPlusPicky`, and find expected FUSE operation logs. Harness-level failures usually indicate log path, mount flag, or storage setup problems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readdirplus/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/copy_object_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/copy_object_test.go

## Purpose

This file verifies that copying files or directories into a read-only GCSFuse mount fails.

## Important APIs, Types, and Functions

`checkIfFileCopyFailed` attempts to copy a source file into the read-only subdirectory destination and expects an error. `TestCopyFile` and `TestCopyFileFromBucketDirectory` exercise file copies from root-level and directory-level files. `checkIfDirCopyFailed` expects `operations.CopyDir` to fail. `TestCopyDirectory` and `TestCopySubDirectory` exercise directory-copy attempts.

## Control Flow

Each test constructs source and destination paths under `setup.MntDir()` and the seeded `TestDirForReadOnlyTest` tree. It invokes the copy helper and reports an error if the copy unexpectedly succeeds.

## State and Persistence Behavior

The tests rely on read-only fixture data created by `readonly_test.go`. They should not create destination files or directories; success would indicate an unintended mutation of the mounted bucket.

## Dependencies and Integration Points

The file depends on `operations.CopyFile`, `operations.CopyDir`, `setup.MntDir`, `setup.GenerateRandomString`, and constants from the package harness. It runs under `--o=ro`, restrictive file/dir mode, persistent mount, and viewer-credential variants configured by the harness.

## Risks and Edge Cases

The helper only checks that an error occurred; it does not validate that the error is specifically read-only for copy operations. Destination names include randomness for files, reducing collisions, while directory destination paths are fixed by fixture layout.

## Test Signals

Passing tests mean copy operations return errors and therefore do not mutate the read-only mount. Unexpected success is a direct read-only enforcement regression.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/copy_object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/create_object_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/create_object_test.go

## Purpose

This file verifies that creating files or directories through a read-only GCSFuse mount fails with a read-only filesystem error.

## Important APIs, Types, and Functions

`checkIfFileCreationFailed` calls `os.OpenFile` with `os.O_CREATE` and validates failure with `operations.CheckErrorForReadOnlyFileSystem`. `TestCreateFile` and `TestCreateFileInDirectory` cover root-level and nested file creation. `checkIfDirCreationFailed` calls `os.Mkdir` and validates read-only failure. `TestCreateDir` and `TestCreateSubDirectoryInDirectory` cover directory creation.

## Control Flow

Tests build paths under the mounted fixture tree, attempt creation, fail if creation succeeds, and validate the returned error. The file helper defers `file.Close()` even when `file` may be nil if creation failed, which depends on Go allowing method calls on nil interface values only if not reached through a nil concrete pointer; in practice this defer can panic if not guarded.

## State and Persistence Behavior

The expected behavior is no new objects or directories in GCS. All state comes from the read-only fixture seeded before tests.

## Dependencies and Integration Points

It uses standard `os`/`io/fs`, `operations.CheckErrorForReadOnlyFileSystem`, setup permissions, and package constants. It runs under the read-only harness's multiple mount and credential configurations.

## Risks and Edge Cases

The unconditional `defer file.Close()` in `checkIfFileCreationFailed` is risky when `os.OpenFile` returns a nil file with an error. The tests validate error type for create operations, which is stronger than copy tests. Directory mode uses `fs.ModeDir` rather than permission bits, but failure is expected before mode matters.

## Test Signals

Passing signal is read-only error on file and directory creation attempts. Any successful create is a mutation bug; any wrong error may indicate path resolution or permission behavior drift.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/create_object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/delete_object_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/delete_object_test.go

## Purpose

This file verifies that deleting files, directories, subdirectories, or the mount root through a read-only mount fails.

## Important APIs, Types, and Functions

`checkIfObjDeletionFailed` calls `os.RemoveAll` and requires a non-nil error validated by `operations.CheckErrorForReadOnlyFileSystem`. Tests cover deleting the main fixture directory, root file, subdirectory, nested file, and all objects via the mount root.

## Control Flow

Each test builds the target path from `setup.MntDir()` and fixture constants, calls the helper, and fails if deletion succeeds.

## State and Persistence Behavior

The expected behavior is preservation of all seeded fixture objects and directories. No new state is created. Because `os.RemoveAll` can return nil for non-existent paths, fixture correctness is important for meaningful coverage.

## Dependencies and Integration Points

It depends on standard `os`, setup constants, and read-only error validation from operations. It is part of the broader read-only package matrix.

## Risks and Edge Cases

`os.RemoveAll` semantics differ from simple `Remove`; if paths are absent, success may be ambiguous. The tests rely on fixture paths existing. Recursive delete of the mount root is a high-impact operation, so a regression could wipe test data if read-only enforcement fails.

## Test Signals

Passing means delete attempts are rejected with read-only filesystem errors. Fixture-preservation checks in other tests add indirect confidence that failed deletes did not remove source data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/delete_object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/list_objects_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/list_objects_test.go

## Purpose

This file verifies that read-only mounts still allow directory listing and expose the expected seeded objects.

## Important APIs, Types, and Functions

`TestListObjectsInBucket` lists the read-only test root and expects the `Test` directory and `Test1.txt` file. `TestListObjectsInBucketDirectory` lists the nested `Test` directory and expects `a.txt` and `b`.

## Control Flow

Each test calls `os.ReadDir`, checks the number of entries, then checks names and `IsDir` flags by index.

## State and Persistence Behavior

The tests read fixture state created by `createTestDataForReadOnlyTests`. They do not mutate the filesystem. Listing order is treated as stable and part of the assertion.

## Dependencies and Integration Points

It depends on fixture constants, `setup.MntDir`, and standard `os.ReadDir`. It complements the mutation-denial tests by proving read/list operations remain available under read-only flags and viewer credentials.

## Risks and Edge Cases

The tests assume deterministic ordering from `os.ReadDir`, which is sorted by filename in Go, matching expected names. They use `log.Fatal` on read errors, which exits the test process rather than failing only the current test. The fixture object count must remain aligned with setup.

## Test Signals

Passing indicates directory listing works under read-only mode and object/directory classification is correct. Failures suggest fixture setup, implicit directory, read permission, or list behavior regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/list_objects_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/read_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/read_test.go

## Purpose

This file verifies that existing files can be read through a read-only mount and non-existent files fail with "no such file or directory".

## Important APIs, Types, and Functions

`checkIfFileReadSucceeded` reads a file with `operations.ReadFile` and compares string content. `TestReadFile`, `TestReadFileFromBucketDirectory`, and `TestReadFileFromBucketSubDirectory` cover seeded files at different depths. `checkIfNonExistentFileFailedToOpen` opens with `os.O_RDONLY|syscall.O_DIRECT` and validates the not-found error. Three tests cover missing files at matching depths.

## Control Flow

Existing-file tests construct paths and compare contents against constants from setup. Missing-file tests attempt direct-read opens and call `checkErrorForObjectNotExist`.

## State and Persistence Behavior

The file reads seeded GCS objects but does not mutate state. Direct I/O open attempts for missing files do not create objects.

## Dependencies and Integration Points

It uses package fixture constants, `operations.ReadFile`, setup permissions, and the package-level not-found validator. It runs under multiple read-only mount and credential configurations.

## Risks and Edge Cases

`checkIfNonExistentFileFailedToOpen` defers `file.Close()` even if open fails and returns a nil file, which can panic. Existing content constants include trailing newlines and must match setup writes exactly. `O_DIRECT` may influence error behavior on some platforms.

## Test Signals

Passing means read-only does not block reads, fixture contents are exact, and missing files surface not-found rather than read-only errors. Failures separate data access regressions from negative path behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/read_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/readonly_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/readonly_test.go

## Purpose

`readonly_test.go` is the harness and fixture setup for read-only integration tests. It seeds a known object hierarchy, defines shared constants, configures read-only mount variants, and runs the package under static, persistent, and viewer-credential modes.

## Important APIs, Types, and Functions

Constants define the fixture tree, expected object counts, file contents, missing names, and rename targets. `createTestDataForReadOnlyTests` writes three objects to the target bucket using the storage client. `checkErrorForObjectNotExist` validates not-found errors by substring. `TestMain` handles config, environment, storage client, fixture creation, mounted-directory mode, path rewriting, flag-set generation, and test execution.

## Control Flow

`TestMain` parses flags, loads or synthesizes `ReadOnly` config, sets up storage client and bucket environment, writes fixture objects, optionally delegates to mounted-directory mode, prepares test directories and rewritten paths, builds flag sets, then runs tests first with static mounting, then persistent mounting, then with `creds_tests.RunTestsForDifferentAuthMethods` using objectViewer permissions.

## State and Persistence Behavior

Fixture objects persist in GCS for the package run. The harness may use read-only flags, restrictive file/dir modes, gRPC, and file cache. It mutates global `storageClient` and `ctx`. It does not explicitly clean the fixture prefix in this file, so cleanup is delegated to broader setup or test environment.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, credential test helpers, static/persistent mounting helpers, setup/test-suite helpers, and sibling test files. It integrates with IAM behavior by re-running tests under viewer credentials.

## Risks and Edge Cases

The suite changes bucket permissions for credential variants, so it is listed as non-parallel in the e2e runner. Fixture setup writes directly to GCS before read-only mounting; failures there invalidate all tests. Error validators rely on string matching. Cleanup gaps can leave seeded objects if broader cleanup fails.

## Test Signals

A full pass demonstrates that read/list/stat operations work while create/write/append/copy/delete/rename fail across read-only flag styles, persistent mount, file cache, gRPC, and viewer credentials.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/readonly_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/rename_object_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/rename_object_test.go

## Purpose

This file verifies that file and directory rename operations fail on a read-only mount and that source objects remain intact while destination paths are not created.

## Important APIs, Types, and Functions

`checkIfRenameFileFailed` calls `operations.RenameFile`, validates read-only failure, stats the old path, and ensures the new path does not exist. `checkIfRenameDirFailed` does the same for directories. Tests cover root file, nested file, subdirectory file, top-level directory, and subdirectory renames, with extra child-listing checks for directory cases.

## Control Flow

Each test constructs old and new paths under the fixture tree, invokes the helper, and for directory tests reads the original directory to ensure children remain present and correct.

## State and Persistence Behavior

Expected state is no mutation: original files/directories remain, destination names are absent, and child entries are unchanged. Directory tests explicitly verify source subtree preservation after failed rename.

## Dependencies and Integration Points

It depends on operations rename helpers, read-only error validation, `os.Stat`, `os.ReadDir`, setup paths, and fixture constants. It is part of the read-only package matrix.

## Risks and Edge Cases

Directory listing checks assume sorted order and exact fixture counts. Error validation is strong for rename helpers. If rename partially mutates before failing, the explicit old/new stat and listing assertions should catch it.

## Test Signals

Passing signal is read-only errors on all rename attempts plus preserved old paths and absent new paths. Failures indicate read-only enforcement gaps or partial-rename rollback problems.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/rename_object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/stat_object_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/stat_object_test.go

## Purpose

This file verifies `os.Stat` behavior on read-only mounts for existing files/directories and missing objects.

## Important APIs, Types, and Functions

`statObject` wraps `os.Stat` and returns `os.FileInfo`. Tests cover existing root file, nested files, directory, and subdirectory. `checkIfNonExistentObjectFailedToStat` expects `os.Stat` failure and validates a not-found error. Four negative tests cover missing files and directories at different depths.

## Control Flow

Existing-object tests stat a path and compare returned `Name` and `IsDir` values. Negative tests stat missing paths and call the package not-found validator.

## State and Persistence Behavior

The file only reads metadata from the seeded fixture hierarchy. It does not mutate local or remote state.

## Dependencies and Integration Points

It depends on standard `os.Stat`, setup paths, and fixture constants from the package harness. It complements list/read tests by validating metadata access under read-only and viewer-credential scenarios.

## Risks and Edge Cases

`statObject` logs a test error but still returns `file`, which may be nil if `os.Stat` fails; subsequent use could panic. Negative tests rely on substring matching for "no such file or directory". Directory semantics depend on implicit directory handling and seeded object prefixes.

## Test Signals

Passing indicates metadata lookup works for existing read-only objects and missing paths produce not-found errors. Failures suggest stat-cache, implicit-directory, permissions, or fixture setup regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/stat_object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/write_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/write_test.go

## Purpose

This file verifies that write and append attempts fail on read-only mounts for existing and non-existing files.

## Important APIs, Types, and Functions

`checkIfFileFailedToOpenForWrite` calls `operations.WriteFile` and validates read-only error. Tests cover existing files at root, directory, and subdirectory. `checkIfNonExistentFileFailedToOpenForWrite` expects a not-found error for writes to missing paths. `checkIfFileFailedToOpenForAppend` calls `operations.WriteFileInAppendMode` and validates read-only error. `checkIfNonExistentFileFailedToOpenForAppend` expects not-found for missing append targets.

## Control Flow

Each test constructs a mounted path, attempts write or append, and validates either read-only or not-found error depending on whether the target exists.

## State and Persistence Behavior

Expected behavior is no content change and no file creation. Existing fixture files should remain unchanged, and missing paths should remain absent.

## Dependencies and Integration Points

It depends on `operations.WriteFile`, `operations.WriteFileInAppendMode`, read-only and not-found validators, setup paths, and fixture constants. It is central to the read-only enforcement suite.

## Risks and Edge Cases

For non-existent write/append attempts, the expected error is not-found rather than read-only; this encodes current path resolution semantics. The tests do not re-read existing file content after failed writes, relying on errors as the main signal.

## Test Signals

Passing means existing writes/appends are rejected as read-only and missing writes/appends are rejected as not-found. Unexpected success indicates a serious mutation bug.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly/write_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly_creds/failure_during_file_sync_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly_creds/failure_during_file_sync_test.go

## Purpose

This suite validates behavior when credentials allow reading/listing but not object creation. It ensures failed file syncs do not leave phantom entries in directory listings.

## Important APIs, Types, and Functions

`readOnlyCredsTest` stores the mounted test directory path. `assertFailedFileNotInListing` reads the directory and requires it to be empty. `assertFileSyncFailsWithPermissionError` closes a file handle and requires a permission-denied error. `TestEmptyCreateFileFails_FailedFileNotInListing` and `TestNonEmptyCreateFileFails_FailedFileNotInListing` cover empty and non-empty create/sync failures. `TestReadOnlyTest` runs the suite.

## Control Flow

Each test opens a file with create/truncate flags. In zonal bucket runs, open itself is expected to fail with permission denied. In other runs, open can return a local file handle, and the permission failure is expected on close/sync; the non-empty test writes content before close. Both tests then list the directory and require no entries.

## State and Persistence Behavior

The test directory exists before credentials are reduced. Failed files may exist transiently in local write staging, but must not persist in GCS or listings after failure. The suite reads the mounted directory to verify no ghost state.

## Dependencies and Integration Points

It depends on the `readonly_creds` harness, `operations.WriteWithoutClose`, setup flags, and credential-mode execution using objectViewer permissions. It uses `testify` assertions for zonal-specific behavior.

## Risks and Edge Cases

Behavior differs between zonal and non-zonal buckets, so assertions branch on `setup.IsZonalBucketRun`. Permission errors are checked by substring. If local staging cleanup is asynchronous, immediate listing could be timing-sensitive, though the current tests do not retry.

## Test Signals

Passing means create/sync fails with permission denied and the failed file is absent from listings for both empty and non-empty writes. Failures indicate credential enforcement, staging cleanup, or listing consistency bugs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly_creds/failure_during_file_sync_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly_creds/readonly_creds_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/readonly_creds/readonly_creds_test.go

## Purpose

This harness runs readonly-credential tests under an objectViewer credential context, validating failed write/create behavior when the mount is not explicitly read-only but credentials prevent writes.

## Important APIs, Types, and Functions

Constants define the test directory, filename, content, and permission-denied substring. `env` stores storage client, context, config, and bucket type. `TestMain` handles config, environment, storage client lifecycle, GKE skip behavior, initial test directory creation, path rewriting, flag-set generation, credential-mode execution, and cleanup.

## Control Flow

`TestMain` parses flags, loads or synthesizes `ReadonlyCreds` config with implicit-dir variants, initializes environment and storage client, skips mounted-directory/GKE mode, creates the test directory before dropping privileges, prepares mount directories and flags, then calls `creds_tests.RunTestsForDifferentAuthMethods` with role `objectViewer`. It cleans the test prefix from GCS afterward.

## State and Persistence Behavior

The harness creates the GCS test directory while it still has full credentials, then runs tests under restricted credentials. It mutates package global `testEnv`, `mountDir`, and `rootDir`. Cleanup uses the original storage client after credential test execution.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, `creds_tests`, setup/test-suite helpers, and sibling suite tests. It is listed as non-parallel in the e2e runner because credential manipulation can affect shared bucket permissions.

## Risks and Edge Cases

Mounted-directory mode is skipped because the credential switching assumptions do not apply. Permission-denied behavior varies by bucket type and write path. Cleanup must run with sufficient credentials or failed test artifacts can remain.

## Test Signals

Harness success means the readonly-credential suite ran under objectViewer for compatible bucket types and cleaned its test prefix. Failures usually indicate IAM setup, credential generation, or permission semantics regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/readonly_creds/readonly_creds_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/release_version/release_version_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/release_version/release_version_test.go

## Purpose

This test validates the user-visible `gcsfuse --version` output format for release builds.

## Important APIs, Types, and Functions

`TestReleaseVersion` runs `exec.Command("gcsfuse", "--version")`, captures combined output, trims whitespace, and matches it against the regexp `^gcsfuse version (\d+\.\d+\.\d+) \(Go version (go.+)\)$`. It extracts and checks non-empty gcsfuse and Go versions.

## Control Flow

The test executes the binary, fails immediately if command execution fails, logs the output for debugging, applies the regexp, and reports detailed mismatch information if the shape is wrong.

## State and Persistence Behavior

No filesystem or bucket state is mutated by the test itself. It depends on the active `gcsfuse` binary in `PATH`, which is set up by package harness or external test environment.

## Dependencies and Integration Points

It uses standard `os/exec`, `regexp`, `strings`, and `testing`. It integrates with the release-version harness that prepares the test environment but does not mount a bucket.

## Risks and Edge Cases

The regexp requires three numeric semver components and exact text casing/parentheses. Pre-release/build metadata, distro suffixes, or alternate Go version formatting would fail. The test validates format, not that the version matches a release tag.

## Test Signals

Passing means the installed or built binary prints a release-style version line with both gcsfuse and Go versions. Failure is a packaging/build metadata or CLI output regression.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/release_version/release_version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/release_version/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/release_version/setup_test.go

## Purpose

This harness prepares the release-version test package. The package does not mount GCSFuse; it only needs an available `gcsfuse` binary.

## Important APIs, Types, and Functions

`TestMain` parses setup flags, loads or synthesizes `ReleaseVersion` config, skips mounted-directory mode, calls `setup.SetUpTestDirForTestBucket`, runs tests, and exits with the result.

## Control Flow

After config loading, any non-empty `GKEMountedDirectory` causes an immediate skip with exit code 0. Otherwise, setup prepares the test directory and binary environment, then `m.Run` executes `TestReleaseVersion`.

## State and Persistence Behavior

The harness may create standard integration-test temp directories through setup but creates no bucket objects and performs no mount/unmount. It relies on setup to make the correct binary discoverable.

## Dependencies and Integration Points

It depends on `setup` and `test_suite` helpers. It is included in e2e package arrays for flat/HNS/zonal runs but is independent of bucket type except for setup plumbing.

## Risks and Edge Cases

Skipping mounted-directory mode means release-version coverage is absent in environments that only provide an already-mounted directory. If setup does not put the intended binary first in `PATH`, the test may inspect a system-installed version instead.

## Test Signals

Harness success is simply execution of the version-format test in a non-mounted-directory environment. Failures point to binary setup or CLI output issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/release_version/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/move_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/move_dir_test.go

## Purpose

This file validates directory move semantics through GCSFuse, including moving populated and empty directories into non-existing, empty, and non-empty destinations.

## Important APIs, Types, and Functions

Constants define source/destination directory names, file names, expected content, and expected listing counts. `createSrcDirectoryWithObjectsForMoveDirTest` creates a source directory with one file and one subdirectory. `checkIfMovedDirectoryHasCorrectData` validates moved listing and file content. `checkIfSrcDirectoryGetsRemovedAfterMoveOperation` requires source removal. `createDestNonEmptyDirectoryForMoveTest` creates a destination with an existing subdirectory. `checkIfMovedEmptyDirectoryHasNoData` validates empty-directory moves.

## Control Flow

Each test creates a fresh package test directory, builds a source tree, optionally builds destination state, calls `operations.Move`, and validates destination shape plus source removal. Populated-source tests cover move-to-new-path, move-into-empty-directory, and move-into-non-empty-directory. Empty-source tests cover move into non-empty, empty, and non-existing destinations.

## State and Persistence Behavior

The tests create and move GCS-backed directories/objects through the mounted filesystem. Expected final state is source absence and destination presence with either preserved source contents or empty directory content. Existing destination children must remain unaffected.

## Dependencies and Integration Points

It depends on standard `os`, `path`, `operations` helpers for move/create/read/write, and setup test directories. It runs under the rename-dir-limit package harness across static, only-dir, and persistent mounting.

## Risks and Edge Cases

The listing assertions assume deterministic ordering. `log.Fatal` in helper validation exits the process on listing errors. The file focuses on successful move behavior and does not directly assert rename-dir-limit rejection; that is covered in `rename_dir_test.go`.

## Test Signals

Passing means directory moves preserve contents, retain existing destination entries, remove sources, and handle empty directories correctly. Failures indicate recursive rename/move, implicit-directory, or cleanup semantics bugs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/move_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/rename_dir_limit_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/rename_dir_limit_test.go

## Purpose

This is the harness for directory rename-limit integration tests. It configures `--rename-dir-limit=3` scenarios for flat buckets and default behavior for HNS/zonal buckets, then runs tests under static, only-dir, and persistent mounts.

## Important APIs, Types, and Functions

Constants define package test directory names, directory fixture names, rename targets, temp-file prefixes, and only-dir prefix. Package globals store `storageClient` and `ctx`. `TestMain` controls config loading, storage setup, mounted-directory mode, flag-set generation, mount-mode execution, and process exit.

## Control Flow

`TestMain` parses flags, loads or creates `RenameDirLimit` config, initializes environment and storage client, delegates mounted-directory mode if supplied, builds compatible flags, prepares the test bucket directory, then runs static mounting. If successful, it runs only-dir mounting and then persistent mounting.

## State and Persistence Behavior

The harness creates bucket-backed test directories and mutates package globals. Only-dir mounting sets a dedicated prefix. Storage client state is used by sibling tests to detect hierarchical bucket type and skip flat-only limit failures.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, static/only-dir/persistent mounting helpers, setup/test-suite helpers, and sibling rename/move tests. It integrates with e2e mounted-directory scripts that explicitly run rename-dir-limit under several flag combinations.

## Risks and Edge Cases

Compatibility differs by bucket type: flat buckets use explicit rename-dir-limit flags, while HNS/zonal buckets use default config because native hierarchical operations change semantics. Multiple mount modes can leave state that affects later modes if cleanup is incomplete.

## Test Signals

Harness success across all mount modes indicates directory rename and move semantics are stable for configured bucket type. Failures may reflect mount option translation, bucket capability differences, or recursive operation regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/rename_dir_limit_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/rename_dir_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/rename_dir_test.go

## Purpose

This file validates `--rename-dir-limit=3` behavior and destination-directory rename semantics. It checks success at or below the object limit, failure above the limit for flat buckets, and behavior when the destination directory already exists.

## Important APIs, Types, and Functions

Tests create directory trees using `operations.CreateDirectoryWithNFiles` and rename using `os.Rename` or Python `os.rename` via `exec.Command`. Cases cover three files, two files, four files, two files plus empty directory, two files plus non-empty directory, existing empty destination, and existing non-empty destination. `setup.ResolveIsHierarchicalBucket` skips flat-limit failure expectations on hierarchical buckets.

## Control Flow

Success cases create a source directory whose object count is at or below the limit, remove any stale destination, call `os.Rename`, and expect no error. Failure cases create more than the limit and expect `os.Rename` to fail unless the bucket is hierarchical. Existing-destination cases use Python because Go's `os.Rename` wrapper does not support the exact directory overwrite behavior being tested; the non-empty destination case expects `ENOTEMPTY`.

## State and Persistence Behavior

The tests create and rename mounted directories backed by GCS objects. Successful renames remove old paths and populate new paths. Failure cases should leave source data intact, though not all failure tests explicitly revalidate source preservation.

## Dependencies and Integration Points

It depends on setup constants/globals from the harness, operations helpers, standard `os/exec/syscall`, and `testify/assert`. It is coupled to flat bucket rename emulation and HNS native rename semantics.

## Risks and Edge Cases

The comment for the four-file test says "two, greater than limit" but the code creates four files. Object-count semantics around empty directories differ between flat and hierarchical buckets. Python command construction embeds paths directly into source strings; unusual quotes in paths would be unsafe, though generated test paths are controlled. Existing empty-destination behavior is platform/FUSE specific.

## Test Signals

Passing confirms limit boundary behavior, over-limit rejection for flat buckets, source-to-existing-empty replacement behavior, and `ENOTEMPTY` for existing non-empty destinations. Failures indicate rename limit counting, recursive rename, or destination conflict handling regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/rename_dir_limit/rename_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/requester_pays_bucket/operations_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/requester_pays_bucket/operations_test.go

## Purpose

This suite verifies basic directory and file operations on a requester-pays bucket mounted with a billing project and key file.

## Important APIs, Types, and Functions

`operationTests` is a `testify/suite` suite. `SetupSuite` creates the test directory under the mount, and `TearDownSuite` removes it. `TestDirOperations` creates, stats, renames, stats, and removes a directory. `TestFileOperations` creates a file with content, stats, renames, stats, and removes it.

## Control Flow

The directory test first asserts non-existence, creates a directory, verifies it is a directory, renames it, verifies old path absence and new path presence, removes it, and verifies absence. The file test follows the same lifecycle for a file created with random content.

## State and Persistence Behavior

The suite creates temporary objects under `RequesterPaysBucketTests` in the requester-pays bucket and removes them in test and suite flow. All operations should be billed to the configured billing project.

## Dependencies and Integration Points

It depends on standard `os`/`io/fs`, `filepath`, operations file creation helper, setup random string generation and permissions, and `testify` suite/assertions. It is mounted and configured by `setup_test.go`.

## Risks and Edge Cases

The suite validates functional operations but does not directly inspect billing attribution; missing billing project usually manifests as permission/billing errors. Random names avoid collisions. Cleanup uses `os.RemoveAll` through the requester-pays mount, so cleanup can fail if billing or credentials regress.

## Test Signals

Passing means create/stat/rename/delete work for files and directories on requester-pays buckets with the configured billing project and credentials. Failures often reveal missing `--billing-project`, bad key file, requester-pays enablement, or operation regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/requester_pays_bucket/operations_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/requester_pays_bucket/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/requester_pays_bucket/setup_test.go

## Purpose

This harness configures and runs requester-pays bucket tests. It enables requester-pays on the bucket when needed, injects billing project and service-account key flags, and runs tests under static and only-dir mounting.

## Important APIs, Types, and Functions

Constants define test prefixes, service account name, Secret Manager credential name, and target billing project. `env` stores test directory, storage client, context, and bucket name. `TestMain` is the full setup/teardown orchestrator.

## Control Flow

`TestMain` rejects zonal buckets, loads or synthesizes config, replaces `${BILLING_PROJECT}` and `${KEY_FILE}` placeholders in non-GKE mode, creates a temporary service-account key with `creds_tests.CreateCredentialsForSA`, extracts the billing project from flags, sets it globally, creates the storage client, enables requester-pays if not already enabled, handles mounted-directory mode, builds flag sets, prepares the bucket test directory, runs static mounting, then only-dir mounting, saves logs on failure, cleans the test prefix, and disables requester-pays if this run enabled it.

## State and Persistence Behavior

The harness mutates bucket-level requester-pays configuration and may create a temporary key file on local disk. It records whether requester-pays was already enabled to avoid disabling a pre-existing state. It creates/removes GCS test prefixes. Billing project is stored in setup global state for clients and helpers.

## Dependencies and Integration Points

It depends on Cloud Storage, credential helpers, static/only-dir mounting, setup/test-suite helpers, and client helpers for enabling/disabling requester-pays. It integrates with e2e scripts that run requester-pays scenarios separately.

## Risks and Edge Cases

Requester-pays is a bucket-level setting, so failed cleanup can leave billing behavior changed. The harness requires specific service account, secret, IAM roles, and billing project. Placeholder replacement and billing-project extraction are string-based. Zonal buckets are unsupported and fail fast.

## Test Signals

Success means the bucket was mounted with billing credentials and operations passed in static and only-dir modes. Failures usually point to IAM, Secret Manager, billing project, requester-pays enablement, or mount flag substitution issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/requester_pays_bucket/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/resource_usage.sh -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/resource_usage.sh

## Purpose

`resource_usage.sh` collects and prints coarse CPU, memory, and disk usage during long integration test runs. It supports a collection mode that writes samples to a file and a print mode that renders text graphs from that file.

## Important APIs, Types, and Functions

The script uses `set -euo pipefail`, constants for 10-second interval and 3-hour duration, and commands `COLLECT` and `PRINT`. `usage` prints help. `get_cpu_usage` parses `top`, `get_mem_usage` parses `free`, and `get_disk_usage` parses `df -P /`. `collect_all_metric` writes a header and sample rows. `print_each_metric` reads columns into an associative array and prints vertical ASCII graphs. A trap exits cleanly on SIGINT/SIGTERM.

## Control Flow

The script validates exactly two arguments, records command and file path, installs the signal trap, and dispatches to collect or print. Collection loops until Bash `SECONDS` reaches the duration, appending `CPU MEM DISK` samples. Print reads the file header, groups values by metric, computes a capped graph ceiling, and prints one graph per resource.

## State and Persistence Behavior

Collection overwrites the target file header and appends samples. Print mode reads the target file but does not modify it. The script depends on process runtime through `SECONDS` and host system commands.

## Dependencies and Integration Points

It depends on Bash, `top`, `free`, `df`, `awk`, `tail`, and basic shell builtins. It is intended for Kokoro/VM integration runs with a 3-hour timeout.

## Risks and Edge Cases

Parsing `top` is locale/platform dependent; the script expects `%Cpu` and idle in field 8. `print_each_metric` assumes well-formed rows with all columns. Under `set -u`, missing associative array entries or empty files can fail. Disk usage is only root filesystem usage, not necessarily cache or mount-specific usage.

## Test Signals

Useful signals are a file beginning with `CPU MEM DISK`, sample rows every 10 seconds, and printable graphs for each metric. Failures indicate missing host utilities, format drift, or malformed sample files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/resource_usage.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/run_benchmarking_tests.sh -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/run_benchmarking_tests.sh

## Purpose

This short script documents and runs the benchmarking integration test package with a fixed bucket and benchmark iteration count.

## Important APIs, Types, and Functions

It invokes `GODEBUG=asyncpreemptoff=1 go test ./tools/integration_tests/benchmarking/... -bench=. -benchtime=5x --integrationTest -v --testbucket=princer-empty-bucket`.

## Control Flow

There is no argument parsing or function dispatch. Running the script immediately starts the benchmark package with all benchmarks enabled and each benchmark run five times.

## State and Persistence Behavior

The script does not create explicit state itself, but the benchmark package will mount/use the hard-coded bucket and may create objects depending on benchmark implementation. It relies on the current environment for credentials and GCSFuse binary selection.

## Dependencies and Integration Points

It depends on Bash, Go tooling, the integration test benchmark package, and access to the hard-coded bucket. `GODEBUG=asyncpreemptoff=1` aligns with other integration runners for timing stability.

## Risks and Edge Cases

The hard-coded bucket makes the script environment-specific. There is no `set -e`, no usage text, and no way to pass bucket, timeout, or installed-package flags. It is best treated as an example rather than the main CI harness.

## Test Signals

Benchmark output from `go test` is the primary signal. Failures likely indicate missing credentials, unavailable bucket, package build failures, or benchmark regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/run_benchmarking_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/run_e2e_tests.sh -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/run_e2e_tests.sh

## Purpose

`run_e2e_tests.sh` is the main end-to-end integration runner for GCSFuse. It provisions buckets, optionally builds GCSFuse once, installs dependencies, runs integration packages in parallel and non-parallel groups for flat/HNS/zonal/TPC/emulator scenarios, captures logs, and cleans up buckets and build artifacts.

## Important APIs, Types, and Functions

Top-level arguments control installed-package testing, skipping non-essential tests, bucket location, TPC endpoint testing, presubmit mode, zonal bucket mode, and whether the script builds binaries. Arrays define parallel and non-parallel package groups for normal and zonal buckets. Key functions include `build_gcsfuse_once`, `cleanup_gcsfuse_once`, `delete_buckets_listed_in_file`, `upgrade_gcloud_version`, `install_packages`, bucket creation helpers, `run_parallel_tests`, `run_non_parallel_tests`, `print_test_logs`, scenario runners for flat/HNS/zonal/TPC/emulator, and `main`.

## Control Flow

The script validates arguments and bucket-location constraints, adjusts timeout and flags for short/presubmit runs, optionally builds gcsfuse into a temp directory and passes `--gcsfuse_prebuilt_dir`, then chooses zonal-only or normal flat/HNS execution. Flat and HNS paths create separate buckets for parallel and non-parallel package groups. Parallel packages run in background with per-package log files and PID tracking; non-parallel packages run sequentially because they may alter bucket permissions or shared state. On failure, logs are printed. The exit trap cleans built binaries and deletes all buckets listed in the generated bucket file.

## State and Persistence Behavior

The script creates temporary bucket-name and log-list files, multiple GCS buckets, optional HNS/zonal bucket resources, temporary build directories, and per-package logs under `/tmp`. It installs or upgrades system packages and modifies `PATH`/`CLOUDSDK_PYTHON`. Cleanup is trap-based and best-effort for buckets.

## Dependencies and Integration Points

It depends on Bash, `gcloud`, Go, Python, apt packages, project-specific perfmetrics install scripts, `tools/build_gcsfuse`, and every package under `tools/integration_tests`. It integrates with bucket projects `gcs-fuse-test-ml` and `gcs-fuse-test`, HNS and zonal bucket creation, TPC endpoint tests, and emulator tests.

## Risks and Edge Cases

The script has several shell robustness risks: early use of `$4` before checking argument count, a stray quote in `upgrade_gcloud_version`, global variables shared across functions, and extensive unquoted expansions. Bucket cleanup is critical because it creates real cloud resources. Parallel package execution can mask shared-resource conflicts if a package is incorrectly classified. Hard-coded projects and locations require CI-specific permissions.

## Test Signals

Primary signals are package-level pass/fail logs, final exit code, and printed logs on failure. Strong success means flat/HNS or zonal bucket groups complete, all created buckets are removed by the trap, and optional built binaries are cleaned.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/run_e2e_tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/run_tests_mounted_directory.sh -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/run_tests_mounted_directory.sh

## Purpose

This script runs a broad integration-test matrix against an already provided mount directory. It repeatedly mounts and unmounts a supplied bucket with different GCSFuse flags, then invokes targeted `go test` packages with `--mountedDirectory` and `--testbucket`.

## Important APIs, Types, and Functions

Inputs are test bucket, mount directory, and optional zonal flag. It exports `CGO_ENABLED=0` and uses `ZONAL_BUCKET_ARG` for zonal runs. Helper functions include `read_cache_test_setup`, `cleanup_test_environment`, `generate_config_file`, `run_read_cache_test`, and `run_chunk_cache_test` for the read-cache matrix. The rest of the script is a sequential set of `gcsfuse` or `mount.gcsfuse`, `go test`, and `sudo umount` blocks.

## Control Flow

The script validates the optional zonal argument, then runs package groups in a fixed order: operations, readonly, rename-dir-limit, implicit/explicit dirs, list/read/write large files, gzip/local-file/read-cache variants, managed folders, gRPC core tests, concurrent operations, benchmarking, kernel list cache, stale handle, streaming writes, inactive stream timeout, cloud profiler, readdirplus, dentry cache, buffered read, requester-pays, and flag optimizations. For read-cache, it generates config files and mounts for specific test cases and cache settings. Each scenario unmounts before moving to the next.

## State and Persistence Behavior

The script writes temporary config files under `/tmp`, log directories under `/tmp`, cache directories under `/tmp`, and repeatedly mutates the supplied mount directory state. It creates and deletes bucket content indirectly through tests. It does not install a global cleanup trap for every mount, so an early failure can leave the bucket mounted.

## Dependencies and Integration Points

It depends on `gcsfuse`, `mount.gcsfuse`, `go test`, `sudo umount`, Bash, and all integration packages it invokes. It is the mounted-directory counterpart to per-package harnesses and e2e CI scripts.

## Risks and Edge Cases

The script lacks `set -euo pipefail`, so failures may not stop subsequent scenarios unless individual commands exit the shell in the execution environment. Many variables are unquoted. It assumes sudo umount works and the mount directory is reusable after every scenario. Because it is long and sequential, one stale mount or leftover config/cache path can affect many later tests.

## Test Signals

Passing signal is successful completion of the entire sequential matrix without lingering mounts. Individual `go test` output identifies package-level failures. Readdirplus, read-cache, buffered-read, requester-pays, and flag-optimization sections provide targeted coverage for the files in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/run_tests_mounted_directory.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/shared_chunk_cache/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/shared_chunk_cache/setup_test.go

## Purpose

This harness prepares tests for the experimental shared chunk cache. It configures primary and secondary mount directories so two mounts can share the same chunk-cache directory.

## Important APIs, Types, and Functions

Constants define `testDirName` and `GKETempDir`. `env` stores storage client, context, config, and bucket type. `TestMain` loads config, synthesizes a default shared-cache dual-mount config if absent, initializes storage, handles GKE mounted-directory mode, creates a secondary mount directory for GCE mode, runs tests, and cleans the GCS test prefix.

## Control Flow

`TestMain` parses flags, configures `SharedChunkCache` with primary and secondary flags that both enable shared chunk cache and point at `/gcsfuse-tmp/shared-cache`, creates the storage client, handles mounted-directory mode by assigning primary/secondary mounted directories, otherwise prepares a test bucket directory, rewrites temp paths, creates a secondary local mount directory under the test temp root, runs `m.Run`, cleans GCS, and exits.

## State and Persistence Behavior

The harness creates local mount directories and a shared cache directory path, plus bucket objects under `SharedChunkCacheTest`. It stores mutable global `testEnv`. The actual mounting/unmounting is done by the suite in `shared_chunk_cache_test.go`.

## Dependencies and Integration Points

It depends on Cloud Storage, integration `client`, setup/test-suite helpers, and the shared chunk cache suite. It relies on `ConfigItem.SecondaryFlags` and `GCSFuseMountedDirectorySecondary`, which are specific to dual-mount scenarios.

## Risks and Edge Cases

GKE mode assumes both primary and secondary mounted directories are already available. Non-GKE mode creates a secondary mount dir but does not remove it explicitly here. Path rewriting must update both primary and secondary cache-dir flags. The feature is experimental, so flag names and cache layout may change.

## Test Signals

Harness success means dual-mount suite execution receives two mount directories and common cache flags. Failures typically indicate missing secondary mount config, storage setup, or path rewriting issues.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/shared_chunk_cache/setup_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/shared_chunk_cache/shared_chunk_cache_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/shared_chunk_cache/shared_chunk_cache_test.go

## Purpose

This suite validates experimental shared chunk cache behavior for one or two GCSFuse mounts. It checks that a partial read caches a full chunk, that a second mount can reuse the cached chunk without rewriting cache files, and that a single mount gets cache hits on repeated reads.

## Important APIs, Types, and Functions

`mountPoint` records root, mount, test directory, and log paths. `BaseSuite` stores primary/secondary flags, mount points, and shared cache directory. `SharedChunkCacheTestSuite` embeds it. `SetupTest` prepares cache state and mounts primary/secondary GCSFuse instances in GCE mode or records pre-mounted GKE paths. `TearDownTest` saves logs on failure, unmounts/cleans mounts, and removes the shared cache directory. Helpers include `setupTestDir`, `mountGcsfuse`, `unmountAndCleanupMount`, `createTestFile`, `getCachedChunkCount`, and `getCacheFileModTimes`. Tests are `TestCacheMiss`, `TestCacheHit`, and `TestCacheHitSingleMount`. `RunTests` expands config flags into suites.

## Control Flow

Each test removes the shared cache directory first. `TestCacheMiss` creates a 30 MiB file, reads 2 MiB at offset 10 MiB, and expects exactly one `.bin` chunk file. `TestCacheHit` populates cache from the primary mount, records cache file mod times, stats the file on the secondary mount to warm metadata, reads the same chunk from secondary, compares content, requires the cache count to remain unchanged, and requires cache file mod times to remain unchanged. `TestCacheHitSingleMount` performs the same no-modification check for two reads through one mount.

## State and Persistence Behavior

State spans two mounted directories, GCS test objects, local shared cache files under `gcsfuse-shared-chunk-cache`, and per-mount log files. Cache entries are discovered as `.bin` files, and file modification times are used as a proxy for cache reuse versus re-download.

## Dependencies and Integration Points

It depends on GCSFuse internal cache size constants, static mounting helpers, operations read/create helpers, setup cleanup/log helpers, `filepath.WalkDir`, and `testify/suite/require`. It integrates with dual-mount config from `setup_test.go`.

## Risks and Edge Cases

The cache-hit proof relies on unchanged file modification times, which can be coarse on some filesystems. The helper `mountGcsfuse` accepts `mountPoint` by value, so assignments to `mnt.testDirPath` inside the helper do not update the caller's struct; however `setupTestDir` already set the expected path before mounting. GKE mode requires pre-mounted secondary directory when secondary flags exist. Cache layout changes away from `.bin` files would break counters.

## Test Signals

Passing signal is one cached chunk after a partial read, identical bytes from primary and secondary reads, unchanged cache count, and unchanged cache file mod times on cache hits. Failures indicate shared-cache population, cross-mount reuse, cache keying, or cleanup regressions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/shared_chunk_cache/shared_chunk_cache_test.go -->
