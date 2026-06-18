# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/setns-sysvipc.c

Purpose: verifies `/proc/sysvipc` follows the current IPC namespace after `setns()` despite a cached `/proc/sysvipc/shm` dentry.

Important APIs and functions: uses `unshare(CLONE_NEWIPC)`, `shmget` as a namespace distinguisher, `fork`, pipe sync, `/proc/$pid/ns/ipc`, `setns`, and exact header comparison for `/proc/sysvipc/shm`.

Control flow: parent enters IPC namespace and creates shared memory. Child enters another IPC namespace and pauses. Parent pins old `/proc/sysvipc/shm`, switches to child IPC namespace, kills child, and requires the shm file to contain only the architecture-dependent header.

State and persistence: transient IPC namespace and one SysV shm segment in the original namespace. `atexit` kills the child if still present.

Dependencies and integration: requires IPC namespaces, SysV shm, proc sysvipc support, and setns permission.

Risks and test signals: the created shm segment is not explicitly removed, relying on namespace/process lifecycle. Failure indicates stale dcache namespace lookup for sysvipc proc entries.
