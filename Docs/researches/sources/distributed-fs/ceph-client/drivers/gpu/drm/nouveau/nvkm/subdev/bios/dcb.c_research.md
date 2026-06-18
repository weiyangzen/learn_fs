<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dcb.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dcb.c

### Purpose

Parser for the Display Configuration Block. DCB describes display outputs, OR/head/link routing, connector indices, I2C buses, DisplayPort link capabilities, and external encoders.

### Important APIs, types, and functions

`dcb_table()`, `dcb_outp()`, `dcb_outp_parse()`, `dcb_outp_match()`, and `dcb_outp_foreach()` are the main APIs. Internal hash helpers summarize output type/location/extdev and OR/head/link fields.

### Control flow

The table pointer is read from legacy location 0x36 on post-NV04 devices. The parser validates DCB signatures and handles versions >=0x30, >=0x20, and >=0x15 with different header/count/length rules. Output parsing decodes v2+ records and adds v4+ DP link bandwidth/lane and SOR/external-device fields.

### State and persistence behavior

No persistent state; decoded `struct dcb_output` instances are transient. The VBIOS image is the persistent source of truth.

### Dependencies and integration points

Depends on `nvbios_memcmp()` and VBIOS readers. Display engine, connector, I2C, DP, external-device, and init-script code consume DCB output records.

### Risks

DCB version handling is compatibility-sensitive. Bad parsing can disable displays, select wrong I2C/AUX buses, or misprogram SOR links. Very old DCB versions are intentionally rejected as not useful.

### Test signals

Source read size: 235 lines, 6205 bytes. Display enumeration on NV1x through modern GPUs, DCB dump comparison, DP lane/bandwidth validation, multi-head tests, and malformed DCB signature tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/dcb.c -->
