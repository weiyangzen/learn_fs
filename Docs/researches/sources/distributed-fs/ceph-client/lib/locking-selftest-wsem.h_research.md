# sources/distributed-fs/ceph-client/lib/locking-selftest-wsem.h

Purpose: macro adapter selecting write-side rwsem operations for generic locking self-test templates.

Important APIs/types/functions: maps `LOCK`/`WLOCK` to `WSL`, `UNLOCK` to `WSU`, `RLOCK` to `RSL`, and `INIT` to `RWSI`.

Control flow: included before generated testcases so generic lock bodies exercise `down_write()`/`up_write()` and mixed semaphore templates can use read-side operations.

State/persistence: preprocessor mapping only.

Dependencies/integration: requires rwsem helper macros from `locking-selftest.c`.

Risks: rwsems sleep and cannot be used in IRQ contexts; generated self-tests and expectations are limited accordingly. Include guards would break repeated macro remapping.

Test signals: wsem column in lockdep self-test output.
