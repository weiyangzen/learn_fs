<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowramin.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowramin.c

### Purpose

RAMIN shadow backend. It reads a VBIOS image that firmware or hardware left in GPU instance/RAMIN memory.

### Important APIs, types, and functions

`nvbios_ramin` defines callbacks; internal code reads GPU memory through device MMIO/memory access windows and reports source size.

### Control flow

Init prepares any required private state, read copies aligned ranges from RAMIN into the BIOS buffer, and fini releases wrapper allocations. The generic shadow code validates the result.

### State and persistence behavior

No long-lived state unless this candidate wins; the copied image becomes `bios->data`.

### Dependencies and integration points

Depends on NVKM device memory/MMIO access and the shadow-source interface. It is useful when PROM/PCI ROM are not directly readable.

### Risks

RAMIN contents may be stale, relocated, or partially overwritten. Read alignment and size assumptions must match hardware.

### Test signals

Source read size: 123 lines, 3542 bytes. Boot tests on systems where RAMIN is the selected source, comparison to PROM/PCI ROM images, and corrupt/truncated RAMIN fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowramin.c -->
