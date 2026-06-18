# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_preempt.c

## Purpose
Stress-tests whether FPU registers survive preemption across many worker threads.

## Important APIs, Types, and Functions
Defines `PREEMPT_TIME`, `THREAD_FACTOR`, thread-local `darray`, globals `threads_starting`/`running`, external `preempt_fpu()`, `preempt_fpu_c()`, `test_preempt_fpu()`, and `main()`.

## Control Flow
The test creates `online_cpus * 8` threads, each randomizes expected FP data and enters assembly checking loop. After all start, the main thread sleeps 60 seconds to allow preemption, clears `running`, joins workers, and fails on any nonzero worker result.

## State and Persistence
State is thread-local expected arrays, shared counters, and FPU register contents. No durable files.

## Dependencies and Integration Points
Depends on pthreads, `fpu_asm.S`, CPU scheduler preemption, and common harness.

## Risks and Test Signals
Risk is long runtime and scheduler-dependent coverage. Any register mismatch is a strong failure; a pass is stress evidence, not proof that preemption happened.
