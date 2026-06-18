# sources/distributed-fs/ceph-client/ipc/shm.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/shm.c` implements System V shared memory: segment creation, control, attach/detach, VMA wrappers, forced orphan cleanup, namespace initialization/teardown, locking/unlocking, proc reporting, and compat syscall support. The source was read as a complete 1880-line file.

## Important APIs, Types, and Functions

`struct shmid_kernel` stores IPC permissions, backing file, attach count, size, timestamps, creator/last pids, mlock accounting, creator task, creator-list linkage, and namespace pointer. `struct shm_file_data` wraps the real shmem/hugetlb file with shmid, namespace, file, and original vm ops. Public helpers include `ksys_shmget()`, `ksys_shmctl()`, `do_shmat()`, `ksys_shmdt()`, `shm_destroy_orphaned()`, `exit_shm()`, `shm_init_ns()`, `shm_exit_ns()`, and `shm_init()`.

## Control Flow

`shmget` delegates to `ipcget()` with `newseg()` for creation. `newseg()` validates size and namespace page limits, allocates `shmid_kernel`, runs LSM allocation, creates either a hugetlb file or shmem file, initializes metadata, publishes an IPC id, links the segment to the creator task, sets the backing inode number to the shmid, and updates namespace total pages.

`shmctl` dispatches info/stat, permission update, removal, and lock/unlock operations. `IPC_RMID` marks attached segments `SHM_DEST` and hides their key or destroys unattached segments immediately. `SHM_LOCK`/`SHM_UNLOCK` enforce capability/owner and memlock rules, call shmem locking helpers, and track the charging `ucounts`.

`do_shmat()` validates address/alignment/remap flags, derives protections and access mode, checks permissions and LSM policy, increments attach count, creates an outer file clone whose ops point to this file, and maps the real backing file through `do_mmap()`. The wrapper VMA ops forward faults and NUMA policy to the underlying mapping while maintaining SysV attach timestamps and counts. `shmdt` finds all VMA fragments belonging to the segment and unmaps them.

## State and Persistence Behavior

Segments persist in `ns->ids[IPC_SHM_IDS]` until `IPC_RMID`, namespace teardown, or forced orphan cleanup. Backing storage lives in shmem or hugetlbfs files and can remain mapped after `IPC_RMID` until the last attach closes. `shm_nattch`, `shm_atim`, `shm_dtim`, `shm_ctim`, creator/last pids, `SHM_DEST`, `SHM_LOCKED`, namespace total pages, and creator lists are runtime state. `shm_rmid_forced` changes cleanup policy for orphaned creator lists.

## Dependencies and Integration Points

This file integrates generic SysV IPC id management, shmem, hugetlb, VFS file cloning, mmap and VMA operations, mempolicy hooks, LSM and audit, pid/user namespaces, namespace tree init, sysctl orphan cleanup, rlimits/ucounts for mlock, proc sysvipc output, and compat control/attach paths.

## Risks and Edge Cases

Attach/detach lifetime is the central risk. The wrapper file can outlive IPC id removal, so `__shm_open()` checks both id and backing file to detect id reuse. `do_shmat()` increments `shm_nattch` before mapping and must decrement on all failures. `shmdt` must unmap fragmented VMAs without detaching unrelated segments. Forced orphan removal and creator-list cleanup race with task exit, namespace teardown, and `IPC_RMID`, requiring `task_lock`, namespace refs, RCU, and id rwsem coordination.

## Test Signals

Tests should cover shmem and hugetlb creation, size/limit failures, `SHM_NORESERVE`, attach at fixed/rounded addresses, `SHM_REMAP`, read-only and exec attaches, detach of fragmented mappings, `IPC_RMID` while attached, `shm_rmid_forced`, creator task exit, `SHM_LOCK`/`SHM_UNLOCK` permissions and memlock behavior, namespace isolation, proc RSS/swap reporting, and compat `shmctl`/`shmat`.
