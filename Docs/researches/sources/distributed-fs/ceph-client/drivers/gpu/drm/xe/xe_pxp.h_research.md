<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp.h

Purpose: declares the public PXP interface used by query, exec queue, BO, IRQ, debugfs, and power-management code. It keeps PXP consumers insulated from `struct xe_pxp` internals.

Important APIs: feature/status helpers `xe_pxp_is_supported()`, `xe_pxp_is_enabled()`, and `xe_pxp_get_readiness_status()`; lifecycle hooks `xe_pxp_init()`, `xe_pxp_irq_handler()`, `xe_pxp_pm_suspend()`, and `xe_pxp_pm_resume()`; protected queue APIs `xe_pxp_exec_queue_set_type()`, `xe_pxp_exec_queue_add()`, and `xe_pxp_exec_queue_remove()`; BO/object key APIs `xe_pxp_key_assign()`, `xe_pxp_bo_key_check()`, and `xe_pxp_obj_key_check()`.

Dependencies and integration: forward declares DRM GEM, BO, device, exec queue, and PXP types. The header is included by PXP implementation, submit helpers, debugfs, query code, and users of protected object checks.

Risks and test signals: callers must handle `xe->pxp` being NULL, because `xe_pxp_is_enabled()` treats NULL as disabled. Tests should cover each public API with disabled PXP, not-ready PXP, and active PXP where applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_pxp.h -->
