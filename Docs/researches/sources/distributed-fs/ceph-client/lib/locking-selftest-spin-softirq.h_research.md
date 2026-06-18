# sources/distributed-fs/ceph-client/lib/locking-selftest-spin-softirq.h

Purpose: combined adapter for spinlock tests in simulated softirq context.

Important APIs/types/functions: includes `locking-selftest-spin.h` and `locking-selftest-softirq.h`.

Control flow: used before testcase-generation macros to bind generic lock operations to `spin_lock()` and generic IRQ operations to softirq simulation.

State/persistence: preprocessor-only.

Dependencies/integration: consumed by `locking-selftest.c`, mostly in non-RT softirq testcase blocks.

Risks: no include guard by design; PREEMPT_RT changes spinlock sleepability and surrounding code limits use.

Test signals: softirq spinlock variants in irqsafe and inversion test groups.
