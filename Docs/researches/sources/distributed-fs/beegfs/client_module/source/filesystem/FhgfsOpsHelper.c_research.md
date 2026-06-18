# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsHelper.c

## Purpose
`FhgfsOpsHelper.c` implements shared helper paths for BeeGFS client VFS operations: operation logging, directory listing refresh, buffered read/write cache management, append locking, symlink creation, stateless read/write helpers, and sparse-read zero filling. It sits between VFS-facing operation files and `FhgfsOpsRemoting`, translating local inode/file state into metadata/storage RPCs while maintaining BeeGFS client-side cache invariants.

## Important APIs, Types, And Functions
- `FhgfsOpsHelper_logOpMsg()` resolves dentries into paths, reads `EntryInfo` under the inode entry-info lock, and logs operation context with optional formatted detail.
- `FhgfsOpsHelper_refreshDirInfoIncremental()` maintains `FsDirInfo` directory buffers and detects whether the metadata server supports buffer-size based listing (`META_CAP_LISTDIR_BUFSIZE_MODE`) or legacy entry-count mode.
- `FhgfsOpsHelper_writeCached()` and `FhgfsOpsHelper_readCached()` are the public buffered-cache paths used by file operations.
- `__FhgfsOpsHelper_writeCacheFlushed()`, `__FhgfsOpsHelper_readCacheFlushed()`, `__FhgfsOpsHelper_flushCacheUnlocked()`, and `__FhgfsOpsHelper_discardCache()` implement the unlocked cache state transitions; callers must hold the inode file-cache lock.
- `FhgfsOpsHelper_appendfileVecOffset()`, `FhgfsOpsHelper_getAppendLock()`, and `FhgfsOpsHelper_releaseAppendLock()` serialize append writes through metadata append locks.
- `FhgfsOpsHelper_symlink()` creates symlinks as BeeGFS files containing the target path, using create/open/write/close remoting.
- `FhgfsOpsHelper_readStateless()` and `FhgfsOpsHelper_writeStateless()` perform open-read/write-close flows for callers without an existing file handle.

## Control Flow
Logging first checks the configured log level, resolves the path through `__FhgfsOps_pathResolveToStoreBuf()`, locks inode entry info only while reading the entry ID, formats the optional message, and returns any borrowed path buffer to `NoAllocBufferStore`.

Directory refresh decides between three cases: forced refresh, local buffered contents still usable, or remote listing needed. The listing limit is either the configured message buffer size when the server capability is known/supported, or `100` for legacy/probe mode. On remoting error it clears the local directory contents and resets the current position.

Buffered write starts by bypassing the helper cache when coherent-buffer mode sees active mmaps. Otherwise it takes the inode cache exclusive lock, inspects the current `CacheBuffer` type, and either writes through, discards read cache, extends write cache, flushes incompatible write cache, or creates a new write cache. Full write buffers are flushed immediately. Buffered read has a parallel-reader/shared-lock fast path when no cache exists, otherwise it takes the exclusive lock, flushes write cache before reading, handles read-cache overlap, remote-reads gaps before/after the cache, and discards cache when the requested range extends beyond the cached region.

The stateless paths build `RemotingIOInfo` with a temporary `AtomicInt` and `PathInfo`, initialize `firstWriteDone` bitsets based on the stripe pattern target count, perform the remote operation, close with async retry, and free remoting state. Append writes first acquire a metadata append lock, stat the current size, add any caller-supplied end offset, write at that computed offset, and release the append lock even on error.

## State And Persistence Behavior
Persistent server state changes occur through BeeGFS remoting calls: file writes, symlink file creation, close, unlink-on-error cleanup, append locks, and metadata refresh/listing RPCs. Local state includes per-inode `CacheBuffer` fields (`buf`, `bufType`, `bufUsageLen`, `bufUsageMaxLen`, `fileOffset`), `FsFileInfo` cache hit counters and last offsets, `FsDirInfo` listing capability and contents state, `RemotingIOInfo` cleanup flags, and `InodeRefStore` membership for cached inodes. Cache buffers are borrowed from and returned to `NoAllocBufferStore`; cached inodes are reference-tracked for async flush.

## Dependencies And Integration Points
This file depends heavily on `FhgfsInode` locking/state helpers, `FsFileInfo`, `FsDirInfo`, `NoAllocBufferStore`, `InodeRefStore`, `StripePattern`, `RemotingIOInfo`, `FhgfsOpsRemoting`, `InternodeSyncer`, and kernel `iov_iter` copy helpers. It is called by file, inode, symlink, readlink, writeback, and truncate paths. The async retry integration is in the header inline wrappers, but this implementation provides the stateless write and symlink flows that feed those wrappers.

## Risks
- The cache functions rely on strict external locking for unlocked helpers; misuse can leak buffers, corrupt cache state, or race with read/write paths.
- `copy_from_iter()` and `copy_to_iter()` short-copy handling maps to BeeGFS address-fault errors; callers must preserve negative BeeGFS error conventions.
- Append locking sets cleanup flags on failure, so release failures need delayed cleanup elsewhere.
- Directory capability detection is stateful per handle; bad capability transitions could reduce listing correctness or performance.
- Stateless write uses a referenced inode handle when possible, but has to release it reliably after all errors.
- Symlink creation does multi-step remote mutation and must unlink partially created files if open/write fails.

## Test Signals
Useful signals include append-write serialization tests, buffered read/write cache hit/miss and flush tests, mmap coherent-buffer bypass tests, short user-copy fault injection, directory listing against old and new metadata server capabilities, symlink create/read failure cleanup, sparse reads with EOF zero fill, and close/unlock communication-error async retry queue coverage.
