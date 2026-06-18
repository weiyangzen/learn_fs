<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/base.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/base.c

### Purpose

Core VBIOS subdevice implementation and safe read helpers. It shadows a usable ROM image, provides endian-safe byte/word/dword access with bounds checks and image-D address remapping, detects BMP/BIT signatures, and records the VBIOS version.

### Important APIs, types, and functions

`nvbios_pointer()`, `nvbios_rd08/rd16/rd32()`, `nvbios_checksum()`, `nvbios_findstr()`, `nvbios_memcmp()`, `nvbios_extend()`, and `nvkm_bios_new()` are the central APIs. `nvkm_bios_dtor()` releases shadowed data.

### Control flow

Construction allocates `struct nvkm_bios`, calls `nvbios_shadow()`, enumerates ROM images to discover image0 and image-D remapping, scans for BMP and BIT signatures, extracts version from BIT `i` or BMP, then logs the version. Reads route through `nvbios_addr()` so image-D offsets and OOB reads are handled consistently.

### State and persistence behavior

`bios->data`, `bios->size`, image remap fields, BMP/BIT offsets, and version fields persist for the BIOS subdevice lifetime. `nvbios_extend()` can replace the backing buffer during shadow reads.

### Dependencies and integration points

Depends on shadow backends, `bit_entry()`, image parsing, BMP helpers, unaligned little-endian accessors, and NVKM subdevice lifecycle. All other BIOS parsers depend on this file.

### Risks

Bounds behavior returns zero on OOB, which prevents memory corruption but can hide corrupted firmware as absent fields. Shadow selection and image-D remapping affect every table parser.

### Test signals

Source read size: 213 lines, 5432 bytes. Boot with ROM, ACPI, PCI, OF, platform, and firmware sources; invalid ROM/OOB fuzzing; known VBIOS version checks; and parser regression against VBIOS dump corpus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/base.c -->
