# sources/distributed-fs/openafs/src/afs/IRIX/osi_vm.c

## sources/distributed-fs/openafs/src/afs/IRIX/osi_vm.c

Purpose: implements IRIX VM and page-cache integration for AFS vcache recycling, callback invalidation, storeback, fsync invalidation, and truncation.

Important APIs/types/functions: `osi_VM_FlushVCache`, `osi_VM_TryToSmush`, `osi_VM_FSyncInval`, `osi_VM_StoreAllSegments`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: flush-vcache rejects active refs, opens, locks, waiters, and vnodes in inactive transition. It tosses all pages, checks for no pages/mappings/dirty buffers, cleans file locks, reclaims/frees vnode page-cache state, removes behavior descriptors, destroys locks, and resets vnode flags. Store-all releases the vcache write lock and global lock, repeatedly flushes delayed pages with `pdflush`, calls `PFLUSHVP`, falls back to `PINVALFREE` on error, reacquires locks, and warns on failed storeback for linked files. Smush/remap paths drop locks before `remapf`/`PTOSSVP`. FlushPages remaps and tosses all pages; truncate tosses pages beyond length.

State/persistence: manipulates IRIX VM page cache, dirty-page lists, vnode file locks, behavior heads, and vcache lock ownership. Store paths persist dirty mapped data to the AFS cache/server path via page flush operations.

Dependencies/integration: depends on IRIX vnode page-cache APIs, behavior descriptors, file lock cleanup, OpenAFS vcache locks, and macros in `osi_vfs.h`.

Risks/test signals: very high-risk due to assertions around no dirty/mapped pages, lock dropping/reacquisition, and vnode reclaim ordering. Test vcache recycle after mmap, callback revocation, fsync with invalidation, truncation, dirty mmap last-close storeback, file locks, and error injection in page flush.
