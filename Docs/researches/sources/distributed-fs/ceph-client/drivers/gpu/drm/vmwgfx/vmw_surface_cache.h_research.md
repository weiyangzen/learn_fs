# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmw_surface_cache.h

## Purpose
Provides inline geometry, size, offset, and dirty-tracking helpers for SVGA3D surface formats. It converts user-visible surface dimensions into block-aligned byte layouts, mip-chain offsets, screen-target format predicates, and offset-to-subresource locations used by dirty tracking and CPU blit/update paths.

## Important APIs, Types, And Functions
- `clamped_umul32()` saturates 32-bit multiplication to avoid wraparound.
- `vmw_surface_get_desc()`, `vmw_surface_get_mip_size()`, and `vmw_surface_get_size_in_blocks()` derive descriptor and block dimensions.
- `vmw_surface_get_image_buffer_size()`, `vmw_surface_get_serialized_size()`, and `_extended()` compute backing-store sizes.
- `vmw_surface_get_pixel_offset()` and `vmw_surface_get_image_offset()` map coordinates, faces, and mips to byte offsets.
- `struct vmw_surface_cache`, `struct vmw_surface_mip`, and `struct vmw_surface_loc` cache per-mip layout and offset-derived locations.
- `vmw_surface_setup_cache()`, `vmw_surface_get_loc()`, `vmw_surface_inc_loc()`, `vmw_surface_min_loc()`, and `vmw_surface_max_loc()` support dirty-region computation.

## Control Flow
Callers set up a cache from base dimensions, format, mip levels, layers, and sample count. The cache precomputes mip sizes, bytes, row stride, image stride, total mip-chain bytes, and sheet bytes. Offset-to-location walks sheet, layer, mip, z, y, and x in that order. Increment/min/max helpers produce SVGA box-compatible ranges for touched subresources.

## State, Persistence, Dependencies, And Integration
All state is caller-owned stack or embedded cache data. There is no persistence or locking. The header depends on SVGA surface descriptors from `device_include/svga3d_surfacedefs.h` and DRM vmwgfx UAPI sizes. It is used by surface validation, dirty tracking, copy/update code, and screen-target creation checks.

## Risks And Test Signals
Risks are arithmetic overflow, invalid zero strides, descriptor mismatch for planar/compressed formats, and off-by-one errors when translating byte ranges to SVGA boxes. Test signals include maximum dimension saturation, compressed block formats, planar YUV sizing, multisample size multiplication, all mip/layer offset boundaries, and dirty-range conversion at the first and last byte of each subresource.
