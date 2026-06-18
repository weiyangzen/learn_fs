<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core907d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core907d.c

## Purpose
This file defines the GF110-era core channel function table and a class-specific capability notifier initialization path.

## Important APIs, Types, and Functions
It implements `core907d_caps_init`, defines the `core907d` function table, and provides `core907d_new`.

## Control Flow
Capability init clears the GF110 notifier field (`NV907D_CORE_NOTIFIER_3.CAPABILITIES_4.DONE`), reuses `core507d_read_caps`, then waits for the GF110 notifier done bit. The constructor delegates to `core507d_new_`. The function table reuses NV507D init/notifier/update, selects `head907d`, enables optional `crc907d`, and uses `dac907d`/`sor907d` output handlers.

## State and Persistence Behavior
State behavior follows the shared core channel, but capability completion is tracked in a different notifier layout. Optional CRC state is available under debugfs.

## Dependencies and Integration Points
It depends on `cl907d`, BO notifier macros, NVIF timer, `head907d`, `crc907d`, `dac907d`, and `sor907d`.

## Risks
Caps init logs timeout but returns success. Reusing `core507d_read_caps` assumes the GET_CAPABILITIES method is compatible while notifier layout differs. CRC pointers are build-conditional.

## Test Signals
GF110 core init, caps read completion, timeout injection, CRC debugfs capture where enabled, DAC/SOR output control, and atomic commit update behavior validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core907d.c -->
