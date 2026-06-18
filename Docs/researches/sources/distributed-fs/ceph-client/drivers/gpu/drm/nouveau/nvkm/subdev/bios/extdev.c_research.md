<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/extdev.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/extdev.c

### Purpose

Parser for external display/device entries attached to DCB. It identifies external encoder/controller functions and whether probing should be skipped.

### Important APIs, types, and functions

`nvbios_extdev_skip_probe()`, `nvbios_extdev_parse()`, and `nvbios_extdev_find()` are the exported helpers. Internal code locates the extdev table from DCB+18 and decodes type, I2C address, and bus selector.

### Control flow

The table is accepted only for DCB versions 0x30, 0x40, and 0x41. Header flags can request skipped probing. Parse/find functions index or scan entries and fill `struct nvbios_extdev_func`.

### State and persistence behavior

No persistent state. External-device metadata is decoded on demand from VBIOS data.

### Dependencies and integration points

Depends on DCB parsing and generic reads. It integrates with external TMDS/LVDS/encoder discovery and with ICC sense parsing that references external power monitors.

### Risks

Limited DCB version acceptance may miss future layouts. Wrong bus/address parsing can probe the wrong I2C device or skip a required external encoder.

### Test signals

Source read size: 110 lines, 3140 bytes. External encoder detection tests, VBIOS fixtures with skip-probe flags, I2C probe traces, and display bring-up on boards with external display chips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/extdev.c -->
