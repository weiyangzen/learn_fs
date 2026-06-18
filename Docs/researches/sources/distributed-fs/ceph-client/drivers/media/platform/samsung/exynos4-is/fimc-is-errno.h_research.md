# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-is-errno.h

## Purpose
`fimc-is-errno.h` defines the FIMC-IS firmware error ABI: high-level firmware command failures, per-subblock power/path/frame errors, set-parameter validation errors, and the timeout flag.

## Important APIs, Types, and Functions
The first anonymous enum defines `IS_ERROR_*` values grouped by general, sensor, ISP, DRC, scaler, ODC, DIS, TDNR, scalerP, FD, and unknown categories. `IS_ERROR_TIME_OUT_FLAG` marks timeout-qualified errors. `enum fimc_is_error` defines lower-level set-parameter errors for common/control/OTF/DMA/global/sensor/ISP/FD/scaler parameter validation. The header declares `fimc_is_strerr()`.

## Control Flow
There is no executable flow. The constants are consumed by firmware reply logging and by parameter structure `err` fields.

## State and Persistence
No runtime state is stored here. Values are part of the host/firmware ABI and must remain stable for matching firmware.

## Dependencies and Integration Points
The header is included by FIMC-IS core, register, and parameter code. `fimc-is-errno.c` implements the string mapping for selected top-level error values.

## Risks and Edge Cases
The driver only decodes a subset of all defined errors to strings. Numeric ranges overlap in conceptual categories between top-level `IS_ERROR_*` and set-parameter `ERROR_*` values, so callers must know which ABI field they are interpreting. The version macro is decimal-looking but written with a leading zero, so it should be treated as a legacy marker rather than arithmetic input.

## Test Signals
Useful checks include compilation of all enum users, not-done logging for representative error categories, timeout-flag handling, parameter command failure recovery, and firmware compatibility tests against expected numeric values.
