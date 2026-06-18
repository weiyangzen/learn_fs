# sources/distributed-fs/ceph-client/lib/locking-selftest-rlock-softirq.h

Purpose: combined macro adapter for read-lock tests in simulated softirq context.

Important APIs/types/functions: includes `locking-selftest-rlock.h` and `locking-selftest-softirq.h`.

Control flow: lets generated generic test event bodies use `read_lock()`/`read_unlock()` and softirq enter/exit helpers.

State/persistence: preprocessor-only mapping with no runtime storage.

Dependencies/integration: used by `locking-selftest.c` for softirq variants, often disabled under `CONFIG_PREEMPT_RT` via surrounding `NON_RT` or `#ifndef CONFIG_PREEMPT_RT` logic.

Risks: same re-inclusion/order sensitivity as other self-test adapters. Softirq cases differ under RT, so expectations live in the including C file.

Test signals: softirq read-lock columns/rows in generated lockdep self-test output.
