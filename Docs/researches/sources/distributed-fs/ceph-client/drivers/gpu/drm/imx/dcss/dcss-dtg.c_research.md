# sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-dtg.c

## Purpose
Programs the i.MX8MQ DCSS display timing generator. It derives display, plane, context-load, vblank, and context-load-kick timing from DRM videomodes, controls channel enable and foreground alpha state, and owns the DTG interrupt lines used by the DCSS CRTC for vblank and context-load commits.

## Important APIs, types, and functions
- `struct dcss_dtg` stores the mapped DTG registers, context-loader link, cached display origin, control register image, alpha configuration, and `ctxld_kick` IRQ enable state.
- `dcss_dtg_init()` allocates and maps the DTG block, initializes the default overlay/video alpha control bits, and installs the context-load kick IRQ handler with `IRQF_NO_AUTOEN`.
- `dcss_dtg_sync_set()` programs total/display timing registers, sets the pixel clock, records display upper-left coordinates, and sets context-load and interrupt trigger lines.
- Plane/channel APIs are `dcss_dtg_plane_pos_set()`, `dcss_dtg_plane_alpha_set()`, `dcss_dtg_ch_enable()`, `dcss_dtg_global_alpha_changed()`, and `dcss_dtg_css_set()`.
- Runtime control and IRQ APIs are `dcss_dtg_enable()`, `dcss_dtg_shutoff()`, `dcss_dtg_vblank_irq_enable()`, `dcss_dtg_vblank_irq_clear()`, `dcss_dtg_vblank_irq_valid()`, and `dcss_dtg_ctxld_kick_irq_enable()`.

## Control flow
Initialization maps the register window and prepares a cached `control_status` value with overlay data mode, video alpha selection, and default foreground alpha. IRQ configuration masks line0/line1 interrupts, obtains the `ctxld_kick` IRQ by name, and registers the handler disabled.

Mode setup converts `struct videomode` porches and sync lengths into DCSS last-row/column and display-window coordinates, disables and reprograms the pixel clock, writes timing registers through `dcss_dtg_write()`, and places line interrupts so line1 acts as vblank and line0 kicks the context loader near the end of active scanout. `dcss_dtg_write()` writes live hardware only before `in_use` is set and always queues the same write to the context loader.

Plane updates offset plane rectangles by the current display origin and program channel top/bottom registers, with an all-zero rectangle used as the disable sentinel. Channel enable recomputes `TC_CONTROL_STATUS`, merges the current alpha mode, and writes it only if the cached value changes. Enable sets `DTG_START` through context load and marks the DTG in use; shutoff directly clears the hardware start bit and marks it idle. The line0 IRQ handler validates the interrupt source, calls `dcss_ctxld_kick()`, and clears the line0 interrupt.

## State and persistence
Persistent runtime state is in the `dcss_dtg` object allocated for the lifetime of the DCSS device. `control_status`, `alpha`, and `alpha_cfg` are cached software mirrors of hardware fields. `dis_ulc_x/y` persist from the most recent mode setup and are required for later plane coordinate conversion. Register writes are persisted both in the hardware block and in the DCSS context-loader buffer, with behavior depending on whether the block is already active.

## Dependencies and integration points
This file depends on the DCSS common MMIO helpers, `dcss_ctxld_write()`, `dcss_ctxld_kick()`, and pixel-clock ownership in `struct dcss_dev`. It is driven by the DCSS CRTC mode set, vblank enable/disable, and plane update paths. Its alpha behavior is tied to DRM plane alpha and format metadata, while its IRQ names and register base are supplied by the platform device resources.

## Risks
The timing equations include several `- 1` offsets and unusual vertical display-origin handling; regressions can shift active video, vblank, or context-load timing by a line or pixel. `dcss_dtg_plane_pos_set()` computes lower-right as upper-left plus width/height, so consumers must agree with the hardware's inclusive/exclusive convention. The context-load kick IRQ uses line0 and is separately masked and Linux-disabled; mismatched mask/enable state can leave commits stuck. Channel arrays assume valid `ch_num` in the range 0..2.

## Test signals
Useful signals include successful modeset with the requested pixel clock, vblank interrupt delivery on line1, context-loader progress after line0 IRQs, correct overlay position after panning or mode changes, foreground alpha behavior for formats with and without alpha, and suspend/remove paths that free the IRQ without interrupt warnings.
