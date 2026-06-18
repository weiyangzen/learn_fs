<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.h

Purpose: private display head header defining head state, callback contracts, constructors, and generation-specific head exports.

Important APIs and types: `struct nvkm_head` stores callback table, display pointer, ID, list node, arm/asy `nvkm_head_state`, and embedded object. `nvkm_head_state` stores horizontal/vertical totals, sync and blanking edges, refresh rate, and pre-GF119 output depth. `struct nvkm_head_func` supplies state readout, raster position, raster clock divisor, and vblank get/put callbacks.

Control flow: no direct flow; generation files instantiate heads with `nvkm_head_new_()` and implement callbacks such as `nv50_head_new`, `gf119_head_new`, and `gv100_head_new`.

State and persistence: defines the cached arm/asy state fields used by modeset/supervisor code. Vblank callback state is hardware-owned and controlled through function pointers.

Dependencies and integration points: includes NVIF object definitions and display private state. `base.c` uses `vblank_get/put` through this contract; generation files use count/new exports.

Risks: field width choices (`u16` timings, `u32 hz`) must match hardware register decoding. Adding state fields requires updating generation state readers.

Test signals: head state reads across generations, vblank subscription/unsubscription, raster position queries, and modeset state comparison.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.h -->
