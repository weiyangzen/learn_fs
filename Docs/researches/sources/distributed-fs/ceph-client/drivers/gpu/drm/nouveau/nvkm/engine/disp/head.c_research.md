<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.c

Purpose: common display head object lifetime and lookup helpers. Heads represent scanout/timing engines in the NVKM display model.

Important APIs and functions: `nvkm_head_find()` searches `disp->heads` by ID. `nvkm_head_new_()` allocates, initializes function pointer/display/id, links the head into `disp->heads`, and logs construction. `nvkm_head_del()` logs destruction, removes from the list, frees memory, and nulls the caller pointer.

Control flow: simple list allocation/lookup/free. Generation files provide the `nvkm_head_func` callback table for state, raster position/clock, and vblank enablement.

State and persistence: persistent per-head state is defined in `head.h`; this file owns list membership and lifecycle. Deletion mutates the display's head list.

Dependencies and integration points: used by display generation oneinit paths and vblank event code in `base.c`. User head wrappers and supervisor/modeset code look up or iterate these objects.

Risks: deleting heads while events or outputs still reference them would break vblank and state queries; display destructor ordering currently finalizes events before deleting heads.

Test signals: head count creation on probe, `nvkm_head_find()` for valid/invalid IDs, vblank event init/fini, and teardown leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/engine/disp/head.c -->
