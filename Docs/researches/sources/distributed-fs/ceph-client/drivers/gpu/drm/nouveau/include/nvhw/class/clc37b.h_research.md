<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37b.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37b.h

Purpose: `clc37b.h` defines the `NVC37B` window-immediate class and its simple DMA packet format. It supports immediate point/output updates and optional interlock with regular window state.

Important APIs and types: the DMA packet macros define opcode, method count, method offset, data, jump offset, and subdevice mask fields for method, jump, non-incrementing method, and set-subdevice-mask commands. Class methods include `NVC37B_UPDATE` with `INTERLOCK_WITH_WINDOW` and indexed `NVC37B_SET_POINT_OUT(b)` packing X/Y coordinates.

Control flow: `dispnv50/wimmc37b.c` includes this header for window immediate commits. The driver programs output point coordinates, optionally asks update to interlock with the normal window channel, then emits update to apply the immediate state without a full core modeset.

State and persistence: point-out coordinates persist in the immediate window channel until replaced. DMA opcode definitions affect pushbuffer decoding but hold no state. Interlock state is per update and coordinates with other display channel updates.

Dependencies and integration: included by `wimmc37b.c` and `include/nvif/pushc37b.h`. It fits into Nouveau's Volta/Turing display split where window immediate state is separate from core, cursor, and regular window channels.

Risks: DMA packet field widths differ from `NV906F`; using the wrong packet encoder would corrupt display channel command parsing. Interlock misuse can apply immediate window changes out of sync with regular window updates. Coordinate packing must stay within 16-bit X/Y ranges.

Test signals: atomic plane position changes that use the window-immediate path, especially with and without interlock. Visual signals include tear-free plane movement, no stale coordinates after update, and no display channel exceptions from malformed DMA methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37b.h -->
