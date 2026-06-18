<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.c

### Purpose
`oimm.c` selects and initializes the overlay immediate channel used with pre-GV100 overlay planes.

### Key APIs And Functions
`nv50_oimm_init()` probes a class table for overlay immediate classes from GK104 down to NV50 and dispatches to `oimm507b_init()`. It logs and returns the probe error when no supported class is present.

### Control Flow And State
The function only probes and delegates. The selected initializer attaches an immediate-channel object and function table to an existing overlay `nv50_wndw`.

### Dependencies And Integration
It depends on `oimm.h`, NVIF class IDs, and `nv50_disp()`. `nv50_ovly_new()` calls it after constructing a DMA overlay channel.

### Risks And Test Signals
Overlay immediate channel absence prevents overlay plane creation on old hardware. Tests should cover class selection across NV50/G82/GT214/GF110/GK104 and failure cleanup in `nv50_ovly_new()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.c -->
