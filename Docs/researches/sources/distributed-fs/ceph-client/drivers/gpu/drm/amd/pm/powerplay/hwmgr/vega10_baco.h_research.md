# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_baco.h

## Purpose
This header declares the Vega10 BACO transition entry point and imports the SMU9 BACO state contract. It is the narrow public surface between the Vega10 hardware manager and the implementation in `vega10_baco.c`.

## Important APIs, Types, and Functions
- `vega10_baco_set_state(struct pp_hwmgr *hwmgr, enum BACO_STATE state)`: transitions a Vega10 ASIC to the requested BACO state.
- `enum BACO_STATE`: imported from `smu9_baco.h` and shared with generic SMU9 BACO helpers such as `smu9_baco_get_state()`.

## Control Flow and Integration
This file has no executable logic. It is consumed by `vega10_hwmgr.c`, which wires `vega10_baco_set_state()` into the `pp_hwmgr_func` table, and by `vega10_baco.c`, which provides the implementation.

## State and Persistence
No state is stored in the header. Runtime state lives in hardware, the SMU firmware, and the `pp_hwmgr` backend.

## Dependencies
- `smu9_baco.h` for the common SMU9 BACO state definitions and helper declarations.
- `struct pp_hwmgr` is expected through the included PowerPlay/SMU headers.

## Risks
- The declaration couples callers to the SMU9 BACO ABI. If `enum BACO_STATE` or the helper semantics change, both the implementation and hardware-manager callback contract must remain aligned.
- Missing include guards or wrong SMU generation includes would cause build or behavioral failures; this file correctly uses a unique guard and SMU9 include.

## Test Signals
- Kernel build tests should confirm that `vega10_baco.c` and `vega10_hwmgr.c` share a consistent declaration.
- Runtime coverage comes from the same BACO in/out tests used for `vega10_baco.c`.
