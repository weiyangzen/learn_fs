<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowrom.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowrom.c

### Purpose

PROM/ROM shadow backend. It reads the GPU's on-board VBIOS ROM through device ROM access registers.

### Important APIs, types, and functions

`nvbios_prom` is the exported `nvbios_source`; callbacks read ROM bytes and report size through the NVKM device interface.

### Control flow

The backend opens access to the PROM, reads requested offsets for `shadow_fetch()`, and lets the generic shadow scorer validate image signatures and checksums.

### State and persistence behavior

Backend state is temporary; a selected PROM image persists as the BIOS data buffer.

### Dependencies and integration points

Depends on low-level NVKM device ROM reads and the shadow-source interface. It is one of the first sources tried for a native ROM image.

### Risks

ROM access can fail on some laptops or firmware-managed systems; wrong size reporting causes shadow validation failures.

### Test signals

Source read size: 64 lines, 2035 bytes. PROM boot tests, forced source selection with `NvBios=prom`, checksum failure fallback, and comparison with PCI ROM dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowrom.c -->
