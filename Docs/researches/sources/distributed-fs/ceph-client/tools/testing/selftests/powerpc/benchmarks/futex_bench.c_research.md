# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/futex_bench.c

## Purpose
Measures raw futex wait/wake syscall throughput in a tight loop.

## Important APIs, Types, and Functions
Defines `ITERATIONS`, `futex(...)` syscall macro, `test_futex()`, and `main()` using `test_harness()`.

## Control Flow
`test_futex()` records timebase start/end around `ITERATIONS` calls to `FUTEX_WAKE` on a stack word, then prints elapsed time through `printf()`.

## State and Persistence
No durable state; the futex word and timing data are process-local.

## Dependencies and Integration Points
Depends on Linux futex syscall, `utils.h` timebase helpers, and PowerPC kselftest harness.

## Risks and Test Signals
Risk is that this is a benchmark with broad timing variance; functional failure only occurs if the syscall path or harness fails.
