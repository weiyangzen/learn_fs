# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/progs/verifier_or_jmp32_k.c

## Purpose
This focused test verifies 32-bit bitwise OR/AND reasoning followed by immediate conditional jumps on an unknown value.

## Important APIs, Types, And Functions
It is a single socket naked program `or_jmp32_k` using inline ALU32 operations, branches, and an intentionally invalid scalar memory access.

## Control Flow
The program builds a 32-bit scalar from `0xffffffff`, masks and ORs it, compares it against constants, then follows branch paths that should prove or disprove reachability of an invalid write through scalar `r0`.

## State And Persistence
There is no runtime state. Verifier state is scalar tnum/range information across ALU32 operations and conditional jump refinement.

## Dependencies And Integration Points
It integrates with verifier ALU32 bound propagation and branch pruning logic.

## Risks
If the verifier mishandles OR-derived tnums, it may either miss an unsafe scalar pointer dereference path or reject safe code.

## Test Signals
The expected failure message is `R0 invalid mem access 'scalar'`.
