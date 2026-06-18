# sources/distributed-fs/ceph-client/drivers/gpu/drm/ttm/ttm_module.h

Purpose: private TTM module header for shared internal declarations.

Important APIs and declarations: defines `TTM_PFX` as the debug/logging prefix, forward declares `struct dentry` and `struct ttm_device`, declares external `ttm_debugfs_root`, and declares `ttm_sys_man_init(struct ttm_device *bdev)`.

Control flow and state: no executable behavior exists here. It provides shared linkage for files that need the global debugfs root or system manager initializer. `ttm_debugfs_root` is created and destroyed in `ttm_device.c`; `ttm_sys_man_init()` is implemented outside this subset in the system manager file but is called by `ttm_device_init()`.

Dependencies and integration: included by core TTM implementation files such as device, pool, BO, and module code. It keeps private declarations out of public DRM TTM headers.

Risks and test signals: declaration drift would be caught at build time. The main integration risk is global debugfs root lifetime: files using it assume global initialization has happened through `ttm_device_init()` before debugfs entries are created.
