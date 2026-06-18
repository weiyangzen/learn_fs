# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvif/timer.h

## Purpose
Declares GPU-timer-based wait helpers for polling hardware conditions using PTIMER time.

## Important APIs, Types, And Functions
Defines `struct nvif_timer_wait`, `nvif_timer_wait_init`, `nvif_timer_wait_test`, and macros `nvif_nsec`, `nvif_usec`, and `nvif_msec`.

## Control Flow
The wait macro initializes a deadline, executes caller-supplied polling code in a loop, and stops when `nvif_timer_wait_test()` reports timeout or the caller breaks.

## State And Persistence
Wait state stores device, limit, initial/current times, and read count for one polling operation.

## Dependencies And Integration Points
Depends on `nvif_device_time()` through the implementation and is used by hardware init, firmware boot, and register polling paths.

## Risks
Polling code must break on success. Timeout return semantics are unusual: timeout returns negative while break returns elapsed nanoseconds.

## Test Signals
Register polling success/timeout tests, firmware boot waits, and timer monotonicity validate behavior.
