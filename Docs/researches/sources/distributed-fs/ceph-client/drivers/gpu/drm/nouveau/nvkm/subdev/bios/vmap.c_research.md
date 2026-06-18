<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vmap.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vmap.c

### Purpose

Parser for voltage-map tables. It maps voltage ids or VID indexes to actual microvolt values and policy fields.

### Important APIs, types, and functions

`nvbios_vmapTe/Ee/Ep()` parse table headers and entries; match helpers locate records by voltage id or index depending on table version.

### Control flow

The table pointer is read from BIT P metadata. Supported versions expose header/count/entry size, and entry parsing extracts voltage ids, min/max or mapped voltage values, and version-specific flags.

### State and persistence behavior

No persistent state. Voltage subdevices consume decoded maps to build runtime voltage tables.

### Dependencies and integration points

Depends on BIT P, generic reads, and voltage parser users such as `volt.c` and pstate/reclock code.

### Risks

Wrong units or id matching can choose unsafe voltages. Unsupported versions need graceful failure to keep conservative defaults.

### Test signals

Source read size: 121 lines, 3618 bytes. Voltage table dump comparison, reclocking voltage transitions, VBIOS fixtures, and power/thermal stress after voltage changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/vmap.c -->
