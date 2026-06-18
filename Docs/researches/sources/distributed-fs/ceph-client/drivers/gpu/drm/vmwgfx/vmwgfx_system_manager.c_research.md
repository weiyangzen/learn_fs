# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_system_manager.c

Purpose: Provides the TTM resource manager for vmwgfx's driver-specific system placement `VMW_PL_SYSTEM`.

Important APIs/types: `vmw_sys_man_alloc()`, `vmw_sys_man_free()`, `vmw_sys_manager_func`, `vmw_sys_man_init()`, and `vmw_sys_man_fini()`.

Control flow: Init allocates a `ttm_resource_manager`, sets `use_tt`, installs alloc/free callbacks, initializes it, registers it on `dev_priv->bdev` for `VMW_PL_SYSTEM`, and marks it used. Fini evicts all resources, marks the manager unused, cleans it up, unregisters it, and frees it.

State/persistence: The manager persists in the TTM device as the placement manager for `VMW_PL_SYSTEM`. Per-allocation state is a zeroed `ttm_resource` initialized from the BO/place.

Dependencies/integration: DRM TTM resource-manager APIs and vmwgfx BO placement/move validation.

Risks/test signals: Teardown assumes users are quiesced. Test driver load/unload, BO placement to `VMW_PL_SYSTEM`, eviction during fini, suspend/resume, and TTM leak checks.
