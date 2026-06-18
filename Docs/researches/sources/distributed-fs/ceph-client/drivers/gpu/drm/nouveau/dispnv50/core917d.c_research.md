<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core917d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core917d.c

## Purpose
This file defines the GK/GM/GP-era core channel function table by combining GF110 capability handling with newer head programming.

## Important APIs, Types, and Functions
It defines the `core917d` `nv50_core_func` table and public `core917d_new`.

## Control Flow
The constructor delegates to `core507d_new_`. The function table reuses NV507D init/notifier/update, GF110 `core907d_caps_init`, selects `head917d`, enables optional `crc907d`, and uses `dac907d`/`sor907d` output handlers.

## State and Persistence Behavior
No unique state is introduced; channel, notifier, caps, and output state use shared helpers and selected function tables.

## Dependencies and Integration Points
It depends on `head917d`, shared `core507d` helpers, `core907d_caps_init`, optional CRC, and GF110-era output handlers. `core.c` selects it for GK104/GK110, GM107/GM200, GP100/GP102, and related classes.

## Risks
The class compatibility assumption spans several GPU generations. Any method or notifier divergence not represented by this table could break caps, update, or output control. CRC support is reused from GF110.

## Test Signals
Core init and modeset on Kepler, Maxwell, and Pascal, caps reads, CRC debugfs where enabled, SOR/DAC output control, and suspend/resume are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core917d.c -->
