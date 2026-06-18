<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.h

### Purpose
`disp.h` declares the shared NV50 display device/channel structures and synchronization-memory offsets used by the dispnv50 implementation.

### Key APIs And Types
`struct nv50_disp` holds the NVIF display object, core channel, caps object, shared sync BO, and display mutex. Macros define offsets for core notifier, window semaphores, and window notifiers. `struct nv50_disp_interlock` describes interlock type/data/wimm state. `struct nv50_chan`, `struct nv50_dmac`, and `struct nv50_outp_atom` define common channel and output-atomic state. The header declares DMA channel creation/destruction, `nv50_real_outp()`, display modifiers, and shared helpers.

### Control Flow And State
There is no control flow in the header. Its definitions persist through the whole KMS lifecycle: `nv50_disp` is stored in `nouveau_display(dev)->priv`, `nv50_dmac` backs core/window push channels, and `nv50_outp_atom` nodes live inside an atomic commit state.

### Dependencies And Integration
It depends on Linux workqueues, NVIF memory/push APIs, and Nouveau display headers. Nearly every dispnv50 file includes it directly or indirectly for sync offsets, channel state, and display-private access.

### Risks And Test Signals
Offset macros are hardware contracts shared by notifiers and semaphores. Tests should validate notifier/semaphore completion for base, overlay, window, and core channels, and build coverage should catch structure users when fields evolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/disp.h -->
