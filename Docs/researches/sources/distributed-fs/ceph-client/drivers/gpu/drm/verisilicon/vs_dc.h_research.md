<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.h

## Purpose
`vs_dc.h` declares the central VeriSilicon display-controller state shared by platform, DRM, CRTC, bridge, and plane code.

## Important APIs, Types, and Functions
It defines `VSDC_MAX_OUTPUTS`, `VSDC_RESET_COUNT`, and `struct vs_dc` containing regmap, core/AXI/AHB clocks, per-output pixel clocks, reset bulk data, DRM device pointer, and chip identity.

## Control Flow
Probe fills `struct vs_dc`; DRM initialization and atomic callbacks then use it to access registers, clocks, output count, supported formats, and CRTC pointers.

## State and Persistence Behavior
`struct vs_dc` persists for the platform-device bind lifetime and owns no devm resource directly, but stores pointers to devm-managed resources. `drm_dev` is set during DRM initialization and cleared during finalize.

## Dependencies and Integration Points
The header depends on clock, regmap, reset, DRM device, and hardware database definitions. It is the shared state contract for all VeriSilicon DC files.

## Risks
Array fields are fixed at two outputs; future hardware with more outputs requires coordinated updates. `drm_dev` can be NULL during probe failure/finalize and must not be dereferenced outside initialized paths.

## Test Signals
Compile tests and dual-output modeset/IRQ coverage validate the shared state layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_dc.h -->
