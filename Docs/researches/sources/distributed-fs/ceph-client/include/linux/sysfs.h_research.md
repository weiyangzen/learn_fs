<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysfs.h -->
# sources/distributed-fs/ceph-client/include/linux/sysfs.h

## Purpose
defines the kernel-facing sysfs attribute model layered over kernfs: text attributes, binary attributes, attribute groups, visibility callbacks, permission helpers, link/group/file creation APIs, ownership-changing APIs, and no-op stubs for builds without CONFIG_SYSFS.

## Important APIs, Types, and Functions
The file is 825 lines and exports these visible symbol families: types/enums `kobject`, `module`, `bin_attribute`, `kobj_ns_type`, `attribute`, `attribute_group`, `file`, `vm_area_struct`, `address_space`, `sysfs_ops`, `kernfs_node`; macros/constants `_SYSFS_H_`, `SYSFS_PREALLOC`, `SYSFS_GROUP_INVISIBLE`, `__ATTR_NULL`, `__ATTR_IGNORE_LOCKDEP`, `__BIN_ATTR_NULL`; function-like macros `sysfs_attr_init`, `__SYSFS_FUNCTION_ALTERNATIVE`, `DEFINE_SYSFS_GROUP_VISIBLE`, `DEFINE_SIMPLE_SYSFS_GROUP_VISIBLE`, `DEFINE_SYSFS_BIN_GROUP_VISIBLE`, `DEFINE_SIMPLE_SYSFS_BIN_GROUP_VISIBLE`, `SYSFS_GROUP_VISIBLE`, `__ATTR`, `__ATTR_PREALLOC`, `__ATTR_RO_MODE`, `__ATTR_RO`, `__ATTR_RW_MODE`, `__ATTR_WO`, `__ATTR_RW`, and 21 more; inline helpers `sysfs_enable_ns`, `sysfs_create_dir_ns`, `sysfs_remove_dir`, `sysfs_rename_dir_ns`, `sysfs_move_dir_ns`, `sysfs_create_mount_point`, `sysfs_remove_mount_point`, `sysfs_create_file_ns`, `sysfs_create_files`, `sysfs_chmod_file`, `sysfs_break_active_protection`, `sysfs_unbreak_active_protection`, `sysfs_remove_file_ns`, `sysfs_remove_file_self`, and 36 more; external prototypes `umode_t`, `DEFINE_SYSFS_GROUP_VISIBLE`, `DEFINE_SIMPLE_SYSFS_GROUP_VISIBLE`, `sysfs_create_dir_ns`, `sysfs_remove_dir`, `sysfs_rename_dir_ns`, `sysfs_move_dir_ns`, `sysfs_create_mount_point`, `sysfs_remove_mount_point`, `sysfs_create_file_ns`, `sysfs_create_files`, `sysfs_chmod_file`, `sysfs_unbreak_active_protection`, `sysfs_remove_file_ns`, and 34 more.

## Control Flow
Drivers declare `struct attribute`, `struct bin_attribute`, or `struct attribute_group` objects, usually through the `__ATTR*`, `ATTRIBUTE_GROUPS`, and `BIN_ATTR*` macros, then attach them to a `kobject` with create/group/link helpers. Show/store/read/write callbacks are invoked later by VFS/sysfs paths through `sysfs_ops` or binary attribute callbacks. Removal APIs tear down nodes, and `sysfs_notify*` wakes pollers when values change.

## State and Persistence Behavior
The header itself stores no state, but its objects become kernfs nodes with lifetime bound to the owning kobject and module/static storage of callback tables. Attribute visibility and ownership are evaluated at creation/update time; `sysfs_break_active_protection()` temporarily alters active protection for self-removal paths.

## Dependencies and Integration Points
It depends on kobject, kernfs, namespace, stat, lockdep, and uid/gid types. It is a central integration point for device model, driver-core attributes, module parameters exposed through kobjects, and any subsystem exporting kernel state through `/sys`. Direct includes are `linux/kernfs.h`, `linux/compiler.h`, `linux/errno.h`, `linux/list.h`, `linux/lockdep.h`, `linux/kobject_ns.h`, `linux/stat.h`, `linux/atomic.h`.

## Risks and Edge Cases
Common failure modes are unsafe permissions, non-terminated attribute arrays, callbacks returning more than PAGE_SIZE, lifetime bugs when dynamic attributes are removed while callbacks run, and forgetting that CONFIG_SYSFS stubs return success while exporting nothing. `VERIFY_OCTAL_PERMISSIONS()` intentionally rejects world-writable files and non-octal-like modes.

## Test Signals
Build with CONFIG_SYSFS on and off, enable lockdep for dynamically allocated attributes, exercise create/update/remove/link/group paths under kobject teardown, validate permissions with sysfs selftests, and run poll/notify plus binary read/write/mmap coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/sysfs.h -->
