# sources/distributed-fs/ceph-client/ipc/namespace.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/namespace.c` implements IPC namespace creation, reference management, teardown, proc namespace operations, and generic cleanup of per-namespace IPC objects. The source was read as a complete 257-line file.

## Important APIs, Types, and Functions

`copy_ipcs()` clones or references an IPC namespace depending on `CLONE_NEWIPC`. `create_ipc_ns()` allocates and initializes a new namespace. `free_ipcs()` walks an `ipc_ids` table and calls a type-specific free function. `put_ipc_ns()` drops namespace references and schedules asynchronous teardown. Proc namespace operations are `ipcns_get()`, `ipcns_put()`, `ipcns_install()`, and `ipcns_owner()`, exposed through `ipcns_operations`.

## Control Flow

Namespace creation charges `UCOUNT_IPC_NAMESPACES`, allocates `struct ipc_namespace`, initializes common namespace state, assigns namespace tree id and user namespace, creates the mqueue mount, registers mqueue and SysV IPC sysctls, initializes message, semaphore, and shared-memory namespaces, then adds the namespace to the namespace tree. Failure unwinds in reverse order.

Namespace put is asynchronous. When the last reference is dropped under `mq_lock`, `mq_clear_sbinfo()` prevents new VFS lookups from taking namespace references, the namespace is removed from the tree, and work is queued. `free_ipc()` marks mqueue mounts short-term, waits for an RCU grace period, then calls `free_ipc_ns()` to free mqueues, semaphores, messages, shm, sysctls, ucounts, user namespace, common namespace state, and memory.

## State and Persistence Behavior

The IPC namespace owns SysV IPC id tables, mqueue mount and limits, sysctl registrations, user namespace reference, ucounts charge, namespace tree id, and teardown list linkage. State persists until reference count reaches zero and asynchronous cleanup completes.

## Dependencies and Integration Points

This file integrates user namespaces and ucounts, mount/VFS lifetime rules for mqueuefs, sysctl setup/retire helpers, SysV IPC subsystem init/exit functions, RCU, namespace tree registration, `nsproxy`, and `/proc/<pid>/ns/ipc` operations.

## Risks and Edge Cases

The critical race is between last-task namespace exit and another mount namespace accessing the mqueue superblock. `mq_lock`, `mq_clear_sbinfo()`, and the RCU-delayed free path are designed to close that race. Namespace creation must unwind partial initialization precisely. `ipcns_install()` must require `CAP_SYS_ADMIN` in both the target namespace owner and caller credential user namespace.

## Test Signals

Tests should cover `unshare(CLONE_NEWIPC)`, `setns()` permission checks, mqueue mount access after namespace exit, namespace limit exhaustion and delayed free retry, cleanup of live msg/sem/shm objects on namespace exit, and proc namespace owner/reference behavior.
