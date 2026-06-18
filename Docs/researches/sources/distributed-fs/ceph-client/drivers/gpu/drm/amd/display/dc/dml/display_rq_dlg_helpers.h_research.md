# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/display_rq_dlg_helpers.h

## Purpose
`display_rq_dlg_helpers.h` declares debug-print APIs for RQ, DLG, and TTU calculation structures.

## Important APIs, Types, And Functions
It includes `display_mode_lib.h` and declares printers for RQ params, data sizing params, data DLG params, data misc params, DLG system params, data RQ regs, whole RQ regs, DLG regs, and TTU regs.

## Control Flow
The header has no runtime flow. It exposes printer declarations to calculator files.

## State, Persistence, And Dependencies
There is no state. The header depends on full DML display struct definitions from `display_mode_lib.h`, which is necessary because the function signatures use concrete `_vcs_dpi_display_*` types.

## Integration Points
`dml1_display_rq_dlg_calc.h` includes this file, so users of the DCN1 RQ/DLG API can also access diagnostic printers.

## Risks
The broad include creates a dependency edge from debug helpers to the full display mode library. Struct renames or layout changes can cause wide rebuild fallout.

## Test Signals
Compile coverage is the key signal. DML logging smoke tests confirm declarations and definitions remain linked.
