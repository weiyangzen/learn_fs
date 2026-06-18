# sources/distributed-fs/ceph-client/lib/locking-selftest-mutex.h

Purpose: macro adapter selecting mutex operations for generic locking self-test templates.

Important APIs/types/functions: maps `LOCK` to `ML`, `UNLOCK` to `MU`, and `INIT` to `MI`; undefines read/write lock-specific macros.

Control flow: `locking-selftest.c` includes this header before `GENERATE_TESTCASE()` blocks so generic `LOCK(A)` bodies become `mutex_lock(&mutex_A)` style operations.

State/persistence: no runtime state; preprocessor mapping only.

Dependencies/integration: requires `ML`, `MU`, and `MI` macros from `locking-selftest.c`.

Risks: no include guard by design. Mutexes are not valid in all IRQ contexts, so generated expectations must account for sleepability and PREEMPT_RT differences.

Test signals: mutex columns in the locking API self-test output reflect cases generated through this adapter.
