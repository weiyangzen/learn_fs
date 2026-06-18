# sources/distributed-fs/ceph-client/drivers/gpu/drm/exynos/regs-decon7.h

## Purpose
This header defines register offsets and bitfield macros for the Exynos7 DECON display controller. It covers video control, output interface selection, clocking, shadow control, window configuration, framebuffer addresses and offsets, OSD geometry, color keying, blending equations, interrupts, timing, CRC, clock gating, and update control.

## Important APIs, Types, and Functions
Important offset macros include `VIDCON0`, `VIDOUTCON0`, `VCLKCON*`, `SHADOWCON`, `WINCON(_win)`, `VIDW_*`, `VIDOSD_*`, `WINxMAP`, `WKEYCON*`, `BLENDE(_win)`, `VIDINTCON*`, `VIDCON1(_x)`, `VIDTCON*`, `CRCCTRL`, `DECON_CMU`, and `DECON_UPDATE`. Bitfields encode enable/reset/stop status, RGB/I80 output, burst lengths, buffer selection, triple buffering, pixel formats, alpha selection, OSD coordinates, color map/key values, 8-bit alpha blend mode, interrupt frame/fifo selection, line count, RGB order, timing porch/sync/active sizes, CRC start, and standalone update.

## Control Flow
There is no code flow. Exynos7 DECON code uses these macros during atomic enable, mode programming, plane setup, shadow protect/unprotect, vblank IRQ handling, and update triggering.

## State and Persistence Behavior
The header maps DECON hardware state. Programmed windows, buffer addresses, timing, blend equations, and clock/update registers persist in MMIO until reset or overwritten. Shadow and update bits coordinate active versus pending state for atomic commits.

## Dependencies and Integration Points
The direct consumer is `exynos7_drm_decon.c`. It integrates with Exynos DRM plane state, DRM display modes, framebuffer DMA addresses, interrupt handling, CRC/debug paths, and display interface setup for RGB or I80 outputs.

## Risks
Several macros rely on caller-supplied window indexes and shift constants, so invalid window numbers can compute valid-looking but wrong offsets. `VIDW_BLKSIZE(win)` references `_win` in the macro body while the parameter is named `win`, which is a source-level defect if used. Some burst mask definitions mask only one bit while values encode more than one, so callers must verify the register layout before reusing. Shadow/update sequencing is critical to prevent tearing or partial plane state.

## Test Signals
Compile Exynos7 DECON paths, run atomic modesets across supported pixel formats, verify triple/double buffering, window OSD coordinates, color key and blending equations, RGB/I80 output selection, vblank and extra interrupt delivery, CRC operation, and standalone update behavior.
