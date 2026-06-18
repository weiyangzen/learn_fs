# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_syscall.c

## Purpose
Tests whether FPU registers survive syscall/fork paths under additional process activity.

## Important APIs, Types, and Functions
Defines external `test_fpu()`, global `darray`, `syscall_fpu()`, `test_syscall_fpu()`, and `main()`.

## Control Flow
`syscall_fpu()` randomizes FP data and calls assembly `test_fpu()` 1000 times; that assembly performs fork and validates FPRs in parent/child paths. `test_syscall_fpu()` forks additional processes to increase context switching and aggregates child results.

## State and Persistence
State includes global expected FP array and child process statuses. No files are written.

## Dependencies and Integration Points
Depends on `fpu_asm.S`, fork/wait, scheduler behavior, and PowerPC harness.

## Risks and Test Signals
Risks include high fork count and noisy failures if fork is resource-limited. Failure indicates FPU register corruption across syscall/fork or child status errors.
