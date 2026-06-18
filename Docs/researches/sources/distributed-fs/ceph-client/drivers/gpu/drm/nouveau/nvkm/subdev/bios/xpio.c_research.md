<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/xpio.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/xpio.c

### Purpose

Parser for external GPIO provider tables. It complements DCB GPIO parsing when GPIO functions live behind external devices.

### Important APIs, types, and functions

`dcb_xpio_table()`, entry accessors, parse/match helpers decode XPIO records and provider metadata from DCB-related tables.

### Control flow

The parser locates XPIO table pointers from modern DCB data, validates version/header/count/length, and decodes external GPIO line, function, and provider identifiers.

### State and persistence behavior

No state. The GPIO subsystem owns live external GPIO objects after consuming decoded records.

### Dependencies and integration points

Depends on DCB, GPIO table parsing, and generic BIOS reads. It integrates with display hotplug, fan, and board-control GPIO logic.

### Risks

Wrong provider/line parsing can toggle external devices incorrectly or miss GPIO-backed signals.

### Test signals

Source read size: 74 lines, 2521 bytes. External GPIO board tests, hotplug/fan GPIO validation, VBIOS fixture parsing, and absent-XPIO fallback tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/xpio.c -->
