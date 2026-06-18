# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/sw/nvsw.c

## Purpose
Implements the generic NVSW software object attached to a software channel. It provides object methods and uevent registration.

## Important APIs, types, and functions
`nvkm_nvsw_new_()` and `nvkm_nvsw_new()` allocate objects. `nvkm_nvsw_mthd()` delegates object methods to an optional `nvkm_nvsw_func`. `nvkm_nvsw_uevent()` subscribes userspace uevents to the channel page-flip event.

## Control flow, state, and persistence
Object creation stores the function table and owning `nvkm_sw_chan`. Method calls are forwarded if a generation-specific handler exists, otherwise return `-ENODEV`. Uevent setup validates argument size and adds a listener for `NVKM_SW_CHAN_EVENT_PAGE_FLIP`.

## Dependencies and integration points
Depends on `if0004` event argument ABI, `nvkm_uevent_add()`, and channel events from `chan.c`. Used by NV10, NV50, GF100, and by NV04 through a custom method table.

## Risks and test signals
Argument-size mismatch returns `-ENOSYS`; method absence returns `-ENODEV`. Test signals are page-flip event delivery and NV04 custom method forwarding.
