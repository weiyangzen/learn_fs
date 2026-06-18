# sources/distributed-fs/ceph-client/drivers/gpu/drm/mgag200/mgag200_mode.c

## Purpose
Implements shared mgag200 KMS mode-setting: CRTC register programming, gamma LUT handling, primary shadow plane updates into VRAM, display enable/disable, mode validation, atomic CRTC state management, and DRM mode_config setup.

## Important APIs, types, and functions
- Gamma helpers `mgag200_crtc_fill_gamma()` and `mgag200_crtc_load_gamma()` program DAC palette entries for RGB565/RGB888/XRGB8888.
- Register programming helpers: `mgag200_init_registers()`, `mgag200_set_mode_regs()`, `mgag200_set_format_regs()`, `mgag200_enable_display()`.
- Plane helpers: `mgag200_primary_plane_helper_atomic_check/update/enable/disable()` and `mgag200_primary_plane_helper_get_scanout_buffer()`.
- CRTC helpers: `mgag200_crtc_helper_mode_valid()`, `mgag200_crtc_helper_atomic_check/flush/enable/disable()`, state reset/duplicate/destroy functions.
- `mgag200_mode_config_init()` initializes DRM mode_config and VRAM availability.

## Control flow
Atomic plane check enforces no scaling and marks the CRTC mode changed when the framebuffer format changes, then stores the format in mgag200 CRTC state. Plane update copies damaged rectangles from the shadow buffer into MMIO VRAM, sets scanout start address to zero, and updates pitch/offset registers. Plane enable/disable toggles sequencer screen-off with a delay.

CRTC atomic check verifies a primary plane, asks the chip-specific PIXPLLC checker to populate CRTC state when the mode changes, and validates gamma LUT size. Atomic enable programs format and timing registers, calls chip-specific PLL update, loads gamma, and enables display. Atomic flush updates gamma on color-management-only changes. Mode validation enforces chip-specific max dimensions, 8-pixel horizontal granularity, CRTC register limits, VRAM capacity, and optional memory bandwidth limits.

Mode config wraps atomic commit tail with `mdev->rmmio_lock` so concurrent DDC register use cannot interleave with modesetting.

## State and persistence
`mdev->vram_available` persists the probed VRAM limit. `mgag200_crtc_state` persists the active format, PLL values, and BMC reset flag across atomic duplicates. Hardware CRTC, sequencer, graphics, DAC, palette, start address, offset, and display-enable registers persist until later commits or shutdown.

## Dependencies and integration points
Depends on DRM atomic, GEM shadow plane, damage helper, framebuffer format helpers, color management, panic scanout buffer support, and `mgag200_ddc.h`/driver structures. Chip-specific files install these helpers into their plane and CRTC function tables.

## Risks
Hardware timing encoding is packed across VGA CRTC and extended registers; off-by-one or high-bit mistakes produce invalid sync. The driver always scans out from VRAM offset zero due to hardware and BMC quirks, so damage copying must keep VRAM current. MMIO VRAM writes through `drm_fb_memcpy()` can be performance-sensitive. Busy-wait display enable/disable lacks vblank IRQ integration. Bandwidth validation uses an approximation and maximum bpp, which can reject or accept borderline modes conservatively.

## Test signals
Atomic modeset tests, format changes among RGB565/RGB888/XRGB8888, gamma LUT set/reset, damage clipping, panic scanout buffer export, memory-size rejection, bandwidth rejection, horizontal granularity checks, and concurrent EDID reads during modeset are key signals.
