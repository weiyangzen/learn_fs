# sources/distributed-fs/ceph-client/lib/locking-selftest-hardirq.h

Purpose: macro adapter for lockdep self-tests that should run in simulated hardirq context.

Important APIs/types/functions: defines `IRQ_ENABLE`, `IRQ_DISABLE`, `IRQ_ENTER`, and `IRQ_EXIT` to the hardirq versions after undefining any prior mapping.

Control flow: included repeatedly by `locking-selftest.c` before testcase generation macros. It changes the meaning of generic IRQ macros used by generated event bodies.

State/persistence: no runtime state; preprocessor state only.

Dependencies/integration: depends on `HARDIRQ_ENABLE`, `HARDIRQ_DISABLE`, `HARDIRQ_ENTER`, and `HARDIRQ_EXIT` being defined by the including C file.

Risks: include order matters. It intentionally has no include guard because it must be re-includable with different lock adapters.

Test signals: generated hardirq variants in `locking-selftest.c` exercise the mapping.
