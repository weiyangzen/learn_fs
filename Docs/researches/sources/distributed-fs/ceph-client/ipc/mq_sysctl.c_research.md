# sources/distributed-fs/ceph-client/ipc/mq_sysctl.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/mq_sysctl.c` registers per-IPC-namespace sysctls for POSIX message queue defaults and limits under `fs/mqueue`. The source was read as a complete 167-line file.

## Important APIs, Types, and Functions

The sysctl table exposes `queues_max`, `msg_max`, `msgsize_max`, `msg_default`, and `msgsize_default`. `setup_mq_sysctls()` duplicates and registers the table for a namespace. `retire_mq_sysctls()` unregisters it. Permission helpers `mq_set_ownership()` and `mq_permissions()` map ownership and access checks through the namespace's user namespace.

## Control Flow

Setup initializes `ns->mq_set`, clones `mq_sysctls`, rewrites each table entry from `init_ipc_ns` fields to the target namespace fields, and registers under `fs/mqueue`. On failure it frees the clone and retires the sysctl set. Teardown unregisters, retires the set, and frees the cloned table.

## State and Persistence Behavior

Values are stored in `ipc_namespace` fields and persist for the namespace lifetime. They control future POSIX mqueue creation, default queue attributes, and non-privileged limits; existing queues keep their inode-local attributes.

## Dependencies and Integration Points

This file integrates `mqueue.c`, IPC namespaces, sysctl, user namespaces, and capability policy. The min/max handlers enforce hard message-count and message-size bounds through `MIN_MSGMAX`, `HARD_MSGMAX`, `MIN_MSGSIZEMAX`, and `HARD_MSGSIZEMAX`.

## Risks and Edge Cases

As with SysV IPC sysctls, pointer rewriting must be correct for namespace isolation. Limit writes can affect resource-exhaustion behavior for later queue creation. Permission handling must reflect root/group in the namespace rather than global root assumptions.

## Test Signals

Tests should verify per-namespace isolation of `/proc/sys/fs/mqueue/*`, min/max rejection for message counts and sizes, creation behavior before and after default changes, and permission behavior from nested user namespaces.
