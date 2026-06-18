# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/shmobile/shmob_drm_drv.c

## Purpose

`shmob_drm_drv.c` is the platform DRM driver for legacy Renesas SH Mobile LCDC hardware. It selects clocks, allocates the DRM device, maps MMIO, initializes KMS and IRQ handling, manages runtime/system PM, and registers the DRM device.

## Important APIs, Types, and Functions

Important functions are `shmob_drm_setup_clocks()`, `shmob_drm_irq()`, system/runtime PM callbacks, `shmob_drm_probe()`, `shmob_drm_remove()`, and `shmob_drm_shutdown()`. `shmob_drm_driver` advertises GEM/modeset/atomic support with GEM DMA and fbdev helpers. OF match data supplies `shmob_arm_config`.

## Control Flow

Probe accepts either OF match config or platform data, allocates managed DRM private data, copies config, maps MMIO, selects the dot-clock source, enables runtime PM, initializes vblank, initializes modeset, gets and requests the IRQ, registers DRM, and starts a DRM client with RGB565. The IRQ handler locks around `LDINTR`, acknowledges pending status bits, handles vblank, and completes page flips. Runtime suspend/resume gates the selected clock. System sleep delegates to DRM mode config suspend/resume. Remove unregisters, atomic-shuts down, and finalizes polling.

## State and Persistence Behavior

`struct shmob_drm_device` persists as DRM private state and stores config/platform data, MMIO, clock, prepared `lddckr`, IRQ lock/number, CRTC, encoder, and connector. Runtime PM controls clock lifetime, while CRTC enable/disable controls LCDC register state.

## Dependencies and Integration Points

The driver depends on platform/OF/PM runtime/clock/IRQ APIs, DRM core/client/GEM/vblank helpers, local KMS/CRTC/plane/register code, and optional platform data.

## Risks and Edge Cases

- Interrupt enable and status share `LDINTR`, requiring the spinlock discipline used here; all other writers must follow it.
- Probe supports platform data and OF; missing both fails early.
- `shmob_drm_setup_clocks()` maps logical clock sources to clock names and register selectors; wrong platform data breaks output clocking.
- Remove ordering must prevent IRQ/page-flip activity after DRM unregister/shutdown.

## Test Signals

Probe with OF and platform data, IRQ/vblank/page-flip completion, runtime PM clock gating, system suspend/resume, remove/shutdown, and clock source selection for bus/peripheral/external clocks are important.
