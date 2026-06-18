# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/ltc/base.c

## Purpose
Provides the common LTC subdevice wrapper for cache tag clearing, zero-bandwidth clear programming, cache invalidation/flush, interrupt dispatch, and subdevice lifetime.

## Important APIs, Types, and Functions
Public helpers are `nvkm_ltc_tags_clear`, `nvkm_ltc_zbc_color_get`, `nvkm_ltc_zbc_depth_get`, `nvkm_ltc_zbc_stencil_get`, `nvkm_ltc_invalidate`, `nvkm_ltc_flush`, and `nvkm_ltc_new_`. Internal subdev hooks are `nvkm_ltc_oneinit`, `nvkm_ltc_init`, `nvkm_ltc_intr`, and `nvkm_ltc_dtor`.

## Control Flow, State, and Persistence
Construction stores the chip `nvkm_ltc_func`, initializes the mutex, and calculates valid ZBC color/depth index ranges while reserving index 0. Init replays all stored ZBC color/depth/stencil entries before invoking the chip init hook. Tag clearing validates the tag range, serializes through `ltc->mutex`, calls hardware clear, and waits.

## Dependencies and Integration Points
It depends on chip callbacks in `priv.h`, `nvkm_memory_unref` for `tag_ram`, public `subdev/ltc.h`, and framebuffer tag allocation users.

## Risks and Test Signals
Risks include invalid tag range BUGs, missing optional stencil callbacks, stale ZBC replay after reset, and cache flush hooks being absent on a chip. Test with ZBC allocation/replay, compression tag allocation, interrupt dispatch, cache invalidation/flush, and subdevice teardown.
