# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/qp_tables.h

## Purpose
`dsc/qp_tables.h` contains static DSC rate-control QP lookup tables.

## Important APIs, Types, And Functions
It defines `static const qp_table` objects for min and max QP sets across 444, 422, and 420 modes at 8, 10, and 12 bits per component. Each table row maps a `float bpp` to a 15-entry `qp_set`.

## Control Flow
The file is pure data. Runtime selection happens in `rc_calc_fpu.c` through table hashing and a half-bpp index calculation.

## State, Persistence, And Dependencies
The arrays are translation-unit-local read-only data when included. They require `qp_table`, `qp_set`, and `struct qp_entry` definitions from `rc_calc_fpu.h`.

## Integration Points
The tables feed `_do_calc_rc_params()` for DSC PPS/rate-control programming.

## Risks
Including this header from more than one C file duplicates static data. `get_qp_set()` assumes table ordering and half-step bpp spacing. Unsupported bpp values can select wrong rows or exceed bounds. Manual table edits are high risk.

## Test Signals
Cover every mode/bpc/min-max combination, first and last rows, half-step bpp values, out-of-range bpp logging, and known DSC QP fixtures.
