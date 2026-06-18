<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pcir.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pcir.c

### Purpose

Parser for PCI ROM PCIR-compatible headers. It extracts vendor/device/class, image size/type/revision, and last-image markers.

### Important APIs, types, and functions

`nvbios_pcirTe()` validates PCIR/RGIS/NPDS signatures and returns version/header length; `nvbios_pcirTp()` decodes `struct nvbios_pcirT`.

### Control flow

The parser reads the header pointer at image base + 0x18, adds the image base, validates one of the accepted signatures, then reads fixed fields including size in 512-byte units and the last-image bit.

### State and persistence behavior

No mutable state. Decoded PCIR information is caller-owned.

### Dependencies and integration points

Depends on generic BIOS reads. `image.c`, `npde.c`, and shadow validation use PCIR metadata.

### Risks

Bad PCIR parsing affects image enumeration and ROM validation. Accepting alternate signatures is intentional but must remain precise.

### Test signals

Source read size: 69 lines, 2490 bytes. PCI ROM corpus tests, vendor/device/type comparison with lspci/ROM tools, and multi-image traversal tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/pcir.c -->
