# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_validation.h

Purpose: Declares vmwgfx validation context state, dirty flags, initialization macro, TTM reservation wrappers, and validation transaction APIs.

Important APIs/types: `VMW_RES_DIRTY_*`, `struct vmw_validation_context`, `DECLARE_VAL_CONTEXT`, `vmw_validation_has_bos()`, `vmw_validation_bo_reserve()`, `vmw_validation_bo_fence()`, `vmw_validation_align()`, and add/prepare/done/revert prototypes.

Control flow: Callers declare a context, add resources/BOs, call `vmw_validation_prepare()`, submit commands, then call `vmw_validation_done()` or `vmw_validation_revert()`. Inline wrappers delegate BO reserve/fence to TTM execbuf utilities.

State/persistence: Context fields are temporary per transaction: lists, optional hash context, page allocator, ww ticket, resource mutex, duplicate-merge flag, and allocator cursor.

Dependencies/integration: Linux list/hash/ww mutex, TTM execbuf utility, vmwgfx BO/resource/fence types, and `vmwgfx_validation.c`.

Risks/test signals: Macro/struct drift, dirty flag overwrite semantics, context reuse after cleanup, no-BO validation, duplicate merge modes, and error paths that cleanup once.
