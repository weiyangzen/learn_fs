<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.c

## Purpose

`atmel_hlcdc_dc.c` is the main platform DRM driver for Atmel/Microchip HLCDC/XLCDC display controllers. It describes SoC-specific layer layouts and display limits, performs DRM device load/unload, installs interrupts, initializes modesetting, and handles PM suspend/resume.

## Important APIs, Types, And Functions

- SoC descriptor tables: layer layouts and `struct atmel_hlcdc_dc_desc` instances for at91sam9n12, at91sam9x5, sama5d2/d3/d4, sam9x60, sam9x75 XLCDC, and sama7d65 XLCDC.
- `atmel_hlcdc_of_match[]`: maps parent MFD compatible strings to descriptors.
- `atmel_hlcdc_dc_mode_valid()`: validates DRM mode porch/sync/display dimensions against descriptor limits.
- IRQ helpers: `atmel_hlcdc_dc_irq_handler()`, install/uninstall/disable/postinstall, and per-layer dispatch to plane IRQ handlers.
- `atmel_hlcdc_dc_modeset_init()`: initializes mode config, planes, CRTC, and outputs, sets min/max dimensions and atomic funcs.
- `atmel_hlcdc_dc_load()` / `_unload()`: bind descriptor/MFD data, enable clocks/runtime PM, initialize vblank/modeset/IRQ, and clean up.
- Platform driver hooks: probe, remove, shutdown, suspend, resume, with `drm_module_platform_driver()`.

## Control Flow

Probe allocates the DRM device, loads it, registers it, then starts the DRM client helper. Load matches the parent MFD node, enables the peripheral clock, enables runtime PM, initializes vblank/modeset, resets mode config, installs IRQs under runtime PM, stores platform data, and starts polling. IRQ handling reads IMR and ISR, masks active status, handles SOF as CRTC vblank, then dispatches layer status bits. Suspend saves atomic state and interrupt mask, disables interrupts and the peripheral clock; resume restores the clock, interrupt mask, and atomic state.

## State And Persistence Behavior

Persistent software state lives in `struct atmel_hlcdc_dc`: descriptor pointer, MFD pointer, CRTC pointer, layer array, DMA descriptor pool, DRM device, and saved suspend state/IMR. Hardware state includes HLCDC layer/global registers, interrupt masks, and clock state. Suspend stores a DRM atomic state pointer until resume consumes it.

## Dependencies And Integration Points

It depends on the Atmel HLCDC MFD, regmap, clocks, IRQs, runtime PM, platform bus, DRM GEM DMA helpers, KMS helpers, and local plane/CRTC/output code. Device-tree compatible strings on the parent MFD select the hardware descriptor.

## Risks And Edge Cases

Descriptor accuracy is critical because register offsets, layer capabilities, maximum mode sizes, clock-source behavior, and XLCDC operations all derive from tables. The vertical sync check uses `max_spw` for `vsync_len`, matching the existing code but easy to misread against `max_vpw`. IRQ status is shared between SOF and layer bits; stale masks can cause missed or spurious handling. Suspend/resume assumes a valid `dev_private` and successful clock re-enable.

## Test Signals

Build and boot on each compatible family, probe/remove cycles, vblank IRQ tests, page flips, suspend/resume with active scanout, mode-boundary tests, plane overrun debug signals, runtime PM checks, and device-tree descriptor validation are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/atmel-hlcdc/atmel_hlcdc_dc.c -->
