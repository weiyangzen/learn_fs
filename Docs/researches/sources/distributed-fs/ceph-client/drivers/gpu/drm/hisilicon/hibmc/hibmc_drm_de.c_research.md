# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/hibmc/hibmc_drm_de.c

Purpose: implements the HIBMC display engine CRTC and primary plane. It validates atomic plane state, programs VRAM scanout registers, manages display power and vblank, configures CRT timing/PLL registers, and initializes plane/CRTC DRM objects.

Important APIs/functions: `hibmc_de_init()` creates the primary plane and CRTC. Plane helpers check no scaling, nonnegative position, visible bounds, and 128-byte stride alignment, then program framebuffer address, width, pitch, and pixel format. CRTC helpers manage DPMS, atomic enable/disable, begin/flush, mode validation, timing programming, vblank IRQ enable, and gamma LUT upload.

Control flow: during KMS init, this file registers the universal primary plane and CRTC. Atomic commits call plane check/update and CRTC helper callbacks. Enabling powers mode 0 and display/localmem gates, turns vblank on, and sets DPMS on. Mode set writes PLL values from a fixed resolution table and programs horizontal/vertical timing, sync, auto-centering, clock select, and plane enable bits.

State and persistence: hardware state is MMIO registers in `priv->mmio`; persistent software state is the DRM CRTC/plane state and gamma store. Supported PLL values are fixed in `hibmc_pll_table`.

Dependencies and integration points: depends on DRM atomic helpers, GEM VRAM helpers, vblank core, `hibmc_set_power_mode()`, `hibmc_set_current_gate()`, and `hibmc_drm_regs.h`. Outputs feed both VGA and optional DP encoders through the same CRTC.

Risks: mode validation only accepts 59-61 Hz and tabled resolutions. Unsupported scaling and stride alignment failures are user-visible. PLL programming relies on magic values. Plane address assumes VRAM object was pinned by helper prepare paths. Gamma setter ignores supplied arrays and reloads `crtc->gamma_store`.

Test signals: atomic modesets for every tabled resolution, stride-alignment failures, vblank IRQ delivery, DPMS transitions, framebuffer format coverage, gamma update, suspend/resume, and clone behavior with VGA/DP encoders.
