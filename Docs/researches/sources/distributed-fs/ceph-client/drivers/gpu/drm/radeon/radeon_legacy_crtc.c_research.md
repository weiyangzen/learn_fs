<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_crtc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_crtc.c

## Purpose

`radeon_legacy_crtc.c` implements pre-Atom/legacy Radeon CRTC programming for modesetting. It handles framebuffer base and tiling setup, legacy timing registers, PLL programming for PPLL/P2PLL, RMX panel scaling on the first CRTC, overscan reset, DPMS sequencing, CRTC prepare/commit/disable hooks, and legacy helper registration.

## Important APIs, Types, and Functions

- `radeon_legacy_init_crtc()`: assigns CRTC2 register offset and attaches legacy DRM CRTC helper functions.
- `radeon_crtc_set_base()` / `radeon_crtc_do_set_base()`: pin scanout BOs into VRAM, compute display base, pitch, tiling offset, and format, program offset/pitch/tile registers, unpin old framebuffers, and update bandwidth.
- `radeon_set_crtc_timing()`: computes and writes horizontal/vertical total/display/sync registers, format bits, CRTC enable mask defaults, merge controls, and TV-adjusted timings.
- `radeon_set_pll()`: computes or reuses BIOS PLL dividers, handles LVDS/TV constraints, programs PPLL or P2PLL with atomic-update sequencing, and switches pixel clock source.
- `radeon_legacy_rmx_mode_set()`: configures legacy flat-panel scaler/stretch registers for full/aspect/center/off modes.
- `radeon_crtc_dpms()`: toggles CRTC display/hsync/vsync bits, vblank delivery, LUT reload, and power-management clock recomputation.
- `radeon_crtc_prepare()`, `radeon_crtc_commit()`, and `radeon_crtc_disable()`: helper lifecycle methods for safely reprogramming legacy CRTCs and unpinning disabled scanout BOs.

## Control Flow

Mode setting calls `radeon_crtc_mode_set()`, which sets the scanout base, programs timings, programs PLLs, clears overscan, applies RMX scaling for CRTC0, and resets cursor state. Prepare turns off all CRTCs before reconfiguration because some legacy hardware wedges when one CRTC is reconfigured while another runs. Commit reenables previously enabled CRTCs.

Base setting validates the framebuffer format, reserves the GEM BO, pins it into VRAM under the 27-bit legacy CRTC offset limit, reads tiling flags, computes pitch in register units, and derives the CRTC offset. Macro-tiled buffers use chipset-specific offset math; microtiled scanout logs an error. If pinning a new framebuffer fails due to old small-VRAM hardware, it may unpin the old framebuffer first and retry.

Timing setup derives sync widths and polarities from the adjusted mode, detects whether the CRTC drives TV output, writes CRTC1 or CRTC2 control bits, and lets `radeon_legacy_tv_adjust_crtc_reg()` override values for TV modes. PLL setup chooses PPLL/P2PLL by CRTC, sets legacy PLL flags based on pixel clock and encoder type, optionally uses COMBIOS LVDS dividers, lets TV helpers override PLL values, and performs register update/reset/clock-source sequencing with lock delays.

## State and Persistence Behavior

Persistent state includes pinned scanout BOs, `radeon_crtc->legacy_display_base_addr`, `crtc_offset`, enabled state, RMX/native mode fields, PLL state in `rdev->clock`, display register programming, and global PM clock decisions. BO pin counts and `vram_pin_size` persist until explicit unpin. Register state persists across modes until next modeset, DPMS, suspend/resume restore, or teardown.

## Dependencies and Integration Points

This file depends on DRM CRTC helper APIs, DRM framebuffer formats, Radeon BO/pin/tiling APIs, register macros, PM clock recomputation, bandwidth updates, cursor reset, PLL computation helpers, legacy TV helpers, encoder active-device state, and BIOS-provided LVDS private data. It is paired with `radeon_legacy_encoders.c` for output routing.

## Risks and Edge Cases

- Legacy CRTC offsets are limited to 27 bits; pinning outside that range fails, so small/fragmented VRAM paths are fragile.
- Scanout of microtiled buffers is only logged as an error after pinning; the function still proceeds.
- Register programming is heavily chipset-specific, especially R300 tiling, RS4xx enable quirks, mobility PLL avoidance, and TV path overrides.
- Busy waits around PLL atomic-update bits can hang if hardware never clears expected bits; some loops have workaround bounds, others spin until clear.
- `radeon_crtc_prepare()` globally disables all CRTCs, so incorrect enabled tracking can blank outputs after modeset.

## Test Signals

Validation should include mode set on CRTC0 and CRTC1, 8/16/24/32-bpp scanout, framebuffer panning offsets, macro-tiled and linear scanout, small VRAM old-GPU retry paths, LVDS RMX full/center/aspect/off, TV output timing/PLL adjustment, DPMS on/off and vblank state, cursor reset after modeset, suspend/resume preserving display, and lockdep/reservation tests around BO pin/unpin.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/radeon_legacy_crtc.c -->
