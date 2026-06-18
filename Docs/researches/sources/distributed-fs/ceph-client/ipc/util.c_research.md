# sources/distributed-fs/ceph-client/ipc/util.c

## Purpose
`ipc/util.c` is the common SysV IPC support layer used by semaphores, message queues, and shared memory. It initializes IPC namespaces and `/proc/sysvipc`, manages IPC object identifiers, translates permission structures, enforces generic IPC permissions, and provides shared lookup/creation helpers for `semget`, `msgget`, and `shmget` style operations.

## Important APIs, types, and functions
The file centers on `struct ipc_ids`, `struct kern_ipc_perm`, and helper descriptors from `util.h` such as `struct ipc_ops` and `struct ipc_params`. `ipc_init()` creates the proc directory and calls `sem_init()`, `msg_init()`, and `shm_init()`. `ipc_init_ids()` initializes per-namespace identifier state: `rwsem`, rhashtable key lookup, IDR, sequence counters, and checkpoint-restore fields.

ID allocation is split between `ipc_idr_alloc()` and `ipc_addid()`. `ipc_idr_alloc()` assigns an IDR index, computes the sequence component, handles `CONFIG_CHECKPOINT_RESTORE` requested IDs, and publishes the object with ordering comments around RCU visibility. `ipc_addid()` initializes the object refcount, spinlock, creator credentials, deletion flag, inserts into IDR and the key rhashtable when the key is public, and returns the object locked on success.

Lookup and control helpers include `ipc_findkey()`, `ipc_obtain_object_idr()`, `ipc_obtain_object_check()`, `ipcget()`, `ipcctl_obtain_check()`, `ipc_rmid()`, `ipc_set_key_private()`, `ipc_rcu_getref()`, and `ipc_rcu_putref()`. Permission conversion and enforcement are provided by `ipcperms()`, `kernel_to_ipc64_perm()`, `ipc64_perm_to_ipc_perm()`, and `ipc_update_perm()`. The procfs path is implemented by `ipc_init_proc_interface()` and the `sysvipc_proc_*` seq-file operations.

## Control flow
Creation through `ipcget()` branches on `IPC_PRIVATE`. Private objects call `ipcget_new()`, which takes `ids->rwsem` for writing and delegates to the resource-specific `getnew`. Public keys call `ipcget_public()`, which takes the same writer semaphore because it may create a new object. It searches by key in the rhashtable, creates if missing and `IPC_CREAT` is present, rejects `IPC_CREAT|IPC_EXCL` conflicts, runs resource-specific `more_checks`, then calls `ipc_check_perms()`.

Deletion via `ipc_rmid()` removes the IDR entry, removes the key hash entry if needed, decrements `in_use`, marks the object deleted, and recalculates `max_idx` if the removed index was the maximum. Procfs iteration takes `ids->rwsem` for reading, maps seq-file positions to IDR indexes, locks each object while formatting, and releases namespace references on file close.

## State and persistence behavior
IPC state is in-memory and namespace-scoped. Persistence is limited to object lifetime, ID sequence numbers, and procfs visibility. `ids->seq`, `last_idx`, and `max_idx` prevent stale ID reuse from being accepted without a matching sequence. Object memory is RCU protected: readers may obtain objects without immediate object locks, while final freeing is scheduled with `call_rcu()`.

## Dependencies and integration points
This file integrates with IDR, rhashtable, RCU, namespace lifetime, procfs seq-file support, LSM hooks (`security_ipc_permission` and resource-specific `associate` callbacks), audit hooks (`audit_ipc_obj`, `audit_ipc_set_perm`), capabilities, user namespaces, and the IPC resource implementations in `sem.c`, `msg.c`, and `shm.c`.

## Risks and invariants
The main risk is violating the documented locking model. `ids->rwsem` protects creation, removal, and proc iteration; `kern_ipc_perm.lock` protects per-object mutation; RCU protects lockless lookup windows. Incorrect publication ordering could expose partially initialized objects, and incorrect sequence handling could make stale user-visible IDs valid. Permission paths must preserve the order of normal DAC checks, capability checks in the IPC namespace userns, LSM checks, and audit logging.

## Test signals
Useful signals include SysV IPC creation/removal stress across namespaces, concurrent `IPC_CREAT` with shared keys, `IPC_RMID` races with lookup and procfs iteration, permission tests for owner/group/other/capability paths, checkpoint-restore requested IDs, and `/proc/sysvipc/*` formatting under churn. Kernel concurrency tools such as KCSAN/lockdep are relevant because most failures would be locking or lifetime regressions.
