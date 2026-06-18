<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sem.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/sem.h

Purpose: defines the System V semaphore userspace ABI, including semop flags, semctl commands, legacy structures, semop payloads, semctl union, and default limits.

Important APIs, types, and functions: `SEM_UNDO` requests undo-on-exit behavior. Semctl commands include `GETPID`, `GETVAL`, `GETALL`, `GETNCNT`, `GETZCNT`, `SETVAL`, `SETALL`, `SEM_STAT`, `SEM_INFO`, and `SEM_STAT_ANY`. `struct sembuf` carries semaphore index, operation, and flags. `union semun` is the semctl argument shape. `struct seminfo` and constants such as `SEMMNI`, `SEMMSL`, `SEMMNS`, `SEMOPM`, `SEMVMX`, and `SEMAEM` describe limits. Legacy `struct semid_ds` remains for compatibility while `asm/sembuf.h` supplies modern 64-bit layouts.

Control flow: userspace creates semaphore sets through SysV IPC, performs arrays of `sembuf` operations via semop/semtimedop, and manages/query sets through semctl commands.

State and persistence behavior: semaphore sets, values, wait queues, undo lists, timestamps, and permissions live in the kernel IPC namespace until removed. Undo state is per process and applied on exit. The header defines ABI shapes only.

Dependencies and integration points: depends on `linux/ipc.h` and architecture semaphore buffer layouts. It integrates with SysV IPC namespaces, libc semctl wrappers, ipcs/ipcrm tools, and checkpoint/compat code.

Risks and edge cases: `union semun` contains userspace pointers and differs from some libc declarations. Large `SEMOPM` values can trigger allocation fragmentation, as documented. Legacy and 64-bit time layouts must be kept compatible.

Test signals: semget/semop/semctl tests for all command values, SEM_UNDO on process exit, IPC namespace isolation, 32-bit compat semid layouts, limit sysctl changes, and large semop array failure behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/sem.h -->
