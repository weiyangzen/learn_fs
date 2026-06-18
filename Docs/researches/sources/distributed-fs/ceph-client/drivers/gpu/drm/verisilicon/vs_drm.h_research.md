<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.h

## Purpose
`vs_drm.h` declares the VeriSilicon DRM device wrapper and lifecycle/IRQ APIs used by the platform DC driver.

## Important APIs, Types, and Functions
It defines `struct vs_drm_dev` embedding `struct drm_device`, storing `struct vs_dc *dc`, and a CRTC pointer array sized by `VSDC_MAX_OUTPUTS`. It declares `vs_drm_initialize()`, `vs_drm_finalize()`, `vs_drm_shutdown_handler()`, and `vs_drm_handle_irq()`.

## Control Flow
The platform driver calls initialize after resources are ready, finalize during remove, shutdown handler during system shutdown, and IRQ handler from the top-level interrupt routine.

## State and Persistence Behavior
The DRM wrapper persists for the DRM device lifetime and points back to DC state. CRTC pointers are populated during initialization and consumed by IRQ dispatch.

## Dependencies and Integration Points
It depends on platform device and DRM device types and on `VSDC_MAX_OUTPUTS` from the included DC context. It is shared between DC, DRM, CRTC, and IRQ code.

## Risks
The header relies on `VSDC_MAX_OUTPUTS` being visible from included dependencies. Null CRTC entries are possible when outputs are skipped or initialization is partial.

## Test Signals
Compile tests and probe/remove/IRQ tests validate this API contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_drm.h -->
