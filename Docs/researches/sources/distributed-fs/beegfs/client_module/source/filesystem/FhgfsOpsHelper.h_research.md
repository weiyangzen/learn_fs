# sources/distributed-fs/beegfs/client_module/source/filesystem/FhgfsOpsHelper.h

## Purpose
`FhgfsOpsHelper.h` declares the BeeGFS helper API used by file, inode, directory, page-cache, and symlink code. It also provides inline wrappers for hot logging, readlink, close retry, and lock-unlock retry behavior.

## Important APIs, Types, And Functions
- Public cache APIs: `FhgfsOpsHelper_flushCache()`, `FhgfsOpsHelper_flushCacheNoWait()`, `FhgfsOpsHelper_writeCached()`, and `FhgfsOpsHelper_readCached()`.
- Unlocked cache internals: `__FhgfsOpsHelper_flushCacheUnlocked()`, `__FhgfsOpsHelper_writeCacheFlushed()`, `__FhgfsOpsHelper_readCacheFlushed()`, and `__FhgfsOpsHelper_discardCache()`.
- Append and stateless I/O: `FhgfsOpsHelper_appendfileVecOffset()`, `FhgfsOpsHelper_getAppendLock()`, `FhgfsOpsHelper_releaseAppendLock()`, `FhgfsOpsHelper_readStateless()`, and `FhgfsOpsHelper_writeStateless()`.
- Directory and symlink helpers: `FhgfsOpsHelper_refreshDirInfoIncremental()`, `FhgfsOpsHelper_getRelativeLinkStr()`, `FhgfsOpsHelper_symlink()`, and `FhgfsOpsHelper_readlink_kernel()`.
- Inline retry wrappers: `FhgfsOpsHelper_closefileWithAsyncRetry()`, `FhgfsOpsHelper_unlockEntryWithAsyncRetry()`, and `FhgfsOpsHelper_unlockRangeWithAsyncRetry()`.

## Control Flow
The `LOG_DEBUG_MESSAGES` macro controls whether `FhgfsOpsHelper_logOpDebug()` emits log calls or compiles away. `FhgfsOpsHelper_logOp()` performs an inline level check before calling the formatted logger. `FhgfsOpsHelper_readlink_kernel()` builds a stack `kvec` iterator and delegates to the stateless read helper.

The close/unlock retry inlines call the matching `FhgfsOpsRemoting_*` operation first. If the result is `FhgfsOpsErr_COMMUNICATION` or `FhgfsOpsErr_INTERRUPTED`, they enqueue delayed cleanup in `InternodeSyncer`. For successful/non-retry close calls, any supplied file event is uninitialized immediately.

## State And Persistence Behavior
The header itself owns no persistent state. It defines contracts for helpers that mutate server file state, per-inode caches, and delayed retry queues. The inline retry wrappers copy enough `EntryInfo`/`RemotingIOInfo` state into `InternodeSyncer` queues to persist cleanup work across transient communication failures.

## Dependencies And Integration Points
The declarations pull in `App`, `StorageErrors`, `MetadataTk`, `InternodeSyncer`, `FsDirInfo`, `FsFileInfo`, and `FhgfsOpsRemoting`. It is a central integration header for VFS operation files and remoting code. Kernel API dependencies include dentries, inodes, and `iov_iter`.

## Risks
- Several non-`static` inline function definitions live in the header; build settings must avoid duplicate symbol issues in this kernel-module style.
- Retry wrappers assume communication/interruption errors are the only cases needing delayed cleanup.
- The unlocked cache declarations make lock ownership a caller responsibility, so misuse is not type-enforced.
- `FhgfsOpsHelper_readlink_kernel()` depends on the stack iterator macro and assumes the target buffer remains valid through the synchronous read.

## Test Signals
Compile coverage across debug/non-debug builds, close/unlock communication fault injection, readlink buffer limit tests, and static analysis for unlocked helper callers are the strongest signals for this header.
