# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bar/base.c

## Purpose
Implements common BAR subdevice lifecycle and public helpers for BAR1/BAR2 VMM access, reset, init/fini, and flush.

## Important APIs, types, and functions
Exports `nvkm_bar_flush()`, `nvkm_bar_bar1_vmm()`, `nvkm_bar_bar1_reset()`, `nvkm_bar_bar2_vmm()`, `nvkm_bar_bar2_init()`, `nvkm_bar_bar2_fini()`, `nvkm_bar_bar2_reset()`, and `nvkm_bar_ctor()`. Subdev callbacks call generation `oneinit`, `init`, `fini`, and `dtor`.

## Control flow, state, and persistence
Init programs BAR1 then optional generation init. BAR2 is initialized lazily only after oneinit and tracked by `bar->bar2`; fini disables BAR1 and, outside suspend, BAR2. Public VMM helpers deny BAR2 before initialization so instmem can fall back to BAR0.

## Dependencies and integration points
Depends on generation `nvkm_bar_func`, subdev lifecycle, and device-level `device->bar`. Used by memory managers, instmem, and SW semaphore paths.

## Risks and test signals
BAR2 lifetime is shared with instmem, so suspend/fini ordering matters. Signals include successful BAR1/BAR2 VMM retrieval, flush completion, and absence of mapping faults.
