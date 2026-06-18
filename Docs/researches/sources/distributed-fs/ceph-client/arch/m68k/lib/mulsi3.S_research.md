# sources/distributed-fs/ceph-client/arch/m68k/lib/mulsi3.S

## Purpose

`mulsi3.S` implements the compiler runtime helper `__mulsi3` for 32-bit integer multiplication on m68k targets that need software support.

## Important APIs, Types, and Functions

The exported symbol is `__mulsi3`. The file uses the same assembler portability macros as the division/remainder helpers.

## Control Flow

The helper multiplies two 32-bit operands using a shift/add algorithm or available partial multiply instructions in the helper body, accumulating the low 32-bit product returned according to the compiler ABI.

## State and Persistence Behavior

No persistent state is used. Only volatile helper registers are mutated during the call.

## Dependencies and Integration Points

It is selected by `arch/m68k/lib/Makefile` for CPU/toolchain combinations that require software 32-bit multiplication. It satisfies compiler-generated `__mulsi3` calls from arbitrary C code.

## Risks and Edge Cases

The low 32-bit wraparound result must match C unsigned/signed two's-complement multiplication behavior. Register preservation is critical because the helper may be inserted into any compiled code path.

## Test Signals

Exercise multiplication for zero, one, negative values, high-bit operands, and overflow wraparound. Build logs should show no unresolved `__mulsi3`.
