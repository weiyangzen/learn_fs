# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/loop.S

## Purpose
`loop.S` defines deterministic POWER assembly workloads for PMU tests: a fixed 32-instruction loop and a variant containing load-linked/store-conditional traffic.

## Important APIs, Types, and Functions
The exported symbols are `thirty_two_instruction_loop` and `thirty_two_instruction_loop_with_ll_sc`, declared with `FUNC_START`/`FUNC_END` from `ppc-asm.h`. Callers pass loop counts and memory operands according to the local selftest ABI.

## Control Flow and State
Each routine executes a predictable instruction sequence and loops with the count register/branch instructions. The LL/SC variant repeatedly exercises reservation and conditional-store behavior. State is limited to caller registers, condition codes, and the memory location touched by the LL/SC loop.

## Dependencies and Integration Points
The file depends on powerpc assembler syntax and the local ppc assembly macro headers. It is linked into PMU tests that need controlled instruction counts or reservation-failure workloads.

## Risks and Test Signals
Risks are ABI/register convention drift, assembler macro incompatibility, and compiler/linker options that alter symbol visibility. Test signals are stable PMU instruction/cycle counts and successful linkage from C tests.
