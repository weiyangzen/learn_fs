# sources/distributed-fs/ceph-client/fs/bpf_fs_kfuncs.c

## Purpose
Registers filesystem-related BPF kfuncs for BPF LSM programs. The file exposes controlled helpers for executable-file references, path resolution, extended attribute reads/writes/removals, cgroup xattr reads, and hook-specific lock-state discovery.

## Important APIs, Types, And Functions
Public kfuncs include `bpf_get_task_exe_file()` with acquire semantics, `bpf_put_file()` with release semantics, `bpf_path_d_path()`, `bpf_get_dentry_xattr()`, `bpf_get_file_xattr()`, `bpf_set_dentry_xattr()`, `bpf_remove_dentry_xattr()`, and, under `CONFIG_CGROUPS`, `bpf_cgroup_read_xattr()`. Internal locked variants `bpf_set_dentry_xattr_locked()` and `bpf_remove_dentry_xattr_locked()` are intended for LSM hooks where `d_inode` is already locked.

Permission helpers `bpf_xattr_read_permission()` and `bpf_xattr_write_permission()` constrain xattr namespaces. Registration uses `BTF_KFUNCS_START(bpf_fs_kfunc_set_ids)`, per-function flags such as `KF_ACQUIRE`, `KF_RELEASE`, `KF_RET_NULL`, and `KF_SLEEPABLE`, and `register_btf_kfunc_id_set()` in `bpf_fs_kfuncs_init()`. `bpf_fs_kfuncs_filter()` limits the set to BPF LSM programs. `bpf_lsm_has_d_inode_locked()` consults a BTF id set of hooks that already hold inode locks.

## Control Flow
The executable-file kfunc directly calls `get_task_exe_file()` and requires BPF verifier-enforced release through `bpf_put_file()`. Path resolution calls `d_path()`, then moves the returned pathname down to the beginning of the supplied BPF buffer. Xattr reads validate a dynptr buffer, require `user.` or `security.bpf.` prefixes, check read permission with `inode_permission()`, and call `__vfs_getxattr()`.

Xattr writes/removals are stricter: only `security.bpf.` names are allowed and write permission is checked. Unlocked variants lock `d_inode`, call the locked helper, and unlock. Locked helpers call `__vfs_setxattr()` or `__vfs_removexattr()`, then notify with `fsnotify_xattr()` on success. They intentionally avoid calling LSM post-setxattr/post-removexattr hooks because these changes are initiated from BPF LSM and recursive callbacks could deadlock. Cgroup xattr reads only allow `user.` names and call `kernfs_xattr_get()` on the cgroup kernfs node.

## State And Persistence
`bpf_get_task_exe_file()` acquires a live `struct file` reference that must be released. Xattr set/remove kfuncs persist metadata changes to the target filesystem object and emit fsnotify notifications. Reads and path resolution do not persist data. Registration creates a kernel-global BTF kfunc id set available after late init.

## Dependencies And Integration Points
The file integrates BPF verifier kfunc metadata, BPF LSM program type filtering, VFS path and xattr APIs, dynptr internals, inode permission checks, fsnotify, cgroup kernfs xattrs, and BTF IDs for LSM hook names. It depends on BPF verifier enforcement for reference lifetime and sleepable-kfunc placement.

## Risks
The security boundary is intentionally narrow. Prefix checks must remain correct because broader xattr access would let BPF LSM programs read or mutate unrelated metadata. Lock selection is subtle: calling an unlocked helper from an already-locked hook can deadlock, while calling a locked helper without the lock can race. Avoiding post-xattr LSM callbacks prevents recursion but also means observers relying only on those hooks will not see these BPF-originated changes. Dynptr size/data validation is required to avoid invalid kernel memory access.

## Test Signals
Verifier tests should confirm acquire/release pairing, LSM-only access, sleepable restrictions, and locked-vs-unlocked helper availability by hook. Runtime tests should cover reading `user.` and `security.bpf.` xattrs, rejecting other prefixes, setting/removing `security.bpf.` xattrs with fsnotify visibility, permission failures, zero-size path buffers, path resolution truncation behavior, cgroup `user.` xattr reads, and recursion/deadlock resistance in LSM hooks.
