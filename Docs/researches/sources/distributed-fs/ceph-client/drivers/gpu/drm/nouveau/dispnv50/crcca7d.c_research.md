<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcca7d.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcca7d.c

### Purpose
`crcca7d.c` implements GB202/Blackwell CRC callbacks. It keeps the C37D notifier record format but replaces legacy context-DMA programming with physical CRC surface-address methods.

### Key APIs And Functions
`crcca7d_set_ctx()` enables or disables the CRC surface address by splitting `ctx->mem.addr` into high and low physical fields. `crcca7d_set_src()` disables CRC and context when no source is requested, otherwise maps SOR/SF source types, programs the context, and writes `HEAD_SET_CRC_CONTROL`. The exported `crcca7d` table reuses C37D entry reading and completion callbacks.

### Control Flow And State
Enabling CRC first programs the physical notifier target as `PHYSICAL_NVM`, then emits CRC control with core as controlling channel. Disabling clears control before disabling the surface. Runtime state is generic CRC state plus the VRAM notifier memory allocated by `crc.c`.

### Dependencies And Integration
The file depends on `clca7d`, `pushc97b`, `crcc37d.h`, and head/core abstractions. `coreca7d.c` wires this table into the GB202 core function table under debugfs.

### Risks And Test Signals
`primary_crc` is assigned only for supported nonzero source types; invalid future source mappings would be risky. Tests should cover Blackwell CRC enable/disable, physical address alignment, SOR and SF captures, source rejection paths, and suspend/resume cleanup of mapped notifier memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/crcca7d.c -->
