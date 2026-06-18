<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.h

### Purpose
`curs.h` declares cursor immediate-channel constructors and the common helper used by generation wrappers.

### Key APIs And Functions
The header exposes `curs507a_new()`, `curs507a_new_()`, `curs907a_new()`, `cursc37a_new()`, and `nv50_curs_new()`. `curs507a_new_()` accepts a `nv50_wimm_func` table plus interlock data, allowing later generations to reuse the common cursor plane creation while changing immediate-channel methods.

### Control Flow And State
There is no runtime logic in the header. It defines the construction contract that produces an `nv50_wndw` cursor plane with embedded immediate-channel state.

### Dependencies And Integration
It includes `wndw.h` for `nv50_wndw` and `nv50_wimm_func`. `head.c` uses the public constructor through `nv50_curs_new()`.

### Risks And Test Signals
Signature drift here would affect all head creation paths. Build coverage across NV50, 907A, and C37A cursor implementations is the key signal, with runtime checks for cursor interlock masks on different generations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/curs.h -->
