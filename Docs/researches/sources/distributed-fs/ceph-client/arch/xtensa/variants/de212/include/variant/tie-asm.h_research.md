# sources/distributed-fs/ceph-client/arch/xtensa/variants/de212/include/variant/tie-asm.h

## Purpose
This assembler header saves/restores `de212` optional non-coprocessor state.

## Important APIs, types, and functions
`xchal_ncp_store/load` cover `ACCLO`, `ACCHI`, `SCOMPARE1`, and `M0`-`M3`. The full selection/alloc macro interface is present, and one temporary register is declared.

## Control flow
Macro expansion aligns the save pointer, conditionally includes compiler-used MAC16 accumulator state and non-compiler-used conditional-store/MAC16 multiplier state, then emits register moves and memory accesses.

## State and persistence behavior
The saved payload is 28 bytes in the `tie.h` layout, padded to a 32-byte total save area. There is no `THREADPTR`, `BR`, or coprocessor state.

## Dependencies and integration points
This file must match `de212` `core.h` feature absence and `tie.h` register list. It is used by low-level Xtensa context preservation paths.

## Risks and edge cases
Using generic code that expects a thread pointer or CP save macro would be incorrect. Offset accounting must preserve the 28-byte payload/32-byte total distinction.

## Test signals
Compile save/restore assembly, run MAC16 and conditional-store tests across preemption and signal delivery, and verify TLS code does not depend on a hardware thread pointer.
