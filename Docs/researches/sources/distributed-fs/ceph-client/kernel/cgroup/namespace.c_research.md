# sources/distributed-fs/ceph-client/kernel/cgroup/namespace.c

## Purpose

`namespace.c` implements cgroup namespace creation, installation, lookup, release, and proc namespace operations. Cgroup namespaces virtualize cgroup paths relative to a namespace root css set.

## Important APIs, Types, and Functions

Key functions are `copy_cgroup_ns()`, `free_cgroup_ns()`, `cgroupns_install()`, `cgroupns_get()`, `cgroupns_put()`, and `cgroupns_owner()`. The file registers `cgroupns_operations` with procfs namespace support. It uses `struct cgroup_namespace`, `struct ucounts`, `struct css_set`, `struct nsproxy`, and `struct ns_common`.

## Control Flow and State

Without `CLONE_NEWCGROUP`, `copy_cgroup_ns()` simply references the old namespace. With `CLONE_NEWCGROUP`, it requires `CAP_SYS_ADMIN` in the relevant user namespace, charges the per-user namespace count, pins the current task's css set under `css_set_lock`, allocates and initializes a namespace object, stores the user namespace, ucounts, and root css set, and adds it to the namespace tree. Release removes the namespace from the tree, drops the css set, ucounts, and user namespace references, calls `ns_common_free()`, and defers freeing with RCU.

## Dependencies and Integration Points

It depends on user namespace capabilities and ucounts, cgroup css-set lifetime rules, task `nsproxy`, proc namespace operations, namespace tree tracking, and RCU-safe namespace traversal.

## Risks and Edge Cases

Creation cannot take `cgroup_mutex`, so it relies on `css_set_lock` for current css-set pinning. Permission checks during `setns` require capability in both the caller's user namespace and the target cgroup namespace owner. Release order matters because namespace tree traversal can be concurrent and requires an RCU grace period.

## Test Signals

Tests should cover clone with and without `CLONE_NEWCGROUP`, ucount exhaustion, permission failures, `setns()` into another cgroup namespace, proc namespace get/put, namespace tree visibility, and release while namespace traversal is active.
