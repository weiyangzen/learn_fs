<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/rammap.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/rammap.c

### Purpose

Parser for RAM frequency and RAM configuration maps under BIT `P`. It maps memory frequency ranges to RAM timing/config subentries and includes compatibility helpers for older performance-table embedded RAM data.

### Important APIs, types, and functions

`nvbios_rammapTe/Ee/Ep/Em()`, `nvbios_rammapSe/Sp()`, and `_from_perf` helpers decode table entries, select entries by MHz, and decode per-RAMCFG subrecords.

### Control flow

The table pointer is read from BIT P version 2 at offset +4. Versions 0x10 and 0x11 expose entry and subentry sizes. Match flow chooses the frequency range containing the requested MHz, then callers index subentries for the selected RAM config.

### State and persistence behavior

No durable state. The returned `struct nvbios_ramcfg` carries many bitfields used later by RAM training and timing code.

### Dependencies and integration points

Depends on BIT P, performance parser compatibility, and BIOS readers. Memory clock/reclock paths consume this with `timing.c` and `ramcfg.c`.

### Risks

Large bitfield surface is fragile; wrong offsets can break memory controller programming. Frequency range matching must be deterministic for overlapping or malformed entries.

### Test signals

Source read size: 258 lines, 10098 bytes. Memory reclocking tests, RAM timing dump comparison, VBIOS corpus fixtures for v0x10/v0x11, and malformed range tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/rammap.c -->
