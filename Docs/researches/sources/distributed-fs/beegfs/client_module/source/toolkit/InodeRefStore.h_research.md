## sources/distributed-fs/beegfs/client_module/source/toolkit/InodeRefStore.h

**Purpose:** Defines a mutex-protected inode reference store for async cache flush and similar workflows that need to hold at most one reference per inode.

**Important APIs/types/functions:** Defines `struct InodeRefStore` containing a pointer RB tree and mutex. Inline APIs include init/construct/uninit/destruct, `addAndReferenceInode`, `addOrPutInode`, `getAndRemoveFirstInode`, `getAndRemoveNextInode`, `removeAndReleaseInode`, and `getSize`.

**Control flow:** Add-and-reference inserts only if absent, then calls `ihold` inside the mutex. Add-or-put assumes caller already has a reference and drops it with `iput` if the inode is already present. Get-and-remove returns an inode without dropping the held reference, transferring release responsibility to caller. Next-iteration can temporarily insert the old inode pointer as a search key when it is no longer in the tree.

**State and persistence behavior:** The store persists only transient inode references in memory. Uninit iterates all remaining entries and calls `iput`, then destroys the tree and mutex.

**Dependencies and integration points:** Depends on `PointerRBTree`, `Mutex`, kernel inode reference APIs, and `os_kmalloc`. Used by async flushing or cache invalidation logic outside this subset.

**Risks:** Caller ownership differs by method: removed returned inodes still need `iput`, while explicit remove releases immediately. Temporary insertion in `getAndRemoveNextInode` must not call `ihold` and relies on pointer ordering only. Holding `iput` inside the mutex avoids races but may have side effects if final inode teardown is expensive.

**Test signals:** Test duplicate insertion, add-or-put reference balancing, iteration/removal order, remove-and-release races with add, uninit releasing leftovers, and lockdep behavior around `iput`.
