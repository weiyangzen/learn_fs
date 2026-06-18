<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/samsung_fimd.h -->
# sources/distributed-fs/ceph-client/include/video/samsung_fimd.h

## Purpose
This header defines Samsung S3C/Exynos FIMD framebuffer register offsets and bit helpers for display output, timing, windows, DMA buffers, interrupts, color keying, dithering, palette, blending, and v8 offset variants.

## Important APIs, Types, And Functions
- `VIDCON0`/`VIDCON1`/`VIDCON2` fields configure output type, RGB/i80/TV/writeback paths, clock source/divider, scan mode, data width, polarity, and enable bits.
- `VIDTCON0`/`VIDTCON1`/`VIDTCON2` macros compose vertical/horizontal timing values and extended 12-bit active sizes.
- `WINCON(_win)` and `WINCONx_*`/`WINCON0_*`/`WINCON1_*` select per-window enable, local input, buffer auto-select, byte/word swaps, burst length, color formats, and alpha/blending behavior.
- `SHADOWCON`, `VIDOSD*`, `VIDW_BUF_*`, `VIDINTCON*`, `WKEYCON`, `DITHMODE`, `WINxMAP`, `WPALCON`, `BLENDEQx`, `BLENDCON`, and `DP_MIE_CLKCON` define shadow protection, window geometry, DMA start/end/stride, interrupt selection/status, color keying, dithering, palette format, blend equations, and DisplayPort/MIE clock control.

## Control Flow
Driver mode-set flow computes timing fields, selects a clock, programs global output in `VIDCON*`, configures each active window's format/geometry/DMA buffer, updates shadow registers, enables interrupts, and finally sets `VIDCON0_ENVID`/`VIDCON0_ENVID_F`. Plane updates use window-specific offsets and may protect/unprotect shadow state.

## State And Persistence
Display state is in FIMD hardware registers and DMA framebuffer memory. Window enable, DMA addresses, blend/palette/color-key state, interrupt enables, and shadow-protect bits persist until changed or reset. No software storage is declared in this header.

## Dependencies And Integration Points
This is consumed by Samsung fbdev/DRM display code and SoC-specific clock, DMA, interrupt, and panel/bridge code. The macros encode differences across S3C2443+, S3C64xx, S5PV210, Exynos, and FIMD v8 register layouts.

## Risks And Edge Cases
The bpp matrix shows unsupported per-window formats; using a valid value on the wrong window can fail silently. Active size helpers split extended bits, so off-by-one or missing `_E()` bits can truncate large modes. Shadow protection and buffer address updates must be ordered to avoid tearing or fetching invalid memory.

## Test Signals
Signals include clean mode set across supported SoCs, correct per-window formats and byte order, working overlays/alpha/color keying, no FIFO underruns, correct frame interrupts, palette updates with `WPALCON_PAL_UPDATE`, and large-resolution modes that validate extended active-size fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/video/samsung_fimd.h -->
