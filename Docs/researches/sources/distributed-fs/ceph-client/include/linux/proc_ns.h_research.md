# sources/distributed-fs/ceph-client/include/linux/proc_ns.h

Purpose: defines procfs namespace operation descriptors and namespace inode allocation helpers used for `/proc/<pid>/ns/*` and nsfs integration.

Important APIs and types: `struct proc_ns_operations` names a namespace type and provides `get`, `put`, `install`, `owner`, and `get_parent` callbacks. Global operation tables are declared for net, UTS, IPC, PID, user, mount, cgroup, and time namespaces, including child namespace variants. Initial inode numbers map to UAPI nsfs constants, and `proc_alloc_inum()` / `proc_free_inum()` manage proc namespace inode numbers when procfs is enabled. `get_proc_ns(inode)` returns the stored `ns_common`.

Control flow: proc namespace files use the operation table to acquire a task's namespace, expose it through nsfs, install a namespace during setns-like operations, and release references. Inode allocation produces stable-looking namespace identifiers for proc/ns entries; disabled procfs returns a harmless inode value.

State and persistence: this header exposes namespace references stored in inode private data. Namespace objects are refcounted runtime state and persist only while referenced by tasks, files, mounts, or nsfs handles.

Dependencies and integration points: depends on `linux/nsfs.h`, UAPI namespace inode constants, namespace implementations, user namespaces, procfs, and setns/open-related-namespace paths.

Risks and test signals: risks include reference leaks in `get`/`put`, wrong owner namespace checks, stale `inode->i_private`, and inode number allocation collisions. Test `/proc/<pid>/ns` open/readlink/setns flows, namespace teardown with open fds, user namespace permission checks, and builds without procfs.
