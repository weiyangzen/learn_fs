# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dml/dml_logger.h

## Purpose
`dml_logger.h` maps DML logging calls to the AMD display core logger.

## Important APIs, Types, And Functions
It defines `DC_LOGGER` as `mode_lib->logger`, `dml_print(str, ...)` as `DC_LOG_DML`, and `DTRACE(str, ...)` as the same DML log wrapper.

## Control Flow
The macros expand at call sites and assume a visible variable named `mode_lib` exists. Messages are forwarded directly to `DC_LOG_DML`.

## State, Persistence, And Dependencies
The header has no state. The only side effect is logging through the display core backend.

## Integration Points
Mode VBA, RQ/DLG calculators, and debug helper printers use these macros for diagnostics, warnings, and trace dumps.

## Risks
The implicit `mode_lib` variable requirement is fragile. Macro wrappers are not expression-safe in every context. High-volume DTRACE logging can affect performance when enabled.

## Test Signals
Compile all logging call sites and run DML logging smoke tests to verify messages route to the expected DC log category.
