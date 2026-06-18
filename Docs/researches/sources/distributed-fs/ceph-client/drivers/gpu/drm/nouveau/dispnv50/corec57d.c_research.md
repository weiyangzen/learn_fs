<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec57d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec57d.c

### Purpose
`corec57d.c` defines the GV100/Turing-era display core-channel function table for the C57D core class. It initializes display window usage limits and binds the core channel to the matching head, SOR, notifier, capability, and optional CRC implementations.

### Key APIs And Functions
`corec57d_init()` writes `NVC57D` methods for notifier DMA setup plus per-window format and usage bounds. The exported `corec57d_new()` passes the static `nv50_core_func corec57d` to `core507d_new_()`. The function table reuses C37D notifier/caps/update/window-owner helpers and selects `headc57d`, `sorc37d`, and debugfs `crcc57d`.

### Control Flow And State
Initialization reserves push space, programs all eight windows with packed RGB support, disables rotated formats, sets fetch/scaler restrictions, marks `core->assign_windows`, and kicks the core channel. Persistent state is limited to the core function table choice and the `assign_windows` flag consumed by the atomic commit path.

### Dependencies And Integration
The file depends on Nouveau push macros, `clc57d` register definitions, `core.h`, `head.h`, C37D shared helpers, and NVIF class IDs. It is selected by core-channel class probing and feeds `disp.c` atomic commits through `core->func`.

### Risks And Test Signals
The hard-coded eight-window count and usage bounds are hardware assumptions; wrong bounds can reject otherwise valid plane configurations or permit unsupported ones. Tests should cover initial modeset on GV100/TU-class hardware, window ownership assignment, debugfs CRC availability, and plane format/scaler validation across all advertised windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/corec57d.c -->
