# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvif/chanc36f.c

## Purpose
This file implements C36F/Hopper-era channel behavior using usermode doorbells and updated semaphore method encodings.

## Important APIs, Types, and Functions
Main entry point is `nvif_chanc36f_ctor`. Internal helpers are `nvif_chanc36f_gpfifo_kick` and `nvif_chanc36f_sem_release`; the function table reuses 906F GET/post readers and 506F GPFIFO entry format.

## Control Flow
Constructor delegates to 906F setup with the C36F function table, then records usermode object and doorbell token. Kick writes the GPFIFO PUT, uses a barrier and readback to flush BAR1 writes to video memory, then rings the usermode doorbell. Semaphore release emits C36F SEM_ADDR/PAYLOAD/EXECUTE methods.

## State and Persistence Behavior
State includes mapped userd/sema/push/GPFIFO memory, a usermode object pointer, and doorbell token.

## Dependencies and Integration Points
It depends on NVIF usermode doorbell functions, C36F method definitions, and generic/906F channel support.

## Risks
Ordering is critical: doorbell before BAR1 flush can make the GPU read incomplete GPFIFO state. Doorbell tokens must match channel allocation.

## Test Signals
Signals include doorbell submission, BAR1 flush ordering, semaphore post, C36F channel construction, and timeout behavior under full rings.
