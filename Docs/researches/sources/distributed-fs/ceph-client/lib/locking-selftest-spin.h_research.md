# sources/distributed-fs/ceph-client/lib/locking-selftest-spin.h

Purpose: macro adapter selecting spinlock operations for generic locking self-test templates.

Important APIs/types/functions: maps `LOCK` to `L`, `UNLOCK` to `U`, and `INIT` to `SI`; undefines read/write lock-specific macros.

Control flow: included repeatedly before generated testcase bodies in `locking-selftest.c`.

State/persistence: preprocessor-only mapping.

Dependencies/integration: requires `L`, `U`, and `SI` macros from the including self-test implementation.

Risks: generic templates using read/write-specific macros must not include this adapter unless those paths are irrelevant. RT kernels can make `spinlock_t` behave differently than raw spinlocks, so expectations are conditional elsewhere.

Test signals: spin column in lockdep self-test output.
