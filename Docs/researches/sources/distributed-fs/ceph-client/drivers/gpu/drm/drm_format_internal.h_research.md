# sources/distributed-fs/ceph-client/drivers/gpu/drm/drm_format_internal.h

## Purpose
`drm_format_internal.h` defines inline raw pixel conversion primitives used by DRM format helper loops. It keeps per-pixel bit manipulation separate from line-copy mechanics.

## Important APIs, Types, And Functions
The header provides static inline converters from XRGB8888 to R8 luma, RGB332, RGB565, big-endian RGB565, RGBX5551, RGBA5551, XRGB1555, ARGB1555, RGB888, BGR888, ARGB8888, XBGR8888, BGRX8888, ABGR8888, XRGB2101010, ARGB2101010, XBGR2101010, and ABGR2101010. It also provides ARGB8888 to ARGB4444 conversion. The helpers use `u32`, `BIT()`, `GENMASK()`, and `swab16()`.

## Control Flow
Each converter accepts a little-endian logical raw pixel as `u32`, masks source channels, shifts or expands bits into the target layout, and returns a `u32` wide enough for the target value. Alpha-setting variants fill alpha bits to opaque. The BT.601 helper computes grayscale luma as `(77 R + 150 G + 29 B) / 256`.

## State, Persistence, And Dependencies
The header has no state and no exported symbols. It depends only on Linux bit, type, and byte-swap helpers. Its conversion behavior is compiled into users such as `drm_format_helper.c`.

## Integration Points
Line conversion loops in `drm_format_helper.c` pass these functions as per-pixel callbacks to pack converted pixels into 8-, 16-, 24-, or 32-bit destination streams. Drivers indirectly use these helpers through exported DRM framebuffer conversion APIs.

## Risks
All conversions assume little-endian byte-order pixel interpretation at the helper boundary. Bit expansion for 2101010 formats approximates 8-bit channels into 10-bit channels by bit replication; tests should lock down expected values. The header intentionally expects 32-bit input/output and is not sufficient for output formats wider than 32 bits.

## Test Signals
Good tests use fixed XRGB8888 and ARGB8888 pixel fixtures for each converter, alpha-bit assertions for opaque variants, byte-order checks for RGB565BE, BT.601 luma known values, and 2101010 bit replication edge cases such as all-zero, all-one, and single-channel maxima.
