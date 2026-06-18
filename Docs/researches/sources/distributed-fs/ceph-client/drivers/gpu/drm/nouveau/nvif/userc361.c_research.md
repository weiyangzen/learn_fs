# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/userc361.c

## Purpose
This file implements the C361 usermode function table for time reads and doorbell writes.

## Important APIs, Types, and Functions
It defines `nvif_userc361_time`, `nvif_userc361_doorbell`, and exports `const struct nvif_user_func nvif_userc361`.

## Control Flow
Time reading loops until the high 32-bit timer value is stable around the low read, then returns a 64-bit timestamp. Doorbell writes the token to offset `0x90` in the mapped usermode object.

## State and Persistence Behavior
No independent state exists. It operates on the mapped `nvif_user` object.

## Dependencies and Integration Points
It depends on NVIF mapped IO helpers and is selected by `nvif_user_ctor` for Volta and newer usermode classes.

## Risks
Register offsets are class-specific. If the mapped object is invalid, reads/writes fail at the MMIO abstraction level. Time read can spin if high register is unstable, though the loop is normally short.

## Test Signals
Signals include monotonic time reads, high/low rollover correctness, and doorbell-triggered channel submissions.
