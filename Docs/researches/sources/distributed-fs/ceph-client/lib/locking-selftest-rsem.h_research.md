# sources/distributed-fs/ceph-client/lib/locking-selftest-rsem.h

Purpose: macro adapter selecting read-side rwsem operations for generic locking self-test templates.

Important APIs/types/functions: maps `LOCK`/`RLOCK` to `RSL`, `UNLOCK` to `RSU`, `WLOCK` to `WSL`, and `INIT` to `RWSI`.

Control flow: included before testcase-generation macros so generic templates exercise `down_read()`/`up_read()` and mixed read/write semaphore patterns.

State/persistence: preprocessor-only mapping.

Dependencies/integration: requires rwsem macros defined in `locking-selftest.c`.

Risks: rwsems are sleepable and have different recursion/deadlock expectations than rwlocks; generated expectations intentionally mark read recursion failures for rsem cases.

Test signals: rsem column in `locking_selftest()` output, especially recursive read and mixed read/write tests.
