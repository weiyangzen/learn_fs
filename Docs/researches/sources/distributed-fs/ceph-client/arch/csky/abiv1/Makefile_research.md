# sources/distributed-fs/ceph-client/arch/csky/abiv1/Makefile

## Purpose

builds C-SKY ABI v1 support objects for alignment handling, cache flushing, mmap policy, and byte-
swap helpers

## Important APIs, Types, and Functions

Source read size: 6 lines, 180 bytes. Build selections: `obj-y -> bswapdi.o`, `obj-y -> bswapsi.o`,
`obj-y -> cacheflush.o`, `obj-y -> mmap.o`.

## Control Flow and Behavior

object selection adds small ABI compatibility routines into the architecture build

## State and Persistence

state is build output only

## Dependencies and Integration Points

integrates ABI v1 C files with the top-level C-SKY Makefile include path

## Risks and Test Signals

omitting an object breaks ABI v1 runtime traps or helper symbols; ABI v1 build and boot tests cover
it
