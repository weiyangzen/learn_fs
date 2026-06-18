<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core827d.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core827d.c

## Purpose
This file defines the GT200/G82-era core channel function table, reusing NV507D core mechanics with a generation-specific head implementation.

## Important APIs, Types, and Functions
It defines the static `core827d` `nv50_core_func` table and public constructor `core827d_new`.

## Control Flow
The constructor delegates to `core507d_new_` with the `core827d` function table. The function table reuses NV507D init, notifier, caps, and update helpers, selects `head827d`, and keeps NV507D DAC/SOR/PIOR output handlers.

## State and Persistence Behavior
No unique state is introduced; persistent core channel and notifier behavior are inherited from NV507D helpers.

## Dependencies and Integration Points
It depends on `head827d`, `core507d_new_`, and shared output function tables. `core.c` selects it for G82, GT200, GT206, and GT214 classes.

## Risks
The file assumes core method layout remains compatible with NV507D while head programming differs. If output methods diverged for a selected class, reused function tables would misprogram hardware.

## Test Signals
Core channel init and atomic commits on G82/GT200/GT214, head-specific modesets through `head827d`, output control, and caps notifier behavior inherited from NV507D are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/dispnv50/core827d.c -->
