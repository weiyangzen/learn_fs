# sources/distributed-fs/ceph-client/lib/locking-selftest-spin-hardirq.h

Purpose: combined adapter for spinlock tests in simulated hardirq context.

Important APIs/types/functions: includes `locking-selftest-spin.h` and `locking-selftest-hardirq.h`.

Control flow: used by `locking-selftest.c` before generating hardirq spinlock variants for irqsafe and inversion scenarios.

State/persistence: preprocessor-only.

Dependencies/integration: requires spin and hardirq macro definitions in the including file.

Risks: include order is functional and there are no guards. Spinlock behavior differs under PREEMPT_RT, so surrounding code controls which cases run and expected outcomes.

Test signals: hardirq spinlock columns in generated lockdep output.
