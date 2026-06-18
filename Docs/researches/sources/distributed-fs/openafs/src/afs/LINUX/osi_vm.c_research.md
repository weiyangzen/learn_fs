## sources/distributed-fs/openafs/src/afs/LINUX/osi_vm.c

Purpose: Linux VM/pagecache invalidation and writeback helpers used by common OpenAFS cache-management paths.

Important APIs: `osi_VM_FlushVCache`, `osi_VM_TryToSmush`, `osi_VM_FSyncInval`, `osi_VM_StoreAllSegments`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: `osi_VM_FlushVCache` checks vcache reference count and open count, then truncates inode pages via `afs_truncate(ip, 0)` to recycle a vcache. `osi_VM_TryToSmush` invalidates remote inode pages through `invalidate_remote_inode`. `osi_VM_StoreAllSegments` avoids duplicate work if the per-vcache `pagewriters` list is non-empty, drops the vcache lock and GLOCK, calls `filemap_fdatawrite` and `filemap_fdatawait`, then reacquires locks. `osi_VM_FlushPages` locks the inode, calls `truncate_inode_pages`, and unlocks. `osi_VM_Truncate` delegates to `afs_truncate`.

Dependencies and integration: depends on Linux pagecache/writeback helpers and `osi_compat.h` inode locking wrappers. It is invoked by callback breaks, `fs flush`, truncation, writeback/store-all-segments paths, and vcache recycling. Comments note Linux treats VM as a cache updated by AFS writes and reads through the cache, so normal VM flushing is not required the way it is on some other platforms.

State and persistence: mutates Linux pagecache state for AFS inodes. No durable metadata is written here; server/cache persistence is handled by higher AFS writeback and dcache layers.

Risks: concurrency is the main risk. Several functions intentionally drop and reacquire locks, so pages can be recreated by concurrent activity before return. `osi_VM_StoreAllSegments` skips if another pagewriter is active; caller behavior must tolerate that. `osi_VM_FSyncInval` is intentionally empty on Linux.

Test signals: callback revocation invalidates stale mapped/read pages, truncation removes pages beyond EOF, `fs flush`/`fs flushv`, writeback waits for dirty pages, concurrent read/write during flush, and vcache recycle refuses busy objects.
