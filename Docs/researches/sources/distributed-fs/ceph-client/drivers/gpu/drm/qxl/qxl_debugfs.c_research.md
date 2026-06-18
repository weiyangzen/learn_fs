# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_debugfs.c

Purpose: This file exposes debugfs diagnostics for QXL IRQ counters, live buffer objects, and TTM memory managers.

Important APIs, types, and functions: `qxl_debugfs_init(struct drm_minor *minor)` registers built-in debugfs files and calls `qxl_ttm_debugfs_init()`. `qxl_debugfs_add_files()` lets other QXL components register additional `drm_info_list` tables up to `QXL_DEBUGFS_MAX_COMPONENTS`. Readers include `qxl_debugfs_irq_received()` and `qxl_debugfs_buffers_info()`.

Control flow: When `CONFIG_DEBUG_FS` is enabled, driver debugfs init registers `irq_received` and `qxl_buffers`. IRQ output prints total, display, cursor, I/O command, and error counters. Buffer output walks `qdev->gem.objects`, counts bookkeeping fences using `dma_resv_iter`, and prints size, pin count, and release count.

State and persistence: Debugfs state is held in `qdev->debugfs[]` and `debugfs_count`, plus the runtime counters and GEM list being observed. It does not mutate device state except adding debugfs entries.

Dependencies and integration points: Uses DRM debugfs helpers, QXL GEM object lists, DMA reservation fence iteration, and QXL TTM debugfs setup. It is reached through the DRM driver `.debugfs_init` callback in `qxl_drv.c`.

Risks: `qxl_debugfs_buffers_info()` walks the GEM object list without taking `qdev->gem.mutex`, so debugfs reads during object churn depend on external serialization or may be diagnostically racy. Component registration must not exceed the fixed maximum.

Test signals: Mount debugfs and read `irq_received`, `qxl_buffers`, `qxl_mem_mm`, and `qxl_surf_mm` after modesets, cursor updates, and draw activity; build with and without `CONFIG_DEBUG_FS`.
