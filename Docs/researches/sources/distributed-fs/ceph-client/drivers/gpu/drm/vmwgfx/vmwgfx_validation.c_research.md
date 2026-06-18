# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_validation.c

Purpose: Provides vmwgfx's validation transaction layer for command submission and KMS updates: collect resources/BOs, merge duplicates, reserve, validate, commit, or revert.

Important APIs/types: `vmw_validation_bo_node`, `vmw_validation_res_node`, `vmw_validation_add_bo()`, `vmw_validation_add_resource()`, `vmw_validation_res_switch_backup()`, `vmw_validation_res_set_dirty()`, `vmw_validation_prepare()`, `vmw_validation_done()`, `vmw_validation_revert()`, and preload/unref helpers.

Control flow: Add paths allocate page-backed metadata and optional hash entries. Prepare optionally locks a resource mutex, reserves resources in context-priority order, adds backup BOs, reserves BOs with TTM execbuf helpers, validates BO placement with retry/eviction, scans dirty BOs, and validates resources. Done fences BOs, commits dirty/backup changes through resource unreserve, unlocks, and frees references. Revert backs off without committing.

State/persistence: Context owns temporary lists, hash links, allocator pages, ww ticket, and optional mutex. Persistent effects occur only on commit: fences, dirty flags, and backup BO/offset switches.

Dependencies/integration: TTM execbuf reservation/fencing, vmwgfx BO placement/dirty tracking, resource reserve/validate/unreserve, execbuf, KMS, and cotable/context ordering.

Risks/test signals: Deadlock-sensitive ordering, hash cleanup under locks, coherent dirty tracker balance, CPU writer `-EBUSY`, duplicate resources, interrupted waits, and validation failure rollback.
