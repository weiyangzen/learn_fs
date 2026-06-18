# sources/distributed-fs/ceph-client/include/linux/poll.h

Purpose: defines kernel poll/select support structures and helpers used by file `->poll()` implementations and the core select/poll syscalls.

Important APIs and types: `poll_table`, `poll_queue_proc`, `struct poll_table_entry`, and `struct poll_wqueues` describe wait registration and syscall-side wait queues. Helpers include `poll_wait()`, `poll_requested_events()`, `init_poll_funcptr()`, `file_can_poll()`, `vfs_poll()`, `poll_initwait()`, `poll_freewait()`, `select_estimate_accuracy()`, `core_sys_select()`, `poll_select_set_timeout()`, and `mangle_poll()`/`demangle_poll()` for POLL/EPOLL bit translation.

Control flow: a syscall initializes `poll_wqueues`, calls each file's `->poll()` via `vfs_poll()`, and file implementations call `poll_wait()` to register wait queues before returning readiness masks. `poll_wait()` invokes the queue proc and issues a memory barrier paired with waitqueue sleeper checks so readiness checks are ordered after queue insertion.

State and persistence: syscall wait state is stack/temporary memory in `poll_wqueues`, including inline entries sized by stack-budget macros and optional page-backed table entries. No persistent state is stored here.

Dependencies and integration points: integrates with VFS file operations, wait queues, user fd sets, uaccess, ktime/timeouts, UAPI poll and eventpoll masks, and select/poll syscall implementations.

Risks and test signals: risks include missing `poll_wait()` before readiness tests, incorrect readiness mask conversion, stack budget regressions, `file->f_op->poll` NULL handling, and memory-ordering races with wakeups. Test driver poll implementations, epoll/select/poll equivalence, timeout conversion, wake-after-register races, and files without poll support returning default masks.
