# sources/distributed-fs/ceph-client/tools/testing/selftests/signal/sas.c

## Purpose
Tests `sigaltstack(SS_ONSTACK | SS_AUTODISARM)` behavior and verifies `swapcontext()` can be used safely from a signal handler without reusing/corrupting the altstack.

## Important APIs, types, and functions
Uses `sigaltstack()`, `sigaction()`, `mmap(MAP_STACK)`, `getauxval(AT_MINSIGSTKSZ)`, `getcontext()`, `makecontext()`, `swapcontext()`, `setcontext()`, `raise()`, and the `sp` register from `current_stack_pointer.h`. Signal handlers are `my_usr1()` and `my_usr2()`; `switch_fn()` runs on a user context stack.

## Control flow
`main()` sizes and maps an altstack, confirms initial disabled state, enables `SS_AUTODISARM`, builds a user context, and raises `SIGUSR1`. `my_usr1()` verifies the stack pointer is on the signal stack, plants sentinel data, confirms `sigaltstack()` reports disabled while in the handler, then swaps to `uc`. `switch_fn()` raises `SIGUSR2`, whose handler searches for and would corrupt reused stack data, then returns to the saved signal context. After handler completion, `main()` verifies the altstack is back to `SS_AUTODISARM`.

## State and persistence
Global stack pointers, sizes, and contexts hold the alternate stack and user stack for one process lifetime. Sentinel data on the altstack is the corruption detector.

## Dependencies and integration points
Depends on architecture stack pointer mapping, auxv `AT_MINSIGSTKSZ`, POSIX ucontext APIs, and kselftest.

## Risks
If kernel lacks `SS_AUTODISARM`, the test skips after one planned result. ucontext APIs are deprecated on some libc targets but still used for this kernel behavior test. Stack size and pointer checks are architecture-sensitive.

## Test signals
Expected pass results: initial altstack disabled, altstack disabled inside handler due to autodisarm, and altstack still `SS_AUTODISARM` after signal. Failures include stack pointer outside altstack or sentinel corruption.
