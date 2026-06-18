# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_vm.c

## Purpose
Solaris VM coherency helpers for flushing, invalidating, storing, and truncating pages for AFS vcaches and dcaches.

## Important APIs, Types, and Functions
Defines `osi_VM_GetDownD`, `osi_VM_MultiPageConflict`, `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, `osi_VM_PreTruncate`, and `osi_VM_Truncate`.

## Control Flow
`GetDownD` invalidates pages for a specific dcache chunk by calling `afs_putpage` outside GLOCK. `MultiPageConflict` checks whether a dcache chunk overlaps any active multipage getpage range. `FlushVCache` rejects busy refs/opens/locks, invalidates all vnode pages with `pvn_vplist_dirty`, verifies no pages remain, destroys rwlock, and frees stored creds. Store/smush use `pvn_vplist_dirty` with `afs_putapage`. PreTruncate zeros the unused tail of the final page. Truncate invalidates pages beyond new EOF.

## State and Persistence
Mutates Solaris page cache, vcache `credp`, rwlock lifecycle, and global `afs_pvn_vptrunc` counter. It does not directly persist data to the AFS server except through `afs_putapage`/cache writes.

## Dependencies and Integration Points
Depends on Solaris VM/page/pvn APIs, `afs_putpage`/`afs_putapage` from vnodeops, vcache multipage queues, `afs_indexFlags`, and cache eviction/truncation paths.

## Risks
Incorrect page invalidation can deadlock with multipage faults or leave stale cache pages. Lock preconditions are strict and differ by function. `FlushVCache` destroys `rwlock`, so callers must ensure no later users remain.

## Test Signals
Mapped read/write files, dcache eviction during multipage faults, callback flush, truncate to non-page-aligned length, cache pressure reclaim, read-only volume page handling, and lock-order stress tests.
