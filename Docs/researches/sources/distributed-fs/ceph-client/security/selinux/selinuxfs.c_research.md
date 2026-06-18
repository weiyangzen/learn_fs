<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/selinuxfs.c -->
# sources/distributed-fs/ceph-client/security/selinux/selinuxfs.c

## Purpose
Implements the `selinuxfs` pseudo filesystem, the main kernel/userspace control and query surface for SELinux. It exposes policy load/read, enforcing mode, context validation, access/create/relabel/member/validatetrans queries, booleans, status mmap, policy version, MLS status, AVC stats/tuning, initial SID contexts, class/permission indexes, policy capabilities, and the `null` character device.

## Important APIs, Types, and Functions
External entry is `init_sel_fs()` and global `selinux_null`. Filesystem construction uses `sel_fill_super()`, `sel_get_tree()`, `sel_init_fs_context()`, and `sel_kill_sb()`. Policy-load flow is `sel_write_load()` plus `sel_make_policy_nodes()`, `sel_make_bools()`, and `sel_make_classes()`. Query handlers include `sel_write_access()`, `sel_write_create()`, `sel_write_relabel()`, `sel_write_member()`, `sel_write_context()`, and `sel_write_validatetrans()`. State is tracked by `struct selinux_fs_info`; policy reads use `struct policy_load_memory`.

## Control Flow
Mount creation allocates fs-private state, fills root files, creates booleans/class/policycap directories, mounts a kernel instance, and looks up `selinuxfs/null`. Policy writes require `SECURITY__LOAD_POLICY`, copy policy bytes from userspace, call `security_load_policy()`, build replacement boolean/class trees under a hidden `.swapover` directory, atomically exchange dentries, then commit policy. Transaction files parse context strings from a simple transaction buffer and write results back into the same buffer. Boolean writes stage pending values; `commit_pending_bools` applies them through `security_set_bools()`.

## State and Persistence
Persistent filesystem state includes pending boolean names/values, boolean/class dentries, last allocated inode counters, and superblock private data. Global SELinux state is changed through enforcing writes, policy commits, status-page updates, AVC reset, netlink notifications, IMA measurement, and LSM policy-change notifications. Policy read mmap pins a vmalloc snapshot for each open file.

## Dependencies and Integration Points
Depends on VFS/simplefs helpers, fs_context, dentry exchange, SELinux security server, AVC, IMA measurement, audit, generated class/permission metadata, initial SID definitions, mmap/page fault helpers, and sysfs mount point creation. It is the user-visible integration point used by policy loaders, libselinux, setenforce, boolean tools, and policy inspection utilities.

## Risks
Policy-load dentry swapover must keep old and new boolean/class trees consistent on all failure paths. Many write handlers parse whitespace-delimited strings into `size + 1` buffers; overlong contexts are checked against `SIMPLE_TRANSACTION_LIMIT`. Enforcing changes are compiled out except in development builds. Runtime disable and checkreqprot writes are deprecated no-ops but still return success. Policy mmap must remain read-only despite `mprotect()`.

## Test Signals
Test mounting, kernel `null` lookup, policy load success/failure with boolean/class tree replacement, concurrent policy reads during reload, enforcing toggles and notifications, status mmap sequence updates, transaction query outputs, boolean staging/commit, class/perm file indexes, policycap files, AVC stats/tuning, deprecated disable/checkreqprot writes, and unmount cleanup with leak detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/selinuxfs.c -->
