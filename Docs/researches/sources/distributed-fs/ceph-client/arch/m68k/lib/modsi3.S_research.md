# sources/distributed-fs/ceph-client/arch/m68k/lib/modsi3.S

## Purpose

`modsi3.S` implements the compiler runtime helper `__modsi3` for signed 32-bit remainder on m68k targets requiring software arithmetic.

## Important APIs, Types, and Functions

The exported symbol is `__modsi3`. Like the related helper files, it defines assembler portability macros for symbol, register, and immediate syntax.

## Control Flow

The routine follows signed remainder semantics: it records operand signs, derives an unsigned quotient/remainder through division logic, then applies the dividend sign to the remainder before returning it.

## State and Persistence Behavior

It uses only call-local registers and stack state. No global state persists.

## Dependencies and Integration Points

It is selected by the m68k library Makefile and satisfies compiler-generated `%` operations for signed 32-bit integers on targets without a suitable hardware instruction sequence.

## Risks and Edge Cases

Remainder sign must follow C semantics for signed division. Division by zero and `INT_MIN % -1` behavior must align with the compiler runtime contract. Register clobbers must match ABI expectations.

## Test Signals

Compile and run signed modulo tests for positive/negative dividends and divisors, zero dividend, large values, and edge cases against compiler or generic C results.
