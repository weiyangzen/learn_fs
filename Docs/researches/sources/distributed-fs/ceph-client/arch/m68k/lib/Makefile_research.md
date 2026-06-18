# sources/distributed-fs/ceph-client/arch/m68k/lib/Makefile

## Purpose

This Makefile selects m68k architecture library objects for memory routines, user access, checksums, and compiler helper arithmetic.

## Important APIs, Types, and Functions

Common objects are `checksum.o`, `muldi3.o`, `memcpy.o`, `memmove.o`, and `memset.o`. MMU or ColdFire builds also include `uaccess.o`. Non-ColdFire 68000 builds include 32-bit arithmetic helper assembly objects such as `divsi3.o`, `udivsi3.o`, `modsi3.o`, `umodsi3.o`, and `mulsi3.o`.

## Control Flow

There is no runtime flow. Kbuild expands `lib-y` according to `CONFIG_MMU`, `CONFIG_COLDFIRE`, and `CONFIG_CPU_HAS_NO_MULDIV64`.

## State and Persistence Behavior

No state is owned. The selected objects provide runtime symbols linked into the kernel or modules.

## Dependencies and Integration Points

It integrates with compiler-generated helper calls, generic string/memory APIs, networking checksum code, and user access helpers. The C files and assembly files in this subset are selected here.

## Risks and Edge Cases

Omitting compiler helper objects can produce unresolved symbols on CPU/toolchain combinations without native multiply/divide support. Selecting `uaccess.o` for the wrong memory model would expose inappropriate copy semantics.

## Test Signals

Build matrix coverage for MMU, no-MMU, ColdFire, and 68000 targets should show no unresolved `__divsi3`, `__modsi3`, `__mulsi3`, memory, checksum, or uaccess symbols.
