# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_drv.c

## Purpose

`tilcdc_drv.c` is the platform DRM driver for TI LCDC controllers. It allocates the driver-private DRM device, discovers hardware revision and pixel formats, reads DT limits, initializes CRTC/encoder/vblank/IRQ/debugfs/client setup, and handles suspend/resume, remove, shutdown, and optional cpufreq notifications.

## Important APIs, Types, and Functions

- `enum tilcdc_variant` distinguishes AM33xx and DA850 for FIFO threshold defaults.
- Pixel-format arrays select rev1, straight wiring, crossed wiring, and legacy wiring formats.
- `tilcdc_atomic_check()` reruns modeset checks after plane checks because plane format changes can set `mode_changed`.
- `modeset_init()` configures mode limits and mode config funcs.
- `cpufreq_transition()` updates CRTC clock after CPU frequency changes when enabled.
- `tilcdc_irq_install()` and `_uninstall()` request/free the platform IRQ.
- Debugfs helpers expose register dumps and DRM MM state.
- `tilcdc_pdev_probe()` performs complete device initialization and registration.
- `tilcdc_pdev_remove()` and `_shutdown()` tear down or disable active scanout.

## Control Flow

Probe allocates `struct tilcdc_drm_private`, initializes DRM mode config, creates an ordered workqueue, maps MMIO, gets the functional clock, enables runtime PM, reads `LCDC_PID_REG` to determine rev1/rev2, chooses pixel formats based on revision and optional `blue-and-red-wiring`, reads `max-bandwidth`, `max-width`, and `max-pixelclock`, sets FIFO threshold by variant, creates the CRTC, initializes mode config, registers cpufreq notifier, creates the encoder/connector from DT bridge, initializes vblank and IRQ, resets mode config, initializes polling, registers the DRM device, and starts DRM client setup with a selected color depth.

Error paths unwind cpufreq, PM, clock, and workqueue state. Remove unregisters DRM, stops polling, uninstalls IRQ, unregisters cpufreq notifier, disables PM, puts the clock, and destroys the workqueue. System PM uses DRM mode-config helper suspend/resume plus pinctrl sleep/default state selection.

## State and Persistence Behavior

Driver-private state persists for the platform device lifetime and stores MMIO, clock, revision, IRQ, DRM device, format list, max mode limits, FIFO threshold, cpufreq notifier, workqueue, CRTC, encoder, connector, and IRQ-enabled flag. Runtime PM state is enabled after clock acquisition and disabled on teardown.

## Dependencies and Integration Points

The file depends on platform/OF matching, runtime PM, pinctrl PM states, DRM managed allocation, DMA GEM/fbdev helpers, bridge connector flow through `tilcdc_encoder.c`, CRTC creation through `tilcdc_crtc.c`, register helpers, debugfs, cpufreq when enabled, and DRM client setup.

## Risks and Edge Cases

- `clk_get()` is not devm-managed and must match all error/remove paths; the code handles this manually.
- If encoder creation finds no bridge, probe later returns `-EPROBE_DEFER` because `priv->connector` remains NULL.
- Unknown PID defaults to revision 1, reducing feature support and possibly misprogramming rev2-compatible hardware.
- `pm_runtime_get_sync()` result during PID read is ignored.
- Debugfs register reads perform runtime PM get/put without error handling.
- Workqueue ownership is mixed with recovery work in the CRTC file, which uses `system_wq`.

## Test Signals

Probe tests should cover AM33xx/DA850 matches, rev1/rev2 PIDs, unknown PID fallback, all wiring modes, DT max limits, missing clock/MMIO/IRQ, deferred bridge probing, cpufreq notifier registration, debugfs register access, suspend/resume pinctrl transitions, and remove/shutdown with active display.
