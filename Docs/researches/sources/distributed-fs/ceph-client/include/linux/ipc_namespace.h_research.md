# sources/distributed-fs/ceph-client/include/linux/ipc_namespace.h

## Purpose
`ipc_namespace.h` defines per-namespace IPC state for SysV IPC and POSIX message queues, including object ID tables, resource limits, sysctl registration, mqueue mounts, and namespace reference management.

## Important APIs, types, and functions
Core types are `struct ipc_ids` and `struct ipc_namespace`. Exports include `init_ipc_ns`, `mq_lock`, `copy_ipcs`, `get_ipc_ns`, `get_ipc_ns_not_zero`, `put_ipc_ns`, `mq_init_ns`, sysctl setup/retire helpers, and `shm_destroy_orphaned`. It also defines POSIX mqueue defaults and hard limits.

## Control flow
Namespace creation copies or rejects IPC namespaces depending on `CLONE_NEWIPC` and configuration. SysV IPC uses `ids[3]` IDR/rhashtable sets. POSIX mqueue setup creates namespace-local defaults, sysctls, and mqueue mount state. Reference helpers increment/decrement namespace lifetime around users.

## State and persistence
State is namespace-scoped and runtime-only: IPC object IDs, sem/msg/shm counters, mqueue counts and limits, sysctl headers, mount references, owning user namespace, ucounts, and `ns_common`.

## Dependencies and integration points
It integrates namespaces, nsproxy, user namespaces, IDR, rhashtable, sysctl, percpu counters, mqueuefs, and SysV IPC implementations.

## Risks and test signals
Risks include reference underflow, mqueue counter drift, sysctl teardown races, limit enforcement errors, and forced shared-memory removal surprises. Tests should cover `CLONE_NEWIPC`, disabled feature stubs, mqueue limit sysctls, namespace teardown with live queues/segments, and checkpoint-restore `next_id`.
