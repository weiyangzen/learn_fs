<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/priv.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/priv.h

### Purpose

Private header for the NVKM BIOS implementation. It defines the shadow-source abstraction and declares internal shadowing helpers/backends.

### Important APIs, types, and functions

`struct nvbios_source` contains backend name, init/fini/read/size callbacks, and policy flags for read-write support, checksum handling, PCIR bypass, and required checksums. It also declares `nvbios_extend()`, `nvbios_shadow()`, and built-in source objects.

### Control flow

No executable control flow. `shadow.c` iterates these backends and calls their callbacks to read candidate ROM images.

### State and persistence behavior

No state by itself, but the flags define how shadow-source state is scored and validated.

### Dependencies and integration points

Depends on `subdev/bios.h`. Included by base and shadow backend files.

### Risks

Changing callback semantics or flags affects all BIOS source selection. `no_pcir`, checksum, and read-write flags directly influence whether a ROM image is accepted.

### Test signals

Source read size: 29 lines, 910 bytes. Build coverage and BIOS shadow-source tests for PROM, RAMIN, ACPI, PCIROM, platform, OF, and firmware sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/priv.h -->
