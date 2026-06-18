# sources/distributed-fs/ceph-client/drivers/staging/most/dim2/errors.h

## Purpose
Defines HAL error codes for DIM2 initialization, configuration, buffer, underflow, and overflow failures.

## Important APIs, Types, And Functions
`enum dim_errors_t` includes `DIM_NO_ERROR`, init errors for base address, MediaLB clock, channel address, out-of-memory, runtime not-initialized, bad config, bad buffer size, underflow, and overflow.

## Control Flow
HAL functions return these values or pass them to `dimcb_on_error()`; `dim2.c` maps nonzero init/config results to Linux errors and logs them.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by `hal.c`, `hal.h` API callers, and `dim2.c` error reporting.

## Risks And Test Signals
Error values are part of the internal driver/HAL contract. Test signals include forcing bad clock, invalid channel address, oversized DBR allocation, invalid sync/isoc packet sizes, and enqueue overflow.
