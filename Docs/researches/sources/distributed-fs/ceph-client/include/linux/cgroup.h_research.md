# sources/distributed-fs/ceph-client/include/linux/cgroup.h

## Purpose

`cgroup.h` is the public kernel interface to cgroup core. It declares controller registration/file APIs, task migration and fork/exit hooks, css/cgroup iteration and lookup helpers, refcount accessors, path/name helpers, recursive accounting hooks, freezer hooks, socket cgroup hooks, and disabled-config stubs.

## Important APIs, Types, and Functions

Important APIs include `cgroup_on_dfl()`, css lookup/get helpers, cgroup get-from-path/fd/id helpers, attach/transfer functions, cftype add/remove and file notification helpers, fork/cancel/post/exit/dead/release/free hooks, init functions, task iterators, descendant iteration macros, `cgroup_css()`, css online/dying tests, `task_css*` helpers, `task_get_css()`, ancestry helpers, cgroup path/name helpers, rstat/accounting functions, freezer functions, BPF ref helpers, and `task_get_cgroup1()`.

## Control Flow

Kernel lifecycle flow calls cgroup hooks during fork, post-fork, exit, task release, and free. Controllers iterate tasksets and css descendants under documented locking. Accounting paths charge CPU time through cpuacct and default hierarchy stats. Freezer paths enter/leave frozen state and migrate freezer accounting during task movement.

## State and Persistence Behavior

The header manipulates state declared in `cgroup-defs.h`: css refs, task css_set pointers, default hierarchy membership, kernfs ids, recursive stats, freezer flags, and BPF refs. Disabled `CONFIG_CGROUPS` stubs return neutral behavior.

## Dependencies and Integration Points

It includes scheduler, nodemask, kernfs, namespaces, notifier, user namespace, stats, and cgroup definition/namespace headers. It is used by controllers, scheduler, fork/exit code, procfs, networking, BPF, and namespace code.

## Risks and Edge Cases

Many helpers require `cgroup_mutex`, RCU, or task locks; misuse can produce stale css pointers. Iterators may see offline or not-yet-online csses unless controllers synchronize. `task_get_css()` can return offline css for exiting tasks by design. Disabled-config stubs can hide missing coverage if code assumes real hierarchy behavior.

## Test Signals

Use lockdep-enabled task migration and controller attach tests, css iterator tests under concurrent cgroup deletion, fork/exit hook tests, CPU accounting validation, namespace path tests, freezer migration tests, BPF refcount tests, and builds with `CONFIG_CGROUPS=n`.
