<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm507b.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm507b.c

### Purpose
`oimm507b.c` constructs the NV50-style overlay immediate-channel object and binds it to a common immediate function table.

### Key APIs And Functions
`oimm507b_init_()` creates and maps a `kmsOvim` NVIF display channel for `wndw->id`, assigns `wndw->immd`, and logs allocation failures. `oimm507b_init()` calls it with the cursor immediate function table `curs507a`, reusing point/update behavior.

### Control Flow And State
The initializer creates the NVIF object under the display object, maps it, and stores the immediate callback pointer in the overlay window. State persists in `wndw->wimm.base.user` and `wndw->immd`.

### Dependencies And Integration
It depends on `oimm.h`, `if0014` display-channel arguments, and `curs507a` from the cursor implementation. It is called by `nv50_oimm_init()` after overlay DMA channel creation.

### Risks And Test Signals
Reusing cursor immediate callbacks for overlay immediate behavior relies on compatible method semantics. Tests should cover overlay point/update immediate operations, allocation failure paths, and object teardown through window destruction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/oimm507b.c -->
