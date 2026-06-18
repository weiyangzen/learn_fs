# sources/distributed-fs/ceph-client/drivers/gpu/drm/renesas/rz-du/rzg2l_du_drv.c

## Purpose

`rzg2l_du_drv.c` is the platform DRM driver for RZ/G2L Display Unit devices. It provides SoC routing data, allocates the DRM device, maps MMIO, sets DMA constraints, initializes KMS, registers the DRM device, and handles remove/shutdown.

## Important APIs, Types, and Functions

SoC data tables describe `r9a07g043u`, `r9a07g044`, and `r9a09g057` channel masks and output ports. `rzg2l_du_output_name()` formats output names. `rzg2l_du_probe()`, `rzg2l_du_remove()`, and `rzg2l_du_shutdown()` implement platform lifecycle. `rzg2l_du_driver` advertises GEM, modeset, and atomic support with GEM DMA/fbdev helpers.

## Control Flow

Probe exits when firmware-only DRM drivers are requested, allocates a managed DRM device, stores device info from OF match data, maps MMIO, coerces DMA to 32-bit coherent, initializes modeset objects, registers the DRM device, logs probe success, and starts DRM client setup. Remove unregisters the DRM device, performs atomic shutdown, and finalizes polling. Shutdown performs atomic shutdown only.

## State and Persistence Behavior

`struct rzg2l_du_device` persists as the DRM private object and stores MMIO, device info, CRTC, and VSP structures. Hardware state is shut down through DRM atomic helper paths on remove/shutdown.

## Dependencies and Integration Points

The file depends on platform/OF APIs, DRM core/client/GEM DMA helpers, DMA mask helpers, and `rzg2l_du_modeset_init()`. It binds to Renesas DU compatible strings.

## Risks and Edge Cases

- DMA is forced to 32-bit; buffers outside addressable range must be rejected or bounced by DMA infrastructure.
- Probe error path only finalizes KMS polling after modeset init failure; managed DRM allocation handles most object cleanup.
- Routing tables must match DT port numbering and hardware output capabilities.

## Test Signals

Probe/remove/shutdown on all compatibles, 32-bit DMA buffer allocation, no encoder case, firmware-only suppression, and module unload/reload are useful signals.
