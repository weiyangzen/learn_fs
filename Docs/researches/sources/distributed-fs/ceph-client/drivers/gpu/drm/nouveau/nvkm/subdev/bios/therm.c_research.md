<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/therm.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/therm.c

### Purpose

Parser for thermal sensor, threshold, and fan policy records from BIT `P` thermal tables.

### Important APIs, types, and functions

`nvbios_therm_sensor_parse()` decodes core-domain sensor calibration and thresholds; `nvbios_therm_fan_parse()` decodes fan duty limits, trip points, periods, linear mode, and PWM frequency.

### Control flow

The thermal table pointer is read from BIT P version 1 or 2 at different offsets. Entries are type/value pairs; sensor parsing tracks threshold and sensor sections, while fan parsing accumulates trip points and mode from entry ids.

### State and persistence behavior

No persistent state. Thermal subdevices own live sensor/fan state after consuming decoded policy.

### Dependencies and integration points

Depends on BIT P and therm public types. It integrates with thermal monitoring, fan control, and power safety paths.

### Risks

Entry ids are sparse and partially understood. Wrong threshold or fan-duty parsing can cause overheating, noisy fan behavior, or missing shutdown thresholds.

### Test signals

Source read size: 212 lines, 5656 bytes. Thermal sensor calibration checks, fan curve tests, threshold trip tests, VBIOS fixture parsing, and Fermi+ linear-mode fallback validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/therm.c -->
