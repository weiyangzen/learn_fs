<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.c

### Purpose
`crc.c` implements DRM debugfs CRC capture for NV50+ display heads when `CONFIG_DEBUG_FS` is enabled. It validates CRC source strings, allocates notifier memory, programs CRC source/context state during atomic commits, drains hardware CRC entries on vblank, and exposes a per-head debugfs flip-threshold control.

### Key APIs And Functions
Public entry points include `nv50_crc_verify_source()`, `nv50_crc_get_sources()`, `nv50_crc_set_source()`, `nv50_crc_handle_vblank()`, the atomic helpers `nv50_crc_atomic_*()`, `nv50_head_crc_late_register()`, and `nv50_crc_init()`. Internal helpers parse source names, map output encoders to CRC source types, initialize/free notifier contexts, wait for context completion, flip double-buffered notifier contexts, and read entries through `nv50_crc_func` callbacks.

### Control Flow And State
CRC capture is started through `set_crc_source`, which builds an atomic state, allocates two VRAM notifier contexts per head, sets `asyh->crc.src`, and commits. The atomic tail stops old reporting, initializes contexts, programs the new source, starts vblank reporting, and later releases contexts. During vblank, `nv50_crc_handle_vblank()` uses a spinlock, checks whether a context flip finished, drains nonzero entries into `drm_crtc_add_crc_entry()`, advances frame and entry counters, resets old contexts, and schedules the next flip via `drm_vblank_work`.

### Dependencies And Integration
The code depends on DRM CRTC CRC hooks, atomic state helpers, `drm_vblank_work`, NVIF memory/object/timer APIs, Nouveau core/head/window/output objects, `handles.h`, and generation-specific CRC function tables from `crc907d.c`, `crcc37d.c`, `crcc57d.c`, and `crcca7d.c`. It integrates with `head.c` vblank handling and with `disp.c` atomic sequencing to avoid CRC disable conflicts with output-resource reprogramming.

### Risks And Test Signals
Races around vblank timing, context flips, display mutex contention, and notifier lifetime are the main risks. The code intentionally accounts for one lost CRC frame on context flips. Tests should cover all source names, enable/disable/re-enable cycles, output modesets while CRC is active, busy flip-threshold writes, notifier overflow logging, suspend/resume, and debugfs-disabled builds where the header stubs must compile out the feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crc.c -->
