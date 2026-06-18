<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/cstep.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/cstep.c

### Purpose

Parser for clock-step tables from BIT `P`, used to map pstates to clock-step indexes and voltage/frequency step descriptors.

### Important APIs, types, and functions

`nvbios_cstepTe()`, `nvbios_cstepEe/Ep()`, `nvbios_cstepEm()`, `nvbios_cstepXe/Xp()` parse the table, pstate entries, pstate match, and extra step records.

### Control flow

BIT P version 2 length >= 0x38 provides a pointer at `P+0x34`. Version 0x10 tables include entry count/size and extra-record count/size. Entries encode pstate and step index; extra records encode frequency in kHz, two unknown bytes, and voltage id.

### State and persistence behavior

No persistent state. It decodes into caller-provided structures and returns offsets for further enumeration.

### Dependencies and integration points

Depends on BIT P and VBIOS reads. Clock and voltage transition code uses cstep metadata with pstate/perf tables.

### Risks

Unsupported table versions return zero. Misinterpreting the pstate bitfield or voltage byte can destabilize reclocking.

### Test signals

Source read size: 122 lines, 3467 bytes. VBIOS parser fixtures, reclocking tests through pstate changes, voltage-step validation, and absent-table fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/cstep.c -->
