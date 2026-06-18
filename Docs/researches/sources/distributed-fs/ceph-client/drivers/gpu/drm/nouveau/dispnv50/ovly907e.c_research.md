
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly907e.c

## Purpose
Implements the NV907E overlay window backend used by Nouveau display code. It supplies the `nv50_wndw_func` method table for a 90-series overlay channel and creates overlay planes with the supported DRM formats.

## Important APIs, types, and functions
- `ovly907e_image_set()` writes NV907E present, DMA context, composition, surface offset, size, storage, format, and color-space methods.
- `const struct nv50_wndw_func ovly907e` wires common overlay helpers (`ovly507e_acquire`, `ovly507e_release`, `base507c_*`, `ovly827e_*`) to the NV907E image setter.
- `ovly907e_format[]` permits YUYV, UYVY, XRGB8888, XRGB1555, XBGR2101010, and XBGR16161616F.
- `ovly907e_new()` calls `ovly507e_new_()` with the overlay head mask `0x00000004 << (head * 4)`.

## Control flow
Plane creation is delegated to the shared 507E overlay constructor with this file's function table and format list. During an atomic flush, the generic overlay path calls `ovly907e_image_set()` after `nv50_wndw` state has prepared `asyw->image`. The function reserves push space, programs ASAP present control with the requested minimum present interval, binds the ISO DMA handle, forces opaque composition, and describes a single surface plane.

## State and persistence
The file owns no persistent state. It serializes fields already stored in `struct nv50_wndw_atom`, including `handle[0]`, `offset[0]`, dimensions, pitch/block layout, format, color space, and interval, into the display engine channel. Those hardware methods persist until replaced or cleared by shared `base507c_image_clr()`.

## Dependencies and integration points
Depends on `ovly.h`, `atom.h`, `nvif/push507c.h`, and `nvhw/class/cl907e.h`. It integrates with the shared NV50 overlay infrastructure, DRM plane format selection, and the display pushbuffer/interlock update path.

## Risks
The storage method writes both `PITCH` fields from block count and pitch expressions, so the method definition must match the generated class field aliases. Offset and pitch are shifted by eight bits, making alignment assumptions important. Format support is narrow and must match both DRM format validation and the NV907E hardware format field.

## Test signals
Build coverage catches method/class mismatches. Runtime signals are overlay plane enablement on supported GPUs, correct format/color output, no pushbuffer reservation failures, and successful atomic flips with non-tearing interval changes.
