<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/coreca7d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/coreca7d.c

### Purpose
`coreca7d.c` defines the GB202/Blackwell display core-channel implementation. It adapts the C37D/C57D core model to newer `NVCA7D` methods that use physical notifier/surface addresses rather than legacy CTXDMA handles.

### Key APIs And Functions
`coreca7d_update()` optionally programs the core notifier physical address, emits cursor/window interlock flags, issues `UPDATE`, and disables notifier writes afterward. `coreca7d_init()` programs window usage bounds, physical window assignment, head usage bounds, per-head tile masks, and tile sizes. `coreca7d_new()` installs the `coreca7d` function table with `headca7d`, `sorc37d`, `crcca7d`, and `GB202_DISP_CAPS`.

### Control Flow And State
On init, eight windows and four heads are configured before `assign_windows` is set. On update, the notifier offset is derived from the display sync BO, split into high/low physical fields, and used only when the caller requests notification. State persists in `core->assign_windows` and in the active hardware core channel.

### Dependencies And Integration
The file depends on `pushc97b`, `clca7d`, `nouveau_bo`, NVIF class IDs, and the shared core/head abstractions. It is the core-channel endpoint used by `disp.c` for Blackwell atomic commits, CRC context programming, and notifier completion.

### Risks And Test Signals
The switch away from CTXDMA handles makes address alignment and target selection critical. Tests should include core updates with and without notification, suspend/resume reinitialization, window/head assignment on all heads, and CRC plus plane commits on GB202-class hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/coreca7d.c -->
