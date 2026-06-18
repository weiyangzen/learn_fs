<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/volt.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/volt.c

### Purpose

Parser for primary voltage tables under BIT `P`. It decodes voltage table metadata, entries, GPIO/VID relationships, and voltage ranges.

### Important APIs, types, and functions

`nvbios_voltTe/Tp()`, `nvbios_voltEe/Ep()`, and matching helpers expose table and entry parsing for `struct nvbios_volt*` consumers.

### Control flow

The parser locates the voltage table pointer from BIT P, accepts supported versions, reads header/count/entry sizes, then decodes VID, voltage in microvolts, and min/max or PWM/GPIO-related fields by version.

### State and persistence behavior

No state. The voltage subdevice owns any live voltage rails or regulator objects created from decoded data.

### Dependencies and integration points

Depends on BIT P, VBIOS reads, and vmap/perf/pstate code. Reclocking and power management use these limits.

### Risks

Voltage parsing mistakes are high risk because they can overvolt or undervolt hardware. Missing tables must leave conservative behavior.

### Test signals

Source read size: 160 lines, 4808 bytes. Voltage table fixtures, regulator programming tests, pstate transition tests, and hardware telemetry comparison where available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/volt.c -->
