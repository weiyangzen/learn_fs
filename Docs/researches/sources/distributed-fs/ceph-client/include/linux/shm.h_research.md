# sources/distributed-fs/ceph-client/include/linux/shm.h

## Purpose

`shm.h` defines the kernel-side SysV shared-memory hooks stored in tasks and used for attach and exit handling. It provides real declarations under `CONFIG_SYSVIPC` and no-op or `-ENOSYS` stubs otherwise.

## Important APIs, Types, And Functions

`struct sysv_shm` contains `shm_clist` when SysV IPC is enabled and is empty otherwise. APIs are `do_shmat()`, `exit_shm()`, and `shm_init_task()`. `do_shmat()` attaches a SysV shared-memory segment and returns the mapped address via an output pointer. `exit_shm()` releases per-task shared-memory attachments. `shm_init_task()` initializes the per-task list.

## Control Flow

With SysV IPC enabled, fork or task initialization calls `shm_init_task()`, `do_shmat()` handles the attach syscall path, and task exit calls `exit_shm()`. Without SysV IPC, `do_shmat()` fails with `-ENOSYS` and the lifecycle hooks do nothing.

## State And Persistence

Per-task state is the `sysvshm.shm_clist` list, which tracks attachments for cleanup. Persistent shared-memory segment state is owned outside this header by IPC and memory-management implementations.

## Dependencies And Integration Points

Dependencies include basic types, page definitions, architecture `shmparam`, `struct task_struct`, and user pointers. Integration points are SysV IPC syscalls, task lifecycle, mm attach/mmap behavior, and architecture SHMLBA alignment.

## Risks And Test Signals

Risks are task-exit leaks, wrong SHMLBA alignment, and call sites that do not handle `-ENOSYS` in non-SysV builds. Test signals include `shmat()`/`shmdt()` syscall tests, process exit cleanup, fork behavior, namespace interactions, and non-`CONFIG_SYSVIPC` build coverage.
