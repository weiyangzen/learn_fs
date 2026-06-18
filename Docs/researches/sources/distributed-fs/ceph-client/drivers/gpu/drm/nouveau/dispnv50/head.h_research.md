<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.h

### Purpose
`head.h` defines the NV50 head object and the generation-specific head programming function table used by common CRTC code.

### Key APIs And Types
`struct nv50_head` contains the selected `nv50_head_func`, display pointer, embedded `nouveau_crtc`, CRC state, output LUT memory, and optional MST encoder. `struct nv50_head_func` declares callbacks for view, mode, OLUT, core surface, cursor, base/overlay usage, dither, procamp, output resource, static window mapping, and display ID programming. The header also declares all exported generation helpers and function tables.

### Control Flow And State
The header does not execute logic. Its callback table determines which register methods common `head.c` flushes during atomic commits, while the `nv50_head` structure persists for the lifetime of a DRM CRTC.

### Dependencies And Integration
It includes local `disp.h`, `atom.h`, `crc.h`, and `lut.h`, plus Nouveau CRTC/encoder headers. It is consumed by `head.c`, core function tables, cursor/CRC/output code, and all `head*` generation files.

### Risks And Test Signals
Callback optionality is important: common code checks some function pointers but assumes others for active generations. Build and runtime coverage should include each display class table, including paths with no `or`, no `core_calc`, and Blackwell physical-address callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/head.h -->
