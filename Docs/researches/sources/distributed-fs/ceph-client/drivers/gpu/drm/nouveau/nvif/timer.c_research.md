# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/timer.c

## Purpose
This file provides a small helper for polling elapsed GPU device time with timeout and stalled-clock detection.

## Important APIs, Types, and Functions
Public functions are `nvif_timer_wait_init` and `nvif_timer_wait_test`.

## Control Flow
Initialization stores the device, nanosecond limit, and resets read count. Each test reads `nvif_device_time`, initializes the baseline on first read, detects repeated identical timestamps for up to 16 reads, checks elapsed time against the limit, and returns elapsed time or `-ETIMEDOUT`.

## State and Persistence Behavior
State lives in caller-provided `struct nvif_timer_wait`: device, limit, first time, last time, and repeated-read count.

## Dependencies and Integration Points
It depends on `nvif_device_time` and is used by polling loops that prefer GPU time over CPU time.

## Risks
If device time stalls, timeout is triggered after repeated reads. If time wraps or is non-monotonic, elapsed comparisons may be wrong depending on counter width.

## Test Signals
Signals include normal elapsed polling, forced stalled time, timeout limit behavior, and usermode vs method-backed device time.
