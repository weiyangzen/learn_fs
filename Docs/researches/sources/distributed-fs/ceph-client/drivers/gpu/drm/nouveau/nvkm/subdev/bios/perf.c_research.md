<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/perf.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/perf.c

### Purpose

Parser for performance/pstate tables under BIT `P`. It describes performance levels, domains, clock/memory entries, and voltage indexes used for reclocking.

### Important APIs, types, and functions

`nvbios_perf_table()`, `nvbios_perf_entry()`, `nvbios_perfEp()`, domain/subentry parsers, and matching helpers decode pstate records and nested per-domain records.

### Control flow

The table pointer is selected from BIT P, with special cases for older PCI/subsystem layouts. Supported versions expose header/count/entry/subentry sizing; entry parsing decodes pstate id, core/memory/shader domains, voltage, and flags according to version.

### State and persistence behavior

No stored state. Parsed performance records are transient inputs to clock, memory, and voltage code.

### Dependencies and integration points

Depends on BIT P, PCI subdevice data, RAM map helpers, and generic BIOS access. Clock and voltage subdevices consume this to build pstate tables.

### Risks

Pstate parsing is hardware-sensitive. Wrong units or domain indexes can over/underclock the GPU or choose an invalid voltage.

### Test signals

Source read size: 216 lines, 6073 bytes. Reclocking tests, pstate table dumps, VBIOS corpus comparison, voltage/frequency sanity checks, and absent/legacy table fallbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/perf.c -->
