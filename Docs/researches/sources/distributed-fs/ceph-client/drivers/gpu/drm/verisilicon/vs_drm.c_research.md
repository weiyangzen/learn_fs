<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.c

## Purpose
`vs_drm.c` implements the DRM-device layer for VeriSilicon DC: GEM/dumb buffer policy, mode-config setup, CRTC/bridge creation, vblank init, device registration, fbdev/client setup, shutdown, and IRQ dispatch.

## Important APIs, Types, and Functions
Key APIs are `vs_drm_initialize()`, `vs_drm_finalize()`, `vs_drm_shutdown_handler()`, and `vs_drm_handle_irq()`. Important internal pieces include `vs_gem_dumb_create()`, `vs_drm_driver`, mode-config funcs, and `vs_mode_config_init()`.

## Control Flow
Initialization allocates a managed `struct vs_drm_dev`, links it to `vs_dc`, initializes mode config, removes conflicting firmware framebuffers, creates a CRTC and bridge for each hardware display, initializes vblank, sets mode bounds and atomic helpers, starts connector polling, resets mode config, registers the DRM device, and starts DRM clients. Finalize unregisters DRM, stops polling, performs atomic shutdown, and clears `dc->drm_dev`. IRQ handling walks display outputs, sends vblank events for known VSYNC bits, and warns once on unknown interrupts.

## State and Persistence Behavior
Persistent state is `struct vs_drm_dev`, its CRTC pointer array, and the linked `struct vs_dc`. Dumb buffers are DMA GEM objects with 128-byte aligned pitches. DRM registration exposes device nodes and fbdev/client state until finalize.

## Dependencies and Integration Points
The file depends on DRM driver, atomic helper, GEM DMA/fbdev DMA, aperture removal, bridge/CRTC init, vblank, connector polling, and top-level IRQ bit definitions. It is called exclusively by the platform DC driver.

## Risks
The CRTC array assignment happens even when `vs_bridge_init()` returns NULL for skipped outputs, so display count and bridge presence must be handled by userspace/DRM correctly. `vs_gem_dumb_create()` enforces pitch alignment but format support remains governed by planes. Unknown IRQ bits may indicate unhandled hardware events. Shutdown assumes `dc->drm_dev` is valid.

## Test Signals
Tests should cover conflicting simple-framebuffer removal, registration failure unwind, dumb buffer pitch alignment, dual-output vblank handling, skipped bridge outputs, DRM hotplug polling, remove, and system shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.c -->
