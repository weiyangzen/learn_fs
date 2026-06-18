## sources/distributed-fs/openafs/src/afs/NBSD/osi_vcache.c

Purpose: NetBSD vcache/vnode allocation and recycling hooks for OpenAFS.

Important APIs: `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_AttachVnode`, `osi_PostPopulateVCache`, and `osi_vnhold`.

Control flow: `osi_TryEvictVCache` optionally logs debug messages, calls `osi_VM_FlushVCache`, and reports success if VM flush succeeds. `osi_NewVnode` allocates a `struct vcache` with `afs_osi_Alloc` and clears `tvc->v` so later attach logic knows no vnode exists yet. `osi_PrePopulateVCache` zeros the entire vcache. `osi_AttachVnode` drops `afs_xvcache` and GLOCK, calls `afs_nbsd_getnewvnode(avc)` to allocate/attach a NetBSD vnode with one refcount, reacquires locks, and initializes an older-kernel vnode rwlock when needed. `osi_PostPopulateVCache` sets the vnode mount to `afs_globalVFS` and default type to regular file. `osi_vnhold` wraps `VN_HOLD`.

Dependencies and integration: depends on NetBSD vnode allocation helper `afs_nbsd_getnewvnode`, global VFS state from `osi_vfsops.c`, NetBSD VM flush routines, and common vcache locks. It is called by common OpenAFS vcache allocation/reuse paths.

State and persistence: creates and mutates in-memory vcaches and attached NetBSD vnodes. No durable state.

Risks: dropping locks during vnode allocation is necessary but opens races; code reacquires `afs_xvcache` afterward. Zeroing the full vcache in `osi_PrePopulateVCache` must only occur before fields needing preservation are initialized. The TODO comment asks whether `vgone()` or `vrecycle()` should be used for eviction, suggesting lifecycle semantics may be incomplete.

Test signals: vcache allocation/attach, vnode refcount behavior, recycle under low-memory/cache pressure, NetBSD 5 and older lock initialization, and root/global mount assignment.
