# sources/distributed-fs/ceph-client/drivers/gpu/drm/etnaviv/etnaviv_cmdbuf.h

## Purpose
Declares etnaviv command buffer structures and suballocator APIs.

## Important APIs, Types, and Functions
Defines `struct etnaviv_cmdbuf` with suballocator pointer, suballocation offset, CPU address, total size, and used size. Declares suballocator lifecycle, map/unmap, cmdbuf init/free, and address translation functions.

## Control Flow
No executable flow beyond declarations; callers allocate cmdbufs, emit commands through `etnaviv_buffer.h`, translate to GPU VA with a mapping, and free when complete.

## State and Persistence
Documents the state fields maintained by `etnaviv_cmdbuf.c` and command emitters.

## Dependencies and Integration Points
Included by buffer, driver, dump, GEM submit, GPU, MMU, and flop reset code.

## Risks
Consumers must keep `user_size <= size`, use the correct IOMMU mapping for VA translation, and free suballocations once hardware is done.

## Test Signals
Build coverage and submit/ring buffer runtime tests exercise this contract.
