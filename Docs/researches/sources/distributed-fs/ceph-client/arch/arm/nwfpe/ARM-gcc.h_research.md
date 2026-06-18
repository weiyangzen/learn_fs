# sources/distributed-fs/ceph-client/arch/arm/nwfpe/ARM-gcc.h

## Purpose
Provides compiler and integer-type adaptation for the SoftFloat code used by the NetWinder Floating Point Emulator. It defines exact-width and convenient-width integer aliases, 64-bit literal handling, inlining, and optional libfloat symbol remapping.

## Important APIs, Types, And Functions
Defines `flag`, `uint8`, `int8`, `uint16`, `int16`, `uint32`, `int32`, `bits8/16/32/64`, `sbits*`, `uint64`, `int64`, `LIT64(a)`, and `INLINE`. Under `__LIBFLOAT__`, it maps SoftFloat function names to GCC runtime helper names or private glue names.

## Control Flow
No runtime control flow. The preprocessor configures SoftFloat compilation for GCC/ARM and optionally for soft-float library symbol compatibility.

## State, Dependencies, And Integration
No state. Included by `milieu.h`, which is included by NWFPE and SoftFloat sources. Integration risk is broad because these typedefs determine the representation used by all emulator arithmetic.

## Risks And Test Signals
Risks include type-width mismatch on unusual compilers, wrong literal suffixes, and symbol collisions when `__LIBFLOAT__` is used. Test signals are compile coverage, structure-size checks in `fpmodule.c`, and floating-point emulator arithmetic tests.
