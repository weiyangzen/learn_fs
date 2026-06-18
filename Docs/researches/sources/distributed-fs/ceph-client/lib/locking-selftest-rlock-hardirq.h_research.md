# sources/distributed-fs/ceph-client/lib/locking-selftest-rlock-hardirq.h

Purpose: combined macro adapter for read-lock tests in simulated hardirq context.

Important APIs/types/functions: includes `locking-selftest-rlock.h` to select `read_lock()`/`read_unlock()` and `locking-selftest-hardirq.h` to select hardirq enter/exit/disable/enable helpers.

Control flow: consumed by `locking-selftest.c` testcase-generation macros where both generic lock and generic IRQ operations are used.

State/persistence: preprocessor-only mapping.

Dependencies/integration: depends on the base rlock and hardirq adapter headers and the macros defined by `locking-selftest.c`.

Risks: include order is the behavior; because there is no include guard, accidental insertion of guards would break repeated generation.

Test signals: hardirq read-lock variants in irqsafe, inversion, and recursion self-tests.
