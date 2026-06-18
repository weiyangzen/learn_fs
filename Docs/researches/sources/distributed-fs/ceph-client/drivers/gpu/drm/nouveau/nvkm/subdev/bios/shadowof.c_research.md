<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowof.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowof.c

### Purpose

Open Firmware/device-tree VBIOS shadow backend. It reads a ROM blob property supplied by firmware on OF platforms.

### Important APIs, types, and functions

`nvbios_of` and `nvbios_platform`-style OF source definitions expose init/fini/read/size callbacks. The private state stores a pointer and size for the firmware-provided ROM data.

### Control flow

Init locates the firmware property, read copies requested ranges into `bios->data`, size reports the blob length, and fini releases any allocated wrapper state.

### State and persistence behavior

Persistent state is only selected if `shadow.c` chooses this backend; otherwise the copied candidate buffer is freed.

### Dependencies and integration points

Depends on OF/device-tree APIs and the generic shadow-source interface. Used mainly on non-PC platforms where PCI ROM access may not be available.

### Risks

Firmware-provided blobs can be missing, truncated, or not PCIR formatted depending on platform. Source flags determine whether PCIR/checksum validation is required.

### Test signals

Source read size: 89 lines, 2391 bytes. OF platform boot tests, VBIOS property fixture validation, short-read tests, and fallback to other sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/shadowof.c -->
