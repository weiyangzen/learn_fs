<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/iccsense.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/iccsense.c

### Purpose

Parser for input-current/current-sense metadata from BIT P. It describes external/current-sense devices and rails used by power monitoring.

### Important APIs, types, and functions

`nvbios_iccsense_parse()` and table helpers locate version 0x10/0x20 ICC sense tables and fill `struct nvbios_iccsense` records with rail/device/address/resistor configuration.

### Control flow

The table pointer comes from BIT P version 2 at `P+0x28`. The parser validates version, header, count, and length, indexes entries, and may cross-reference external-device information for sensor addressing.

### State and persistence behavior

No persistent state. Power sensor code consumes decoded rail descriptions and owns live readings.

### Dependencies and integration points

Depends on BIT P, external-device types, and BIOS reads. It integrates with power-budget and hwmon/power monitoring paths.

### Risks

Bad resistor/address parsing produces wrong current or power readings. Unsupported versions must fail without enabling bogus sensors.

### Test signals

Source read size: 128 lines, 3551 bytes. Power sensor bring-up, rail reading sanity checks against board specs, VBIOS corpus fixtures for v0x10/v0x20, and absent-table fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/iccsense.c -->
