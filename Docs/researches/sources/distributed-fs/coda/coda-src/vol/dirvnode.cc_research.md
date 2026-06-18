# sources/distributed-fs/coda/coda-src/vol/dirvnode.cc

Purpose: manages directory vnode interaction with the directory cache and recoverable directory inode pages. It keeps VM directory handles synchronized with RVM-backed `PDirInode` state and supports directory copy-on-write.

Important APIs: `VN_DCommit` commits dirty directory cache pages into RVM and updates `vnp->disk.node.dirNode`; for deleted directories it nulls the pointer and decrements the previous directory inode. `VN_DAbort` frees VM directory data and drops new uncommitted handles. `VN_SetDirHandle`, `VN_PutDirHandle`, and `VN_DropDirHandle` bridge a vnode to the directory cache. `VN_CopyOnWrite` detaches a cloned directory from its old RVM inode, either marking the existing cache entry copy-on-write or cloning VM pages when other users still reference the old entry.

Control flow/state: callers set a handle before operating on directory contents. On transaction commit, dirty VM pages are copied into RVM with `DI_DhToDi`, rehashed, and installed into the vnode disk object. On abort or vnode eviction, the code frees or drops cache entries depending on whether the directory ever acquired an RVM inode.

Dependencies/integration: integrates `codadir` directory cache primitives with `Vnode` dirty/delete state and RVM transactions from the vnode/volume layer. Risks include reference-count mismatches because comments explicitly say `VN_SetDirHandle` calls are not perfectly paired with puts, and copy-on-write correctness depends on `DC_Count - dh_refc`. Test signals: create/abort directory, modify/commit directory, clone a directory with and without shared cache users, delete cloned directories, and assert no leaked or double-dropped `PDCEntry` references.
