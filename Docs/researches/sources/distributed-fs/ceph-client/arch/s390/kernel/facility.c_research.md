# sources/distributed-fs/ceph-client/arch/s390/kernel/facility.c

## Purpose
Provides a cached helper for determining how many facility-list doublewords the current machine reports through STFL(E).

## Important APIs, Types, And Functions
`stfle_size()` calls `__stfle_asm(&dummy, 1) + 1` on first use, stores the result in a static `size`, and exports the function.

## Control Flow
Callers read the cached size with `READ_ONCE`. If zero, the function executes the STFL(E) helper with a dummy one-doubleword buffer, converts the returned last-doubleword index to a count, writes it with `WRITE_ONCE`, and returns it.

## State And Persistence
The static `size` cache persists for the boot lifetime. There is no external persistence.

## Dependencies And Integration Points
Depends on `asm/facility.h` and export infrastructure. Used by code sizing facility masks or presenting facility information.

## Risks And Edge Cases
Concurrent first calls can repeat the same query, which is benign. The helper assumes facility-list size is stable after boot. The dummy buffer is only for the query return convention.

## Test Signals
Signals include facility-list reporting on different machine generations, module calls to `stfle_size()`, and comparison with actual facility bits exposed elsewhere.
