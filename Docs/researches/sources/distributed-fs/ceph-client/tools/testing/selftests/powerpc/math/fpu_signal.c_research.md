# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_signal.c

## Purpose
Checks that FPU register state is accurately represented in signal contexts while worker threads continuously validate registers.

## Important APIs, Types, and Functions
Defines `ITERATIONS`, `THREAD_FACTOR`, thread-local `darray`, `signal_fpu_sig()`, `signal_fpu_c()`, `test_signal_fpu()`, and `main()`, using external `preempt_fpu()`.

## Control Flow
Workers install a SIGUSR1 SA_SIGINFO handler, randomize FPU data, and enter the assembly checking loop. The main thread sends SIGUSR1 to every worker repeatedly, then stops workers and fails if either assembly checks or signal-context FP register comparisons failed.

## State and Persistence
State is thread-local expected FP arrays, global `bad_context`, shared counters, and signal handlers. No persistence.

## Dependencies and Integration Points
Depends on pthread signals, ucontext/mcontext FP register layout, `fpu_asm.S`, and harness utilities.

## Risks and Test Signals
Risks include signal delivery timing and scratch-register exclusions for f30/f31. Failure signals are nonzero worker return or `bad_context` true.
