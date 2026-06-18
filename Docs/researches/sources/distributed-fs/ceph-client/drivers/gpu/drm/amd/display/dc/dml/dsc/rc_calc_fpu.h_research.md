# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dsc/rc_calc_fpu.h

## Purpose
`dsc/rc_calc_fpu.h` defines the DSC rate-control parameter data model and declares the floating-point RC calculation entry point.

## Important APIs, Types, And Functions
It defines `QP_SET_SIZE`, `qp_set`, `struct rc_params`, `enum colour_mode`, `enum bits_per_comp`, `enum max_min`, `struct qp_entry`, `qp_table`, and `_do_calc_rc_params()`.

## Control Flow
There is no executable flow. The header defines the structures and enum values used by the implementation and QP table data.

## State, Persistence, And Dependencies
There is no header state. It depends on `os_types.h` and `<drm/display/drm_dsc.h>`. Output state persists in caller-owned `struct rc_params` objects.

## Integration Points
DSC code includes this header to request RC parameter generation. `qp_tables.h` depends on its table and QP type definitions.

## Risks
Enum values must stay consistent with table hashing. The misspelled `is_navite_422_or_420` parameter is part of the signature. Fixed QP and threshold sizes mirror DSC assumptions and should not change casually.

## Test Signals
Compile all callers and verify every supported enum combination populates a complete `struct rc_params`.
