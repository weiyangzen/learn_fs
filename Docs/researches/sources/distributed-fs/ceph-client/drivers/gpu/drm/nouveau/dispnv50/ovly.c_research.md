<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.c

### Purpose
`ovly.c` selects and creates pre-GV100 overlay DMA channels and attaches the matching overlay immediate channel.

### Key APIs And Functions
`nv50_ovly_new()` probes overlay DMA/control classes from GK104 down to NV50, dispatches to `ovly917e_new()`, `ovly907e_new()`, `ovly827e_new()`, or `ovly507e_new()`, then calls `nv50_oimm_init()` on the created window.

### Control Flow And State
The function chooses the highest supported class, constructs the overlay `nv50_wndw`, and initializes immediate-channel state. The persistent state is stored in the returned window object.

### Dependencies And Integration
It depends on `ovly.h`, `oimm.h`, NVIF class probing, and `nv50_disp()`. `head.c` calls it while creating old-generation heads.

### Risks And Test Signals
Both DMA and immediate objects must be created successfully for a usable overlay plane. Tests should cover class selection, failure cleanup, overlay plane visibility changes, and old display classes where overlay support differs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.c -->
