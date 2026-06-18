## sources/distributed-fs/openafs/src/afs/LINUX/osi_vcache.c

Purpose: Linux-specific vcache/vnode lifecycle helpers that bridge OpenAFS `struct vcache` objects to Linux `struct inode` and dentry-cache behavior.

Important APIs and state: exports `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, `osi_ResetRootVCache`, `osi_vnhold`, `osi_ShouldDeferRemunlink`, and `osi_ResetVCache`. Important internal state includes Linux inode aliases, dentry `d_time`, `afs_globalVp`, `afs_globalVFS`, per-vcache pagewriter lists, `target_link`, unlink state, and vcache reference/open counts.

Control flow: `osi_TryEvictVCache` first tries to prune dcache aliases, dropping AFS and vcache locks around Linux dcache operations, then calls `afs_FlushVCache` if reference/open counts allow. Directory alias eviction uses `shrink_dcache_parent` and `__d_drop` carefully under dentry locks. `osi_NewVnode` allocates a new inode with `new_inode(afs_globalVFS)` and either gets the embedded vcache from inode allocation hooks or allocates one manually. `osi_ResetRootVCache` rebuilds the root fid for a new root volume, obtains the new vcache, fills its inode, moves the root dentry alias from the old root inode to the new inode, releases the old root, and updates `afs_globalVp`.

Dependencies and integration: depends on Linux inode/dentry APIs, OpenAFS vcache locks, global GLOCK discipline, and `osi_compat.h` wrappers for dentry alias iteration. It integrates with Linux VFS root handling, cache invalidation, and silly-unlink cleanup.

State and persistence: all state is in kernel memory. `osi_ResetVCache` marks cached dentries and direct children stale by zeroing `d_time`; later dentry revalidation performs the actual refresh.

Risks: dentry alias manipulation is race-prone. The code deliberately drops locks around dcache pruning, restarts alias iteration after drops, and avoids `d_invalidate` in places to prevent CWD `ENOENT` and submount loss. `osi_ShouldDeferRemunlink` avoids known panics when `current->fs == NULL` with UFS disk cache and security modules.

Test signals: vcache recycle under open/closed reference patterns, root volume change, directory dentry invalidation, mountpoint/submount retention, unlink during process exit with UFS cache, and stress tests involving concurrent lookup, rename, and cache flush.
