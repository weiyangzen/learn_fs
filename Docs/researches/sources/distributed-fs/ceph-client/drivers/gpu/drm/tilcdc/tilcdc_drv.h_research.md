# sources/distributed-fs/ceph-client/drivers/gpu/drm/tilcdc/tilcdc_drv.h

## Purpose

`tilcdc_drv.h` defines the TI LCDC driver's private state, default hardware limits, wrappers for plane/encoder objects, debug macro, and cross-file function prototypes.

## Important APIs, Types, and Definitions

- Default limits: `TILCDC_DEFAULT_MAX_PIXELCLOCK`, `TILCDC_DEFAULT_MAX_WIDTH_V1`, `TILCDC_DEFAULT_MAX_WIDTH_V2`, and `TILCDC_DEFAULT_MAX_BANDWIDTH`.
- `struct tilcdc_drm_private` embeds MMIO, clock, revision, IRQ, DRM device, mode limits, FIFO threshold, format list, cpufreq notifier, workqueue, CRTC, encoder, connector, and IRQ-enabled state.
- `ddev_to_tilcdc_priv()` converts embedded DRM device to private state.
- CRTC API declarations include create, IRQ, clock update, shutdown, and framebuffer update.
- `struct tilcdc_plane` and `struct tilcdc_encoder` wrap DRM objects.
- `tilcdc_plane_init()` creates the primary plane.

## Control Flow

`tilcdc_drv.c` fills the private struct during probe. `tilcdc_regs.h` uses it for MMIO access. `tilcdc_crtc.c`, `tilcdc_plane.c`, and `tilcdc_encoder.c` retrieve state through `ddev_to_tilcdc_priv()` and update shared CRTC/encoder/connector pointers.

## State and Persistence Behavior

`struct tilcdc_drm_private` persists for the DRM device lifetime. Some fields are immutable after probe, while `irq_enabled`, connector pointers, and CRTC runtime fields change during operation.

## Dependencies and Integration Points

The header depends on cpufreq and DRM print declarations plus forward-declared DRM types. It is the central internal ABI for all tilcdc source files.

## Risks and Edge Cases

- The embedded `struct drm_device ddev` means conversion macros depend on layout.
- Public mutable fields can be modified by any tilcdc module.
- Defaults are fallback policy; DT values must be validated in runtime mode checks.
- Conditional cpufreq field requires all users to guard access under `CONFIG_CPU_FREQ`.

## Test Signals

Build tests should cover cpufreq enabled/disabled and all tilcdc modules. Runtime tests should validate private-field initialization, connector presence, IRQ flag transitions, and limit enforcement from defaults and DT overrides.
