<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane_regs.h

## Purpose
`vs_primary_plane_regs.h` defines VeriSilicon framebuffer/primary-plane register offsets and bitfields.

## Important APIs, Types, and Functions
Key macros include `VSDC_FB_ADDRESS`, `VSDC_FB_STRIDE`, `VSDC_FB_CONFIG` fields for format/swizzle/tile/rotation/scale/YUV, `VSDC_FB_SIZE`, `VSDC_FB_CONFIG_EX` commit/enable/zpos/display ID bits, position registers, and blend-disable bit.

## Control Flow
`vs_primary_plane_atomic_update()` writes these registers and then sets the commit bit. Enable/disable paths also use config-ex enable/display/commit bits.

## State and Persistence Behavior
The macros describe persistent display-controller plane state. There is no software state.

## Dependencies and Integration Points
It depends on Linux bit macros and common plane packing macros from `vs_plane.h` for values written to size/position registers.

## Risks
`VSDC_FB_CONFIG_TILE_MODE(v)` shifts by 14 while the mask is bits 21:17, which appears inconsistent and should be reviewed before tile-mode support is used. Display ID mask currently covers one bit, matching two outputs only.

## Test Signals
Register encoding tests should validate format, swizzle, display ID, enable/disable, geometry, and tile-mode macros before adding tiled formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/verisilicon/vs_primary_plane_regs.h -->
