# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/hdlcd_drv.c

## Purpose

`hdlcd_drv.c` is the top-level ARM HDLCD platform DRM driver. It owns device allocation, MMIO mapping, hardware identity checks, clock/resource setup, IRQ installation, mode-config setup, component binding to an external encoder, vblank initialization, debugfs counters, runtime/system power hooks, and DRM device registration.

## Important APIs, Types, And Functions

The driver defines `hdlcd_driver`, `hdlcd_mode_config_funcs`, `hdlcd_master_ops`, and `hdlcd_platform_driver`. Probe is split between `hdlcd_probe()`, which builds a component-master match from OF graph port 0, and `hdlcd_drm_bind()`, which allocates `struct hdlcd_drm_private`, initializes mode config, calls `hdlcd_load()`, binds child components, registers vblank, and registers the DRM device. `hdlcd_irq()` services VSYNC and optional debug interrupts. Debugfs exposes `interrupt_count` and `clocks` when enabled.

## Control Flow

Probe obtains the remote output node and registers a component master. Bind allocates the DRM device, initializes mode-config limits and callbacks, then `hdlcd_load()` gets the `pxlclk`, maps MMIO, validates `HDLCD_REG_VERSION`, initializes optional reserved memory, sets a 32-bit DMA mask, creates the CRTC, gets the IRQ, and installs the handler. Bind then stores the CRTC output port, binds external components, enables runtime PM, initializes vblank, disables any firmware-left-enabled controller and removes conflicting aperture users, resets mode config, initializes polling, adds debugfs files, registers the DRM device, and starts the DRM client setup. Unbind unregisters and shuts down in reverse.

## State And Persistence Behavior

`struct hdlcd_drm_private` stores MMIO, clock, CRTC, plane pointer, IRQ number, and optional atomic interrupt counters. Hardware state persists in HDLCD registers until atomic commits, IRQ acknowledgement, cleanup, or disable. Reserved-memory attachment persists for the device lifetime. Runtime PM state is enabled after component binding and disabled during unbind/error paths. Debug counters are in-memory atomics reset at load.

## Dependencies And Integration Points

The file integrates Linux platform devices, OF graph, component framework, reserved memory, DMA mask setup, aperture takeover, DRM atomic/modeset/vblank/client helpers, fbdev DMA helper ops, GEM DMA helper ops, HDLCD CRTC setup, and an external encoder component discovered through DT. It depends on register definitions from `hdlcd_regs.h` and private state/accessors from `hdlcd_drv.h`.

## Risks And Edge Cases

Error unwinding crosses DRM-managed and non-managed resources: IRQ install, reserved memory, CRTC cleanup, component binding, PM enablement, and OF node references must stay balanced. `pm_runtime_get_sync()` in unbind is not checked. Firmware takeover only checks `HDLCD_REG_COMMAND`, so stale register state beyond the command bit may remain until the first modeset. IRQ debug counters are conditional, and debug IRQ mask differs from VSYNC mask used by vblank enable.

## Test Signals

Validation should cover probe/remove, invalid product-id rejection, missing output graph, missing clock/IRQ, reserved-memory success and absence, simplefb/aperture handoff, component bind/unbind failure paths, vblank interrupt delivery, debugfs counter increments, system suspend/resume via DRM mode-config helpers, and DRM client/fbdev setup on systems with and without fbdev emulation.
