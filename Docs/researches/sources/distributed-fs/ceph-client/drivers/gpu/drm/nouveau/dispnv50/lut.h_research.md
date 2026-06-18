<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.h

### Purpose
`lut.h` declares the NV50 output LUT memory wrapper and load/init/fini helpers.

### Key APIs And Types
`struct nv50_lut` contains two `nvif_mem` buffers for double-buffered LUT updates. The header declares `nv50_lut_init()`, `nv50_lut_fini()`, and `nv50_lut_load()`, with the load API accepting a generation-specific writer callback.

### Control Flow And State
The header has no executable control flow. Its state contract is embedded in `struct nv50_head` and used by head atomic commits.

### Dependencies And Integration
It includes `nvif/mem.h` and forward-declares DRM property/color LUT and `nv50_disp` types. It is included by `head.h` and implemented by `lut.c`.

### Risks And Test Signals
The double-buffer invariant is shared with head atomic state. Build tests should catch callback signature drift; runtime tests should verify gamma updates do not tear or overwrite active hardware reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/lut.h -->
