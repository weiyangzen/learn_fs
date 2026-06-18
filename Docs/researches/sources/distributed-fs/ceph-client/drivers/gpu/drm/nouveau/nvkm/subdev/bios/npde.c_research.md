<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/npde.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/npde.c

### Purpose

Parser for NPDE metadata that can follow PCIR in newer ROM images. It refines image size and last-image status.

### Important APIs, types, and functions

`nvbios_npdeTe()` locates and validates the NPDE signature; `nvbios_npdeTp()` fills `struct nvbios_npdeT` with image size and last flag.

### Control flow

The code first parses PCIR, aligns the post-PCIR offset to 16 bytes, checks for the `NPDE` signature, and decodes size in 512-byte units plus the high last-image bit.

### State and persistence behavior

No persistent state; returned metadata is used immediately by image enumeration.

### Dependencies and integration points

Depends on `pcir.c` and generic BIOS reads. `image.c` consumes NPDE for image sizing.

### Risks

If alignment or signature handling is wrong, multi-image ROM traversal can stop early or overrun into unrelated image data.

### Test signals

Source read size: 59 lines, 2024 bytes. ROM image fixture tests with and without NPDE, multi-image enumeration, and shadow-source validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/npde.c -->
