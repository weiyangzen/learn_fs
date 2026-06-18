# sources/distributed-fs/ceph-client/arch/csky/abiv2/Makefile

## Purpose

builds C-SKY ABI v2 support objects, optimized string routines, mcount, cache flushing, and optional
FPU support

## Important APIs, Types, and Functions

Source read size: 14 lines, 375 bytes. Build selections: `obj-y -> cacheflush.o`, `obj-y ->
memcmp.o`, `obj-y -> memcpy.o`, `obj-y -> memmove.o`, `obj-y -> memset.o`, `obj-y -> strcmp.o`,
`obj-y -> strcpy.o`, `obj-y -> strlen.o`, `obj-y -> strksyms.o`.

## Control Flow and Behavior

Kbuild includes assembly implementations for memcpy/memmove/memset/strcmp/strcpy/strlen/memcmp plus
conditional fpu.o

## State and Persistence

state is build output only

## Dependencies and Integration Points

integrates ABI v2 optimized routines and ftrace/FPU support with kernel linkage

## Risks and Test Signals

bad object selection affects core string semantics or tracing; ABI v2 builds, boot, lib/string
tests, and ftrace tests are signals
