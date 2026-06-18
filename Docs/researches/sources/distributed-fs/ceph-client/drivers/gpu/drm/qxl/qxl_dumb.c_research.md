# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_dumb.c

Purpose: This file implements DRM dumb-buffer creation for QXL.

Important APIs, types, and functions: `qxl_mode_dumb_create()` fills `struct drm_mode_create_dumb`, maps 16 bpp to `SPICE_SURFACE_FMT_16_565` and 32 bpp to `SPICE_SURFACE_FMT_32_xRGB`, creates a CPU-domain GEM object with QXL surface metadata, marks the resulting BO as dumb, and returns handle/pitch/size.

Control flow: The function computes pitch and page-aligned size, rejects unsupported bpp, creates a GEM handle through `qxl_gem_object_create_with_handle()`, marks `qobj->is_dumb = true`, drops the local object reference, and updates the ioctl args.

State and persistence: The created BO persists as a GEM/TTM object and carries `is_dumb` plus `surf` metadata. It may later be assigned a shared dumb shadow BO by the display plane preparation path.

Dependencies and integration points: Called by DRM core through `.dumb_create` in `qxl_drv.c`. It depends on GEM creation in `qxl_gem.c`, BO conversion macros, and SPICE surface formats from `qxl_dev.h`.

Risks: Pitch calculation uses simple multiplication without explicit overflow checks. Dumb BOs are initially CPU-domain and need display code to manage shadows for scanout. Only 16 and 32 bpp are supported.

Test signals: `modetest`/kms dumb buffer creation for 16 and 32 bpp, rejection of other bpp values, large dimensions near overflow/VRAM limits, mmap/map offset flow, and scanout through primary planes.
