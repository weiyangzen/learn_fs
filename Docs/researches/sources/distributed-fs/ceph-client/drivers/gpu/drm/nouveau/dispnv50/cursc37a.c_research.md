<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/cursc37a.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/cursc37a.c

### Purpose
`cursc37a.c` implements the Volta-and-newer cursor immediate-channel method variants while reusing common cursor plane validation and construction.

### Key APIs And Functions
`cursc37a_update()` writes `NVC37A UPDATE`. `cursc37a_point()` writes indexed hotspot coordinates with `SET_CURSOR_HOT_SPOT_POINT_OUT(0)`. The static `cursc37a` immediate function table is passed to `curs507a_new_()` by `cursc37a_new()`, using `0x00000001 << head` interlock data.

### Control Flow And State
Channel wait precedes every immediate write. All plane validation, image preparation, and object mapping are inherited from `curs507a_new_()`.

### Dependencies And Integration
The file depends on `clc37a`, `atom.h`, and `curs.h`. `curs.c` selects it for GV100/TU102/GA102/GB202 cursor classes; `headc37d`, `headc57d`, and `headca7d` provide the matching head-side cursor programming.

### Risks And Test Signals
The class uses different method addresses and interlock semantics from 507A/907A. Tests should verify cursor position and image updates on Volta-or-newer heads, including 128/256 cursor layouts supplied by newer head functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/cursc37a.c -->
