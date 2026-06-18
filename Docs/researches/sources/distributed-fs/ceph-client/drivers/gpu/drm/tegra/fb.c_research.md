# sources/distributed-fs/ceph-client/drivers/gpu/drm/tegra/fb.c

Purpose: provides Tegra DRM framebuffer allocation and validation helpers around GEM-backed planes.

Important APIs/functions: `tegra_fb_get_plane()` converts a DRM framebuffer plane object to `struct tegra_bo`. `tegra_fb_is_bottom_up()` checks the BO bottom-up flag. `tegra_fb_get_tiling()` maps DRM modifiers, including NVIDIA tiled/block-linear and sector-layout modifiers, into `struct tegra_bo_tiling`. `tegra_fb_alloc()` allocates a DRM framebuffer, fills mode metadata, attaches GEM objects, and calls `drm_framebuffer_init()`. `tegra_fb_create()` is the userspace-facing constructor that looks up GEM handles, validates each plane size against pitch/offset/dimensions, and delegates allocation.

Control flow and state: framebuffer state is held by DRM core; this file only binds existing GEM objects to framebuffer planes. On failure during handle lookup or size validation, already referenced plane GEM objects are dropped.

Dependencies/integration: integrates DRM GEM framebuffer helpers, FourCC modifiers, Tegra GEM BO types, and downstream plane code that consumes `tegra_fb_get_tiling()` and `tegra_fb_get_plane()`.

Risks: plane size math uses `unsigned int`, so very large mode/pitch inputs depend on DRM core constraints to avoid overflow. NVIDIA modifier decoding changes `sector_layout` only inside the vendor branch; callers should not assume it is initialized if an invalid non-NVIDIA modifier path is taken.

Test signals: framebuffer creation IOCTL tests for multi-plane formats, invalid handles, undersized GEM buffers, unsupported modifiers, and block-linear/sector-layout planes should exercise the critical paths.
