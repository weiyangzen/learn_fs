# sources/distributed-fs/ceph-client/include/linux/cgroup_namespace.h

## Purpose

`cgroup_namespace.h` defines cgroup namespace state and APIs for copying, referencing, freeing, and rendering cgroup paths relative to a namespace root.

## Important APIs, Types, and Functions

`struct cgroup_namespace` embeds `ns_common`, `user_namespace`, `ucounts`, and root `css_set`. APIs include `to_cg_ns()`, `free_cgroup_ns()`, `copy_cgroup_ns()`, `cgroup_path_ns()`, `get_cgroup_ns()`, and `put_cgroup_ns()`, with stubs when cgroups are disabled.

## Control Flow

Namespace copy occurs during clone/unshare depending on flags. Reference helpers increment/decrement namespace refs, freeing when the last ref drops. Path rendering converts a cgroup to a namespace-relative string.

## State and Persistence Behavior

Runtime namespace state records the user namespace, ucounts, and css_set root that defines visibility. It persists for the lifetime of namespace references.

## Dependencies and Integration Points

It depends on `ns_common` and integrates with user namespaces, nsproxy, cgroup core, procfs path display, and clone/unshare code.

## Risks and Edge Cases

Reference handling must pair `get_cgroup_ns()` and `put_cgroup_ns()`. Disabled cgroup stubs return the old namespace and do no ref work. Path rendering must enforce namespace boundaries.

## Test Signals

Test clone/unshare cgroup namespace, namespace-relative `/proc/*/cgroup` paths, refcounted teardown, disabled-cgroup builds, and interactions with user namespace lifetime.
