# sources/distributed-fs/ceph-client/ipc/ipc_sysctl.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/ipc_sysctl.c` registers per-IPC-namespace sysctls for System V shared memory, messages, semaphores, and checkpoint/restore next-id controls. It also supports the `ipcmni_extend` early boot parameter. The source was read as a complete 334-line file.

## Important APIs, Types, and Functions

Handlers include `proc_ipc_dointvec_minmax_orphans()` for `shm_rmid_forced`, `proc_ipc_auto_msgmni()` for the legacy no-op `auto_msgmni`, and `proc_ipc_sem_dointvec()` for validating semaphore tunables through `sem_check_semmni()`. The exported setup/teardown functions are `setup_ipc_sysctls()` and `retire_ipc_sysctls()`. Global limits are `ipc_mni`, `ipc_mni_shift`, and `ipc_min_cycle`, modified by `ipc_mni_extend()`.

## Control Flow

`setup_ipc_sysctls()` initializes `ns->ipc_set`, duplicates the static `ipc_sysctls` table, rewrites every `.data` pointer from `init_ipc_ns` storage to the target namespace storage, and registers the table under `kernel`. `retire_ipc_sysctls()` unregisters and frees the duplicated table. `ipc_sysctl_init()` registers sysctls for `init_ipc_ns` at device init time.

## State and Persistence Behavior

Sysctl values live in `struct ipc_namespace`: shared memory limits and forced removal flag, message queue limits, semaphore control array, and optional next-id fields. Writes persist for the namespace lifetime. Enabling `shm_rmid_forced` can immediately destroy orphaned shared-memory segments through `shm_destroy_orphaned()`.

## Dependencies and Integration Points

This file integrates the sysctl core, IPC namespace ownership, user namespace uid/gid mapping, checkpoint/restore privilege checks, and SysV IPC subsystems. Permission callbacks make sysctls appear owned by root in the owning user namespace and give checkpoint/restore-capable tasks write access to next-id fields when configured.

## Risks and Edge Cases

Pointer rewriting must be exhaustive; a stale pointer to `init_ipc_ns` would make one namespace mutate another. Semaphore sysctl writes must roll back invalid `semmni` changes. `shm_rmid_forced` has destructive side effects, so handler ordering matters. Permission calculations are namespace-sensitive and must not accidentally grant host-level access from another user namespace.

## Test Signals

Tests should create IPC namespaces, read/write `/proc/sys/kernel/{shmmax,shmall,shmmni,shm_rmid_forced,msgmax,msgmni,msgmnb,sem}`, verify isolation between namespaces, validate invalid `sem` writes roll back, exercise `shm_rmid_forced` orphan cleanup, and boot with `ipcmni_extend` to confirm extended id limits.
