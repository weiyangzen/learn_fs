# sources/distributed-fs/ceph-client/lib/locking-selftest-softirq.h

Purpose: macro adapter for lockdep self-tests that should run in simulated softirq context.

Important APIs/types/functions: maps `IRQ_ENABLE`, `IRQ_DISABLE`, `IRQ_ENTER`, and `IRQ_EXIT` to softirq helpers.

Control flow: included before generated softirq variants so generic IRQ event bodies use local BH disable/enable and lockdep softirq enter/exit paths.

State/persistence: preprocessor mapping only.

Dependencies/integration: requires `SOFTIRQ_ENABLE`, `SOFTIRQ_DISABLE`, `SOFTIRQ_ENTER`, and `SOFTIRQ_EXIT` from `locking-selftest.c`.

Risks: no include guard by design. Many softirq tests are skipped under PREEMPT_RT by the including file.

Test signals: generated softirq irqsafe and inversion cases in `locking_selftest()`.
