# subset-b-009582 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/name.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/name.go

Purpose: defines the inode `Name` value object that translates between local filesystem names and GCS object names. It is a small immutable struct with `bucketName` and `objectName`; an empty `bucketName` means a single mounted bucket, while a non-empty bucket name represents multi-bucket mounting where local paths are prefixed with the bucket directory.

Important APIs: `NewRootName`, `NewDirName`, `NewFileName`, and `NewDescendantName` construct names for bucket roots, directory marker-style object names, files, and descendants. `IsBucketRoot`, `IsDir`, `IsFile`, `GcsObjectName`, `LocalName`, `String`, `IsDirectChildOf`, and `ParentName` provide interpretation and navigation. Directories are represented by empty object name for roots or by trailing slash for non-root directories; files are anything else. `NewDirName` and `NewFileName` panic on invalid child construction, such as adding children under files or using empty child names.

Control flow and state: the code is pure string manipulation with no external persistence. `IsDirectChildOf` first rejects cross-bucket and non-prefix cases, then strips the parent prefix and ensures the remaining path segment does not contain another slash after optional trailing slash removal. `ParentName` trims a trailing slash, locates the last slash, and returns either bucket root or the slash-terminated parent directory object name; bucket roots return an error.

Dependencies and integration: it depends only on `errors`, `fmt`, and `strings`, but it is foundational for inode creation, lookup, directory listing, recursive operations, and GCS object naming throughout `internal/fs/inode`.

Risks: invariants are convention-based. Calling `IsDir` with a malformed `Name{objectName:""}` is safe because bucket root is checked first, but hand-built `Name` values that omit trailing slashes for directories will be interpreted as files. `NewDescendantName` does not verify that the descendant name is actually under the ancestor; callers must enforce that relationship.

Test signals: `name_test.go` covers bucket-prefixed and unprefixed mounts, directory/file classification, local and GCS name formatting, direct-child relationships, map-key comparability, and parent resolution including root error behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/name.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/name_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/name_test.go

Purpose: verifies the `inode.Name` contract for root, directory, file, descendant, map-key, and parent-name behavior. It is an external package test (`inode_test`) and therefore exercises the exported API surface rather than private fields.

Important tests: `TestName` runs the same scenarios for single-bucket mounts (`bucketName == ""`) and multi-bucket local names (`bucketx/`). It constructs root, nested directories, root files, nested files, and a descendant name, then checks `IsBucketRoot`, `IsDir`, `IsFile`, `GcsObjectName`, `LocalName`, and `IsDirectChildOf`. `TestNameAsMapKey` confirms that `Name` is comparable and can safely be used as a Go map key. `TestParentName` covers parent resolution for directory and file names at several depths. `TestParentNameReturnsErrorOnBucketRoot` asserts the explicit root error.

Control flow and state: the tests are table-like but written inline, with assertions repeated for both bucket modes. No filesystem or GCS state is created; all behavior is deterministic value semantics. The parent-name checks compare both GCS object names and local names, which catches bucket-prefix mistakes as well as object-name mistakes.

Dependencies and integration: uses `github.com/googlecloudplatform/gcsfuse/v3/internal/fs/inode` plus ogletest/oglematchers assertions. These tests protect callers in directory lookup, rename, symlink, and listing code from path-shape regressions.

Risks and coverage gaps: the tests do not assert the panic paths in `NewDirName` or `NewFileName`, nor the weak validation behavior of `NewDescendantName`. They also do not exercise child names that already contain slashes except by passing `"child/"` in a separate recursive-cancellation test through `NewDirName`, which the constructor normalizes only by ensuring a final slash.

Test signals: the strongest signal is dual-mode coverage of local path prefixing. Any change that alters trailing-slash directory representation, direct-child detection, or parent trimming will fail here.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/name_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/recursive_cancellation_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/recursive_cancellation_test.go

Purpose: verifies that cancelling prefetch work at a directory inode propagates to child and grandchild directory contexts. This protects metadata prefetch behavior from leaking goroutines or continuing recursive work after a parent directory is invalidated or torn down.

Important APIs and helpers: the `RecursiveCancellationTest` suite builds a fake GCS bucket, wraps it in `gcsx.NewSyncerBucket`, and prepares a `cfg.Config` with metadata prefetch enabled and metadata cache sizes/TTL set. `createDirInode` calls `NewDirInode` with a parent context, standard directory attributes, implicit directories enabled, a one-minute TTL, a weighted semaphore, and the suite config, then casts the result to `*dirInode` so it can inspect private `Context()` and cancellation behavior.

Control flow and state: `SetupTest` initializes a simulated clock, fake bucket, syncer bucket, and config. `TestRecursiveCancellation` creates a root dir with no parent context, a child using `rootDir.Context()`, and a grandchild using `childDir.Context()`. It first asserts all contexts are active, then calls `rootDir.CancelSubdirectoryPrefetches()` and expects `context.Canceled` on all three contexts.

Dependencies and integration: this is an internal package test, so it reaches `dirInode` internals. It integrates with `cfg`, `gcsx`, fake storage, `fuseops`, `timeutil`, and `golang.org/x/sync/semaphore`. It is coupled to the directory inode context tree used by metadata prefetch.

Risks: the test only exercises a simple linear tree and does not start actual prefetch goroutines or validate semaphore release. It assumes `NewDirInode` returns `*dirInode` for this configuration. It also uses repeated `NewDirName(..., "child/")` style inputs, relying on constructor behavior that accepts already slash-terminated directory names.

Test signals: failures indicate broken recursive cancellation propagation, a changed context-parenting model, or cancellation no longer reaching descendants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/recursive_cancellation_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/symlink.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/symlink.go

Purpose: implements symlink inode support backed by GCS objects. It supports legacy gcsfuse symlinks where the target is stored in custom metadata, and newer standard symlinks where metadata marks the object as a symlink and the object content stores the target path.

Important APIs/types: `SymlinkMetadataKey` is the legacy metadata key, while `StandardSymlinkMetadataKey` is the reserved standard key. `IsSymlink` recognizes any legacy key presence and only recognizes the standard key when its value is `"true"`. `SymlinkInode` implements `Inode` with immutable id, `Name`, `SyncerBucket`, source `Generation`, attributes, target, and metadata, plus mutex-protected lookup count. `NewSymlinkInode` initializes inode attributes from `gcs.MinObject`, records source generation/size/metageneration, initializes lookup count, and resolves the target before returning.

Control flow and state: `resolveSymlinkTarget` prioritizes standard symlinks by opening a generation-pinned reader and reading the object body; legacy symlinks return metadata directly. `openReader` calls `SyncerBucket.NewReaderWithReadHandle` with the object name and source generation. Not-found on that exact generation is wrapped as `gcsfuse_errors.FileClobberedError`, preserving stale-handle semantics. `Source` reconstructs a `gcs.MinObject` from inode state, and `UpdateSize` only mutates generation size metadata, not the target string.

Dependencies and integration: integrates with GCS read APIs, `gcsx.SyncerBucket`, FUSE inode attributes, lookup-count lifecycle, logger warnings on close failures, and the broader inode interface used by filesystem operations such as `ReadSymlink`, lookup, and unlink.

Risks: standard symlink target resolution requires a GCS read during inode construction, so missing or clobbered objects fail creation. Metadata is retained by map reference rather than deep copy. Legacy and standard metadata conflict behavior is fixed by priority: standard `"true"` wins over legacy target. `Attributes` ignores the clobbered-check flag and returns cached attrs.

Test signals: internal and external symlink tests cover detection, attribute/source reporting, size update, legacy and standard target resolution, generation clobbering, read errors, and invalid metadata errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/symlink.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/symlink_internal_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/symlink_internal_test.go

Purpose: internal-package tests for private symlink inode helpers, especially generation-pinned reading and target resolution. The tests validate behavior that external symlink tests cannot reach, such as `openReader` and `resolveSymlinkTarget`.

Important fixtures: `SymlinkInternalTest` owns a background context, fake bucket, and simulated clock. `createSymlinkInode` creates a fake GCS object, converts it to `MinObject`, installs either legacy target metadata or standard symlink metadata plus body content, builds a `gcsx.SyncerBucket`, and calls `NewSymlinkInode`.

Control flow and state: `TestOpenReader` reads standard symlink content through `openReader`. `TestOpenReader_Clobbered` creates a symlink inode, rewrites the same object to change generation, and expects `openReader` to return an error wrapping `FileClobberedError`. `TestResolveSymlinkTarget_Standard` and `_Legacy` validate the two storage formats; `_Clobbered` verifies standard resolution maps stale generations to clobbered errors. Constructor tests cover legacy success, standard success, read error for a missing standard object, and invalid metadata returning `symlink target could not be resolved`.

Dependencies and integration: uses fake storage, `storageutil.CreateObject`, `storageutil.ConvertObjToMinObject`, `gcsx.NewSyncerBucket`, `fuseops`, and `gcsfuse_errors`. It is tightly integrated with GCS generation semantics and the symlink inode constructor path.

Risks: the helper mutates `MinObject.Metadata` after object creation rather than patching bucket metadata, so it tests inode construction from object records rather than a complete storage metadata update path. The tests do not assert reader close warning behavior or precedence when both legacy and standard keys are present.

Test signals: these tests are the main guard for stale-generation safety in symlink target reads and for maintaining both legacy and standard symlink compatibility.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/symlink_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/symlink_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/symlink_test.go

Purpose: external-package tests for the exported symlink inode surface and symlink detection helper. It verifies compatibility metadata, public attributes, size update behavior, and source-object reconstruction.

Important tests: `TestIsSymLinkWhenMetadataKeyIsPresent`, `TestIsSymLinkWhenMetadataKeyIsNotPresent`, `TestIsSymLinkWhenStandardMetadataKeyIsPresent`, `TestIsSymLinkWhenStandardMetadataKeyIsFalse`, and `TestIsSymLinkForNilObject` cover `IsSymlink` recognition rules. `TestAttributes` builds a legacy symlink inode and asserts stable attributes for both `clobberedCheck` values, including `Nlink`, `Uid`, `Gid`, and `Mode`. `TestUpdateSize` checks that `UpdateSize` changes `SourceGeneration().Size`. `TestSource` creates a standard symlink object, builds an inode, and verifies `Source()` mirrors name, generation, metageneration, size, metadata, and update time.

Control flow and state: setup creates a fake bucket wrapped in `gcsx.SyncerBucket`. Tests generally construct `gcs.MinObject` records directly for legacy symlinks and use `storageutil.CreateObject` for the standard symlink source test. State is confined to fake bucket objects and inode-local cached metadata.

Dependencies and integration: uses ogletest, fake storage, `storageutil`, `fuseops`, and the public `inode` package. It complements `symlink_internal_test.go` by checking the package boundary expected by filesystem code.

Risks and coverage gaps: the external tests still expect `CreateLink` legacy metadata semantics elsewhere in `local_modifications_test.go`, while `symlink.go` now supports standard content-backed symlinks. This mixed model may be intentional for backward compatibility but is a migration-sensitive area. These tests do not validate `Target()` for standard symlinks except indirectly through constructor success in other tests.

Test signals: failures identify breaks in public symlink detection semantics, inode attribute caching, generation size bookkeeping, or source-object reconstruction.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/symlink_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_inifinite_ttl_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_inifinite_ttl_test.go

Purpose: tests kernel directory-list caching when `KernelListCacheTtlSecs` is `-1`, meaning the kernel list cache should not expire by time. The filename contains the spelling `inifinite`, but the suite name and config describe infinite TTL behavior.

Important APIs/types: `SkipTestForUnsupportedKernelVersion` skips suites when `common.IsKLCacheEvictionUnSupported` reports an unsupported kernel. `KernelListCacheTestWithInfiniteTtl` embeds `fsTest` and `KernelListCacheTestCommon`. `SetupSuite` enables implicit directories, sets kernel list cache TTL to `-1`, disables metadata cache TTL, sets rename dir limit, and uses noop metrics/tracing.

Control flow and state: the tests inherit common setup that creates `explicitDir/`, two explicit files, and implicit directory files, then sets `cacheClock`. `TestKernelListCache_AlwaysCacheHit` lists `explicitDir`, creates `file3.txt` out-of-band in the bucket, advances the cache clock by five years, and expects the second listing to still return only the first two files. `TestKernelListCache_RemoveDirAfterListIsCachedWorks` verifies `os.RemoveAll` can delete a cached directory and future reads fail. `TestKernelListCache_RemoveDirAfterListCacheInvalidatesCache` removes a cached directory, recreates content under the same prefix, and expects a fresh listing with only the new file.

Dependencies and integration: uses the mounted filesystem (`os.Open`, `Readdirnames`, `os.RemoveAll`, `os.ReadDir`) plus fake bucket mutation through shared helpers. It is coupled to kernel invalidation behavior and the FUSE notifier/list-cache implementation.

Risks: cache assertions depend on directory entry ordering and on clock-controlled invalidation. The test must be skipped on unsupported kernels, so CI coverage can vary by environment.

Test signals: confirms infinite TTL preserves stale listings until explicit filesystem mutations invalidate the cache.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_inifinite_ttl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_test.go

Purpose: base and positive-TTL test suite for the kernel list cache feature, where repeated directory listings may be served from the kernel page cache unless TTL expiry or invalidation forces gcsfuse to serve a fresh listing.

Important APIs/types: `KernelListCacheTestCommon` provides setup/teardown, object creation helpers, and `getFilesAndDirStructureObjects`. `KernelListCacheTestWithPositiveTtl` configures `KernelListCacheTtlSecs` to `1000`, disables metadata cache TTL, enables implicit dirs, and installs noop metrics/tracing. The common object structure includes explicit and implicit directories.

Control flow and state: cache-hit tests list a directory, mutate the bucket by adding `file3.txt`, advance the simulated `cacheClock` within TTL, and expect the old two-entry listing. Cache-miss tests perform the same mutation but advance beyond TTL and expect three entries. `TestKernelListCache_CacheHitAfterInvalidation` demonstrates that after a TTL-driven refresh, a later within-TTL read is cached again. Implicit directory variants repeat the semantics for prefix-inferred directories.

Concurrency tests: `Test_Parallel_OpenDirAndLookUpInode`, `Test_Concurrent_ReadDir`, `Test_Parallel_ReadDirAndFileOperations`, and `Test_Parallel_ReadDirAndDirOperations` run goroutines against the same directory, mixing opens/stats/readdirs with create/rename/delete of files and directories. They use five-second timeouts to detect deadlocks or race conditions.

Dependencies and integration: relies on FUSE mount behavior via `os`, fake bucket helpers, shared `cacheClock`, `cfg`, `metrics`, and `tracing`. The tests integrate with kernel-level cache invalidation and gcsfuse directory operation locking.

Risks: listing order is assumed. Timeout-based deadlock tests can be environment-sensitive. The signal for kernel cache behavior is indirect: unchanged listing after bucket mutation means the second read did not reach gcsfuse.

Test signals: protects positive TTL semantics, implicit-dir cache behavior, post-expiry refresh, and concurrent directory operation liveness.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_zero_ttl_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_zero_ttl_test.go

Purpose: tests kernel list cache behavior when `KernelListCacheTtlSecs` is `0`, meaning directory listings should always be served fresh from gcsfuse rather than retained in the kernel list cache.

Important APIs/types: `KernelListCacheTestWithZeroTtl` embeds the common kernel-list-cache fixture and configures implicit directories, zero kernel-list-cache TTL, zero metadata-cache TTL, rename dir limit, and noop metrics/tracing. The suite uses the same `SkipTestForUnsupportedKernelVersion` guard as other kernel list cache suites.

Control flow and state: `TestKernelListCache_AlwaysCacheMiss` opens and lists `explicitDir`, verifies the initial two files, closes the directory handle, creates `explicitDir/file3.txt` directly in the bucket, and lists again. With zero TTL, the second listing should include all three files, proving gcsfuse handled the read instead of the kernel serving the old cached entries.

Dependencies and integration: depends on shared helpers from `kernel_list_cache_test.go`, the mounted filesystem, fake bucket object creation/deletion, `cfg`, `metrics`, `tracing`, and FUSE/kernel support for list-cache invalidation. Metadata cache TTL is disabled to isolate kernel list cache behavior.

Risks: like the positive and infinite TTL suites, it depends on deterministic entry order and an environment where the list cache feature is supported. It covers explicit directories only; implicit zero-TTL semantics are indirectly covered by the positive-TTL file’s implicit miss test.

Test signals: a failure means zero TTL is allowing stale kernel listings, gcsfuse is not invalidating promptly, or the test environment’s kernel cache semantics differ from expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/kernel_list_cache_zero_ttl_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/local_file_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/local_file_test.go

Purpose: integration-style tests for newly created local files when `Write.CreateEmptyFile` is disabled. The suite verifies that local writes remain unsynced until close or sync, interact correctly with directory listings and local deletion, and eventually persist to GCS only when the filesystem semantics require it.

Important APIs/helpers: `LocalFileTest` embeds `fsTest` and testify suite. `SetupSuite` enables implicit directories and disables empty-file creation. Helpers create local files with `os.OpenFile(...O_CREATE|O_TRUNC|O_DIRECT)`, assert the GCS object is absent, validate directory entries, close files, and compare bucket contents via `storageutil.ReadObject` and `bucket.StatObject`.

Control flow and state: tests create files under root, explicit dirs, and implicit dirs, write/truncate/random-write data, and assert no GCS object exists before close. ReadDir and WalkDir tests check that unsynced local files appear in listings alongside GCS-backed entries. Rename and rmdir tests distinguish local-file constraints: renaming a local file persists it under the new name, renaming a directory containing an unsynced local file fails until the file is synced, and removing directories containing local files unlinks them without uploading.

Persistence behavior: close uploads dirty local files unless they were unlinked. `Sync` on an unlinked local file is a no-op for GCS. Deleting a synced local file removes the object. Symlink tests show symlinks can target local unsynced files and become dangling after the local target is removed.

Dependencies and integration: uses mounted filesystem operations, fake bucket state, `storageutil`, `inode.ConflictingFileNameSuffix`, fusetesting time extraction, metrics/tracing config, and implicit-directory behavior.

Risks: some tests rely on entry ordering. `TestStatFailsOnNewFileAfterDeletion` mutates server config inside the test, which can be surprising in a shared suite. Local-vs-GCS state transitions are sensitive to open file handles and kernel writeback.

Test signals: strong coverage for delayed object creation, local listing visibility, unlink/rmdir safety, close-time persistence, timestamps, same-name recreation, and local symlink behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/local_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/local_modifications_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/local_modifications_test.go

Purpose: broad integration contract for modifying a GCS-backed FUSE filesystem through normal local filesystem APIs. It covers open flags, legal filenames, mknod, modes, directories, file data operations, sync/close persistence, symlinks, and rename behavior.

Important APIs/types: suites are ogletest-style (`OpenTest`, `MknodTest`, `ModesTest`, `DirectoryTest`, `FileTest`, `SymlinkTest`, `RenameTest`) embedding `fsTest`. Helpers include `interestingLegalNames`, which generates Unicode, shell-special, control/space-category, and max-length names, `getFileOffset`, `validateObjectAttributes`, and `createFile`.

Control flow and state: open tests validate nonexistent opens, create-on-open, truncation, multiple handles observing each other, legal and illegal names. Mode tests validate read-only/write-only/read-write errors and writes, append behavior, `WriteAt` offset preservation, and sparse writes with zero filling. Directory tests cover `Mkdir`, stat/read entries, non-empty and open rmdir, recreation with same name, unsupported hard links, chmod/chtimes no-op success, timestamp reasonableness, and GCS content type for directory marker objects.

Persistence behavior: file tests verify writes past EOF, truncation, seek, stat/lstat, unlink while open, bucket-side deletion races, same-name recreation, chmod/chtimes, dirty and clean sync, clobbered sync/close preserving the newer bucket generation, and content-type retention. Attribute tests compare extended GCS object attributes before and after append/write-at to ensure rewrites preserve relevant metadata while creating a new generation.

Symlink and rename integration: symlink creation writes legacy `gcsfuse_symlink_target` metadata and supports readlink/lstat/stat/remove. Rename tests cover directory naming conflicts, recursive directory rename limits, nested directories, cross-directory file moves, cross-device failures, overwrite semantics, wrong-type errors, and missing sources.

Dependencies: uses `os`, `syscall`, `storageutil`, fake GCS bucket, `gcs`, integration operations helpers, fusetesting, ogletest, and runtime-specific name limits.

Risks: large suite is environment-sensitive, especially kernel/FUSE error text, name limits, writeback caching, and time slop. It encodes both legacy symlink metadata and generation-clobber safety, making it a high-signal migration guard.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/local_modifications_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/metrics_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/metrics_test.go

Purpose: validates OpenTelemetry-backed metrics emitted by monitored filesystem operations, read paths, file cache behavior, GCS request accounting, read block-size histograms, and streaming-write fallback reasons.

Important APIs/types: `serverConfigParams` controls read/write/cache/streaming options for test filesystem creation. `createTestFileSystemWithMetrics` installs a manual OTel metric reader, creates `metrics.NewOTelMetrics`, builds a fake bucket and `fs.ServerConfig`, optionally configures file cache or sparse chunk cache, and returns the bucket, filesystem, metric handle, and reader. Tests wrap the server with `wrappers.WithMonitoring`.

Control flow and state: operation metrics tests create minimal FUSE ops (`LookUpInodeOp`, `OpenFileOp`, `ReadFileOp`, `MkDirOp`, etc.), call server methods directly, wait briefly for processing, and verify `fs/ops_count` and `fs/ops_latency` with `fs_op` attributes. Unsupported operations such as xattrs, fallocate, and hard links still emit metrics under either their explicit op or `Others`.

Read/cache metrics: buffered read tests expect `gcs/download_bytes_count`, `gcs/read_bytes_count`, and buffered latency. Sequential and random file-cache tests assert cache-hit labels, read types, and byte counts, including range-read disabled behavior. Sparse cache tests verify only the relevant chunk is downloaded. Kernel multi-range reader and GCS reader tests distinguish parallel, sequential, and random read types and request method metrics.

Persistence/instrumentation state: tests use fake bucket content and direct FUSE ops rather than mounting. File cache uses a temporary cache directory. Streaming-write fallback tests check fallback counters for existing files, out-of-order writes, and concurrency-limit breach.

Dependencies and integration: integrates `internal/fs`, monitoring wrappers, fake storage, `cfg`, `metrics` verification helpers, OTel SDK manual reader, `fuseops`, and tracing noop.

Risks: metric assertions are coupled to exact metric names and attribute sets. `waitForMetricsProcessing` is sleep-based. Global OTel meter provider is temporarily replaced, so cleanup is important and present. Direct server calls bypass kernel behavior.

Test signals: strong coverage for observability regressions across filesystem ops, read implementations, cache modes, GCS reads, block-size histograms, and streaming write fallback accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/notifier_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/notifier_test.go

Purpose: tests that FUSE notifier invalidation prevents stale cached dentries from causing persistent failures after a GCS object is clobbered outside the mounted filesystem.

Important APIs/types: `NotifierTest` embeds `fsTest`. `SetupSuite` enables implicit directories, sets a long inode attribute cache TTL, installs `fuse.NewNotifier`, enables experimental dentry cache, enables streaming writes, and starts the filesystem. Tests use `storageutil.CreateObject` to create and then clobber bucket objects behind gcsfuse’s back.

Control flow and state: `TestWriteFileWithRootDirParent` creates `fileName` in GCS, stats it to cache the entry, overwrites the object in GCS to change generation, then writes through the mount. The first write should fail with `ESTALE`, and the second write should succeed after notifier invalidation. `TestWriteFileWithNonRootDirParent` repeats the same scenario for `dir/foo`, validating parent lookup/invalidation below root. `TestReadFileDoNotFailPersistently` performs a stale read after clobber and expects the second read to succeed once the entry has been invalidated.

Dependencies and integration: uses mounted filesystem helpers from `common`, fake bucket storage utilities, `fuse.NewNotifier`, cfg dentry-cache and streaming-write options, syscall error matching, and long cache TTLs to make stale entries observable.

Risks: assertions depend on stale generation detection and notifier support. The exact first read error is only checked as non-nil, while write tests check `ESTALE`. The tests do not verify notification counts or exact parent invalidation calls; they validate externally visible recovery.

Test signals: a failure means stale cached inode/dentry state can persist after clobbering, causing repeated user-visible failures rather than one stale-handle error followed by recovery.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/notifier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/parallel_dirops_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/parallel_dirops_test.go

Purpose: tests filesystem behavior when parallel directory operations (`readdir` and lookup) are enabled. It verifies that concurrent lookups, listings, creates, deletes, mkdirs, and renames produce valid outcomes with and without metadata caches.

Important APIs/types: `ParallelDiropsTest` embeds `fsTest`; `ParallelDiropsWithoutCachesTest` embeds it and reruns the same tests with `DirTypeCacheTTL` and `InodeAttributeCacheTTL` set to zero. Setup enables implicit directories, sets `DisableParallelDirops: false`, configures rename limit and noop metrics/tracing, and creates a bucket structure with root files, an explicit directory with files, and an implicit directory.

Control flow and state: simple parallel tests perform two simultaneous `os.Stat` calls for the same file or directory, two `os.ReadDir` calls for explicit/implicit directories, and mixed parent/child readdir. Mutation races pair lookup/read-dir with `os.Create`, `os.Mkdir`, `os.Remove`, `os.RemoveAll`, and `os.Rename` on the same path. Assertions allow either valid ordering: lookup/list may see the old state or may get `os.IsNotExist`, while the mutating operation must succeed and final state is checked.

Dependencies and integration: uses mounted filesystem operations, fake GCS object setup, `sync.WaitGroup`, `os`, `path`, `cfg`, and testify assertions. It exercises the actual directory-operation locking and cache interaction in the mounted server rather than direct method calls.

Risks: the concurrency is only two goroutines per scenario and does not loop heavily, so rare races may escape. It assumes specific listing order for initial structure. Some assertions use `assert.Contains(filePath, stat.Name())`, which is permissive and mostly checks basename inclusion.

Test signals: protects against deadlocks and invalid state transitions introduced by parallel dirops, especially when caches are disabled and lookups/listings must consult backing storage more often.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/parallel_dirops_test.go -->
