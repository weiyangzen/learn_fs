## sources/distributed-fs/openafs/src/afs/NBSD/osi_vm.c

Purpose: NetBSD VM/buffer-cache integration for OpenAFS vcache recycling, page flush, store, invalidation, and truncation.

Important APIs: `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: `osi_VM_FlushVCache` validates that the vcache has a vnode, drops GLOCK, calls `cache_purge(vp)` and `vflushbuf(vp, 1)`, then reacquires GLOCK. `osi_VM_StoreAllSegments` drops the vcache lock and GLOCK, enters the vnode interlock, calls `VOP_PUTPAGES` for all pages with clean/synchronous flags, then reacquires AFS locks. `osi_VM_TryToSmush` releases the vcache lock, flushes the vcache, and reacquires it. `osi_VM_FlushPages` purges name/cache state and invalidates buffers with `vinvalbuf`. `osi_VM_Truncate` calls `vtruncbuf` to purge buffers beyond the new length.

Dependencies and integration: depends on NetBSD vnode buffer/page APIs (`cache_purge`, `vflushbuf`, `VOP_PUTPAGES`, `vinvalbuf`, `vtruncbuf`), `curlwp`, AFS debug flags, and GLOCK/vcache locks. It is used by callback invalidation, vcache recycle, flush commands, truncation, and store-all-segments paths.

State and persistence: mutates NetBSD VM/buffer-cache state for AFS vnodes. Durable data movement is performed by NetBSD vnode paging/buffer machinery and common AFS store logic, not by this file directly.

Risks: correct lock dropping is essential because VM operations can block. `osi_VM_FlushVCache` returns 0 even for `vp == NULL` after logging, so callers treat missing vnode as flush success. `osi_VM_StoreAllSegments` explicitly enters `v_interlock` before `VOP_PUTPAGES`; API expectations must match target NetBSD versions.

Test signals: callback page invalidation, dirty page store on fsync/sync, truncate behavior, vcache recycle with/without vnode, debug-lock kernels, and NetBSD version matrix for vnode paging APIs.
