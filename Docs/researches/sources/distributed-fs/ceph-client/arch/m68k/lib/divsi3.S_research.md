# sources/distributed-fs/ceph-client/arch/m68k/lib/divsi3.S

## Purpose

`divsi3.S` implements the compiler runtime helper `__divsi3` for signed 32-bit division on m68k targets that need software arithmetic support.

## Important APIs, Types, and Functions

The exported symbol is `__divsi3`. The file defines portability macros for user label prefixes, register prefixes, immediate prefixes, and symbolic register names so the same helper style can work across assembler conventions.

## Control Flow

The routine receives numerator and denominator in the ABI-defined registers/stack convention used by compiler helper calls, normalizes signs, performs unsigned division through shifts/subtracts or m68k division instructions where available in the helper body, applies the final sign, and returns the quotient.

## State and Persistence Behavior

No global state is used. Only registers and stack according to the ABI are mutated for the duration of the helper call.

## Dependencies and Integration Points

It is selected by `arch/m68k/lib/Makefile` for non-ColdFire 68000-oriented builds and satisfies compiler-generated calls when the target lacks native 32-bit signed division.

## Risks and Edge Cases

Division by zero behavior must match the compiler/libgcc expectation for the target. Signed overflow such as `INT_MIN / -1` is ABI/compiler-sensitive. Register preservation must match the m68k calling convention or arbitrary C code can be corrupted.

## Test Signals

Compile code that forces signed 32-bit division and compare results for positive, negative, mixed-sign, zero numerator, large values, and edge values against a reference implementation.
