# sources/distributed-fs/ceph-client/lib/locking-selftest-rtmutex.h

Purpose: macro adapter selecting rtmutex operations for generic locking self-test templates when `CONFIG_RT_MUTEXES` is enabled.

Important APIs/types/functions: maps `LOCK` to `RTL`, `UNLOCK` to `RTU`, and `INIT` to `RTI`; undefines read/write-specific macros.

Control flow: included inside `#ifdef CONFIG_RT_MUTEXES` blocks before testcase generation, adding rtmutex variants to the same deadlock/double-unlock/init-held matrix.

State/persistence: preprocessor-only mapping.

Dependencies/integration: requires `RTL`, `RTU`, and `RTI` macros from `locking-selftest.c` and rtmutex declarations to exist.

Risks: only valid when rtmutex support is compiled. RT behavior can differ from raw spin and mutex semantics.

Test signals: rtmutex column in locking self-test output when built.
