# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_asm.S

## Purpose
Assembly routines that load, check, and preserve FPU registers across fork, preemption, and signal tests.

## Important APIs, Types, and Functions
Exports `check_fpu`, `check_all_fprs`, `test_fpu`, and `preempt_fpu`; uses `basic_asm.h` and `fpu_asm.h` save/restore macros.

## Control Flow
`check_all_fprs` compares f0-f31 against an expected double array. `test_fpu` loads FPRs, performs a fork syscall, returns the child pid to C, and checks registers. `preempt_fpu` loads FPRs, atomically decrements a start counter, loops checking registers while a running flag remains true, and restores state.

## State and Persistence
Mutates FPU registers, stack frame, shared counters, and fork child state. No files are written.

## Dependencies and Integration Points
Linked into `fpu_syscall`, `fpu_preempt`, and `fpu_signal` targets.

## Risks and Test Signals
Risks include ABI save/restore errors, use of scratch registers f30/f31 during checks, and syscall clobber assumptions. C tests report any nonzero return as register corruption.
