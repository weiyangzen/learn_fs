# sources/distributed-fs/ceph-client/lib/locking-selftest-wlock-hardirq.h

Purpose: combined adapter for rwlock write-side tests in simulated hardirq context.

Important APIs/types/functions: includes `locking-selftest-wlock.h` and `locking-selftest-hardirq.h`.

Control flow: used by generated hardirq testcase matrices where generic lock operations should be write locks and generic IRQ operations should be hardirq simulation.

State/persistence: preprocessor-only.

Dependencies/integration: requires base wlock and hardirq macros from the self-test implementation.

Risks: include-order sensitive and intentionally unguarded. Write locks participate in exclusive dependency cycles and are expected to fail in many generated scenarios.

Test signals: hardirq wlock variants in lockdep self-test output.
