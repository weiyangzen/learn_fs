## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/aspeed_gfx.h

Purpose: shared private header for the ASPEED GFX simple DRM driver, defining device state, register offsets, and control bit macros used by probe, CRTC, and connector code.

Important type is `struct aspeed_gfx`, embedding `drm_device`, MMIO base, clock/reset handles, SCU regmap, per-SoC register offsets/defaults, a `drm_simple_display_pipe`, and one connector. Important macros define CRT register offsets (`CRT_CTRL1`, `CRT_HORIZ0`, `CRT_ADDR`, `CRT_THROD`, etc.) and fields for enable, DAC, color format, sync polarity, vblank interrupt, timings, offset, terminal count, and thresholds.

Control flow is indirect: CRTC code writes these fields during pipe enable/update/vblank setup, while driver code stores SoC-specific offsets and thresholds. State persists in hardware registers and the `aspeed_gfx` device struct. Dependencies include DRM device and simple KMS headers, clock/reset/regmap users, and SoC manuals.

Risks include register-field names with minor spelling issues, hardcoded 40 MHz/simple-mode assumptions in consumers, and fragile bitfield macros without range checking. Test signals are correct MMIO writes for RGB565/XRGB8888, vblank interrupt status handling, DAC mux behavior, and mode timing register programming.
