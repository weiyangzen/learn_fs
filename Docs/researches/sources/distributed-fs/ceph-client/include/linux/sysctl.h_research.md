<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysctl.h -->
# sources/distributed-fs/ceph-client/include/linux/sysctl.h

## Purpose

`sysctl.h` declares the kernel `/proc/sys` sysctl table infrastructure and standard proc handlers for text, integer, unsigned, boolean, bitmap, static key, and bounded numeric values. It also preserves warnings about legacy binary sysctl numbering exported through UAPI.

## Important APIs, types, and functions

It defines constant value pointers such as `SYSCTL_ZERO`, `SYSCTL_ONE`, `SYSCTL_INT_MAX`, long equivalents, direction helpers `SYSCTL_USER_TO_KERN()`/`SYSCTL_KERN_TO_USER()`, `proc_handler`, many `proc_do*` conversion handlers, `struct ctl_table_poll`, `DEFINE_CTL_TABLE_POLL`, `struct ctl_table`, `struct ctl_node`, `struct ctl_table_header`, `struct ctl_dir`, `struct ctl_table_set`, and `struct ctl_table_root`. Registration APIs include `register_sysctl()`, `register_sysctl_sz()`, `register_sysctl_init()`, `__register_sysctl_table()`, `unregister_sysctl_table()`, `register_sysctl_mount_point()`, and namespace/set setup/retire helpers, with stubs when sysctl is disabled.

## Control flow

Subsystems define arrays of `ctl_table`, register them at a path, and procfs mirrors leaf entries as files. Reads and writes call the table’s `proc_handler`, which copies between kernel variables and user buffers with optional range/conversion constraints. Pollable entries increment an event counter and wake waiters through `proc_sys_poll_notify()`. Namespaced roots can choose visible sets and ownership/permission behavior.

## State and persistence behavior

Registered table headers persist until unregistered. Header fields track use counts, registration counts, RCU lifetime, parent directory, inodes, and table type. Poll state stores an atomic event counter and waitqueue. Sysctl data pointers refer to caller-owned variables.

## Dependencies and integration points

It depends on lists, RCU, waitqueues, rbtrees, uid/gid types, and UAPI sysctl constants. It integrates with procfs, kernel parameter parsing, namespaces, permissions, and subsystem tunables across VM, networking, kernel, fs, and drivers.

## Risks and test signals

Risks include changing exported numeric IDs, registering transient table memory, bad maxlen/mode/handler combinations, min/max pointer type mismatches, unregister races with proc inodes, namespace visibility bugs, and stubs hiding missing sysctl support. Tests should cover handler conversion/range checks, read/write direction, poll notifications, registration/unregistration under concurrent access, mount points, namespace permissions, boot-time init tables, and CONFIG_SYSCTL disabled builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysctl.h -->
