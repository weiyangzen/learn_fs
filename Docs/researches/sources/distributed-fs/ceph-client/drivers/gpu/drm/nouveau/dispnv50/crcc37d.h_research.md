<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.h

### Purpose
`crcc37d.h` defines the shared C37D-style CRC notifier layout and helper declarations used by Volta and newer CRC implementations.

### Key APIs And Types
The header defines `CRCC37D_MAX_ENTRIES` as 2047, `CRCC37D_FLIP_THRESHOLD` as 30 entries before the end, and the packed `crcc37d_notifier` containing a status word, reserved padding, and `crcc37d_entry` records with status, compositor, RG, and output CRC fields. It declares `crcc37d_set_ctx()`, `crcc37d_get_entry()`, and `crcc37d_ctx_finished()`.

### Control Flow And State
The header contains no control flow. Its layout is the persistent memory contract between hardware-written VRAM notifier contexts and `crc.c` readers. The threshold constant controls when the generic double-buffer flip work schedules the next notifier context.

### Dependencies And Integration
It includes Linux integer types and `crc.h`, and is included by `crcc37d.c`, `crcc57d.c`, and `crcca7d.c`.

### Risks And Test Signals
Packed layout accuracy is critical because entries are read with MMIO helpers from mapped VRAM. Tests should validate notifier length against hardware expectations, capture at high refresh rates near 2047 entries, and ensure newer classes that reuse the layout still write compatible fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcc37d.h -->
