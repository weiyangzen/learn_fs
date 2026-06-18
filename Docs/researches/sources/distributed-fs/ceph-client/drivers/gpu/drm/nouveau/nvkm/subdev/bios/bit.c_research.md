<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/bit.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/bit.c

### Purpose

Minimal parser for the BIT table directory in NVIDIA VBIOS images.

### Important APIs, types, and functions

`bit_entry()` locates one BIT directory entry by one-byte id and returns its id, version, length, and 16-bit offset in `struct bit_entry`.

### Control flow

If `bios->bit_offset` is present, the function reads the entry count and entry stride from the BIT header, then linearly scans entries until the requested id matches. Missing entries return `-ENOENT`; absent BIT support returns `-EINVAL`.

### State and persistence behavior

No state is stored. The function exposes immutable directory metadata from the shadowed BIOS image.

### Dependencies and integration points

Depends on `nvbios_rd08/rd16()`. Almost every modern table parser uses it to find BIT `C`, `D`, `I`, `M`, `P`, `x`, and other directories.

### Risks

A wrong entry stride or BIT offset compromises all downstream parsers. Only 16-bit entry offsets are decoded here, matching the table format used by these VBIOS revisions.

### Test signals

Source read size: 49 lines, 1781 bytes. BIT table parser fixtures, boot logs showing BIT signature detection, and fallback tests on BMP-only legacy VBIOS images.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/bit.c -->
