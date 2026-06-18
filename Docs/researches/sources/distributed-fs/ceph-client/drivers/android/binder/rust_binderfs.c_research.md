# sources/distributed-fs/ceph-client/drivers/android/binder/rust_binderfs.c

Purpose: implements the C binderfs filesystem glue for Rust Binder. It registers the binderfs file system, allocates Binder device nodes, manages minors, creates feature and log files, and bridges Binder device file operations to Rust via `rust_binder_fops`.

Important APIs/types/functions: globals include `binderfs_dev`, `binderfs_minors_mutex`, and `binderfs_minors`. `binderfs_binder_device_create`, `binder_ctl_ioctl`, `binderfs_evict_inode`, mount-option parsers, `binderfs_binder_ctl_create`, `rust_binderfs_create_proc_file`, `rust_binderfs_remove_file`, `init_binder_features`, `init_binder_logs`, `binderfs_fill_super`, `binderfs_init_fs_context`, `binderfs_kill_super`, and `init_rust_binderfs` are central. Feature files expose oneway spam detection, extended error, and freeze notification support.

Control flow: `init_rust_binderfs` validates configured default device names, allocates a char-device major, and registers the filesystem. Mount setup allocates `binderfs_info`, creates the root inode, binder-control device, default configured Binder devices, feature files, and optional global logs. `BINDER_CTL_ADD` copies a device request from userspace and calls `binderfs_binder_device_create`, which reserves a minor, creates a Rust context, allocates a char inode using `rust_binder_fops`, copies major/minor back to userspace, and attaches a persistent dentry. Eviction frees minors and removes Rust contexts.

State and persistence: per-mount `binderfs_info` tracks namespace, mount limits, device count, control dentry, and log directories. Per-device `binder_device` owns its minor and Rust context. Global IDA state tracks minor allocation across mounts.

Dependencies and integration points: includes Linux VFS, fs_context, IDA, ipc namespace, uaccess, and Android binderfs UAPI headers. Calls Rust exports declared in `rust_binder_internal.h` and exposes helper functions declared in `rust_binder.h`.

Risks: minor/device_count accounting must unwind correctly on every error path. `binderfs_binder_ctl_create` appears to allocate a minor but its error path frees only `device` and `inode`, so changes should audit minor cleanup on dentry allocation failure. User namespace behavior depends on controlled device creation and clearing `SB_I_NODEV`. Proc log file names are pid-based and can collide for multiple binder fds in one process.

Test signals: mount with `max` and `stats=global`, remount option validation, default device creation, `BINDER_CTL_ADD`, add failure unwinding, unlink/rename protections for binder-control, per-pid proc log creation/removal, feature file reads, global log reads, unmount cleanup, and minor exhaustion across namespaces.
