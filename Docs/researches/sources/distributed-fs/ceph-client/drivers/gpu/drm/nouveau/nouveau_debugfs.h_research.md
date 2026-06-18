# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nouveau_debugfs.h

Purpose: Declares Nouveau debugfs state and init/fini entry points, with compile-time no-op fallbacks when debugfs is disabled.

Important APIs/types: `struct nouveau_debugfs` contains the nvif control object used by debugfs pstate operations. `nouveau_debugfs(dev)` returns `nouveau_drm(dev)->debugfs`. Public functions are `nouveau_drm_debugfs_init()`, `nouveau_debugfs_init()`, `nouveau_debugfs_fini()`, `nouveau_module_debugfs_init()`, and `nouveau_module_debugfs_fini()`. `nouveau_debugfs_root` is exported under `CONFIG_DEBUG_FS`.

Control flow/state contract: Device initialization should call `nouveau_debugfs_init()` before DRM minor debugfs file creation, and teardown should call `nouveau_debugfs_fini()`. Module init/fini controls the top-level debugfs directory. In non-debugfs builds these functions compile away and return success.

Dependencies/integration: Includes DRM debugfs and Nouveau driver headers only under `CONFIG_DEBUG_FS`. The implementation integrates with nvif control and DRM minor debugfs registration.

Risks/test signals: Callers must tolerate `nouveau_debugfs()` returning NULL if initialization failed or debugfs is disabled. Test signals include compile coverage for both config states, module unload, debugfs file creation, and pstate path behavior when the control object is absent.
