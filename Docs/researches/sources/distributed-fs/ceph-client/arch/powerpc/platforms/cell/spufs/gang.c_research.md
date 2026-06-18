# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/gang.c

Purpose: provides refcounted gang containers used to group SPU contexts and carry affinity metadata across those contexts.

Important APIs: `alloc_spu_gang`, `get_spu_gang`, `put_spu_gang`, `spu_gang_add_ctx`, and `spu_gang_remove_ctx`. The destructor validates that no contexts remain and that the list is empty before freeing.

Control flow: allocation initializes gang refcount, list mutex, affinity mutex, context list, affinity list head, and `alive=1`. Adding a context takes the gang mutex, stores a ref in `ctx->gang`, links `ctx->gang_list`, and increments `contexts`. Removal unlinks affinity membership if present, clears offset validity, removes the gang-list node, decrements `contexts`, unlocks, then drops the gang reference.

State and dependencies: the scheduler and inode creation code use gang `aff_*` fields and `alive`; this file only owns lifetime and list membership. Risks include callers failing to serialize against affinity mutation, stale `AFF_OFFSETS_SET` if contexts are removed outside this path, and leaked refs if context creation partially fails. Test signals are gang create/close, adding/removing multiple contexts, affinity context removal, and warning-free destruction.
