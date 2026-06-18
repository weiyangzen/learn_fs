<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.h

### Purpose
`crc.h` declares the NV50 display CRC abstraction and provides no-op stubs when debugfs support is disabled. It is the contract between the generic CRC state machine in `crc.c`, head atomic state, and generation-specific hardware implementations.

### Key APIs And Types
The enabled path defines `enum nv50_crc_source`, `enum nv50_crc_source_type`, `struct nv50_crc_notifier_ctx`, `struct nv50_crc_atom`, `struct nv50_crc_func`, and `struct nv50_crc`. `nv50_crc_func` supplies `set_src`, `set_ctx`, `get_entry`, `ctx_finished`, `flip_threshold`, `num_entries`, and `notifier_len`. The header declares source validation, source listing, source setting, atomic lifecycle helpers, vblank handling, initialization, and external generation tables.

### Control Flow And State
The header does not execute logic directly, but its structures define persistent per-head CRC state: two notifier contexts, a vblank work item, active source, frame number, entry index, flip threshold, selected context index, and context-changed flag. When debugfs is disabled, matching inline stubs preserve call sites without stateful behavior.

### Dependencies And Integration
It depends on DRM CRTC/vblank work headers, NVIF memory, BIOS/output declarations, and Nouveau encoder/head forward declarations. `head.h` embeds `struct nv50_crc`; `disp.c` and `head.c` call the declared helpers during atomic commits and vblank.

### Risks And Test Signals
Any mismatch between `nv50_crc_func` semantics and generic expectations can corrupt reporting or leak notifier memory. Build tests should cover both `CONFIG_DEBUG_FS=y` and disabled configurations. Runtime tests should validate that each source maps to expected output CRC entries and that per-generation notifier lengths match the hardware layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.h -->
