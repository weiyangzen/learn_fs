<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.h

### Purpose
`oimm.h` declares overlay immediate-channel initialization helpers.

### Key APIs And Functions
It exposes `oimm507b_init()` for generation-specific construction and `nv50_oimm_init()` for class selection.

### Control Flow And State
The header has no logic. Its functions attach immediate-channel state to an already-created `nv50_wndw` overlay plane.

### Dependencies And Integration
It includes `wndw.h` and is used by `ovly.c` and `oimm507b.c`.

### Risks And Test Signals
The interface is narrow but tied to old overlay support. Build coverage plus overlay plane creation tests on pre-GV100 hardware are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm.h -->
