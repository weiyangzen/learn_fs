<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.h

### Purpose
`ovly.h` declares overlay plane constructors and shared overlay helper callbacks for NV50 display classes.

### Key APIs And Functions
It exposes constructors for `ovly507e`, `ovly827e`, `ovly907e`, `ovly917e`, the shared `ovly507e_new_()`, acquire/release/scale helpers, 827E notifier helpers, `ovly827e_format`, `ovly907e`, and the public `nv50_ovly_new()`.

### Control Flow And State
The header has no executable logic. Its declarations define the shared construction and function-table contracts for overlay windows.

### Dependencies And Integration
It includes `wndw.h` and is used by overlay generation files, `ovly.c`, and head creation in `head.c`.

### Risks And Test Signals
The shared helper signatures affect multiple overlay generations. Build tests across enabled generations and runtime overlay tests on 507E/827E/907E/917E classes are important signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly.h -->
