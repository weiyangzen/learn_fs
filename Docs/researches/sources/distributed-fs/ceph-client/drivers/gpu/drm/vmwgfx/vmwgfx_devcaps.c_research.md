# sources/distributed-fs/ceph-client/drivers/gpu/drm/vmwgfx/vmwgfx_devcaps.c

## Purpose
This file snapshots VMware SVGA 3D device capability records and provides the data-copy path used by the GET_3D_CAP ioctl. It supports both guest-backed-object aware userspace, which can consume the raw devcap array, and older compatibility userspace, which expects FIFO-style capability records.

## Important APIs, types, and functions
- `struct svga_3d_compat_cap` wraps `SVGA3dFifoCapsRecordHeader` plus up to `SVGA3D_DEVCAP_MAX` `(cap, value)` pairs.
- `vmw_mask_legacy_multisample()` hides deprecated `SVGA3D_DEVCAP_DEAD5` multisample-maskable-samples data from legacy userspace by returning zero for that cap.
- `vmw_fill_compat_cap()` writes a bounded compatibility record into a caller-provided bounce buffer and sets header length/type.
- `vmw_devcaps_create()` allocates `vmw->devcaps` and reads each indexed `SVGA_REG_DEV_CAP` value when `SVGA_CAP_GBOBJECTS` is present.
- `vmw_devcaps_destroy()` frees and nulls the devcap array.
- `vmw_devcaps_size()` reports the byte count needed for raw guest-backed-aware caps, compatibility caps, legacy FIFO caps, or zero when no source exists.
- `vmw_devcaps_copy()` copies raw devcaps, fills compatibility records, or copies legacy FIFO cap words depending on device capabilities and userspace awareness.

## Control flow
Driver load calls `vmw_devcaps_create()` after SVGA capabilities and TTM managers are initialized. For guest-backed devices, the function writes each devcap index to `SVGA_REG_DEV_CAP` and reads back the value into a fixed-size array. Later ioctl handling asks `vmw_devcaps_size()` for the needed payload size and calls `vmw_devcaps_copy()` to populate the user response. On unload or probe error unwinding, `vmw_devcaps_destroy()` releases the vmalloc allocation.

## State and persistence behavior
The only persistent state is `vmw_private.devcaps`, a vmalloc array of `SVGA3D_DEVCAP_MAX` 32-bit values. It is a boot/probe-time snapshot; this file does not refresh it after device reset except through the broader driver restore/reinitialization path. Legacy FIFO caps are not cached here and are read directly from `vmw->fifo_mem` during copy.

## Dependencies and integration points
The implementation depends on `vmwgfx_drv.h` for `struct vmw_private`, register accessors, capability bits, and `vmw->fifo_mem`, plus SVGA register/development capability definitions. It integrates with `vmwgfx_drv.c` during probe/unload and with ioctl code that exposes 3D capability data to userspace.

## Risks and edge cases
- `vmw_devcaps_copy()` trusts `dst_size` from the caller for raw and FIFO `memcpy()` lengths; callers must obtain or clamp it through `vmw_devcaps_size()` to avoid overread.
- `vmw_devcap_get()` in the header indexes `vmw->devcaps` without bounds checks, so all callers must use valid `SVGA3D_DEVCAP_*` enum values and only after successful devcap creation.
- Non-guest-backed devices with no `fifo_mem` return size zero and copy failure; ioctl callers must surface that cleanly.
- The compatibility size calculation intentionally includes an extra `sizeof(uint32_t)` in `vmw_devcaps_size()` for guest-backed but not gb-aware clients, so consumers should avoid duplicating layout assumptions.

## Test signals
Probe on guest-backed SVGA should allocate a non-null devcap array and expose raw capabilities to gb-aware clients. Legacy clients should receive a caps record with type `SVGA3D_FIFO_CAPS_RECORD_DEVCAPS`, bounded pair count, and zero for the deprecated multisample cap. Non-GB or FIFO-only configurations should still return FIFO 3D caps when `fifo_mem` is present.
