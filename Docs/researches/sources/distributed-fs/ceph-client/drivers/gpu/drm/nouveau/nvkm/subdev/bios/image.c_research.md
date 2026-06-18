<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/image.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/image.c

### Purpose

ROM image enumerator for multi-image PCI VBIOS blobs. It validates image signatures, reads PCIR/NPDE metadata, and returns image base, size, type, and last-image status.

### Important APIs, types, and functions

`nvbios_image()` is the public iterator; `nvbios_imagen()` validates one image and fills `struct nvbios_image`.

### Control flow

Enumeration starts at base 0 and repeatedly advances by the previous image size. Valid signatures include 0xaa55, 0xbb77, and `NV`. PCIR provides default size/type/last; NPDE can override size/last for non-type-0x70 images.

### State and persistence behavior

No persistent state, except it temporarily clears/restores `bios->imaged_addr` while enumerating to avoid remap interference.

### Dependencies and integration points

Depends on `pcir.c`, `npde.c`, and BIOS access. `base.c` uses it to identify image-D remapping and shadow validation uses it to score ROM images.

### Risks

Wrong image size or last handling can truncate ROMs or read into adjacent data. Signature rejection affects shadow-source scoring.

### Test signals

Source read size: 83 lines, 2511 bytes. Multi-image ROM fixture tests, image-D remap validation, shadow-source scoring tests, and comparison with PCI ROM parser output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/image.c -->
