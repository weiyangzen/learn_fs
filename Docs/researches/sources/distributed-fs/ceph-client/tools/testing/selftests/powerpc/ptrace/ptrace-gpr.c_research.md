# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.c

## Purpose
`ptrace-gpr.c` validates ptrace access to general-purpose and floating-point registers by comparing parent-read register sets against values loaded by an assembly child loop.

## Important APIs, Types, and Functions
Important functions are `child()`, `trace_gpr()`, `rand_reg()`, `ptrace_gpr()`, and `main()`. It uses validation helpers from `ptrace-gpr.h` and the external `gpr_child_loop()` assembly routine.

## Control Flow and State
The test creates shared memory, forks, lets the child initialize registers and stop/loop, then the parent attaches or waits, reads GPR/FPR data through ptrace APIs, validates expected values, writes randomized values where applicable, and repeats until pass/fail. State includes shared-memory flags, child pid/status, and expected register constants.

## Dependencies and Integration Points
It depends on `ptrace.h`, register definitions, SysV shared memory, `ptrace-gpr.S`, and kselftest macros.

## Risks and Test Signals
Risks are register save/restore ABI changes, endian/word-width random generation issues, and child synchronization races. A pass means ptrace reports and updates the expected GPR/FPR values.
