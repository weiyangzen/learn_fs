# sources/distributed-fs/ceph-client/lib/locking-selftest-wlock.h

Purpose: macro adapter selecting rwlock write-side operations for generic lockdep self-test templates.

Important APIs/types/functions: maps `LOCK` and `WLOCK` to `WL`, `UNLOCK` to `WU`, `RLOCK` to `RL`, and `INIT` to `RWI`.

Control flow: included before generated testcases so generic locks become `write_lock()`/`write_unlock()`, while mixed templates can also call read locks.

State/persistence: preprocessor-only mapping.

Dependencies/integration: requires rwlock helper macros in `locking-selftest.c`.

Risks: write-side locking is exclusive; generated deadlock expectations differ from read-side recursive cases. No include guards are intentional.

Test signals: wlock column and mixed read/write rwlock cases in `locking_selftest()`.
