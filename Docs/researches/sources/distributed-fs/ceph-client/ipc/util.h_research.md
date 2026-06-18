# sources/distributed-fs/ceph-client/ipc/util.h

## Purpose
`ipc/util.h` is the shared internal header for SysV IPC implementation files. It defines the IPC ID layout, declares namespace initialization/exit helpers, describes common get/create operation callbacks, exposes generic permission/lookup/update helpers, and provides small locking, reference, and PID utility inlines used by semaphore, message queue, and shared memory code.

## Important APIs, types, and macros
The header defines the standard and extended IPCMNI layouts: `IPCMNI_SHIFT`, `IPCMNI_EXTEND_SHIFT`, `IPCMNI`, `IPCMNI_EXTEND`, `ipcmni_seq_shift()`, `IPCMNI_IDX_MASK`, `ipcid_to_idx()`, `ipcid_to_seqx()`, and `ipcid_seq_max()`. These macros define how the user-visible IPC ID is split into an index and a sequence number.

`struct ipc_params` carries common `key`, `flg`, and type-specific creation parameters (`size` for shared memory or `nsems` for semaphores). `struct ipc_ops` supplies resource-specific callbacks for new object creation, LSM association, and optional extra validation. Public APIs include `ipc_init_ids()`, `ipc_addid()`, `ipc_rmid()`, `ipc_set_key_private()`, `ipcperms()`, `ipc_obtain_object_idr()`, `ipcctl_obtain_check()`, `ipc_update_perm()`, `kernel_to_ipc64_perm()`, `ipc64_perm_to_ipc_perm()`, and message helpers such as `load_msg()` and `store_msg()`.

The header also declares procfs support (`ipc_init_proc_interface()`, `ipc_seq_pid_ns()`), namespace hooks for SysV IPC and POSIX mqueue, and compatibility stubs when features are disabled. Locking helpers `ipc_lock_object()`, `ipc_unlock_object()`, and `ipc_assert_locked_object()` wrap the object spinlock.

## Control flow and integration
The header's declarations establish the common path implemented in `util.c`: resource-specific code prepares an `ipc_params` and `ipc_ops`, then calls `ipcget()` or lower-level helpers. Control operations call `ipcctl_obtain_check()` while holding the namespace ID semaphore and RCU read lock. Proc emitters use the `IPC_SEM_IDS`, `IPC_MSG_IDS`, and `IPC_SHM_IDS` indexes to select namespace ID arrays.

## State and persistence behavior
No state is stored in this header, but its macros define persistent ABI behavior for IPC IDs. Changing the ID bit split or masks would alter lookup semantics and stale-ID detection. Conditional externs for `ipc_mni`, `ipc_mni_shift`, and `ipc_min_cycle` make runtime sysctl-selected IPCMNI extension mode visible to all IPC users.

## Dependencies and integration points
It depends on kernel IPC namespace types, PID references, user/kernel IPC permission structures, RCU/refcounted `kern_ipc_perm` objects, and optional configs such as `CONFIG_SYSVIPC`, `CONFIG_PROC_FS`, `CONFIG_POSIX_MQUEUE`, `CONFIG_SYSVIPC_SYSCTL`, `CONFIG_CHECKPOINT_RESTORE`, and `CONFIG_ARCH_WANT_IPC_PARSE_VERSION`.

## Risks and invariants
The critical invariant is that every user of the ID macros agrees on the index/sequence split. `ipc_checkid()` must remain consistent with `ipc_idr_alloc()` in `util.c`. Callers must honor comments about required locks: `ipc_addid()` under write `ids->rwsem`, `ipc_rmid()` with both namespace and object locks, `ipcperms()` with the object locked, and object lookup inside RCU sections.

## Test signals
Compile coverage across relevant config combinations is important because this header has many conditional stubs. Runtime tests should exercise normal and extended IPCMNI modes, namespace init/exit, procfs enabled/disabled builds, old IPC command parsing when configured, and stale-ID rejection after removal and sequence increment.
