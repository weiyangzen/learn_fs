<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs907a.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs907a.c

### Purpose
`curs907a.c` is a small generation wrapper that creates GF110/GK104 cursor immediate channels using the common 507A cursor implementation with a different interlock-bit layout.

### Key APIs And Functions
`curs907a_new()` calls `curs507a_new_(&curs507a, ...)` and passes `0x00000001 << (head * 4)` as the cursor interlock data.

### Control Flow And State
No independent state is introduced. The common constructor creates the DRM cursor plane, NVIF immediate object, and `wndw->immd` state; this wrapper only supplies the generation-specific class and interlock encoding.

### Dependencies And Integration
It depends on `curs.h` and is selected by `nv50_curs_new()` for GF110/GK104 cursor classes.

### Risks And Test Signals
The interlock shift is the only behavior, so regressions would show as cursor updates not synchronizing correctly with core commits on 907A-class hardware. Tests should include cursor movement/image updates during modesets on GF110/GK104.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs907a.c -->
