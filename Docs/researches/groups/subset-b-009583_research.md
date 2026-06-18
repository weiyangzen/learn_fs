<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_cache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/read_cache_test.go

Purpose: integration coverage for the file read cache under mounted gcsfuse. It validates when cache files are populated, reused, evicted, invalidated, rebuilt for new object generations, or intentionally bypassed.

Important APIs/types/functions: ogletest suites `FileCacheTest`, `FileCacheWithCacheForRangeRead`, `FileCacheIsDisabledWithCacheDirAndZeroMaxSize`, and `FileCacheDestroyTest`; helpers `generateRandomString`, `sequentialReadShouldPopulateCache`, `cacheFilePermissionTest`, `writeShouldNotPopulateCache`, `sequentialToRandomReadShouldPopulateCache`, and `excludedFileShouldNotPopulateCache`. Config knobs under test include `cfg.FileCacheConfig.MaxSizeMb`, `CacheFileForRangeRead`, `EnableCrc`, `ExcludeRegex`, and `CacheDir`.

Control flow: setup enables implicit directories, noop metrics/tracing, and a cache directory under `$HOME/cache-dir/file-cache`. Tests create fake GCS objects, read through `mntDir` using `O_DIRECT` or `os.ReadFile`, then inspect `util.GetDownloadPath` on disk. Sequential reads populate the cache, random reads populate only when `CacheFileForRangeRead` is true, writes alone do not populate, and sync after dirtying a cached file refreshes cached content.

State and persistence behavior: persistent signals are on-disk cache files and fake GCS objects. The suite validates cache permissions, max-size rejection for oversized files, LRU promotion on read, eviction when full, range-read asynchronous population, local edits to cache files being served on later reads, and cache survival across unmount. Deletes and renames remove the old cached object path, including nested objects when a directory is renamed.

Dependencies and integration points: depends on the fs test harness, fake bucket object creation, `internal/cache/util` path helpers and size constants, direct I/O behavior, local filesystem cache state, metrics/tracing noops, and the server file-cache handler built from `ServerConfig.NewConfig`.

Risks: tests use global `CacheDir` and `FileCacheDir`, so teardown correctness is important for isolation. Random data and asynchronous range-read cache population can expose timing sensitivity. `O_DIRECT` behavior is platform-sensitive. The `ModifyFileInCacheAndThenReadShouldGiveModifiedData` case intentionally demonstrates that cache trust is strong enough for local cache corruption to affect reads.

Test signals: covers sequential/range/random read cache policy, exclude regex, disabled cache behavior, file-size boundary at equal/greater than cache size, LRU and eviction, stale cache handle behavior after cache-file deletion, invalidation on unlink/rename/renamed directory, concurrent reads from one handle, sync/write correctness, generation rebuild after stat-cache expiry, and unmount persistence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_dir_plus_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/read_dir_plus_test.go

Purpose: validates FUSE `ReadDirPlus` behavior, including entry attributes, dentry/inode attribute caching, implicit directories, symlinks, and local-only files.

Important APIs/types/functions: testify suites `ReadDirPlusTest` and `LocalFileEntriesReadDirPlusTest`; `fusetesting.ReadDirPlusPicky`; mount flag `EnableReaddirplus`; server fields `ImplicitDirectories`, `InodeAttributeCacheTTL`, and `cfg.FileSystem.ExperimentalEnableDentryCache`.

Control flow: suite setup enables readdirplus and dentry cache, creates remote objects and local symlinks/files, then calls `ReadDirPlusPicky` against `mntDir`. The test checks sorted entries and per-entry mode, size, and directory status. A cache test reads directory attributes, mutates the backing GCS object, stats before and after TTL expiry, and expects stale then refreshed attributes.

State and persistence behavior: persistent data is fake GCS content plus local unsynced file state. In-memory state under test includes inode attribute cache and dentry cache entries populated by `ReadDirPlus`. Local-only entries must appear even before they are persisted to GCS.

Dependencies and integration points: exercises `fileSystem.ReadDirPlus`, directory handle listing, local inode merging with GCS entries, symlink creation via `CreateSymlink`, inode attribute cache TTL, and dentry cache integration.

Risks: cache TTL tests rely on wall-clock sleeps, which can be timing-sensitive. Attribute parity between `ReadDirPlus` and later `Stat` is critical because kernels can use readdirplus as a metadata prefetch path.

Test signals: empty directory, mixed file/explicit dir/implicit dir/symlink listing, stat-after-readdirplus cache consistency, local-only file listing, and merged local plus GCS entry listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_dir_plus_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_only_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/read_only_test.go

Purpose: confirms that a read-only mount rejects mutating operations while preserving bucket contents.

Important APIs/types/functions: ogletest suite `ReadOnlyTest`; `SetUpTestSuite` sets `t.mountCfg.ReadOnly = true`; tests `CreateFile`, `ModifyFile`, and `DeleteFile`.

Control flow: the suite mounts read-only, attempts local file creation, opening an existing GCS object for read/write, and removing an existing GCS object through the mount. Each operation must return an error containing `read-only`.

State and persistence behavior: fake GCS objects are the authoritative persistent state. `DeleteFile` reads the object after the failed unlink to prove the bucket was not mutated.

Dependencies and integration points: depends on mount-level read-only enforcement before write paths such as create, open-for-write, and unlink reach object mutation. Uses `storageutil.CreateObject` and `ReadObject` for out-of-band validation.

Risks: `ModifyFile` calls `f.Close()` even when `os.OpenFile` fails, which assumes the returned file value is safe in the runtime path. The important behavioral risk is any write path bypassing the read-only mount guard.

Test signals: creation, modification, and deletion all fail with read-only errors, and GCS object content remains unchanged after deletion attempt.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/read_only_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/rename_dir_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/rename_dir_test.go

Purpose: integration tests for directory rename semantics across missing sources, non-empty destinations, empty directories, local files, open GCS files, same-parent/different-parent moves, replacement of empty destinations, symlink rename, and path reuse after rename/delete.

Important APIs/types/functions: testify suite `RenameDirTests`; standard `os.Rename`, `os.Stat`, `os.ReadDir`, `os.RemoveAll`, `os.Mkdir`; Python `os.rename` workaround for renaming into an existing empty directory.

Control flow: tests assume fixture directories `foo`, `bar`, nested explicit folders, and files from the shared fs test setup. The rename operation is invoked through the mounted filesystem, followed by old-path stat failure, new-path stat success, directory listing validation, or expected error matching.

State and persistence behavior: rename changes visible namespace state in the fake bucket and local inode maps. The suite also verifies that recreating a directory at an old path after rename produces an empty fresh directory, and that deleting/recreating a parent does not poison later local-file creation at the same path.

Dependencies and integration points: exercises `fileSystem.Rename`, directory inode rename logic, local file tracking, symlink handling, GCS copy/delete or folder rename behavior, directory listing cache invalidation, and error mapping to kernel strings such as `file exists`, `operation not supported`, and `no such file or directory`.

Risks: directory rename is consistency-sensitive because it may move many objects and cached inodes. Open local files in a source directory block rename, while open read-only GCS file handles are allowed but become unusable for writes. Existing empty destination behavior differs between Go helper support and raw syscall behavior.

Test signals: validates missing source failure, non-empty destination failure, empty source move, symlink move, local-open-file rejection, same/different-parent subtree preservation, replacement of empty destination, open GCS file behavior, namespace reuse after rename, and local-file reuse after parent deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/rename_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/rename_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/rename_file_test.go

Purpose: integration coverage for file rename semantics, including missing source, replacing an existing destination, same-parent and cross-parent moves, and symlink renames.

Important APIs/types/functions: testify suite `RenameFileTests`; tests `TestRenameFileWithSrcFileDoesNotExist`, `TestRenameFileWithDstDestFileExist`, `TestRenameFile`, and `TestRenameSymlinkToFile`.

Control flow: tests stat fixtures, call `os.Rename`, verify old-path `ENOENT`, verify new path attributes and content, and use `os.Lstat`/`os.Readlink` for symlink preservation.

State and persistence behavior: object namespace state changes in the fake bucket and inode mappings should follow the new name. Destination replacement must expose source content. Symlink rename should move the link object itself rather than the target.

Dependencies and integration points: exercises `fileSystem.Rename` file path, object rewrite/atomic rename behavior depending on bucket type, inode cache refresh, and symlink inode handling.

Risks: rename-over-existing is easy to mishandle with stale destination inodes or cache entries. Symlink rename requires not dereferencing the link. Cross-parent moves need parent directory cache invalidation on both sides.

Test signals: missing source error, destination replacement content, same and different parent moves, old path disappearance, new path stat/read correctness, and symlink target preservation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/rename_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/server.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/server.go

Purpose: constructs the exported FUSE server by creating the core filesystem and layering cross-cutting wrappers for error mapping, optional tracing, monitoring, and optional notifier support.

Important APIs/types/functions: `NewServer(ctx context.Context, cfg *ServerConfig) (fuse.Server, error)`.

Control flow: `NewServer` calls `NewFileSystem`; wraps the resulting `fuseutil.FileSystem` with `wrappers.WithErrorMapping`; conditionally wraps with `wrappers.WithTracing` if `cfg.IsTracingEnabled`; always wraps with `wrappers.WithMonitoring`; then returns either `fuse.NewServerWithNotifier` or `fuseutil.NewFileSystemServer`.

State and persistence behavior: this file owns no persistent state. Its ordering controls runtime state visibility to instrumentation: monitoring observes errors after inner error mapping and optional tracing have processed calls.

Dependencies and integration points: bridges internal `ServerConfig` and `NewFileSystem` with `jacobsa/fuse` server constructors, wrapper packages, tracing config, metrics handle, and dentry notifier.

Risks: wrapper ordering matters for errno categories and tracing spans. A nil metric or trace handle must be valid for wrapper usage via configuration defaults elsewhere. Notifier presence changes the concrete server constructor.

Test signals: indirectly covered by wrapper tests and tracing integration tests in this subset; many fs integration tests call through the server setup path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_common_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_common_test.go

Purpose: shared stale file handle integration tests and helpers for non-streaming writes. It verifies ESTALE when an open file is clobbered remotely, and no error when an unlinked local handle is synced/closed after local deletion.

Important APIs/types/functions: suite `staleFileHandleCommon`; `commonServerConfig`; helpers `clobberFile`, `createGCSObject`; tests `TestClobberedFileSyncAndCloseThrowsStaleFileHandleError` and `TestFileDeletedLocallySyncAndCloseDoNotThrowError`.

Control flow: setup disables metadata cache TTL to force fresh generation checks. Tests dirty `t.f1`, replace or remove the backing object, then sync/close and validate either `ESTALE` or success depending on local deletion semantics.

State and persistence behavior: fake GCS object generation/content is the persistent state. Open file handle state tracks the original generation and dirty local content. Clobbering must prevent unsynced data from overwriting the newer object.

Dependencies and integration points: uses storage utilities and integration `operations` helpers for ESTALE, no-file, close, and object-not-found validation. Exercises file sync/flush generation preconditions.

Risks: stale-handle correctness is central for data safety. The sync path must distinguish remote clobber/delete from a file intentionally unlinked through the same mount while the handle remains open.

Test signals: clobbered dirty file returns ESTALE on sync and close and preserves remote content; locally deleted open file can still be written, synced, and closed without resurrecting the object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_local_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_local_file_test.go

Purpose: runs the common non-streaming stale-handle suite for a local-only file that has not yet been synced to GCS.

Important APIs/types/functions: suite `staleFileHandleLocalFile`; `SetupTest`; `TestStaleFileHandleLocalFile`.

Control flow: each test creates a local file through `operations.CreateLocalFile`, stores the open handle in `t.f1`, and then inherits the common clobber and local-delete tests from `staleFileHandleCommon`.

State and persistence behavior: starts with local inode/file state and no GCS object, then tests introduce or validate GCS object state depending on the common helper. This checks promotion from local-only state under conflict.

Dependencies and integration points: depends on shared stale-handle common tests, local file creation helpers, file sync behavior, and fake bucket validation.

Risks: local-only files do not have an original generation at creation time, so conflict detection must still prevent overwriting a remote object that appears before sync.

Test signals: inherited tests prove local files report ESTALE after remote clobber and do not recreate a file after local unlink followed by sync/close.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_local_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_common_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_common_test.go

Purpose: shared stale-handle tests for the streaming-write path, especially flush/close behavior after a streamed file is clobbered between sync and close.

Important APIs/types/functions: suite `staleFileHandleStreamingWritesCommon`; setup configures `Write.EnableStreamingWrites`, `BlockSizeMb`, `MaxBlocksPerFile`, `GlobalMaxBlocks`, and disables writeback caching; test `TestWriteFileSyncFileClobberedFlushThrowsStaleFileHandleError`.

Control flow: setup enables streaming writes with a small block budget. The test writes 4 MiB at offset 0, calls `Sync`, clobbers the GCS object to a new generation, then closes the file and expects ESTALE.

State and persistence behavior: streaming write state spans local buffers, in-flight uploaded blocks, and final object generation. The test validates that a post-sync close/flush still checks clobber conditions and does not overwrite a newer object.

Dependencies and integration points: uses the common non-streaming config helper, streaming writer configuration, storage utilities, and integration operations for ESTALE validation.

Risks: streaming writes split data upload and finalization; clobbers between stages can corrupt data if close skips generation checks.

Test signals: close returns ESTALE after clobber and remote object content remains the clobber content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_local_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_local_file_test.go

Purpose: stale-handle streaming-write coverage for local-only files when a remote object appears or changes before the first streamed write completes.

Important APIs/types/functions: suite `staleFileHandleStreamingWritesLocalFile`; `SetupTest`; test `TestClobberedWriteFileSyncAndCloseThrowsStaleFileHandleError`.

Control flow: creates a local-only file, clobbers the same object name in GCS, generates 4 MiB of data, attempts `WriteAt`, then validates ESTALE on write, sync, and close.

State and persistence behavior: local handle state conflicts with a remote GCS generation created after the handle opened. The test ensures failed writes do not upload local data and that the remote clobber content remains.

Dependencies and integration points: inherits streaming-write setup, uses `operations.CreateLocalFile`, `GenerateRandomData`, ESTALE validation, and `storageutil.ReadObject`.

Risks: local-file streaming write initialization must detect that the name is no longer safe to create. Both write-time and cleanup-time errors must remain consistent.

Test signals: write, sync, and close all return ESTALE, and remote object content is unchanged.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_local_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_synced_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_synced_file_test.go

Purpose: stale-handle streaming-write coverage for already-synced empty GCS objects, including remote clobber and rename before write.

Important APIs/types/functions: suite `staleFileHandleStreamingWritesSyncedFile`; `SetupTest`; tests `TestWriteToClobberedFileThrowsStaleFileHandleError` and `TestRenameFileWriteThrowsStaleFileHandleError`.

Control flow: setup opens an empty object. One test replaces the object remotely before a 4 MiB `WriteAt`; the other renames the file through the mount before `WriteAt`. Both expect ESTALE on write, while sync/close succeed because no new dirty data was accepted.

State and persistence behavior: original synced object generation and name are tracked by the open handle. Remote replacement or mount rename invalidates that handle for future writes. Existing remote content at the clobbered or renamed name remains unchanged.

Dependencies and integration points: inherits streaming-write common setup and uses object clobber, `os.Rename`, random data generation, ESTALE validation, and storage reads.

Risks: streaming write path must reject writes on stale handles before uploading data. Rename invalidation needs to update handle state and object indexes consistently.

Test signals: write returns ESTALE after clobber or rename, sync/close return nil, and persisted object contents remain the expected empty or clobber data.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_streaming_writes_synced_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_synced_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_synced_file_test.go

Purpose: non-streaming stale-handle coverage for files that start as existing GCS objects.

Important APIs/types/functions: suite `staleFileHandleSyncedFile`; `SetupTest`; tests for clobbered read, clobbered first write, renamed-file write, and remote deletion before sync/close.

Control flow: setup creates a GCS object and opens it for read/write direct I/O. Tests replace, rename, or delete the backing object, then perform reads/writes/sync/close and assert ESTALE or success depending on whether data was accepted.

State and persistence behavior: handle state includes object generation at open. Reads and first writes detect generation mismatch. A failed first write leaves no dirty state, so sync/close can succeed. Dirty data followed by remote deletion fails on sync/close and preserves the deleted/clobbered state.

Dependencies and integration points: uses storageutil for remote mutation, `os.Rename` through mount, and operations helpers for ESTALE and object validation. Exercises file read, write, sync, close, and rename invalidation paths.

Risks: stale reads must fail rather than returning data from an object no longer matching the handle. Sync must not overwrite remote clobbers or resurrect remote deletions, while local unlink semantics from the common suite remain different.

Test signals: ESTALE on clobbered read, ESTALE on clobbered first write with clean sync, ESTALE on write after rename, and ESTALE on sync/close after remote deletion of a dirty handle.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stale_file_handle_synced_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_common_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_common_test.go

Purpose: shared integration tests for streaming-write semantics used by local files and empty synced GCS objects.

Important APIs/types/functions: suite `StreamingWritesCommonTest`; tests `TestUnlinkBeforeWrite`, `TestUnlinkAfterWrite`, `TestRenameFileWithPendingWrites`, `TestTruncateToLowerSizeSyncsFileToGcs`, `TestTruncateToLowerSizeSyncsFileToGcsAndDeletingFileDeletesFromGcs`, `TestOutOfOrderWriteSyncsFileToGcs`, and `TestOutOfOrderWriteSyncsFileToGcsAndDeletingFileDeletesFromGcs`.

Control flow: tests operate on `t.f1` supplied by child suites. They unlink before/after writes, rename a dirty handle, truncate after writing, issue out-of-order `WriteAt`, and then read GCS contents or mounted file content to validate when final data becomes durable.

State and persistence behavior: streaming writes initially upload or buffer sequential data. Truncate to lower size and out-of-order writes force the file into a synced/finalized state on close, with GCS showing old streamed data before close and final content after close. Deleting after forced sync removes the object from GCS.

Dependencies and integration points: depends on child suite setup for streaming write config, storageutil object reads, `gcs.NotFoundError`, and integration `operations`.

Risks: rename/unlink with pending streaming writes can leave temporary objects, stale handles, or resurrected GCS objects if ordering is wrong. Out-of-order writes and truncation are critical fallback paths from streaming append to full object rewrite.

Test signals: unlink removes local/GCS state, rename flushes pending writes to the new name, truncate and out-of-order writes preserve previous GCS content until close then finalize correct content, and delete after fallback sync removes GCS object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_common_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_empty_gcs_object_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_empty_gcs_object_test.go

Purpose: runs the shared streaming-write tests against a file that begins as an empty object in GCS.

Important APIs/types/functions: suite `StreamingWritesEmptyGCSObjectTest`; `SetupSuite`, `SetupTest`, `TearDownTest`, and `TestStreamingWritesEmptyObjectTest`.

Control flow: setup enables streaming writes with block size 1 MiB, no writeback caching, and `CreateEmptyFile=false`. Each test creates an empty object, opens it direct I/O read/write, validates it exists in GCS, then inherits the common tests.

State and persistence behavior: starts with durable empty object state and an open synced handle. The inherited tests verify transitions from empty object to pending writes, rename, truncation, out-of-order rewrite, and deletion.

Dependencies and integration points: uses `storageutil.CreateObject` and `ReadObject`, child configuration for write streaming, and common streaming-write tests.

Risks: empty objects are a special case for streaming writes because they can look like either already-synced data or a creation placeholder. Incorrect state handling can create duplicate writes or lose delete semantics.

Test signals: common streaming-write behaviors pass when the source is an existing empty GCS object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_empty_gcs_object_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_local_file_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_local_file_test.go

Purpose: runs streaming-write coverage for local-only files and adds a directory removal case involving local, empty, and non-empty objects.

Important APIs/types/functions: constant `fileName`; suite `StreamingWritesLocalFileTest`; setup enabling streaming writes and zero metadata TTL; test `TestRemoveDirectoryContainingLocalAndEmptyObject`.

Control flow: setup creates local-only `foo` with no GCS object. Inherited common tests cover unlink, rename, truncate, and out-of-order write behavior. The directory test creates an explicit directory with empty and non-empty objects, adds local and dirty empty-object handles, removes the directory recursively, closes handles, and validates all objects are gone.

State and persistence behavior: local file state transitions to streamed GCS data only when writes are finalized. Recursive directory removal must remove synced objects, empty-object handles, local-only files, and explicit directory object state.

Dependencies and integration points: uses `operations.CreateLocalFile`, fake object creation through `fsTest.createObjects`, direct I/O opens, streaming write config, and object-not-found validation.

Risks: recursive delete while files are open and dirty can leave GCS objects behind or cause close errors. Local-only and empty-object streaming paths must converge on the same cleanup semantics.

Test signals: inherited streaming write suite plus successful `RemoveAll` of a directory containing local dirty file, empty dirty object, non-empty object, and explicit directory marker, with all GCS objects absent after closes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/streaming_writes_local_file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stress_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/stress_test.go

Purpose: concurrency stress tests for common filesystem operations through the mounted gcsfuse filesystem.

Important APIs/types/functions: helper `forEachName`; ogletest suite `StressTest`; tests `CreateAndReadManyFilesInParallel`, `TruncateFileManyTimesInParallel`, `CreateInParallel_NoTruncate`, `CreateInParallel_Truncate`, `CreateInParallel_Exclusive`, `MkdirInParallel`, and `SymlinkInParallel`.

Control flow: `forEachName` fans work out to 8 goroutines and returns the first error. The first stress test writes 32 files in parallel and reads them back. The truncate test shares one file among 16 workers repeatedly truncating to random sizes for 500 ms, then verifies the final size matches one worker's final truncate. Other cases delegate to `fusetesting` parallel create/mkdir/symlink tests.

State and persistence behavior: stresses local in-memory inode/handle state, synchronization, and eventual fake GCS object state under parallel operations. The truncate test checks visible metadata consistency rather than object content.

Dependencies and integration points: uses Go runtime parallelism, `errgroup`, `fusetesting` helpers, and the shared fs test mount.

Risks: these tests can expose races, deadlocks, non-atomic truncate state, duplicate create handling, and symlink/mkdir interleaving bugs. Random truncation means failures may be timing-dependent.

Test signals: parallel create/read content consistency, concurrent truncate final-size coherence, and standard FUSE parallel operation suites for create, exclusive create, mkdir, and symlink.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/stress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/tracing_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/tracing_test.go

Purpose: integration tests that every FUSE operation wrapper emits an OpenTelemetry server span with the expected gcsfuse tracing operation name, under both interrupt-handling modes.

Important APIs/types/functions: suite `TracingTestSuite`; helper `createTestFileSystemWithTraces`; `newInMemoryExporter`; tests `TestTraceLookupInode`, `TestTraceStatFS`, `TestTraceGetInodeAttributes`, `TestTraceSetInodeAttributes`, `TestTraceForgetInode`, `TestTraceMkDir`, `TestTraceMkNode`, `TestTraceCreateFile`, `TestTraceCreateLink`, `TestTraceCreateSymlink`, `TestTraceRename`, `TestTraceRmDir`, `TestTraceUnlink`, `TestTraceOpenDir`, `TestTraceReadDir`, `TestTraceReadDirPlus`, `TestTraceReleaseDirHandle`, `TestTraceOpenFile`, `TestTraceReadFile`, `TestTraceWriteFile`, `TestTraceSyncFile`, `TestTraceFlushFile`, `TestTraceReleaseFileHandle`, `TestTraceReadSymlink`, `TestTraceRemoveXattr`, `TestTraceGetXattr`, `TestTraceListXattr`, `TestTraceSetXattr`, `TestTraceFallocate`, and `TestTraceSyncFS`.

Control flow: each subtest builds a filesystem with tracing enabled and an in-memory OTEL exporter, creates fixture objects/inodes/handles when needed, invokes one FUSE method on the server, then asserts one exported span name and server span kind. Cases run for `IgnoreInterrupts` true and false.

State and persistence behavior: fake bucket and filesystem state are created per test. Span state is exported in memory and reset between tests. Some operations create or remove actual fake bucket objects to reach the target FUSE path.

Dependencies and integration points: exercises `NewFileSystem` plus `wrappers.WithTracing`, gcsfuse tracing constants, `otel/sdk/trace/tracetest`, fuseops structs, fake bucket, and server config.

Risks: because wrappers have one delegator per FUSE operation, missing or wrong operation names are easy regression points. Setup must create enough inode/handle state for each method without making the span assertion dependent on operation success.

Test signals: broad operation-name coverage across lookup, attrs, create, link, symlink, rename, directory operations, file read/write/sync/flush/release, xattrs, fallocate, and syncfs. It also validates span kind is server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/tracing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/type_cache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/type_cache_test.go

Purpose: integration tests for metadata type-cache behavior when object names can be both files and explicit directories, and when cache entries expire by size, TTL, zero size, zero TTL, or infinite TTL.

Important APIs/types/functions: common suite `typeCacheTestCommon`; suites `TypeCacheTestWithMaxSize1MB`, `TypeCacheTestWithZeroSize`, `TypeCacheTestWithZeroTTL`, and `TypeCacheTestWithInfiniteTTL`; helpers `createObjectOnGCS`, `statAndConfirmIsDir`, `statAndExpectNotADirectoryError`, and `testNoInsertionSupported`.

Control flow: setup configures `cfg.MetadataCacheConfig.TypeCacheMaxSizeMb` and `TtlSecs`, mirrors TTL into `ServerConfig.DirTypeCacheTTL` and `InodeAttributeCacheTTL`, then mounts. Tests create file and directory objects with the same basename, call `os.Stat` with or without trailing slash, and observe whether cached type hides the newer remote type.

State and persistence behavior: fake GCS objects are mutable independently of cache. Type-cache state maps name to file/explicit-dir/implicit-dir type and can outlive remote changes until TTL or size eviction. Infinite TTL is mapped to a very large duration. Zero size or zero TTL disables insertion so later stat observes current GCS type.

Dependencies and integration points: depends on `metadata.SizeOfTypeCacheEntry`, fake cache clock `cacheClock`, stat/lookup control flow in `fileSystem.LookUpInode`, and path trailing slash handling.

Risks: stale type-cache entries can cause `not a directory` errors or report a file as a directory after remote changes. Size eviction test creates many long names in parallel, so it is performance-sensitive. Global variables are mutated by suite setup and require serial ogletest behavior.

Test signals: no initial entry gives ENOENT, file hides later dir until eviction, dir hides later file, size-based eviction admits updated dir type, TTL eviction admits updated type, zero size/TTL disable insertion, and infinite TTL never expires even after simulated 100 years.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/type_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/unsupported_path_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/unsupported_path_test.go

Purpose: validates support mode for buckets containing object names with unsupported path components such as duplicate slashes, `.` and `..`, while ensuring supported names remain visible and operable.

Important APIs/types/functions: suite `UnsupportedPathNameTest`; setup config `EnableUnsupportedPathSupport`, `EnableAtomicRenameObject`, `ImplicitDirectories`, and `RenameDirLimit`; tests for read, copy, rename, and delete with unsupported names.

Control flow: setup creates objects containing supported and unsupported path forms, then uses `filepath.Walk`, `cp -r`, `os.Rename`, or `rm -rf` through the mount. Assertions verify only supported names appear and operations complete on the visible subset.

State and persistence behavior: unsupported objects exist in the fake bucket but are filtered from filesystem view. Directory rename/delete operate on the supported visible namespace without failing due to hidden unsupported names.

Dependencies and integration points: exercises directory listing filters, unsupported path support config, atomic object rename, recursive directory rename/delete code, and shell command interoperability.

Risks: hidden unsupported objects can make directory operations appear incomplete or unsafe. Filtering must not hide supported dotfile names such as `.config`, and recursive operations must not accidentally traverse `.` or `..` object keys as real path elements.

Test signals: directory walking shows only supported files/directories, copy copies only supported entries, rename succeeds and visible destination entries are supported only, and recursive delete removes the visible directory without unsupported-name errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/unsupported_path_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping.go

Purpose: FUSE filesystem wrapper that converts internal, GCS, gRPC, HTTP, and context errors into `syscall.Errno` values understood by the kernel, while recovering panics with fatal logging.

Important APIs/types/functions: package variable `DefaultFSError`; helper `errno`; constructor `WithErrorMapping`; type `errorMapping`; methods `handlePanic`, `mapError`, and delegators for all `fuseutil.FileSystem` operations.

Control flow: each method defers panic handling, calls the wrapped filesystem method, and passes the result to `mapError`. `errno` first preserves nil, maps `gcsfuse_errors.FileClobberedError` to `ESTALE`, preserves existing `syscall.Errno`, maps context cancellation and storage object-not-exist, handles selected string patterns, maps gRPC status codes, maps `googleapi.Error` HTTP codes, and falls back to `EIO`.

State and persistence behavior: stateless wrapper, aside from references to wrapped filesystem and global default errno. It affects runtime error state seen by FUSE and outer wrappers.

Dependencies and integration points: used by `fs.NewServer` as the innermost wrapper before tracing/monitoring. Integrates with Cloud Storage errors, google API errors, gRPC status, gcsfuse clobber errors, logger, and every FUSE operation interface.

Risks: error matching by string is brittle. Mapping order is important: `FileClobberedError` must become `ESTALE`; existing errno values should not be overwritten. Panic handling logs fatal, which can terminate process behavior rather than returning an error.

Test signals: companion tests cover gRPC permission/already-exists/not-found/canceled/unauthenticated, HTTP unauthorized, and file-clobbered to ESTALE.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping_test.go

Purpose: unit tests for key branches of `errno` error conversion.

Important APIs/types/functions: suite `ErrorMapping`; `TestWithErrorMapping`; tests for permission denied, already exists, not found, canceled, unauthenticated gRPC, unauthenticated HTTP `googleapi.Error`, and `FileClobberedError`.

Control flow: tests build `status.Error` values, wrap them through `apierror.FromError` when appropriate, pass errors to `errno`, and compare against expected `syscall` errno constants.

State and persistence behavior: stateless unit coverage; no filesystem or bucket state.

Dependencies and integration points: uses gRPC status/codes, google API error types, `apierror`, gcsfuse clobber error, and testify suite/assert.

Risks: coverage is representative but not exhaustive. String-matched cases, context cancellation, storage object-not-exist, existing errno preservation, and fallback EIO are not covered here.

Test signals: confirms important public mappings to `EACCES`, `EEXIST`, `ENOENT`, `EINTR`, and `ESTALE`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/error_mapping_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring.go

Purpose: FUSE filesystem wrapper that records operation counts, error counts by low-cardinality category, latency, and read block sizes for metrics.

Important APIs/types/functions: constants for metrics error categories; helper `categorize`; `recordOp`; constructor `WithMonitoring`; type `monitoring`; `invokeWrapped`; delegators for all FUSE operations. `ReadFile` additionally calls `metricHandle.ReadBlockSizes`.

Control flow: each wrapper method calls `invokeWrapped` with a `metrics.FsOp` label. `invokeWrapped` records start time, invokes the wrapped method, and calls `recordOp`. `recordOp` increments operation count, increments error count when non-nil using `categorize`, and records latency.

State and persistence behavior: stateless wrapper except for metric side effects in the provided `metrics.MetricHandle`. It does not mutate filesystem data.

Dependencies and integration points: used by `fs.NewServer` as the outer wrapper. It relies on errno-like errors from inner wrappers for categorization and on generated metric attribute constants.

Risks: because monitoring is outside error mapping in `NewServer`, category labels are based on mapped errno. If wrapper order changes, non-errno errors default to IO error and category quality drops. The large errno switch must stay aligned with supported Linux errno constants and generated metric labels.

Test signals: companion test verifies representative errno-to-category mappings and fallback for non-errno errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring_test.go

Purpose: unit coverage for filesystem error category classification used by monitoring metrics.

Important APIs/types/functions: `TestFsErrStrAndCategory` table-driven parallel test; representative expected category constants such as `errDirNotEmpty`, `errFileExists`, `errInvalidArg`, `errInterrupt`, `errNetwork`, `errPerm`, and `errTooManyFiles`.

Control flow: each subtest calls `categorize` with either a generic error or a selected `syscall.Errno` and asserts the expected `metrics.FsErrorCategory`.

State and persistence behavior: stateless and parallel-safe.

Dependencies and integration points: validates a subset of categories used by `recordOp` in `monitoring.go`, using generated metrics category attributes.

Risks: the test samples categories rather than every errno in the switch. It does not verify operation count/latency recording or `ReadBlockSizes`.

Test signals: confirms fallback generic errors classify as IO and representative syscall values map to intended low-cardinality metric categories.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/monitoring_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing.go

Purpose: FUSE filesystem wrapper that creates a root OpenTelemetry server span for each filesystem operation and records operation errors on the span.

Important APIs/types/functions: type `tracedFS`; constructor `WithTracing`; `invokeWrapped`; per-operation delegators mapping to tracing constants such as `tracing.StatFS`, `tracing.LookUpInode`, `tracing.ReadFile`, and `tracing.SyncFS`.

Control flow: each method calls `invokeWrapped` with the operation name and a closure for the wrapped method. `invokeWrapped` starts a server span, defers span end, invokes the wrapped operation with the propagated context, and records any returned error.

State and persistence behavior: stateless wrapper except for trace export side effects through `tracing.TraceHandle`. It does not change filesystem state directly.

Dependencies and integration points: inserted by `fs.NewServer` only when tracing is enabled. Uses `wrappedCall` type from monitoring package, `jacobsa/fuse` operation structs, and gcsfuse tracing constants.

Risks: one delegator per FUSE op means new operations can be missed. Wrong span names break observability queries. If the trace handle is nil or non-thread-safe, every operation path can be affected.

Test signals: wrapper-level test checks a span is created for `StatFS`; fs-level tracing integration tests cover all operation names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing_test.go

Purpose: focused unit test for the tracing wrapper's span creation behavior.

Important APIs/types/functions: helper `newInMemoryExporter`; test double `dummyFS` implementing all `fuseutil.FileSystem` methods; test `TestSpanCreation`.

Control flow: installs an in-memory OTEL exporter, constructs `tracedFS` around `dummyFS` with `tracing.NewOTELTracer`, calls `StatFS`, then asserts one exported span named `fs.stat_fs` with `trace.SpanKindServer`.

State and persistence behavior: span export state is held in memory and reset during cleanup. Dummy filesystem performs no state changes.

Dependencies and integration points: OpenTelemetry SDK trace provider/exporter, gcsfuse OTEL tracer, and the traced wrapper.

Risks: only `StatFS` is tested here; broader operation mapping is covered by `internal/fs/tracing_test.go`. Global OTEL tracer provider changes can affect tests if cleanup is incomplete.

Test signals: confirms wrapper starts server spans and uses the expected operation name for `StatFS`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/wrappers/tracing_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/zonal_bucket_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/zonal_bucket_test.go

Purpose: reuses file rename tests under a zonal bucket configuration to validate rename semantics with bucket type set to rapid/zonal behavior.

Important APIs/types/functions: suite `ZonalBucketTests` embeds `RenameFileTests` and `fsTest`; `SetupSuite`, `SetupTest`, and `TestZonalBucketTests`.

Control flow: setup disables implicit directories, sets noop metrics/tracing, sets global `bucketType = gcs.BucketType{Zonal: true}`, and mounts. Each test creates explicit folders and objects, then inherited file rename tests run.

State and persistence behavior: fake bucket layout has explicit folder objects and file objects. Rename state should update in the zonal bucket path the same way as regular file rename tests.

Dependencies and integration points: exercises bucket-type-dependent behavior in the filesystem, especially atomic object rename support expected for zonal buckets, while reusing `RenameFileTests`.

Risks: global `bucketType` mutation must be isolated. Zonal buckets have different read/rename optimization paths, so inherited tests catch regressions where rapid bucket behavior diverges from normal POSIX-like rename.

Test signals: all file rename behaviors from `rename_file_test.go` pass with `gcs.BucketType{Zonal: true}` and explicit directory fixtures.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/zonal_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager.go

Purpose: builds and manages configured GCS bucket wrappers for gcsfuse, including fake bucket support, dummy I/O, monitoring, debug logging, prefix restriction, rate limiting, stat cache, content-type handling, syncer setup, bucket type discovery, and temporary-object garbage collection.

Important APIs/types/functions: `BucketConfig`; `BucketManager` interface; `bucketManager`; `NewBucketManager`; `setUpRateLimiting`; `(*bucketManager).SetUpBucket`; `(*bucketManager).ShutDown`.

Control flow: `NewBucketManager` creates a shared stat LRU cache when configured and a cancellable GC context. `SetUpBucket` obtains a fake or storage-handle bucket, optionally wraps dummy I/O, monitoring, debug logging, prefix bucket, rate limiting, stat cache, content-type bucket, and `SyncerBucket`. It requires `TmpObjectPrefix`, forces bucket type discovery via `BucketType`, starts `garbageCollect` in a goroutine, and returns the syncer bucket.

State and persistence behavior: persistent state is remote GCS bucket/object data plus temporary objects under `TmpObjectPrefix`. In-memory state includes shared stat cache, storage handle, config, and GC cancellation. Garbage collection runs until `ShutDown`.

Dependencies and integration points: integrates `storage.StorageHandle`, `canned` fake bucket, dummy I/O bucket, monitoring bucket, debug bucket, prefix bucket, rate-limit wrappers, metadata stat cache, content type bucket, syncer/compose logic, metrics, logger, and bucket storage-layout metadata.

Risks: wrapper order changes semantics. Missing `TmpObjectPrefix` is fatal to setup. Stat cache shared across multibucket mounts must be namespaced by bucket. Rate limit capacity calculation can fail. GC goroutine lifecycle depends on `ShutDown` being called.

Test signals: companion tests cover construction, setup for single and multibucket mounts, and missing bucket errors. Other integration tests exercise stat cache, prefix, and syncer behavior indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager_test.go

Purpose: unit/integration tests for bucket manager construction and setup against fake storage with mocked storage-layout calls.

Important APIs/types/functions: ogletest suite `BucketManagerTest`; constants `TestBucketName` and `invalidBucketName`; setup with `storage.NewFakeStorageWithMockClient`; tests `TestNewBucketManagerMethod`, `TestSetUpBucketMethod`, `TestSetUpBucketMethod_IsMultiBucketMountTrue`, and missing-bucket variants.

Control flow: setup creates fake storage and configures the mock storage-control client to report hierarchical namespace and zonal location for the test bucket. Tests instantiate `bucketManager` with representative config, call `SetUpBucket`, and assert returned syncer or expected error strings.

State and persistence behavior: fake storage server and mock storage layout are test state. Bucket manager starts GC contexts and wraps fake bucket state, then teardown shuts down fake storage.

Dependencies and integration points: covers `BucketHandle` and `BucketType` storage-layout integration, syncer creation, stat cache config, prefix wrapping through `OnlyDir`, rate limit config, and error propagation from missing buckets.

Risks: tests assert string fragments from storage-layout errors. They do not verify every wrapper layer directly, only that setup completes and syncer is present.

Test signals: construction returns non-nil manager, setup returns non-nil syncer in single and multibucket modes, and missing buckets propagate NotFound storage-layout errors with nil syncer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/bucket_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader.go

Purpose: top-level GCS reader implementation that chooses between a sequential `RangeReader` and a rapid-bucket random-access `MultiRangeReader`, tracks read patterns, serializes range-reader use, and retries short reads for rapid buckets.

Important APIs/types/functions: `ReaderType` enum; `GCSReader`; `GCSReaderConfig`; `NewGCSReader`; `shouldRetryForShortRead`; methods `ReaderName`, `ReadAt`, `read`, `readerType`, `getEndOffset`, `Destroy`, and `CheckInvariants`.

Control flow: `ReadAt` validates offset, builds a `GCSReaderRequest`, calls `read`, and for rapid buckets retries a short read from the remaining offset using `ForceCreateReader`. `read` computes reader type from read classification and bucket type; range-reader reads take a mutex and may recalculate read info after waiting; random reads or skip-size-check reads use MRD. Sequential prefetch end offset is computed from `ReadTypeClassifier`.

State and persistence behavior: no persistent state. In-memory state includes range reader, multi-range reader, read classifier, mutex, object metadata, and bucket reference. Destroy closes child readers and decrements MRD refs.

Dependencies and integration points: implements `gcsx.Reader`; uses `gcsx.ReadTypeClassifier`, metrics read type constants, GCS bucket type rapid/zonal detection, range reader, MRD wrapper, cfg, metrics, and tracing.

Risks: read-type recalculation under lock prevents queued sequential reads from using stale classification. Short-read retry must not retry beyond known object size unless skip size checks is enabled. RangeReader is not used when size checks are skipped. Concurrent random reads bypass the range mutex and rely on MRD concurrency.

Test signals: companion tests cover constructor state, invalid offsets, range reader reuse/reopen, cancellation, inactive timeout reader, zonal random reads, short-read retry, and parallel random reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader_test.go

Purpose: unit tests for `GCSReader` selection, range-reader reuse, read classification, cancellation, inactive timeout wrapping, rapid-bucket MRD behavior, short-read retry, and parallel random reads.

Important APIs/types/functions: suite `gcsReaderTest`; helper `readAt`; constant `sequentialReadSizeInMb`; tests `Test_NewGCSReader`, `Test_ReadAt_InvalidOffset`, `Test_ReadAt_ExistingReaderLimitIsLessThanRequestedDataSize`, `Test_ReadAt_ExistingReaderLimitIsLessThanRequestedObjectSize`, `Test_ReadAt_ExistingReaderIsFine`, `Test_ExistingReader_WrongOffset`, `Test_ReadAt_PropagatesCancellation`, `Test_ReadAt_WithAndWithoutReadConfig`, `Test_ReadAt_ValidateZonalRandomReads`, `Test_ReadAt_ShortReadRetry`, and `Test_ReadAt_ParallelRandomReads`.

Control flow: tests configure a mock bucket, fake readers or fake MRD downloaders, and a read classifier. They call `GCSReader.ReadAt` through a helper that records read info and then assert buffer contents, reader state, expected next offset, mock calls, cancellation effects, and MRD behavior.

State and persistence behavior: all object data is in fake readers/downloaders. In-memory state under test includes `RangeReader.reader/start/limit/readHandle`, `ReadTypeClassifier`, `MultiRangeReader.mrdWrapper`, and cancellation callbacks.

Dependencies and integration points: uses `storage.TestifyMockBucket`, fake storage readers/downloaders, `gcsx.NewMultiRangeDownloaderWrapper`, cfg read options, metrics/tracing noops, and testify suite/mock.

Risks: several tests reset setup inside subtests and manually manipulate internal fields, so they are tightly coupled to implementation. Parallel random read test validates data but can hide races unless run with the Go race detector.

Test signals: proves correct EOF/invalid-offset behavior, reader reopening with read handles, preserving active range reader for partial reads, context cancellation propagation, inactive timeout reader construction, zonal random MRD selection with correct classifier updates, rapid short-read retry, and safe parallel MRD reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/gcs_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/multi_range_reader.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/multi_range_reader.go

Purpose: adapter from `gcsx.GCSReaderRequest` to the shared `MultiRangeDownloaderWrapper` for random or rapid-bucket reads.

Important APIs/types/functions: type `MultiRangeReader`; constructor `NewMultiRangeReader`; methods `readFromMultiRangeReader`, `ReadAt`, and `destroy`.

Control flow: `ReadAt` returns `io.EOF` when offset is beyond object size unless skip-size checks are enabled, otherwise delegates to `readFromMultiRangeReader`. The delegate validates wrapper presence, increments wrapper ref count once using an atomic compare-and-swap, then calls wrapper `Read` with offset/end, metrics, tracing, and force-create flag. `destroy` decrements ref count if MRD was in use.

State and persistence behavior: no persistent state. In-memory state includes object metadata, MRD wrapper pointer, atomic `isMRDInUse`, metric handle, and trace handle. Reference count state lives in the shared wrapper.

Dependencies and integration points: used by `GCSReader` for random rapid-bucket reads and skip-size-check reads. Integrates `MultiRangeDownloaderWrapper`, metrics, tracing, logger, and GCS object metadata.

Risks: nil wrapper is an explicit error. Reference counting must be balanced on destroy; repeated reads share a single increment. Offset validation differs when `SkipSizeChecks` is true, which is needed for reads beyond cached object size.

Test signals: companion tests cover full and partial reads, nil wrapper error, zero-byte read, skip-size-check behavior, and invalid offset EOF.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/multi_range_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/multi_range_reader_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/multi_range_reader_test.go

Purpose: unit tests for `MultiRangeReader` behavior around MRD wrapper use, partial/full reads, nil wrapper, skip-size checks, and invalid offsets.

Important APIs/types/functions: suite `multiRangeReaderTest`; helper `readAt`; constant `TestTimeoutForMultiRangeRead`; tests `Test_ReadFromMultiRangeReader_ReadFull`, `Test_ReadFromMultiRangeReader_NilMRDWrapper`, `Test_ReadFromMultiRangeReader_ReadChunk`, `Test_ReadAt_MRDRead`, `Test_ReadAt_SkipSizeChecks`, and `Test_ReadAt_InvalidOffset`.

Control flow: tests create fake object metadata, a mock bucket, fake MRD wrappers/downloaders, then call internal or public read methods. Assertions check bytes read, buffer contents, errors, and that range-reader APIs are not called.

State and persistence behavior: fake generated byte slices represent object data. In-memory MRD wrapper ref state and `isMRDInUse` are reset between cases.

Dependencies and integration points: uses fake multi-range downloader implementations, `gcsx.NewMultiRangeDownloaderWrapper`, testify mocks/suite, metrics/tracing noops, and GCS bucket type.

Risks: tests couple to fake downloader behavior for reads that extend past object end. They do not directly assert ref-count decrement, but teardown calls `destroy`.

Test signals: full read with exact/larger buffer, nil wrapper error, partial chunk read, zero-byte MRD read, skip-size-check read past object size without EOF, and EOF for invalid offset without skip.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/multi_range_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader.go -->
# Research: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader.go

Purpose: sequential GCS reader that reuses a single `NewReaderWithReadHandle` stream, prefetches ranges, skips small forward gaps, propagates cancellation, records read metrics, and converts object-not-found during open into stale-file-handle errors.

Important APIs/types/functions: constants `MiB` and `maxReadSize`; type `RangeReader`; constructor `NewRangeReader`; methods `checkInvariants`, `destroy`, `closeReader`, `ReadAt`, `readFromRangeReader`, `readFull`, `startRead`, `skipBytes`, `invalidateReaderIfMisalignedOrTooSmall`, and `readFromExistingReader`.

Control flow: `ReadAt` optionally forces a new reader, tries `readFromExistingReader`, and falls back to starting a range reader. Existing readers can be advanced by `skipBytes`, invalidated when misaligned or too small, or reused for the exact requested range. `startRead` opens either an inactive-timeout reader or a bucket read-handle reader with object generation and byte range. `readFull` spawns a cancellation goroutine when interrupts are not ignored. `readFromRangeReader` updates `start`, closes at limit, handles short reads, and discards malfunctioning readers.

State and persistence behavior: no persistent state. In-memory state tracks stream `start`, `limit`, current reader, cancel function, and reusable `readHandle`. Reads target immutable object generation metadata. NotFound during `startRead` becomes `FileClobberedError`, protecting open handles from remote deletion or generation change.

Dependencies and integration points: used by `GCSReader` for sequential/regional reads. Integrates cfg read and filesystem interrupt settings, `gcsx.NewInactiveTimeoutReader`, GCS bucket `NewReaderWithReadHandle`, metrics read capture, tracing context propagation, logger, and gcsfuse stale handle errors.

Risks: invariants must hold across all close/error paths. Cancellation goroutine must not cancel a reader after a successful read returns. `skipBytes` improves throughput but can hide read errors while discarding. Short-read handling must distinguish expected EOF at limit from premature EOF. `invalidateReaderIfMisalignedOrTooSmall` uses object size to decide whether the current stream can serve the request.

Test signals: covered through `gcs_reader_test.go` for reuse, wrong offsets, limit too small, cancellation, inactive timeout wrapping, EOF/short read, and read handle reuse; a separate range reader test file exists outside this work item.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader.go -->
