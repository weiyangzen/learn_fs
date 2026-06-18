# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/exynos_drm_fb.h

Purpose: this header exposes Exynos framebuffer helpers to display controllers and fbdev setup code.

Important APIs: it declares `exynos_drm_framebuffer_init()`, `exynos_drm_fb_dma_addr()`, and `exynos_drm_mode_config_init()`. It includes `exynos_drm_gem.h` because framebuffer creation takes arrays of `struct exynos_drm_gem *`.

Control flow and integration: fbdev emulation calls `exynos_drm_framebuffer_init()` after allocating a GEM buffer. Display controllers call `exynos_drm_fb_dma_addr()` during plane programming. The top-level driver calls `exynos_drm_mode_config_init()` after `drm_mode_config_init()`.

State and persistence: none in the header; it is an internal declaration surface.

Dependencies: DRM framebuffer types and Exynos GEM are required through included headers and forward declarations in C files.

Risks: callers must preserve GEM object references according to DRM framebuffer lifetime rules and only pass valid plane indices.

Test signals: compile all users, fbdev buffer creation, FIMD plane updates, and addfb paths.
