<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/fan.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/fan.c

### Purpose

Parser for the BIT P fan table, primarily used for simple PWM/toggle fan descriptions on newer VBIOS layouts.

### Important APIs, types, and functions

`nvbios_fan_parse()` is the public entry. Internal helpers locate the fan table and first fan entry.

### Control flow

BIT P version 2 length >= 0x5c provides the fan table pointer at `P+0x58`. Version 0x10 entries decode fan type, min/max duty, default linear mode, and 24-bit PWM frequency.

### State and persistence behavior

No stored state. The caller-owned `struct nvbios_therm_fan` receives decoded fan policy fields.

### Dependencies and integration points

Depends on BIT P and therm fan type definitions. Thermal/fan subdevices use it alongside `therm.c` table parsing.

### Risks

Only the first fan entry is parsed. Type 1 and 2 are both treated as PWM with an explicit TODO, so behavior may be approximate on some boards.

### Test signals

Source read size: 94 lines, 2704 bytes. Fan table fixtures, PWM frequency/duty validation, therm fan mode tests, and fallback to thermal-table fan parsing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/fan.c -->
