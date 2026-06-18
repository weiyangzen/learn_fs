# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml_inline_defs.h

## Purpose
`dml_inline_defs.h` centralizes small math helpers used by DML calculation code.

## Important APIs, Types, And Functions
It provides `dml_min*`, `dml_max*`, `dml_ceil()`, `dml_floor()`, `dml_round()`, `dml_log2()`, `dml_pow()`, `dml_fmod()`, `dml_ceil_2()`, `dml_ceil_ex()`, `dml_floor_ex()`, `dml_round_to_multiple()`, and `dml_abs()`.

## Control Flow
Most helpers wrap `dcn_bw_*` primitives. Ceil/floor return zero for zero granularity. `dml_log2()` extracts the exponent bits from a `double`. `dml_round_to_multiple()` rounds unsigned integers up or down depending on its `up` flag.

## State, Persistence, And Dependencies
There is no state. The header depends on `dcn_calc_math.h` and `dml_logger.h`; inline behavior is compiled into each including translation unit.

## Integration Points
Mode VBA and RQ/DLG calculators include this file for spreadsheet-derived arithmetic and register encoding formulas.

## Risks
`dml_log2()` uses pointer type punning and is only appropriate for positive values used by DML. Rounding behavior is hardware-contract-sensitive, so small changes can alter many formulas.

## Test Signals
Test min/max compositions, ceil/floor granularity, round-to-multiple up/down, `dml_log2()` on DML-relevant powers and non-powers, and representative formulas from VBA and RQ/DLG code.
