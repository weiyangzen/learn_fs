# sources/distributed-fs/ceph-client/drivers/gpu/drm/fsl-dcu/fsl_dcu_drm_crtc.c

## Purpose
This file implements the CRTC object for the Freescale DCU DRM driver. It programs display timing, polarity, background, thresholds, update mode, pixel clock, DCU enable/disable, vblank interrupt masking, and page-flip event delivery for atomic KMS.

## Important APIs, Types, and Functions
The public entry point is `fsl_dcu_drm_crtc_create()`, which initializes planes, creates the primary plane, initializes the DRM CRTC with helper and CRTC funcs, and attaches helper callbacks. Important atomic callbacks are `fsl_dcu_drm_crtc_atomic_flush()`, `fsl_dcu_drm_crtc_atomic_disable()`, `fsl_dcu_drm_crtc_atomic_enable()`, and `fsl_dcu_drm_crtc_mode_set_nofb()`. Vblank functions are `fsl_dcu_drm_crtc_enable_vblank()` and `fsl_dcu_drm_crtc_disable_vblank()`.

## Control Flow
CRTC creation calls `fsl_dcu_drm_init_planes()`, creates the primary plane, registers a CRTC through `drm_crtc_init_with_planes()`, and adds helper funcs. During mode set, `mode_set_nofb` sets the pixel clock rate, converts the DRM mode to `struct videomode`, derives pixel/HSYNC/VSYNC polarity from connector bus flags and mode flags, writes horizontal and vertical porch/sync registers, active display size, sync polarity, black background, raster/blend mode, and FIFO thresholds. Atomic enable prepares the pixel clock, sets DCU normal mode, triggers a register update, and enables vblank. Atomic flush triggers a register update and arms or sends pending vblank events. Atomic disable disables planes, turns vblank off, sets DCU off mode, triggers update, and disables the pixel clock.

## State and Persistence Behavior
Runtime state lives in `struct fsl_dcu_drm_device`, especially `regmap`, `pix_clk`, connector, and CRTC. Hardware timing and mode registers persist until the next mode set or disable. Pending page-flip events are stored in `crtc->state->event` and consumed under the DRM event lock. Vblank state is maintained by DRM core and DCU interrupt mask bits.

## Dependencies and Integration Points
The file depends on regmap MMIO access, common clock APIs, videomode conversion, DRM atomic helpers, DRM vblank/event helpers, FSL DCU register macros from the driver headers, RGB connector display info, and plane creation helpers in `fsl_dcu_drm_plane.c`. It is called from KMS initialization in `fsl_dcu_drm_kms.c`.

## Risks
`clk_prepare_enable()` and `clk_set_rate()` return values are ignored in enable and mode-set paths, so pixel-clock failures may become display failures without clear propagation. Event handling sends the event immediately if `drm_crtc_vblank_get()` fails, which is standard but can mask vblank-disabled sequencing problems. Bus flag interpretation defaults to inverted pixel clock unless `DRM_BUS_FLAG_PIXDATA_DRIVE_POSEDGE` is present, so panel/display-info accuracy is important. Register writes are not rolled back if a later mode register programming step would fail, though regmap writes generally do not report here.

## Test Signals
Test CRTC creation, primary plane creation failure cleanup, multiple display modes, pixel clock rates, HSYNC/VSYNC polarity flags, bus pixel data edge flags, atomic enable/disable, page flips with vblank events, vblank interrupt mask/unmask, runtime suspend around the pixel clock, and visual validation of black background and FIFO threshold stability.
