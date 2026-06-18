
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly917e.c

## Purpose
Defines the NV917E overlay constructor variant. It reuses the NV907E overlay implementation while expanding the advertised DRM format list.

## Important APIs, types, and functions
- `ovly917e_format[]` includes the NV907E formats plus `DRM_FORMAT_XRGB2101010`.
- `ovly917e_new()` calls `ovly507e_new_(&ovly907e, ovly917e_format, ...)`.

## Control flow
There is no independent programming path. Construction selects the wider format array, while all acquire, notification, image, scale, and update callbacks come from the `ovly907e` function table and shared overlay helpers.

## State and persistence
No state is stored here. Runtime state is held in `struct nv50_wndw` and `struct nv50_wndw_atom` by the common overlay code.

## Dependencies and integration points
Depends on `ovly.h` and on `ovly907e` being visible from the overlay backend set. This file is an integration shim for GPUs exposing the 917E overlay class but compatible with the 907E method sequence.

## Risks
The main compatibility risk is advertising `XRGB2101010` only when the underlying class and `ovly907e_image_set()` format mapping can represent it correctly. Any divergence between 917E hardware and 907E method layout would break at runtime because the same callbacks are reused.

## Test signals
Plane enumeration should show the additional 10-bit RGB format. Atomic overlay flips in both shared and added formats are the useful runtime check.
