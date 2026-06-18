# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_devcaps.h

## Purpose
This header exposes the device-capability lifecycle and copy helpers used by vmwgfx probe and ioctl code. It also provides a small inline accessor for cached SVGA3D devcaps.

## Important APIs
- `vmw_devcaps_create()` initializes cached devcap storage for guest-backed devices.
- `vmw_devcaps_destroy()` frees cached devcap storage.
- `vmw_devcaps_size()` returns the capability payload size expected by a caller, taking guest-backed awareness into account.
- `vmw_devcaps_copy()` materializes capability data into a destination buffer.
- `vmw_devcap_get()` returns one cached devcap value when `SVGA_CAP_GBOBJECTS` is set, otherwise zero.

## Control flow and integration
`vmwgfx_drv.c` includes this header to initialize devcaps during driver load, query specific devcaps while deriving shader model support, and destroy the cache during unload/error paths. Ioctl code uses the size/copy API to answer user requests without knowing whether data comes from raw devcaps, compatibility records, or FIFO caps.

## State and persistence behavior
The header itself owns no storage, but all APIs operate on `struct vmw_private`. `vmw_devcap_get()` reads `vmw->capabilities` and `vmw->devcaps`, so its correctness depends on probe-time capability discovery and successful `vmw_devcaps_create()`.

## Dependencies
It includes `vmwgfx_drv.h` for `struct vmw_private` and `device_include/svga_reg.h` for `SVGA_CAP_GBOBJECTS`. That inclusion direction is heavier than a pure forward declaration but keeps the inline accessor available.

## Risks and edge cases
- `vmw_devcap_get()` has no `devcap < SVGA3D_DEVCAP_MAX` check and no null check for `vmw->devcaps`. It should only be called after successful devcap initialization and with constants from the SVGA3D devcap enum.
- Returning zero for non-GB devices conflates unsupported caps with valid zero-valued caps; callers use it only in guest-backed shader model detection, where that behavior is acceptable.

## Test signals
Compile tests should ensure the header does not create circular include failures. Runtime probe logs and shader model selection provide indirect checks that `vmw_devcap_get()` sees expected values for DX context, SM4.1, SM5, and GL43 capability bits.
