# sources/distributed-fs/ceph-client/lib/locking-selftest-wlock-softirq.h

Purpose: combined adapter for rwlock write-side tests in simulated softirq context.

Important APIs/types/functions: includes `locking-selftest-wlock.h` and `locking-selftest-softirq.h`.

Control flow: used by `locking-selftest.c` to generate softirq write-lock variants of irqsafe and inversion patterns.

State/persistence: preprocessor-only.

Dependencies/integration: relies on wlock and softirq helper macros from the including file.

Risks: unguarded repeated inclusion is required. Softirq variants are generally disabled on PREEMPT_RT by the surrounding C file.

Test signals: softirq wlock variants in the self-test tables.
