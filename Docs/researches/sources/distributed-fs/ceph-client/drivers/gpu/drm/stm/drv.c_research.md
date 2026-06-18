# sources/distributed-fs/ceph-client/drivers/gpu/drm/stm/drv.c

## Purpose
`drv.c` is the STM32 DRM platform driver front end. It allocates and registers the DRM device, configures mode limits and GEM/DMA helpers, delegates hardware setup to `ltdc_load`, and manages system/runtime power transitions through LTDC suspend/resume helpers.

## Important APIs, Types, and Functions
- `drv_driver`: DRM driver descriptor with modeset, GEM, atomic, DMA GEM, dumb-buffer, and fbdev helper operations.
- `stm_gem_dma_dumb_create`: aligns dumb-buffer pitch to 128 bytes and height to 4 lines before DMA GEM allocation.
- `drv_load` and `drv_unload`: allocate `struct ltdc_device`, initialize mode config, call LTDC load/unload, setup polling, and stash the DRM device in platform data.
- `drv_suspend`/`drv_resume`: use `drm_atomic_helper_suspend/resume`, store `ldev->suspend_state`, and force runtime PM state.
- `stm_drm_platform_probe/remove/shutdown`: own platform lifecycle and DRM registration.
- `drv_dt_ids`: matches STM32 LTDC variants and supplies pad clock limits through `struct ltdc_plat_data`.

## Control Flow, State, and Persistence
Probe removes conflicting framebuffer devices, sets a 32-bit coherent DMA mask, allocates the DRM device, calls `drv_load`, registers DRM, and starts the DRM client with RGB565. `drv_load` creates managed mode config, assigns max dimensions, enables zpos normalization, and calls `ltdc_load`. Remove unregisters DRM, shuts down KMS helpers, unloads LTDC, and drops the DRM device. Suspend persists the atomic state in `ldev->suspend_state` until resume consumes it.

## Dependencies and Integration Points
The file depends on DRM atomic helpers, DMA GEM/fbdev helpers, aperture removal, runtime PM, platform OF matching, and `ltdc.h`. It is the integration point between Linux platform devices and the LTDC implementation.

## Risks and Test Signals
Risks include incomplete cleanup on probe errors, 32-bit DMA assumptions, runtime/system PM ordering, and framebuffer size limits mismatching newer hardware. Tests should cover probe/remove error unwinding, dumb-buffer alignment, suspend/resume with active planes, runtime PM callbacks, OF variant pad limits, and DRM client/fbdev creation.
