<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.h

## Purpose
`vs_crtc.h` defines the VeriSilicon CRTC object, timing limit, container helper, and public initializer.

## Important APIs, Types, and Functions
It defines `VSDC_DISP_TIMING_VALUE_MAX`, `struct vs_crtc` with DRM CRTC base, `struct vs_dc *dc`, and output ID, `drm_crtc_to_vs_crtc()`, and `vs_crtc_init()`.

## Control Flow
The DRM initialization path calls `vs_crtc_init()` for each hardware display output, then bridge and IRQ paths recover the driver object through `drm_crtc_to_vs_crtc()`.

## State and Persistence Behavior
The header declares per-CRTC state ownership. Runtime state is held in allocated `struct vs_crtc` instances and DRM atomic CRTC state.

## Dependencies and Integration Points
It depends on DRM CRTC and vblank headers and forward-declares `struct vs_dc`. It is shared by CRTC, bridge, DRM core, and plane paths.

## Risks
The timing max macro is used for validation and must match hardware bitfield width. The output ID is used as an array index into clocks, CRTCs, and registers.

## Test Signals
Compile coverage and multi-output modeset/vblank tests validate this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_crtc.h -->
