<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/futex.h -->
# sources/distributed-fs/ceph-client/include/linux/futex.h

Purpose: Declares core futex keying and task lifecycle hooks for fast userspace mutex support.

Important APIs/types/functions: `union futex_key` encodes shared inode-backed keys, private mm/address keys, and common hash fields. Low bits of `offset` encode `FUT_OFF_INODE` or `FUT_OFF_MMSHARED`. `futex_init_task()` initializes robust-list pointers, PI state list/cache, exit state, and exit mutex. Runtime APIs include `do_futex()`, `futex_exit_recursive()`, `futex_exit_release()`, `futex_exec_release()`, `futex_hash_prctl()`, and optional private-hash helpers.

Control flow: Syscall handling passes user addresses, op, values, and timeout into `do_futex()`. Task initialization/exit/exec paths call lifecycle hooks to manage robust futexes and priority-inheritance state. Private hash support may allocate/free per-mm hash tables.

State and persistence behavior: Futex wait queues are runtime-only. Keys may hold references to inode or mm depending on mapping type. Task state includes robust lists, PI state, and `futex_state`.

Dependencies and integration points: Depends on scheduler/task, ktime, mm types, and UAPI futex constants. Integrates with clone/fork task init, exec, process exit, robust-list cleanup, and mm lifetime.

Risks: The key layout is hash-sensitive and must not be rearranged without updating hash code. Incorrect inode/mm reference tagging can cause use-after-free or mismatched wait queues. Disabled `CONFIG_FUTEX` stubs return `-EINVAL`.

Test signals: Futex syscall selftests, robust-list exit cleanup, PI futex tests, private versus shared mappings, `execve()` release tests, private-hash configuration builds, and stress tests under heavy mm teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/futex.h -->
