# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_crtc.c

## Purpose

`tilcdc_crtc.c` implements the single CRTC for the TI LCDC DRM driver. It programs LCDC scanout DMA, timings, pixel clock, palette loading, raster enable/disable, page flips, vblank IRQs, sync-lost recovery, and mode validation for LCDC revision 1 and 2 hardware.

## Important APIs, Types, and Functions

- `struct tilcdc_crtc` embeds the DRM CRTC and stores primary plane pointer, pending event, enable/shutdown state, frame-done wait state, IRQ lock, last vblank timestamp, frame duration, deferred framebuffer, sync-lost recovery state, palette DMA memory, and recovery work.
- `set_scanout()` writes framebuffer base/ceiling DMA addresses, using a 64-bit write where available to avoid torn address updates.
- `tilcdc_crtc_load_palette()` loads the required 32-byte true-color palette and waits for palette-loaded IRQ.
- `tilcdc_crtc_set_clk()` sets functional clock/divider and rev2 clock enables.
- `tilcdc_crtc_set_mode()` programs DMA, timing, raster format, polarity, clock, palette, scanout, and cached hardware mode.
- Enable/disable paths: `tilcdc_crtc_enable()`, `tilcdc_crtc_off()`, atomic wrappers, and shutdown helper.
- Flip path: `tilcdc_crtc_update_fb()` either writes scanout immediately or defers to next vblank if too close to frame end.
- IRQ path: `tilcdc_crtc_irq()` handles EOF/vblank, palette load, FIFO underflow, sync lost, frame done, and rev2 end-of-interrupt indication.
- `tilcdc_crtc_create()` allocates the primary plane and CRTC, DMA palette, locks, waitqueue, and managed destroy action.

## Control Flow

Probe creates the CRTC before encoder setup. On atomic enable, the CRTC runtime-resumes hardware, resets rev2 if needed, programs mode registers, enables IRQs, starts raster DMA, and turns DRM vblank on. Plane updates call `tilcdc_crtc_update_fb()`; if the next vblank is near, the new framebuffer is stored in `next_fb` and swapped from the EOF IRQ. Disable clears raster enable, waits for frame-done, sends pending events, disables IRQs, turns vblank off, and drops runtime PM.

Mode validation rejects unsupported width, width not multiple of 16, height over 2048, porch/sync fields outside register ranges, pixel clocks above DT/default limits, and bandwidth above `max_bandwidth`. Mode fixup adjusts HSKEW and horizontal sync polarity for LCDC-specific sync alignment.

## State and Persistence Behavior

The CRTC object persists under DRM managed allocation. Hardware register state is set on enable and lost on reset/PM. Palette memory is coherent DMA memory and persists for device lifetime. `last_vblank`, `next_fb`, pending event, `frame_done`, and sync-lost counters are transient runtime state protected by locks or waitqueues.

## Dependencies and Integration Points

The file depends on DRM atomic/vblank helpers, DMA GEM framebuffer helpers, runtime PM, clocks through the driver private struct, OF graph node ownership, and register helpers from `tilcdc_regs.h`. It integrates with `tilcdc_plane.c` through `tilcdc_crtc_update_fb()` and with `tilcdc_drv.c` through IRQ forwarding, cpufreq clock update, shutdown, and create APIs.

## Risks and Edge Cases

- Several PM calls use `pm_runtime_get_sync()` without checking negative returns.
- `mode->flags == DRM_BUS_FLAG_*` comparisons look like bus-flag checks but `mode->flags` usually contains DRM mode flags; this can miss combined flags or represent a semantic mismatch.
- `tilcdc_crtc_disable_vblank()` clears `LCDC_INT_ENABLE_SET_REG` for rev2 rather than writing the clear register, which should be reviewed against hardware expectations.
- Page-flip event state is split between `tilcdc_crtc->event` and `crtc->state->event`; races are mitigated by locks but need testing.
- Sync-lost flood recovery queues work on `system_wq`, while the driver also owns `priv->wq`; teardown flushes `priv->wq` but not necessarily `system_wq`.
- Palette load timeout leaves the function continuing to raster setup after logging.

## Test Signals

Tests should cover rev1 and rev2 enable/disable, palette-loaded IRQ timeout/success, mode validation boundaries, pixel-clock fallback divider, page flips just before and far from vblank, frame-done wait timeout, FIFO underflow logs, sync-lost flood recovery, cpufreq-triggered clock updates, shutdown with active scanout, and suspend/resume.
