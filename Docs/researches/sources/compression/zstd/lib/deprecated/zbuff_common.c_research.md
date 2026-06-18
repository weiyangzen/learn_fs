# sources/compression/zstd/lib/deprecated/zbuff_common.c

## Purpose
`zbuff_common.c` implements the deprecated ZBUFF error helper functions by forwarding to libzstd's shared error subsystem.

## Important APIs, Types, And Functions
It defines `ZBUFF_isError(size_t errorCode)` and `ZBUFF_getErrorName(size_t errorCode)`. Both are thin wrappers over `ERR_isError()` and `ERR_getErrorName()`.

## Control Flow
Each function performs a single direct call into `error_private.h` helpers and returns the result. There is no branching beyond the underlying error helper behavior.

## State And Persistence
No state is stored or persisted. Results depend only on the numeric zstd error code passed by the caller.

## Dependencies And Integration Points
The file includes `../common/error_private.h` and `zbuff.h`. It provides compatibility symbols for legacy users who still call ZBUFF error helpers after using deprecated compression or decompression wrappers.

## Risks
The main compatibility risk is preserving the exact wrapper names and return types. Any divergence from `ZSTD_isError`/`ZSTD_getErrorName` behavior would surprise legacy callers.

## Test Signals
Tests should verify that known success values are not errors, known zstd error codes are errors, and returned names match the modern ZSTD error-name helper.
