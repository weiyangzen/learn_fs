# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/device_include/svga3d_surfacedefs.h

## Purpose

`svga3d_surfacedefs.h` describes SVGA3D surface formats in a static metadata table. It maps each `SVGA3dSurfaceFormat` to block/category flags, block dimensions, bytes per block, pitch granularity, and channel bit-depth/offset information.

## Important APIs, Types, and Functions

- `SVGA3dBlockDesc`: bitmask taxonomy for color, depth, stencil, compressed, planar YUV, typeless, integer, normalized, sRGB, floating point, bump, BCn, and compound channel descriptions.
- `SVGA3dChannelDef`: unioned channel byte fields for color, bump, YUV, luminance, depth, stencil, and exponent interpretations.
- `SVGA3dSurfaceDesc`: per-format descriptor containing format ID, block descriptor, block size, bytes per block, pitch bytes per block, bit depths, and bit offsets.
- `g_SVGA3dSurfaceDescs[]`: static const descriptor array indexed in the same order as `SVGA3dSurfaceFormat`.
- `STATIC_CONST`: platform-dependent storage-class macro, `static const` in the kernel/GNU path.

## Control Flow

There is no executable control flow. Runtime consumers index or search `g_SVGA3dSurfaceDescs` to validate formats, compute pitches/sizes, and understand channel layout.

## State and Persistence Behavior

The descriptor table is immutable static data. It does not allocate or mutate state; consumers derive transient validation and size calculations from it.

## Dependencies and Integration Points

- Includes `svga3d_types.h` for format IDs and size types.
- Integrates with surface creation validation, format capability checks, pitch/size calculations, and copy/transfer code.
- Must stay synchronized with `SVGA3dSurfaceFormat` enum values and devcap format constants.

## Risks and Edge Cases

- Table ordering must match enum numeric values. Missing or reordered entries can make every later format decode incorrectly.
- Compressed and planar formats use block and pitch units that differ from simple pixel formats; size calculations must use `blockSize`, `bytesPerBlock`, and `pitchBytesPerBlock` correctly.
- Unioned channel names make descriptor interpretation context-dependent.
- The `STATIC_CONST` macro has cross-platform baggage; in kernel builds it should remain static to avoid duplicate global definitions.

## Test Signals

- Static tests should verify `ARRAY_SIZE(g_SVGA3dSurfaceDescs) == SVGA3D_FORMAT_MAX` and descriptor `.format` matches its index where expected.
- Format-size tests should cover RGB, depth/stencil, compressed BC, NV12/YV12 planar, typeless, and buffer formats.
- Validation tests should compare descriptor properties against devcap-supported format flags.
