# sources/distributed-fs/openafs/src/afs/VNOPS/afs_vnop_write.c

## Purpose
Implements cached writes, cache-backend write I/O, partial stores under dirty-cache pressure, close-time storeback, and fsync.

## Important APIs, Types, and Functions
`afs_write` is the main write path. `afs_UFSWriteUIO` writes to the configured disk cache file through OS VOPs or `osi_rdwr`. `afs_StoreOnLastReference` stores all dirty segments on last writer close or records disconnected write-close state. `afs_DoPartialWrite` calls `afs_StoreAllSegments` when dirty chunks exceed the configured limit. `afs_close` handles writer/read close accounting, background stores, error reporting, lock cleanup, and text flushes. `afs_fsync` synchronously stores data or records disconnected write-flush intent.

## Control Flow and State
`afs_write` rejects sticky vnode errors and disconnected non-RW writes, creates a request, locks the vcache unless `noLock`, handles append mode, updates mtime, fake-opens the file for write-token semantics, and loops across chunks. Each iteration obtains a writeable dcache, bounds the transfer to the chunk, writes through `afs_cacheType->vwriteUIO`, updates chunk size/valid position/file length, releases the dcache, and may trigger partial storeback. On backend write failure it zaps and truncates the dcache chunk and clears dirty index flags. `afs_close` evaluates fakestat, releases file locks, and for write closes either stores immediately or queues `BOP_STORE`; it then reports deferred write errors and decrements counters. `afs_fsync` stores all segments under `AFS_SYNC` or records `VDisconWriteFlush`.

Writes first persist to the local cache, marking `CDirty`, `IFDataMod`, chunk sizes, valid positions, file length, and mtime. Connected persistence to the fileserver occurs during partial write, fsync, close, background store, or last-reference store. Disconnected RW writes record dirty flags such as `VDisconWriteClose` and `VDisconWriteFlush`. Sticky `vc_error` carries writeback failures to later close/fsync/read callers.

## Dependencies and Integration Points
Depends on dcache allocation for writing, cache backend ops, `afs_StoreAllSegments`, background daemon `BOP_STORE`, fake-open/close macros from `afs.h`, VM/page flushing hooks, disconnected dirty queues, credential refcounting, and platform-specific VOP write APIs.

## Risks and Test Signals
Fake-close stores credentials in `linkData` while `CCore` is set, so symlink/linkData use must not overlap. Close-time background store transfers errors through `brequest` fields and must wake sleepers correctly. Dirty-cache pressure can force storeback during a write. Backend write errors must clean dcache and dirty accounting consistently. `afs_close` must return deferred quota/ENOSPC errors even if another thread performed the actual store.

Test writes within one chunk, across chunks, append writes, extending file length, disconnected non-RW and RW writes, backend write failure cleanup, dirty-cache partial store, close with synchronous and background store, close after deferred write error, fsync with writers, quota/ENOSPC reporting, sticky `vc_error`, and platform-specific sync flags.
