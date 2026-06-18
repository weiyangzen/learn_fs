# sources/distributed-fs/ceph-client/lib/locking-selftest-rlock.h

Purpose: macro adapter selecting rwlock read-side operations for generic lockdep self-test templates.

Important APIs/types/functions: maps `LOCK` and `RLOCK` to `RL`, `UNLOCK` to `RU`, `WLOCK` to `WL`, and `INIT` to `RWI`.

Control flow: included before generated testcases so generic lock operations become `read_lock()`/`read_unlock()` while mixed read/write templates can still call `WLOCK`.

State/persistence: preprocessor mapping only.

Dependencies/integration: requires `RL`, `RU`, `WL`, and `RWI` macros from `locking-selftest.c`.

Risks: read locks have special recursive semantics in the self-test, controlled by `force_read_lock_recursive`; expectations differ from exclusive locks.

Test signals: rlock self-test cases check both expected no-fail recursive reads and expected failures for mixed read/write dependency cycles.
