<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/ramcfg.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/ramcfg.c

### Purpose

RAM configuration selector. It reads hardware strap bits and translates them into the logical RAM configuration index used by memory init tables.

### Important APIs, types, and functions

`nvbios_ramcfg_count()` returns the number of RAM configurations; `nvbios_ramcfg_index()` returns the selected config; `nvbios_ramcfg_strap()` reads strap bits from register `0x101000`.

### Control flow

The count comes from BIT M version 1 or 2 fields. The selected index starts with strap bits, then uses M0203 RAMCFG translation when available on BIT M v2, otherwise uses an xlat table pointer from BIT M.

### State and persistence behavior

No persistent state here. `init.c` caches the selected RAMCFG in `struct nvbios_init` on newer VBIOSes to avoid repeated strap reads.

### Dependencies and integration points

Depends on BIT M, M0203 parser, generic BIOS access, and MMIO reads. Memory init, RAM map, and init-script RAM restrict opcodes depend on it.

### Risks

Reading the strap register repeatedly can be unsafe on later chipsets, so callers must respect caching behavior. Wrong translation can select incompatible memory timings.

### Test signals

Source read size: 78 lines, 2502 bytes. Memory init boot tests across strap variants, VBIOS fixtures for BIT M v1/v2, M0203 fallback tests, and register-read tracing during init scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/ramcfg.c -->
