# sources/distributed-fs/juicefs/pkg/meta/base.go

## Purpose

`base.go` is the shared metadata orchestration layer for JuiceFS. It defines the backend-facing `engine` interface and the `baseMeta` implementation that wraps concrete metadata stores with common filesystem semantics: sessions and heartbeats, permissions, quota/stat accounting, open-file and symlink caches, trash and delayed deletion workflows, slice allocation and compaction, cloning, directory iteration, ACL/token helpers, and metadata dump/load streaming.

The file is intentionally backend-neutral. Concrete Redis, SQL, KV, and other engines implement `engine.do*` methods, while `baseMeta` owns cross-backend policy, local concurrency controls, Prometheus metrics, and consistent updates around those backend calls.

## Important APIs, Types, and Functions

- `engine` is the central adapter contract. It covers counters, format/session lifecycle, inode/dentry/attribute operations, chunk/slice operations, directory stat and quota persistence, trash/pending object scans, ACLs, tokens, changelog cleanup, directory handlers, and dump/load hooks.
- `baseMeta` is the shared state holder. Key fields include `fmt`, `root`, `sid`, `of` open-file cache, `removedFiles`, `compacting`, delete-slice channels, symlink cache, session context/wait groups, directory stat cache, quota maps, free inode/slice ID ranges, Prometheus collectors, and the concrete `engine`.
- `fsStat`, `dirStats`, `dirParents`, and quota maps maintain local buffered or cached accounting before backend flush.
- `symlinkCache` wraps `sync.Map` plus an atomic size counter and periodically evicts entries when capacity pressure crosses 75%.
- `ugQuotaDelta`/`ugQuotaDeltas` aggregate user/group quota deltas, and `batchCloneResult` carries backend batch-clone accounting.
- `DirHandler`, `dirBatch`, `dirFetcher`, and `dirHandler` implement batched directory listing with injected `.`/`..`, cached fetch windows, and local insert/delete adjustments.

Major public methods:

- Lifecycle and metrics: `Load`, `Init`, `NewSession`, `refresh`, `CloseSession`, `FlushSession`, `InitSharedMetrics`, `InitMetrics`, `OnReload`, `OnMsg`.
- Namespace and attributes: `Lookup`, `Resolve`, `Access`, `GetAttr`, `SetAttr`, `CheckSetAttr`, `Mknod`, `Create`, `Mkdir`, `Symlink`, `Link`, `Unlink`, `Rmdir`, `Rename`, `SetXattr`, `RemoveXattr`.
- File data and chunks: `Open`, `Read`, `NewSlice`, `Write`, `Truncate`, `Fallocate`, `Close`, `InvalidateChunkCache`, `Compact`, `CompactAll`, `compactChunk`.
- Directory and path utilities: `Readdir`, `NewDirHandler`, `GetParents`, `GetPaths`, `walk`, `Chroot`, internal `resolve`.
- Maintenance: `CleanStaleSessions`, `cleanupDeletedFiles`, `cleanupSlices`, `cleanupTrash`, `CleanupTrashBefore`, `cleanupDelayedSlices`, `CleanupDetachedNodesBefore`, `ScanDeletedObject`, `Check`.
- Copy/export helpers: `Clone`, `cloneEntry`, `BatchClone`, `DumpMetaV2`, `LoadMetaV2`.
- ACL/token wrappers: `SetFacl`, `GetFacl`, ACL cache helpers, `StoreToken`, `UpdateToken`, `LoadToken`, `DeleteTokens`, `ListTokens`.

## Control Flow

Startup begins with `Load`, which reads and validates serialized `Format` from the backend, fills storage tiers when missing, and stores it under the base mutex. `NewSession` creates a cancellable session context, launches format/session refresh, loads ACLs and quotas, optionally records or updates the session ID, then starts flush loops and background cleanup workers unless the mount is read-only or background jobs are disabled.

The refresh loop sleeps on the configured heartbeat, updates the session expiry, reloads `Format`, rejects incompatible metadata versions or UUID changes by exiting with `UmountCode`, runs reload callbacks on format changes, refreshes used-space/inode counters, reloads quotas, and periodically elects a client to clean stale sessions with backend `setIfSmall` coordination.

Most filesystem calls follow a common pattern: normalize root via `checkRoot`, reject read-only/trash/invalid-name cases, enforce permissions with `Access`, call the matching backend `do*` method, then update local caches, volume stats, directory stats, and quotas when the backend succeeds. Examples include `Mknod` allocating an inode and charging stats/quotas, `Rename` comparing source and destination quota roots before moving, `Write` invalidating a cached chunk and updating parent/user/group usage from backend deltas, and `Truncate`/`Fallocate` doing full chunk-cache invalidation.

Reads use the open-file cache when possible. `Read` checks cached chunk slices, otherwise reads backend raw slices, builds logical slices, caches the result, touches atime, and opportunistically starts compaction for fragmented chunks. `ReadLink` has a dedicated symlink target cache; when atime matters, cached entries include an encoded atime prefix.

Compaction is guarded by `m.compacting` keyed by inode/chunk index. Non-forced compactions are dropped when too many are active or the same chunk is already compacting; forced/once calls wait. The flow reads raw slices, skips unsuitable leading slices, computes compacted output, allocates a new slice ID, sends a `CompactChunk` message to the data layer, persists the metadata replacement with `doCompactChunk`, invalidates chunk cache on success, and deletes wasted compacted output on conflict.

Deletion is staged. Removed-but-open files are remembered in `removedFiles` until `Close` deletes sustained inode records. Closed files can trigger asynchronous data deletion bounded by `maxDeleting`. Slice deletion can go through a `dslices` worker pool sized by `MaxDeletes`, which sends a `DeleteSlice` message before deleting slice metadata.

Trash cleanup creates hourly sub-trash directories when `TrashDays > 0`, moves/keeps deleted objects according to backend logic, and later removes old sub-trash directories plus delayed slices. Background cleanup uses shared backend counters such as `lastCleanupTrash`, `lastCleanupFiles`, and `nextCleanupSlices` to avoid all clients running the same job.

`Clone` validates source/destination permissions and quota headroom, then recursively clones directories. It creates detached directory trees first, batches non-directory entries through `BatchClone`, processes subdirectories with bounded concurrency, repairs nlink when source children disappear mid-clone, and attaches or cleans up the detached destination tree.

`DumpMetaV2` streams backend dump messages through a channel into backup segments and writes a footer. `LoadMetaV2` prepares the backend, reads backup segments, and dispatches segment loads to a worker pool controlled by `LoadOption.Threads`.

## State and Persistence Behavior

Persistent state is delegated to the backend through `engine`: metadata format, sessions, counters, inode attributes, dentries, xattrs, chunks, delayed slices, directory stats, quotas, ACLs, tokens, changelog rows, and dump/load records. `baseMeta` assumes backend `do*` methods provide the transactional semantics for each store.

Local state is partly authoritative only within a mount session. `newSpace`/`newInodes` are buffered counters flushed by `doFlushStats`; `dirStats` and quota usage are similarly buffered and periodically flushed. `FlushSession` forces stats, dir stats, and quotas before close. Open-file cache entries and symlink cache entries are local performance state and are invalidated or evicted, not persisted.

ID allocation uses backend monotonic counters in batches: `nextInode` reserves `inodeBatch` IDs with prefetch jitter, while `NewSlice` reserves `sliceIdBatch` chunk/slice IDs. This reduces backend round trips but means unused IDs can be skipped after process failure.

Volume stat reporting combines persisted counters with unflushed local deltas. `StatFS` can read remote counters unless `FastStatfs` permits cached values, then applies format capacity/inode limits and walks ancestor directory quotas to clamp available space and inode counts.

Directory parent and quota caches are repaired opportunistically by `Lookup`, `GetAttr`, `Mkdir`, `Rename`, and quota lookup paths. Trash directories and delayed slice buffers are persistent backend entries, but their cleanup is eventually consistent and coordinated by heartbeat-era counters.

## Dependencies and Integration Points

- Internal JuiceFS packages: `aclAPI` for POSIX ACL rules/cache, `object` for storage tiers, `utils` for buffers, jittered sleeps, progress bars, context timeouts, local IP lookup, and `version` for session records.
- External libraries: Prometheus collectors for metrics, `errgroup` for concurrent clone/deleted-object scans, protobuf for dump/load messages, and `pkg/errors` for wrapping/comparison.
- Data-plane integration happens through `newMsg` callbacks. `CompactChunk` and `DeleteSlice` are emitted to registered message handlers before metadata is finalized or cleaned.
- Backend integration is entirely through the `engine` interface. This file is therefore the compatibility boundary every metadata backend must satisfy.
- FUSE/VFS-facing integration is implied by exported methods matching filesystem operations: lookup, attr, open/read/write, mkdir, rename, xattr, ACL, statfs, readdir, and maintenance operations.
- Metrics integration registers shared filesystem gauges, quota gauges, operation histograms/counters, transaction restart counters, and background-job duration/deletion counters.

## Risks and Edge Cases

- Background goroutines rely on `sessCtx` and wait groups. Ordering between `CloseSession`, context cancellation, closing `dslices`, and worker exit is important to avoid blocked sends or leaked goroutines.
- `StatFS` may report approximate data when counters are cached, unflushed, timeout, or clamped by changing quotas. Tests should account for eventual flush behavior.
- Quota and directory-stat updates are split between backend transactions and local buffered updates. Partial failures around clone, rename, or batch operations can leave accounting discrepancies until repair/sync tools run.
- `Clone` can leave partially cloned detached or visible state on backend failures. The code attempts cleanup for detached directory roots, but batch clone tests explicitly cover partial failure leakage.
- Compaction contains concurrency dropping, waiting, and recursive forced retry behavior. Incorrect slice overlap handling can panic, and backend `EINVAL` wastes the newly compacted slice and must delete it.
- Root and trash special cases are pervasive. `RootInode`, mounted subdir root, `TrashInode`, trash parents, and `TrashName` have different permission and lookup behavior.
- Symlink cache stores different byte layouts depending on atime mode. Callers must respect `noatime` handling or risk returning bytes with the atime prefix.
- `dirHandler.Insert` assumes the backend cursor is a `[]byte`; a backend with a different cursor type must avoid this handler or preserve that contract.
- The `engine` interface is very broad. Adding common behavior often requires coordinated changes across all backend implementations and test fixtures.

## Test Signals

Relevant tests live under `sources/distributed-fs/juicefs/pkg/meta`.

- `base_test.go` exercises broad base metadata behavior, including session flushing, stale session cleanup, symlink reads and cache behavior, statfs with quotas/subdirs, compaction cases, batch clone, token/ACL-adjacent behavior, and general filesystem operations.
- `redis_batchclone_test.go` targets backend batch-clone semantics for shared chunk refs, mixed file/symlink batches, duplicate names, space accounting, multi-chunk files, skipped deleted sources, and partial failure state.
- `sql_test.go` includes batch clone coverage for SQL metadata.
- `random_test.go` drives randomized filesystem operations and includes `ReadLink` and `StatFS` paths.
- `load_dump_test.go` validates dump/load behavior with symlinks and metadata reconstruction.
- `benchmarks_test.go` includes benchmark coverage for readlink-heavy paths.
- `utils_test.go` constructs `baseMeta` directly for helper-level behavior.

High-value regression checks for changes in this file are: backend-agnostic `go test ./pkg/meta` from the JuiceFS source root, targeted `TestRedisBatchClone*` when touching clone/accounting, compaction tests when touching slice selection or delete paths, statfs/quota tests when touching counters or quotas, and random/property tests when changing namespace operations.
