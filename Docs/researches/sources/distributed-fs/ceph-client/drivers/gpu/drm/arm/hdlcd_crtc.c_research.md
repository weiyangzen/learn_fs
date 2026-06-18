# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_crtc.c

## Purpose

`hdlcd_crtc.c` implements the CRTC and primary-plane side of the ARM HDLCD DRM driver. HDLCD is modeled as a simple RGB scanout engine with one primary plane and no scaling, with mode timing, pixel format, framebuffer address, pitch, and vblank interrupt enable programmed directly into HDLCD registers.

## Important APIs, Types, And Functions

The file exports `hdlcd_setup_crtc()`. Internally, `hdlcd_plane_init()` creates the primary plane, and `drm_crtc_init_with_planes()` wires it to `hdlcd_crtc_funcs` and `hdlcd_crtc_helper_funcs`. `supported_formats[]` maps DRM FourCC formats to `struct pixel_format` descriptions from `video/pixel_format.h`. `hdlcd_set_pxl_fmt()` programs `HDLCD_REG_PIXEL_FORMAT` and color selector registers. `hdlcd_crtc_mode_set_nofb()` programs timing, bus options, polarities, and pixel clock rate. `hdlcd_plane_atomic_update()` programs line length, pitch, line count, and scanout base.

## Control Flow

CRTC setup allocates a universal primary plane, attaches plane helpers, initializes the CRTC, and attaches CRTC helpers. Atomic checking for the plane rejects line counts beyond `HDLCD_MAX_YRES`, rejects disabling the only plane while the CRTC remains active, and uses `drm_atomic_helper_check_plane_state()` with no scaling. Atomic enable prepares the pixel clock, writes mode registers, enables the controller command bit, and turns vblank accounting on. Atomic disable reverses that order by turning vblank off, clearing command, and disabling the clock. Atomic begin handles pending vblank events by arming them if vblank can be acquired or sending immediately on failure.

## State And Persistence Behavior

CRTC and plane state are DRM-managed atomic objects, while hardware state persists in MMIO registers until mode changes, plane updates, disable, cleanup, or reset. `hdlcd->plane` stores the primary plane pointer. The pixel clock is set to `crtc_clock * 1000` in `hdlcd_crtc_mode_set_nofb()` after programming timing. Cleanup stops the controller by writing zero to `HDLCD_REG_COMMAND`.

## Dependencies And Integration Points

The implementation depends on DRM atomic helpers, DRM fb DMA/GEM DMA helpers for physical scanout addresses, OF graph and clock infrastructure, HDLCD register macros, and `struct hdlcd_drm_private` accessors from `hdlcd_drv.h`. It integrates with the top-level HDLCD probe in `hdlcd_drv.c`, which provides MMIO, clock, IRQ, mode-config, and external encoder component binding.

## Risks And Edge Cases

`hdlcd_set_pxl_fmt()` returns success after `WARN_ON(!format)`, so bad formats should be prevented by plane format advertisement. The plane check debug text says source width but validates height. The driver assumes one active primary plane and no scaling. Register timing values are written as minus-one fields, so zero porch/sync values would underflow if accepted by earlier mode validation. Vblank event handling depends on IRQ installation and correct interrupt mask management.

## Test Signals

Relevant validation includes KMS atomic modeset/page-flip tests, each supported format, max/min resolution boundaries, clock-rounding rejection, vblank enable/disable and event delivery tests, suspend/resume through the parent driver, DMA scanout address correctness for cropped primary-plane state, and underrun visibility when `CONFIG_DRM_HDLCD_SHOW_UNDERRUN` is enabled.
