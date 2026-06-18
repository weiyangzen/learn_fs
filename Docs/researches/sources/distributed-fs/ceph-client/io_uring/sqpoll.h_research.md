# sources/distributed-fs/ceph-client/io_uring/sqpoll.h

Purpose: defines SQPOLL shared thread state and public SQPOLL control APIs.

Important APIs/types/functions: `struct io_sq_data` stores refs, `park_pending`, lock, context list, RCU thread pointer, waitqueue, idle timeout, CPU, task identifiers, work time, state bits, and exit completion. `sqpoll_task_locked()` safely dereferences the thread under `sqd->lock`.

Control flow: inline `sqpoll_task_locked()` uses `rcu_dereference_protected()` with lockdep validation.

State and persistence: header defines per-SQPOLL-thread lifetime state shared by one or more rings.

Dependencies/integration: used by setup, register io-wq affinity handling, teardown, and fdinfo/reporting paths.

Risks/test signals: callers must hold `sqd->lock` for the inline dereference. Lockdep and SQPOLL affinity/teardown tests cover misuse.
