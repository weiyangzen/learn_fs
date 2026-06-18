# File Research: sources/block-storage/linux-dm/drivers/md/dm-bio-prison-v2.c

Implements a v2 bio-prison with shared and exclusive lock semantics over the same style of overlapping range keys. The prison stores a workqueue pointer, spinlock, rb-tree, and mempool-backed cells.

`dm_cell_get_v2()` grants shared access unless an exclusive lock exists at an equal or higher level; blocked bios are appended to the cell. Shared users must call `dm_cell_put_v2()`, which decrements `shared_count`, may queue a quiesce continuation, and frees the cell if no exclusive owner remains.

`dm_cell_lock_v2()` obtains an exclusive cell lock. Existing exclusive lock returns `-EBUSY`; existing shared users cause a positive return indicating quiescing is needed. `dm_cell_quiesce_v2()` either queues the continuation immediately or stores it until shared users drain. `dm_cell_lock_promote_v2()` raises an exclusive lock level and again reports whether quiescing is needed.

`dm_cell_unlock_v2()` merges detained bios into the caller list, clears exclusive state if shared users remain, or erases the cell and returns ownership for freeing. The code notes two limitations: shared locks granted above an exclusive level can starve quiescing, and the implementation cannot yet track individual shared lock levels, so exclusive acquisition quiesces all shared holders.
