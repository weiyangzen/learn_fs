<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly827e.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly827e.c

### Purpose
`ovly827e.c` adapts the base overlay plane to 827E-era hardware. It changes image method encoding, adds 10-bit XBGR format support, and provides notifier reset/wait helpers for the newer notification layout.

### Key APIs And Functions
`ovly827e_image_set()` writes `NV827E` present, context, composition, surface offset/size/storage/params methods. `ovly827e_ntfy_wait_begun()` polls the notification status for `BEGUN` with a 2-second timeout. `ovly827e_ntfy_reset()` clears timestamp/status fields. The `ovly827e` function table reuses 507E acquire/release/scale/update and base notifier set/clear. `ovly827e_new()` calls `ovly507e_new_()`.

### Control Flow And State
The 827E window uses the same DMA-channel lifetime as 507E but with class-specific image methods and notification status handling. Supported formats add `DRM_FORMAT_XBGR2101010`.

### Dependencies And Integration
It depends on `cl827e`, `push507c`, NVIF timers, `nouveau_bo`, `atom.h`, and shared overlay/base helpers. `ovly.c` selects it for GT200/G82/GT214 overlay DMA classes.

### Risks And Test Signals
Notifier polling is timeout-sensitive, and image method fields must match the class layout. Tests should cover notification reset/wait, 10-bit overlay formats, enable/disable cycles, and timeout logging under stalled hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/ovly827e.c -->
