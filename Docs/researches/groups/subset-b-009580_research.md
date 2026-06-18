<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcs_metrics_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/gcs_metrics_test.go

## Purpose

This Go test file validates OpenTelemetry GCS metrics emitted by gcsfuse filesystem operations against a monitored fake bucket. It covers request counts and latencies, download/read byte counters, reader lifecycle counters, cache-hit behavior, parallel download accounting, and retry categorization.

## Important APIs, Types, and Functions

`fakeBucketManagerWithMetrics` is a test `gcsx.BucketManager` that wraps fake buckets in `monitor.NewMonitoringBucket` and `gcsx.NewContentTypeBucket`, making storage calls produce GCS metrics. `createTestFileSystemWithMonitoredBucket` installs an OpenTelemetry manual reader, constructs `metrics.NewOTelMetrics`, configures `fs.ServerConfig`, optionally enables file cache or sparse chunk cache, and returns the fake bucket, FUSE filesystem, metric handle, and manual reader.

The tests exercise `server.LookUpInode`, `GetInodeAttributes`, `CreateFile`, `SyncFile`, `OpenFile`, and `ReadFile`, then assert metrics through `metrics.VerifyCounterMetric` and `metrics.VerifyHistogramMetric`.

## Control Flow

Each test builds an isolated monitored filesystem, seeds fake GCS objects when needed, performs a FUSE operation sequence, waits for metric processing, and reads the manual OpenTelemetry reader. Lookup tests expect `StatObject` increments from directory, file, and attribute refresh paths. Write tests create a local file handle and rely on `SyncFile` to trigger `CreateObject`. Read tests route through buffered read, file cache, or parallel download code paths and verify corresponding `read_type` attributes.

## State and Persistence Behavior

State is test-local: the global OpenTelemetry meter provider is replaced and restored with `t.Cleanup`, temporary cache directories are removed, fake bucket contents hold test objects, and metric data lives in the manual reader. There is no durable repository state. The tests depend on asynchronous metric export timing via `waitForMetricsProcessing`.

## Dependencies and Integration Points

The file integrates `internal/fs`, `internal/fs/wrappers`, `internal/monitor`, `internal/storage/fake`, `storageutil`, `metrics`, `tracing`, FUSE ops, and OpenTelemetry SDK metric readers. It specifically verifies that filesystem operations, storage wrappers, read managers, file cache, parallel downloads, and retry helpers all feed the public GCS metric instruments.

## Risks and Edge Cases

The expected counts encode details of lookup and read implementation. Changes to attribute refresh, wrapper layering, cache behavior, chunk sizing, or OpenTelemetry async collection can make assertions fail even if user-visible behavior is correct. The file cache test assumes the second read is served locally, and the parallel download test assumes 1 MiB chunks for a 5 MiB file.

## Test Signals

Coverage includes `gcs/request_count`, `gcs/request_latencies`, `gcs/download_bytes_count`, `gcs/read_count`, `gcs/reader_count`, `gcs/read_bytes_count`, and `gcs/retry_count`, including retry categories for HTTP 429 and `context.DeadlineExceeded`. It is a metrics regression suite rather than a production implementation file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcs_metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors.go -->
# sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors.go

## Purpose

This package defines filesystem-specific error types. The current file contains `FileClobberedError`, used to report that an object backing a file was modified or deleted externally while gcsfuse was accessing it.

## Important APIs, Types, and Functions

`FileClobberedError` has `Err error` for the underlying cause and `ObjectName string` for the affected GCS object. `Error()` formats a user-facing concurrent modification message including the object name and wrapped error. `Unwrap()` returns `Err`, enabling `errors.Is` and `errors.As` through Go's standard error chaining.

## Control Flow

The type is passive. Callers construct it around lower-level storage or consistency errors. When logged or returned, `Error()` is called by Go error formatting; when matched, `Unwrap()` exposes the original cause.

## State and Persistence Behavior

The error stores only in-memory fields for one failure. It has no global state, no synchronization, and no persistence.

## Dependencies and Integration Points

The only direct dependency is `fmt`. The integration point is any fs/inode/handle path that detects a clobbered object generation or missing source object and wants both a gcsfuse-specific diagnostic and normal wrapped-error behavior.

## Risks and Edge Cases

`Error()` prints `<nil>` when `Err` is nil, which is intentional per tests but can look odd to users. The type uses a pointer receiver, so nil pointer use would panic. Any change to the message string can affect tests and user-facing diagnostics.

## Test Signals

The paired test validates the exact message for nil and non-nil underlying errors and verifies `errors.Is` works when a cause is present.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors_test.go

## Purpose

This test file verifies the behavior of `FileClobberedError`, especially its user-facing string and wrapped error compatibility.

## Important APIs, Types, and Functions

`TestFileClobberedError` is a table-driven testify test. It constructs `FileClobberedError` values with object names and either a concrete underlying error or nil, compares `Error()` output, and checks `errors.Is` for the non-nil case.

## Control Flow

Each test case builds the error, calls `Error()`, compares the resulting string, and conditionally asserts standard wrapping behavior. The nil-underlying-error case verifies that the formatter still produces a stable `<nil>` suffix.

## State and Persistence Behavior

There is no external state. Test data is local to the table.

## Dependencies and Integration Points

The file depends on Go `errors`, `fmt`, `testing`, and `github.com/stretchr/testify/assert`. It protects the contract consumed by higher-level fs code that may match underlying errors after wrapping them in a clobbering diagnostic.

## Risks and Edge Cases

The test intentionally locks the full error string, making wording changes visible. It only checks `errors.Is` for non-nil causes and does not check `errors.As` or behavior when the wrapped error type has custom matching.

## Test Signals

Signals are narrow and strong: exact formatting and unwrap semantics for `FileClobberedError`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/gcsfuse_errors/gcsfuse_errors_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/grpc_metrics_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/grpc_metrics_test.go

## Purpose

This Go test file validates gRPC client metrics emitted when gcsfuse uses the gRPC storage client protocol. It uses a local reflective fake Google Storage service so tests can trigger client-side gRPC instrumentation without importing conflicting generated storage protobuf packages.

## Important APIs, Types, and Functions

`reflectFakeServer` implements dynamic handlers for `GetObject`, `ListObjects`, `ReadObject`, `StartResumableWrite`, and `WriteObject` using `dynamicpb` and `protoregistry`. `registerFakeStorageServer` manually registers the `google.storage.v2.Storage` service, including unary and streaming descriptors. `fakeStorageControlServer` returns a storage layout with HNS disabled. `createTestFileSystemWithGrpcMetrics` starts the fake gRPC service, a fake metadata server for project ID discovery, configures `storage.NewStorageHandle` with `ClientProtocol: cfg.GRPC` and `EnableGrpcMetrics`, then builds `fs.NewFileSystem`.

The tests are `TestGrpcMetrics_LookUpInode`, `TestGrpcMetrics_ReadFile`, and `TestGrpcMetrics_CreateFile`.

## Control Flow

Setup installs environment variables to bypass protobuf registration conflicts and point metadata lookup to the fake metadata server. The filesystem is wrapped with monitoring. Tests perform a short-timeout "poke" to avoid local DirectPath checks blocking the main operation, then execute lookup, read, or create/sync flows. Metrics are collected from an OpenTelemetry manual reader and asserted using subset/at-least matching for `grpc.client.attempt.started` and `grpc.client.call.duration`.

## State and Persistence Behavior

The gRPC server, metadata HTTP server, OpenTelemetry provider, and environment variables are process-global or local runtime resources cleaned with `t.Cleanup`. The fake service returns synthetic object metadata and read bytes; no durable storage is written. Timing sleeps account for delayed metric export.

## Dependencies and Integration Points

The file integrates `internal/storage`, `storageutil`, `gcsx.BucketManager`, `fs.ServerConfig`, monitoring wrappers, OpenTelemetry metrics, gRPC server APIs, storage control protobufs, and dynamic protobuf reflection. It tests the interaction between the gcsfuse FUSE layer, storage gRPC client, Google API gRPC metrics, and monitoring wrapper.

## Risks and Edge Cases

The tests are sensitive to DirectPath initialization behavior, environment variables, metric naming, and generated protobuf descriptors being registered in the global registry. The fake server implements only the paths needed by these tests; production behavior such as pagination, errors, checksums, and full streaming write semantics are not covered.

## Test Signals

Lookup verifies `GetObject` gRPC metrics. Read verifies `ReadObject` metrics. Create/sync verifies an attempted `BidiWriteObject` call even though the fake server returns unimplemented. Assertions use at-least/subset checks to tolerate extra client attempts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/grpc_metrics_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle.go -->
# sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle.go

## Purpose

This file implements `DirHandle`, the FUSE directory-handle state used to serve `ReadDir` and `ReadDirPlus` from a `inode.DirInode`. It buffers directory entries per handle, resolves GCS file-vs-directory name conflicts, merges unsynced local file entries, and assigns FUSE directory offsets.

## Important APIs, Types, and Functions

`DirEntry` abstracts common operations over `fuseutil.Dirent` and `fuseutil.DirentPlus`. The private wrappers `dirent` and `direntPlus` adapt the concrete FUSE types. `DirHandle` stores the backing `inode.DirInode`, an `implicitDirs` flag, a locker, cached `entries`, cached `entriesPlus`, and validity flags.

`NewDirHandle` constructs the handle and invariant-checking lock. `fixConflictingNames` expects sorted entries and appends `inode.ConflictingFileNameSuffix` to the non-directory side of a file/directory name conflict. It also suppresses duplicate file entries when the same file exists in both GCS and local pending entries. `sortAndResolveEntries` merges local entries, sorts, resolves conflicts, and assigns offsets. `readAllEntries` and `readAllEntryCores` page through inode listing APIs. Public methods are `ReadDir`, `FetchEntryCores`, and `ReadDirPlus`.

## Control Flow

`ReadDir` resets cached entries when offset is zero, lazily calls `ensureEntries`, validates the seek offset, then writes dirents into the caller buffer until full. `ensureEntries` locks the inode, reads all paginated entries, sorts and resolves names, then stores the cache. `FetchEntryCores` similarly resets plus-cache state on offset zero and reads all entry cores if the plus cache is invalid. `ReadDirPlus` consumes prebuilt `DirentPlus` entries, merges local entries, sorts/resolves/offsets them once, and writes `DirentPlus` responses from the requested offset.

## State and Persistence Behavior

State is per open directory handle. Cached entry slices persist until offset zero rewinds or the handle is discarded. Offsets are one-based and consecutive. Each listed entry receives a bogus non-root inode ID in `readAllEntries` because FUSE `readdir` does not produce lookup-count forgets for minted IDs. There is no disk persistence.

## Dependencies and Integration Points

The handle depends on `internal/fs/inode` for directory listing and conflict suffix semantics, `internal/locker` for invariant locks, FUSE ops/util types for ABI-facing dirent encoding, and Go `cmp`, `maps`, and `slices`. It sits between the filesystem operation handlers and `DirInode` implementations such as `dirInode` and `baseDirInode`.

## Risks and Edge Cases

Correctness depends on sorted input before conflict resolution, stable offset assignment, and duplicate handling for local-vs-GCS file entries. Invalid `seekdir` offsets return `fuse.EINVAL`. The fake inode ID strategy is a known tradeoff. `FetchEntryCores` returns nil cores when the plus cache is already valid and offset is nonzero, so callers must preserve previously fetched plus entries.

## Test Signals

The paired tests cover GCS-only, local-only, mixed local/GCS listings, duplicate same-name local/GCS files, local file vs GCS directory conflict suffixing, empty listings, `ReadEntryCores`, `FetchEntryCores` cache behavior, and `ReadDirPlus` conflict/offset behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle_test.go

## Purpose

This ogletest suite validates `DirHandle` listing behavior against a fake GCS bucket and real `inode.DirInode` instances. It focuses on merged local/GCS entries, conflict resolution, entry core fetching, and `ReadDirPlus` plus-entry handling.

## Important APIs, Types, and Functions

`DirHandleTest` owns a context, simulated clock, syncer bucket, and handle. `resetDirHandle` builds a `NewDirInode` for `testDir` and a `NewDirHandle`. Helper methods validate plain dirents, build `DirentPlus` values, validate plus entries, and validate file `Core` results.

Test methods include `EnsureEntriesWithLocalAndGCSFiles`, `EnsureEntriesWithSameNameLocalAndGCSFile`, `EnsureEntriesWithSameNameLocalFileAndGCSDirectory`, `ReadAllEntryCoresReturnsAllEntryCores`, `FetchEntryCoresFetchesCores`, `FetchEntryCoresNonZeroOffsetNoFetchIfCacheValid`, `ReadDirPlusSameNameLocalAndGCSFile`, and `ReadDirPlusSameNameLocalFileAndGCSDirectory`.

## Control Flow

Tests seed fake GCS objects under `testDir`, pass synthetic local-file maps, call unexported helpers or public handle methods, and inspect `dh.entries`, `dh.entriesPlus`, returned cores, and offsets. The `ReadDirPlus` tests pass prebuilt plus entries rather than relying on kernel lookup paths.

## State and Persistence Behavior

State is held in the simulated fake bucket and in the `DirHandle` cache fields. Each test starts from a reset handle and simulated clock. No persistent files are written.

## Dependencies and Integration Points

The suite exercises `handle.DirHandle` with `inode.NewDirInode`, `gcsx.NewSyncerBucket`, `fake.NewFakeBucket`, `storageutil.CreateObject`, FUSE dirent types, metadata type classification, and `semaphore.NewWeighted` for inode construction.

## Risks and Edge Cases

The tests inspect internal slices directly, so they are sensitive to sorting order and offset assignment. They cover same-name local/GCS duplicate suppression and directory/file conflict suffixing, but they do not exhaustively test pagination or buffer truncation behavior in `ReadDir`.

## Test Signals

Signals include entry counts, entry names/types, file core names and min object names, plus-cache invalidation behavior, and consecutive offsets for conflict-resolved `DirentPlus` entries.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/dir_handle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/file.go -->
# sources/user-network-fs/gcsfuse/internal/fs/handle/file.go

## Purpose

This file implements `FileHandle`, the per-open-file read-side state for gcsfuse. It coordinates reads through legacy random readers, the newer read manager, optional kernel-optimized readers, file cache or shared chunk cache, workload visualization, metrics/tracing, and inode generation consistency.

## Important APIs, Types, and Functions

`FileHandle` stores the backing `*inode.FileInode`, an invariant mutex, cached `gcsx.RandomReader`, cached `gcsx.ReadManager`, optional `kernelReader`, file cache and shared chunk cache handles, cache/read configuration, metrics/tracing handles, open mode, worker pool, global buffered-read semaphore, and a FUSE handle ID.

`NewFileHandle` registers the handle with the inode, optionally constructs a kernel reader, and initializes invariant locking. `Destroy` deregisters the handle and destroys reader resources. `ReadWithReadManager` reads through `read_manager.ReadManager`, falling back to `inode.Read` when the source generation is not authoritative. `ReadWithKernelReader` uses MRD or range-reader based kernel readers when enabled. `Read` uses `gcsx.RandomReader` for the older read path. Helpers manage lock ordering, reader/read-manager destruction, generation validation, open mode access, and direct-I/O unfinalized object size-check skipping.

## Control Flow

Read methods enter with the inode lock held and unlock it internally. They first ensure cache content if required, then choose between local inode reads and GCS-backed readers based on `SourceGenerationIsAuthoritative`. When using GCS-backed state, they release/reacquire locks via `lockHandleAndRelockInode` to preserve lock ordering, validate cached reader generation, create a new reader/read manager if stale, and perform `ReadAt`. EOF is normalized and non-EOF errors are wrapped with context. `ReadWithReadManager` can wrap the read manager in a workload insight visualizer when configured.

## State and Persistence Behavior

Reader and read-manager instances persist for the lifetime of the file handle as long as their object generation matches the inode's source generation; size is refreshed on valid reuse. Destroy tears them down and deregisters read/write handle counts from the inode. File cache/chunk cache state is external. The workload visualization path may create its configured output file.

## Dependencies and Integration Points

This file sits between FUSE file operations and `inode.FileInode`, `internal/gcsx`, `kernel_readers`, `read_manager`, file cache, workerpool, metrics, tracing, and workload insight. It depends on `cfg.Config` for feature flags, `util.OpenMode` for access/direct flags, and semaphores for buffered-read block limits.

## Risks and Edge Cases

Lock order is a major risk: read paths must avoid deadlocks between inode locks and handle locks. Generation mismatch must destroy stale readers to avoid reading clobbered content. Cache-content mode intentionally forces inode fallback. Kernel reader must be initialized only when enabled. `shouldSkipSizeChecks` assumes `readManager` is non-nil and is only valid after manager creation; it is limited to rapid-write bucket types, direct I/O, unfinalized objects, and reads extending past known size.

## Test Signals

The paired tests cover read/read-manager success, concurrent reads, EOF and wrapped errors, fallback to inode content, generation-change invalidation, kernel-reader zonal vs standard behavior, lock-order deadlock scenarios, destroy/invariant calls, open mode preservation, buffered full and concurrent reads, direct-I/O size-check conditions, and workload insight file creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/file.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/file_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/handle/file_test.go

## Purpose

This testify suite validates `FileHandle` behavior across random-reader, read-manager, kernel-reader, buffered-read, lock-order, lifecycle, open-mode, and workload-insight paths. It uses fake buckets and real file inodes to exercise the handle close to production control flow.

## Important APIs, Types, and Functions

`fileTest` owns a context, simulated clock, and syncer bucket. `createDirInode` constructs a parent directory inode. `createFileInode` creates a fake GCS object and corresponding `inode.FileInode`. The suite uses `read_manager.MockReadManager`, `gcsx.MockRandomReader`, `storage.TestifyMockBucket`, fake multi-range downloaders, worker pools, and semaphores.

Named tests cover reader validity, read success and concurrency, error paths, inode fallback, generation invalidation, kernel reader success/failures, open mode, destroy and invariants, lock helpers, buffered reads, size-check skipping, and workload visualization.

## Control Flow

Most tests build an inode and file handle, manually take the inode lock as required by production method contracts, call the target `FileHandle` method, and then assert data, errors, internal reader state, or mock expectations. Concurrency tests spawn multiple goroutines reading random ranges through a shared file handle and use timeouts to detect deadlocks. Kernel-reader tests branch between zonal MRD and standard range-reader behavior via bucket type.

## State and Persistence Behavior

Fake bucket objects hold test content and generations. File handles cache readers/read managers across calls. Some tests write and sync the inode to change GCS generation, proving stale cached readers are replaced. Workload insight writes `test.txt` and removes it after validation. Worker pools are stopped with defer.

## Dependencies and Integration Points

The suite integrates `inode.FileInode`, `gcsx.SyncerBucket`, fake storage buckets, content cache, read manager, kernel reader dependencies, workerpool, metrics/tracing noops, FUSE handle IDs, semaphores, and `util.OpenMode`. It validates contracts assumed by higher-level FUSE file operation handlers.

## Risks and Edge Cases

The tests are intentionally close to internal locking contracts; incorrect lock ownership can deadlock or panic. Mock-based error tests depend on exact method calls. `shouldSkipSizeChecks` has a panic case for nil read manager but the table currently does not activate it. Concurrency tests use random offsets and timeouts, which can reveal races but may be timing-sensitive.

## Test Signals

Signals include byte-for-byte read data, response sizes, EOF propagation, wrapped error matching, stale reader replacement after generation changes, MRD/range-reader invocation, explicit nil kernel-reader error, no deadlocks under lock contention, open-mode round trips, buffered-read reconstruction, rapid-write direct-I/O skip decisions, and workload insight output file existence.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/handle/file_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/hns_bucket_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/hns_bucket_test.go

## Purpose

This test file validates filesystem behavior for hierarchical namespace buckets. It covers directory listing, deleting explicit and implicit-looking directories, and cache behavior when objects or folders are deleted locally then recreated remotely before TTL expiry.

## Important APIs, Types, and Functions

`HNSBucketTests` composes `fsTest`, `RenameFileTests`, and `RenameDirTests` under a suite with `EnableHns` and atomic rename enabled. `HNSCachedBucketMountTest` configures an HNS fake bucket wrapped in a fast stat cache with directory type caching and file cache defaults. Shared constants define expected file content, HNS type-cache settings, and expected `foo` entries.

## Control Flow

The main HNS suite creates folders and objects in setup, reads `foo` with `os.ReadDir`, removes folders with `os.RemoveAll`, and checks stat failures. The cached suite creates `hns/cache`, creates and stats files or directories through the mount, deletes them, recreates matching objects directly through the uncached bucket, verifies immediate stat still reports not found due to cache, advances cache time past TTL, and verifies the path reappears.

## State and Persistence Behavior

State lives in fake HNS buckets, mounted filesystem state from `fsTest`, metadata/stat caches, and simulated cache time. The tests explicitly rely on cache TTL: local deletion records negative cache state that persists until `cacheClock.AdvanceTime`.

## Dependencies and Integration Points

The file integrates HNS-enabled fs configuration, fake hierarchical buckets, metadata stat/type cache, caching bucket wrappers, file cache config, storage utilities, OS filesystem calls, and rename test suites. It tests interactions among HNS folder APIs, placeholder objects, implicit directory compatibility, and cache invalidation.

## Risks and Edge Cases

HNS buckets represent directories as folders, while gcsfuse also encounters placeholder objects and descendants. Recursive delete must remove the visible directory regardless of backing shape. Cache tests encode the consistency tradeoff where remote recreation remains invisible until TTL expiry, which can surprise users but protects local delete semantics.

## Test Signals

Signals include `os.ReadDir` entry names/types, successful `os.RemoveAll`, expected `no such file or directory` stat errors, and post-TTL successful stats for remotely recreated file and directory paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/hns_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_test.go

## Purpose

This integration-style test suite validates a read-focused filesystem mount with implicit directories enabled. It checks how files, explicit directory placeholder objects, implicit directories from descendants, conflicts, unknown names, directory removal, timestamps, and symlink rename behavior appear through the mounted filesystem.

## Important APIs, Types, and Functions

`ImplicitDirsTest` embeds `fsTest` and enables `serverCfg.ImplicitDirectories`. Tests use `t.createObjects`, `storageutil`, direct bucket deletes, `fusetesting.ReadDirPicky`, `os.Stat`, `os.Lstat`, `os.Remove`, `os.Rename`, and symlink helpers.

Named cases include `NothingPresent`, `FileObjectPresent`, `DirectoryObjectPresent`, `ImplicitDirectory_DefinedByFile`, `ImplicitDirectory_DefinedByDirectory`, multiple `ConflictingNames_*` tests, `StatUnknownName_*`, `ImplicitBecomesExplicit`, `ExplicitBecomesImplicit`, `Rmdir_*`, `AtimeCtimeAndMtime`, and `RenameSymlinkToImplicitDir`.

## Control Flow

Each test seeds fake GCS object names out of band, performs POSIX operations through the mount, and asserts returned file info. Conflict tests create both `foo` and `foo/` or `foo/bar`, then verify listings prefer the directory as `foo` and expose the file or symlink as `foo\n`. Removal tests attempt to delete non-empty implicit directories, delete empty explicit placeholders, and verify directory contents after removal.

## State and Persistence Behavior

The fake bucket is the source of truth, while the mounted filesystem synthesizes implicit directories. Explicit placeholders can be added or removed during a test and subsequent stats should still classify the path correctly. File timestamps for implicit directories are derived from mount or clock state and only checked as "reasonable".

## Dependencies and Integration Points

The suite exercises the whole path from `dirInode` lookup/listing through `DirHandle` conflict resolution to FUSE-visible POSIX calls. It depends on storage object naming conventions, metadata symlink representation, FUSE testing helpers, and fake bucket operations.

## Risks and Edge Cases

Conflict suffix semantics are user-visible and rely on newline being illegal in GCS object names. Unknown-name checks protect prefix false positives such as `foo` vs `foop`. Rmdir behavior must distinguish empty explicit directories from implicit non-empty directories. Remote mutation between implicit and explicit forms must not break stat behavior.

## Test Signals

Signals include directory/file mode bits, sizes, nlink, symlink mode, readlink target, not-found detection, not-empty errors, empty parent listings after rmdir, and timestamp proximity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_with_cache_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_with_cache_test.go

## Purpose

This small integration test suite validates recursive removal and rename of implicit directories when directory type caching is enabled.

## Important APIs, Types, and Functions

`ImplicitDirsWithCacheTest` embeds `fsTest`, enables implicit directories, and sets `DirTypeCacheTTL` to three minutes. `TestRemoveAll` invokes external `rm -r` on an implicit directory. `TestRenameImplicitDir` uses `os.Rename` and validates the moved descendants.

## Control Flow

Tests seed fake GCS objects under `foo/`, making `foo` an implicit directory. `TestRemoveAll` runs `rm -r <mount>/foo/` and expects no output or error. `TestRenameImplicitDir` renames `foo` to `fooNew`, stats the destination directory and children, and verifies the original path no longer exists.

## State and Persistence Behavior

State lives in the fake bucket, mounted filesystem, and type cache. The tests specifically exercise cache-aware operations that update or invalidate cached type knowledge during recursive remove or rename.

## Dependencies and Integration Points

The suite integrates `fsTest`, implicit directory lookup/listing, type cache TTL behavior, OS commands, POSIX rename, and recursive delete/rename logic in the filesystem layer.

## Risks and Edge Cases

External `rm` behavior depends on the host command. Rename and recursive delete of implicit directories require translating a synthetic directory into operations on descendant objects while maintaining cache correctness. The test verifies visible results but not the exact bucket object list after operations.

## Test Signals

Signals are successful `rm -r`, successful rename, destination stats for directory and child files, and source-path not-found error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_with_cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir.go

## Purpose

This file implements `baseDirInode`, a read-only root-like directory for multi-bucket mounts. Its children are bucket roots resolved lazily by name through a `gcsx.BucketManager`; listing all buckets is intentionally unsupported.

## Important APIs, Types, and Functions

`baseDirInode` stores inode ID, root name, attributes, lookup count, a bucket manager, a cache of initialized buckets by name, a metric handle, and a type-cache deprecation flag. `NewBaseDirInode` constructs it and initializes lookup count and lock. It implements the `DirInode` interface with locking, lookup count, attributes, child lookup, listing stubs, mutation stubs, cache hooks, rename/delete stubs, prefetch hooks, context hooks, and writer counters.

`LookUpChild` is the main supported operation: it checks the local bucket map, calls `bucketManager.SetUpBucket(ctx, name, true, metricHandle)` on miss, caches the resulting `SyncerBucket`, and returns a `Core` for the bucket root.

## Control Flow

Base-dir lookups take an exclusive lock via `LockForChildLookup` because the bucket cache may be mutated. Attribute calls return static directory attributes with `Nlink=1`. `ReadEntries` and `ReadEntryCores` return `syscall.ENOTSUP` because enumerating accessible buckets is expensive and unsupported. Mutating operations return `fuse.ENOSYS`.

## State and Persistence Behavior

The inode caches successfully opened buckets in memory for the mount lifetime. Lookup counts track kernel references. No directory listing cache, type cache, prefetch context, local file entries, or active-writer state is meaningful for the base directory. There is no persistence beyond the bucket manager's external behavior.

## Dependencies and Integration Points

The file integrates with `gcsx.BucketManager`, `gcsx.SyncerBucket`, `metrics.MetricHandle`, FUSE inode attributes and errors, GCS object/folder types, and the common `DirInode` interface. It is used for dynamic or multi-bucket root mounts where child names are bucket names.

## Risks and Edge Cases

Because listing is unsupported, callers must handle `ENOTSUP` for directory reads. Bucket setup failures propagate directly. The constructor ignores the supplied `name` for stored name and sets `NewRootName("")`, which is intended for the base root. Mutation stubs must remain consistently unsupported to avoid accidental bucket creation/deletion semantics.

## Test Signals

The paired tests verify ID/name, lookup count, attributes, successful and failed bucket lookup, bucket setup caching, unsupported `ReadEntryCores`, list-cache invalidation default, and type-cache deprecation flag reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir_test.go

## Purpose

This ogletest suite validates `baseDirInode`, the multi-bucket base directory inode.

## Important APIs, Types, and Functions

`BaseDirTest` owns a context, simulated clock, fake bucket manager, and locked `DirInode`. `fakeBucketManager` maps bucket names to `gcsx.SyncerBucket` instances and counts setup calls. `resetInode` constructs `NewBaseDirInode` with fixed attributes and locks it for tests.

Tests cover `ID`, `Name`, lookup counts, attributes with both clobber-check values, missing bucket lookup, successful lookup of bucket roots, cached bucket setup, kernel list-cache invalidation behavior, unsupported `ReadEntryCores`, and `IsTypeCacheDeprecated` true/false construction.

## Control Flow

Setup creates fake buckets `bucketA` and `bucketB`, constructs the base inode, and locks it. Lookup tests call `LookUpChild` and inspect returned `Core` fields. Cache tests check that repeated bucket lookups do not call `SetUpBucket` again for successful names.

## State and Persistence Behavior

The fake bucket manager's `setupTimes` counter and the base inode's internal bucket map are the observed mutable state. Tests unlock the inode in teardown. No durable files are written.

## Dependencies and Integration Points

The suite uses fake GCS buckets, `gcsx.NewSyncerBucket`, FUSE inode attributes, metadata type classification, no-op metrics, and ogletest assertions. It validates the base directory's implementation of the common `DirInode` contract.

## Risks and Edge Cases

The suite does not exercise every unsupported mutation stub, but it verifies listing unsupported behavior through `ReadEntryCores`. Cached lookup tests assume failed lookups are not cached and successful lookups are cached.

## Test Signals

Signals include expected root local/GCS names, bucket root type as `metadata.ImplicitDirType`, setup-call counts, `syscall.ENOTSUP` on listing, and boolean type-cache deprecation reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/base_dir_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/core.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/core.go

## Purpose

This file defines `Core`, the compact pre-inode description used throughout gcsfuse to represent a file, directory, folder, local pending file, implicit directory, or missing lookup result before constructing or returning a full inode.

## Important APIs, Types, and Functions

`Core` contains `FullName Name`, optional `Bucket *gcsx.SyncerBucket`, optional `MinObject *gcs.MinObject`, optional HNS `Folder *gcs.Folder`, and `Local bool`. `Exists` reports whether the pointer receiver is non-nil. `Type` maps the core to `metadata.Type`: nil is unknown, no object/folder/local with a directory name is implicit directory, directory names are explicit directory, symlink metadata is symlink, and all else is regular file. `SanityCheck` verifies folder/object names match `FullName` and that non-local file names have backing objects.

## Control Flow

Lookup/listing code constructs `Core` values from stat, list, folder, or local state. Higher layers inspect `Type()` to choose FUSE dirent type, inode type, cache insertion, and conflict behavior. `SanityCheck` is a guard against inconsistent metadata before using a core.

## State and Persistence Behavior

`Core` has no owned persistence. It references bucket/object/folder metadata supplied by storage or local inode state. A nil `*Core` is the canonical nonexistence representation.

## Dependencies and Integration Points

It integrates `internal/cache/metadata`, `gcsx.SyncerBucket`, `gcs.MinObject`, `gcs.Folder`, and name/symlink helpers in the inode package. It is a central data contract between directory lookup/listing, file/dir inode construction, and metadata caches.

## Risks and Edge Cases

Type precedence matters: HNS folders and object-backed directory names are explicit directories; local objectless file cores are regular files; objectless non-local file names are invalid. `Exists` on a nil pointer is intentionally safe because methods with pointer receivers can be called on nil in Go, but `SanityCheck` uses a value receiver and requires a real value.

## Test Signals

The paired tests verify file, local file, explicit directory, implicit directory, bucket root, nil nonexistent type, sanity-check mismatches, missing object errors, HNS folder sanity, and folder explicit-directory type.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/core.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/core_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/core_test.go

## Purpose

This ogletest suite validates `Core` classification and sanity checks.

## Important APIs, Types, and Functions

`CoreTest` sets up a fake syncer bucket and simulated clock. Tests create GCS objects or folders, construct `inode.Core` values with different combinations of `FullName`, `MinObject`, `Folder`, and `Local`, then assert `Exists`, `Type`, and `SanityCheck`.

## Control Flow

Tests use `storageutil.CreateObject` and `bucket.CreateFolder` to obtain realistic metadata. They construct names with `NewRootName`, `NewFileName`, and `NewDirName`. Sanity tests mutate the relationship between name and object metadata to verify expected errors.

## State and Persistence Behavior

State is test-local fake bucket data and simulated clock. No persistent files are created.

## Dependencies and Integration Points

The suite covers `metadata.Type` mapping, fake storage, `gcsx.SyncerBucket`, storage utilities, HNS folder creation, and symlink-aware type classification indirectly through the default regular file path.

## Risks and Edge Cases

The tests protect nil-core behavior and objectless local file behavior, both of which are easy to regress. They do not construct an actual symlink metadata object in this file, so symlink type coverage depends on other suites.

## Test Signals

Signals include `RegularFileType`, `ExplicitDirType`, `ImplicitDirType`, `UnknownType`, nil/non-nil sanity-check results, and HNS folder explicit directory classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/core_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/dir.go

## Purpose

This file defines the `DirInode` interface and implements `dirInode`, the primary GCS bucket-backed directory inode. It owns directory lookup, listing, type-cache interaction, implicit directory synthesis, HNS folder handling, child creation/deletion/rename, recursive deletion, local-file listing, kernel list-cache invalidation, and metadata-prefetch lifecycle hooks.

## Important APIs, Types, and Functions

`DirInode` extends `Inode` with child lookup, file/folder rename, descendant reads, paginated entry reads, creation/deletion of files, dirs, symlinks, recursive delete, type-cache updates, lookup locking, list-cache invalidation, prefetch cancellation, lifecycle context, unlink flags, and active writer counters. `dirInode` stores the bucket, clocks, optional `MetadataPrefetcher`, recursive context/cancel function, config flags, name, attributes, lock, lookup count, optional type cache, previous listing timestamp, HNS/symlink/unsupported-path flags, unlinked state, metadata TTL, and active-writer count.

Key helpers include `findExplicitInode`, `findExplicitFolder`, `findDirInode`, `lookUpConflicting`, `fetchCoreEntity`, `listObjectsAndBuildCores`, `readObjectsUnlocked`, `deletePrefixRecursively`, and `isBucketHierarchical`.

## Control Flow

`NewDirInode` validates directory names, builds a context derived from the parent directory context, creates the optional metadata prefetcher, and initializes legacy type cache unless deprecated. `LookUpChild` handles conflict suffixes, then optionally tries stat-cache-only lookup when type-cache deprecation is enabled, otherwise reads legacy type-cache hints. Unknown lookups trigger metadata prefetch and concurrently stat/list file and directory candidates with `errgroup`; directories win over files. Results update legacy type cache when enabled.

Listing flows through `ReadEntryCores` -> `readObjects` -> `listObjectsAndBuildCores`, which issues delimiter-based `ListObjects`, converts min objects and collapsed prefixes into `Core` records, handles unsupported paths, HNS folder cores, implicit directories, continuation tokens, and type-cache insertion. Mutation flows create objects/folders/symlinks, delete files/dirs, recursively delete prefixes, move objects, or rename folders while cancelling current prefetch and tracking active writers when stale prefetch could be harmful.

## State and Persistence Behavior

Persistent storage changes happen through the GCS bucket: object creation, copy, delete, move, folder create/delete/rename, and recursive delete. In-memory state includes lookup counts, type cache, previous listing timestamp, lifecycle cancellation context, unlinked flag, and active-writer count. Metadata prefetch can update cache asynchronously unless cancelled or blocked by active writers. HNS deleted folder inodes can be marked unlinked.

## Dependencies and Integration Points

The file is central to fs integration: it uses `cfg`, metadata cache types, `gcsx.SyncerBucket`, `locker`, logger, caching errors, storage GCS APIs, storage utilities, FUSE attributes/dirents, clocks, errgroups, and semaphores. `DirHandle` consumes `ReadEntries` and `ReadEntryCores`; higher-level filesystem operations consume creation/deletion/rename methods.

## Risks and Edge Cases

The largest risks are stale metadata from caches or prefetch, races with writers, HNS-vs-flat directory representation differences, conflict suffix lookup correctness, unsupported path filtering, and recursive delete closure/concurrency behavior. Directory entries must prefer directories over files for conflicts. Type-cache deprecation splits behavior between legacy type cache and stat-cache-only lookup. `readObjectsUnlocked` must avoid cache updates after context cancellation.

## Test Signals

Coverage is distributed across many files: implicit directory tests cover lookup/list conflict semantics and rmdir behavior; HNS tests cover folder listing/deletion/cache consistency; dir prefetcher tests cover async cache population and cancellation; dir handle tests cover listing conversion; base/core tests cover shared interfaces and `Core` classification.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher.go

## Purpose

This file implements `MetadataPrefetcher`, an asynchronous helper that warms directory metadata/type caches after an unknown child lookup. It is designed to improve sibling lookup performance while avoiding stale cache writes during directory lifecycle changes or active writes.

## Important APIs, Types, and Functions

Constants `prefetchReady` and `prefetchInProgress` define atomic state. `MetadataPrefetcher` stores cache TTL, atomic state, inode lifecycle context, current-run cancel function, maximum prefetch count, cache clock, last successful prefetch time, large-directory flag, shared semaphore, a list function callback, and a `shouldRun` callback.

`NewMetadataPrefetcher` wires config values and callbacks. `Run(fullObjectName string)` decides whether to start a background prefetch. `Cancel()` cancels only the current run, not the owning inode context.

## Control Flow

`Run` exits if the inode context is nil/cancelled, if `shouldRun` is false, or if the previous successful prefetch is still within TTL. It atomically switches ready to in-progress, creates a child context for the run, and launches a goroutine. The goroutine tries to acquire the shared semaphore without waiting; if unavailable it skips. It optionally uses `fullObjectName` as `StartOffset` for directories previously marked large, then pages `listCallFunc` up to `maxPrefetchCount`, respecting context cancellation before each call. If the limit is reached with a continuation token, it marks the directory large. On successful completion it records `lastPrefetchTime` and always resets state.

## State and Persistence Behavior

State is in-memory and per directory inode. It tracks current run state, cancellation function, last prefetch timestamp, and large-directory heuristic. Cache persistence is delegated to the `listCallFunc` callback, normally `dirInode.readObjectsUnlocked`, which updates metadata cache under the inode lock after checking context cancellation.

## Dependencies and Integration Points

The prefetcher integrates `cfg.MetadataCache`, inode lifecycle contexts, `timeutil.Clock`, shared `semaphore.Weighted`, `logger`, and `dirInode` listing/cache insertion via callback. `dirInode.LookUpChild` triggers it for unknown type-cache entries; directory writes call cancel/active-writer hooks to avoid stale updates.

## Risks and Edge Cases

The shared `runCancelFunc` is written without its own mutex and relies on caller-side directory locking for setup/cancel coordination. Since semaphore acquisition is non-blocking, prefetch can be skipped under load. TTL is updated only after successful completion. Large-directory mode starts at the looked-up object and will not prefetch lexicographically earlier siblings. Correctness depends on callback-side context checks before cache updates.

## Test Signals

The paired tests cover trigger-on-unknown, large-directory start offset, disabled config, single-run atomic state, destroy cancellation, max count and multi-page limits, shared semaphore concurrency limits, TTL guard, write cancellation race, recursive cancellation, nil context skip, active-writer skip, and stale-prefetch avoidance after delete.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher_test.go

## Purpose

This testify suite validates directory metadata prefetch behavior, including cache warming, large-directory heuristics, concurrency limits, TTL gating, cancellation, and races with writes.

## Important APIs, Types, and Functions

`DirPrefetchTest` owns a context, syncer bucket, fake bucket, simulated clock, `*dirInode`, and config. `setup` builds a directory inode with metadata prefetch enabled or disabled. Helper callbacks include `blockingListFunc` and `mockListFuncWithCtr`. Tests directly inspect `MetadataPrefetcher` atomic state, type cache values, semaphore behavior, and cancellation effects.

## Control Flow

Tests seed directory objects, call `LookUpChild` to trigger prefetch or call `MetadataPrefetcher.Run` directly, then use `assert.Eventually`, sleeps, or blocking channels to coordinate goroutines. Some tests replace the prefetcher's list callback with custom functions that block, count calls, return stale data, or observe context cancellation.

## State and Persistence Behavior

State includes fake bucket contents, `dirInode` type cache, prefetcher atomic state, large-directory flag, last prefetch time, semaphore permits, and cancellable contexts. The suite destroys the inode in teardown, cancelling prefetch contexts. No durable files are written.

## Dependencies and Integration Points

The suite integrates `NewDirInode`, `MetadataPrefetcher`, fake GCS buckets, storage utilities, metadata type cache, simulated clock, semaphores, contexts, atomics, and testify suite/assertions. It validates the contract between `dirInode.LookUpChild`, prefetch callback cache insertion, and directory write cancellation.

## Risks and Edge Cases

Several tests are timing-sensitive and depend on goroutine scheduling. The race-with-delete test is important because stale prefetch data must not overwrite fresh cache invalidation after a write. Large-directory tests encode lexicographic start-offset behavior and max-prefetch limits.

## Test Signals

Signals include expected cache entries for sibling files/implicit dirs, unknown cache entries outside start offset or beyond max count, `prefetchReady` restoration, context cancellation, semaphore saturation, call counts, TTL-respected call suppression, no cache update after cancel, and no prefetch when inode context is nil/cancelled or active writers exist.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/inode/dir_prefetcher_test.go -->
