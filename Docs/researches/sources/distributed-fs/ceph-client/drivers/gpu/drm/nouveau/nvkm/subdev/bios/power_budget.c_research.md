<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/power_budget.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/power_budget.c

### Purpose

Parser for VBIOS power-budget tables referenced from BIT `P`. It provides board power limits and related policy values to power-management code.

### Important APIs, types, and functions

`nvbios_power_budget_header()`, entry accessors, and parse helpers decode versioned power-budget records into structures declared in `power_budget.h`.

### Control flow

The parser reads the BIT P power-budget pointer, validates supported versions, derives header/count/length fields, and indexes records to extract power limit values and policy flags.

### State and persistence behavior

No runtime state. Parsed power limits are caller-owned snapshots of firmware policy.

### Dependencies and integration points

Depends on BIT P and BIOS reads. It integrates with power cap, hwmon, and boost/pstate management.

### Risks

Bad units or version offsets can expose wrong power caps, affecting throttling or boost decisions. Missing tables must be tolerated on older boards.

### Test signals

Source read size: 125 lines, 3422 bytes. Power cap sanity checks, VBIOS fixture parsing, hwmon/power-limit display tests, and stress tests that trigger power throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/bios/power_budget.c -->
