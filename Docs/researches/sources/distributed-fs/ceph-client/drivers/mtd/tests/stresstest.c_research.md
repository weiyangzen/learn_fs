# sources/distributed-fs/ceph-client/drivers/mtd/tests/stresstest.c

## Purpose
Runs random read/write/erase operations against an MTD device to stress driver state transitions and boundary handling.

## Important APIs, Types, and Functions
Module parameters are `dev` and `count` (default 10000). Helpers include `rand_eb()`, `rand_offs()`, `rand_len()`, `do_read()`, `do_write()`, and `do_operation()`. The `offsets` array tracks current written offsets per eraseblock.

## Control Flow
Init opens the device, computes geometry, requires at least two eraseblocks, allocates two-eraseblock buffers and offsets, initializes offsets as full, scans bad blocks, then runs `count` random operations. Writes erase a block when its tracked offset reaches the end, choose page-aligned lengths, erase the next block when crossing into it, and update offsets.

## State and Persistence
The test destructively writes and erases random regions. Runtime state includes random data, read buffer, BBT, and per-eraseblock write offsets. It does not verify data contents against a model, focusing on operation success/failure.

## Dependencies and Integration Points
Depends on MTD read/write/erase APIs, shared test helpers, kernel random APIs, vmalloc, and bad-block handling.

## Risks
Destructive and randomized. `rand_len()` can return zero, so some operations may be no-ops depending on MTD behavior. The test assumes two adjacent eraseblocks unless the second is bad and clamps the range.

## Test Signals
Progress logs every 1024 operations and final operation count. Any read/write/erase error aborts the module load.
