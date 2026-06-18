<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.h

## Purpose
`vs_plane.h` defines VeriSilicon plane format enums, position/size packing macros, shared plane helper prototypes, and the primary-plane initializer declaration.

## Important APIs, Types, and Functions
It defines `VSDC_MAKE_PLANE_SIZE()`, `VSDC_MAKE_PLANE_POS()`, `enum vs_color_format`, `enum vs_swizzle`, `struct vs_format`, `drm_format_to_vs_format()`, `vs_fb_get_dma_addr()`, and `vs_primary_plane_init()`.

## Control Flow
Primary-plane code calls the helper functions and macros during atomic updates to encode framebuffer format, top-left/bottom-right coordinates, size, stride, and DMA address.

## State and Persistence Behavior
The header contains no runtime state. Encoded values become persistent hardware register state after regmap writes.

## Dependencies and Integration Points
It depends on DRM device, framebuffer, plane, and rect definitions. It is included by common plane and primary-plane implementation files.

## Risks
Position/size macros mask to 15 bits, so validation must keep dimensions and coordinates within hardware range. Color enum values must match hardware register encoding.

## Test Signals
Compile coverage and plane atomic update register-value tests validate the definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_plane.h -->
