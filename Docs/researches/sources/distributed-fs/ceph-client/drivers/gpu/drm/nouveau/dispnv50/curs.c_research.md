<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.c

### Purpose
`curs.c` selects and creates the per-head hardware cursor immediate channel for the active display class.

### Key APIs And Functions
`nv50_curs_new()` defines an ordered class table from GB202/GA102/TU102/GV100 down to NV50, uses `nvif_mclass()` to choose the supported cursor class, and dispatches to `cursc37a_new()`, `curs907a_new()`, or `curs507a_new()`.

### Control Flow And State
The function probes the display object's supported classes, logs an error if none match, and delegates object creation to the generation-specific helper. It does not persist state directly; the returned `nv50_wndw` carries the cursor plane, immediate-channel object, and interlock information.

### Dependencies And Integration
It depends on `curs.h`, `disp.h` through `nv50_disp()`, NVIF class IDs, and Nouveau DRM logging. `head.c` calls this during CRTC/head creation after primary and overlay planes are built.

### Risks And Test Signals
Class ordering determines which implementation newer hardware receives. Tests should cover cursor creation on each supported display family, no-supported-class failure, and integration with `drm_crtc_init_with_planes()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.c -->
