<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/boost.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/boost.c

### Purpose

Parser for boost clock tables referenced from BIT `P`. It describes per-pstate boost frequency ranges and per-domain boost percentage/min/max records.

### Important APIs, types, and functions

`nvbios_boostTe()`, `nvbios_boostEe/Ep()`, `nvbios_boostEm()`, and `nvbios_boostSe/Sp()` parse table headers, entries, pstate matches, and subentries.

### Control flow

BIT P version 2 must be at least 0x34 bytes; the boost table pointer is read at `P+0x30`. Version 0x11 tables use fixed header/count/entry/subentry sizes. Match flow walks entries until the requested pstate is found, then callers may enumerate subentries.

### State and persistence behavior

No persistent state. Parsed pstate, min/max kHz, domain, percent, and subentry min/max values are returned in caller-owned structs.

### Dependencies and integration points

Depends on BIT P and VBIOS readers. It feeds clock and performance-management code that constructs boost ranges.

### Risks

Only version 0x11 is supported. Unit conversion multiplies table MHz values by 1000; bad fields can lead to invalid boost envelopes.

### Test signals

Source read size: 126 lines, 3628 bytes. Boost table parse fixtures, pstate/boost sysfs or debug output validation, and frequency transition tests on GPUs with boost tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/boost.c -->
