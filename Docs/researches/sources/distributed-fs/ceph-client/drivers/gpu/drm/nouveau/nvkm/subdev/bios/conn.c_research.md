<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/conn.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/conn.c

### Purpose

Parser for the connector table nested under modern DCB tables. It maps connector indexes to physical connector type, location, HPD, DP, display-id, and LCD metadata.

### Important APIs, types, and functions

`nvbios_connTe/Tp()` find and validate the connector table; `nvbios_connEe/Ep()` locate and decode individual entries into `struct nvbios_connE`.

### Control flow

The parser first calls `dcb_table()`, requires DCB version >= 0x30 and header >= 0x16, reads the connector table pointer from DCB+0x14, then decodes v0x30/v0x40 records. Four-byte records expose extended HPD/DP/DI/SR/LCD id fields.

### State and persistence behavior

No state is stored; output is a decoded snapshot from the VBIOS image.

### Dependencies and integration points

Depends on DCB parsing and generic VBIOS reads. Display output discovery, init scripts, AUX selection, and panel handling use connector metadata.

### Risks

Short entries lose extended metadata by design. Incorrect bit extraction can misroute HPD/AUX/display output and break hotplug or eDP handling.

### Test signals

Source read size: 97 lines, 3151 bytes. DCB/connector dump comparison, hotplug tests across connector types, eDP init-script condition tests, and multi-output boot on boards with v0x30/v0x40 connector tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/conn.c -->
