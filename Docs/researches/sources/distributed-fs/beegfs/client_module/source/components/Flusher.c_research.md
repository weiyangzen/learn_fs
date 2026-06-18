# sources/distributed-fs/beegfs/client_module/source/components/Flusher.c

## Purpose
Implements the background buffered-cache flusher thread for files that need asynchronous cache flush retries.

## Important APIs and control flow
`Flusher_init` initializes the thread. `_Flusher_requestLoop` wakes every five seconds until termination and calls `__Flusher_flushBuffers`. The flush loop removes inodes from `InodeRefStore`, calls `FhgfsOpsHelper_flushCacheNoWait`, drops references on success, re-adds inodes when busy or retryable, performs a final forced flush for unrecoverable errors on closed files, logs discarded buffers, and respects termination between items.

## State, dependencies, integration
State is only the thread and app pointer. It integrates with `InodeRefStore`, `FhgfsInode`, and filesystem helper flush operations.

## Risks and test signals
Reference handling is central: success and discard paths call `iput`, while re-add paths transfer or drop references through `InodeRefStore_addOrPutInode`. Tests should cover busy lock retry, communication failure on open versus closed files, final flush failure logging, and shutdown mid-queue.
