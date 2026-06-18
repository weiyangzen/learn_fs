# sources/distributed-fs/ceph-client/drivers/mtd/tests/mtd_test.h

## Purpose
Declares shared MTD test helper APIs and supplies a cooperative abort point used by long-running test modules.

## Important APIs, Types, and Functions
`mtdtest_relax()` calls `cond_resched()` and aborts with `-EINTR` if the current task has a pending signal. The header declares the erase, BBT scan, read, and write helpers exported from `mtd_test.c`.

## Control Flow
Test loops call `mtdtest_relax()` between eraseblocks or operations to keep the kernel responsive and allow module load/init to abort when signaled.

## State and Persistence
The header has no persistent state. It observes pending task signals and returns an error to the caller.

## Dependencies and Integration Points
It depends on `linux/mtd/mtd.h` and `linux/sched/signal.h`. It is included by the MTD test modules.

## Risks
Callers must actually check and propagate `mtdtest_relax()` errors; otherwise long destructive tests may remain hard to interrupt. The helper declarations must stay in sync with exported implementations.

## Test Signals
Compile coverage validates declarations. Runtime cancellation can be tested by interrupting long-running modules and confirming `-EINTR` propagation.
