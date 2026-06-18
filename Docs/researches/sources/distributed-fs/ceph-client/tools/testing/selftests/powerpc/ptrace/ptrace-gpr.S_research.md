# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-gpr.S

## Purpose
`ptrace-gpr.S` is the assembly child loop for the GPR/FPR ptrace test. It loads known nonvolatile GPR and FPR values, synchronizes with shared-memory flags, and loops so the parent can inspect registers.

## Important APIs, Types, and Functions
The exported function is `gpr_child_loop`; macros define GPR size, first tested GPR, number of GPRs, and stack space. It uses constants from `ptrace-gpr.h` and basic assembly helpers.

## Control Flow and State
The routine establishes known register contents, signals readiness through shared pointers, waits for parent progression, and keeps registers live for ptrace reads. State is architectural register contents plus shared-memory flags.

## Dependencies and Integration Points
It integrates with `ptrace-gpr.c`, `ptrace-gpr.h`, and the powerpc ptrace register-access ABI.

## Risks and Test Signals
Risks are compiler/assembler ABI drift, register clobbering, and shared-memory synchronization errors. Passing means the parent observes the expected GPR/FPR patterns through ptrace.
