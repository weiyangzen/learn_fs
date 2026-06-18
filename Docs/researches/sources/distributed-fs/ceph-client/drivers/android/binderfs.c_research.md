# sources/distributed-fs/ceph-client/drivers/android/binderfs.c

## Purpose
`binderfs.c` implements the Binder filesystem. It provides mount-time Binder device namespaces, a `binder-control` device for dynamic Binder device creation, feature files, optional Binder log files, mount options, minor allocation, and filesystem registration.

## Important APIs, Types, And Functions
Important functions include `init_binderfs`, `binderfs_init_fs_context`, `binderfs_fill_super`, `binderfs_binder_ctl_create`, `binder_ctl_ioctl`, `binderfs_binder_device_create`, `binderfs_evict_inode`, `binderfs_create_file`, `binderfs_create_dir`, `init_binder_features`, `init_binder_logs`, `binderfs_show_options`, `binderfs_fs_context_parse_param`, `binderfs_fs_context_reconfigure`, `binderfs_rename`, `binderfs_unlink`, and `binderfs_kill_super`. Static state includes `binderfs_dev`, `binderfs_minors_mutex`, `binderfs_minors`, mount parameter tables, and feature booleans.

## Control Flow
`init_binderfs` validates default device names, allocates a character-device major, and registers the filesystem. Mounting allocates fs context options, parses `max` and `stats=global`, then `binderfs_fill_super` sets superblock flags, creates root inode, creates `binder-control`, creates default devices from `binder_devices_param`, creates feature files, and optionally creates binder log files. Userspace calls `BINDER_CTL_ADD` on `binder-control` to copy in a `binderfs_device`, allocate a global minor, create a character-device inode/dentry, attach a `binder_device`, copy major/minor back, and add it to Binder's global device list. Eviction frees minors and device state.

## State And Persistence
Per-mount state lives in `struct binderfs_info`: ipc namespace, control dentry, root uid/gid, mount options, device count, and proc log directory. Global minor allocation persists in the IDA. Each device stores `struct binder_device` in inode private data. Feature files expose static booleans. Mount options persist for the superblock, and stats mode cannot be changed on remount.

## Dependencies
The file depends on VFS/simplefs helpers, fs parser, IDA, ipc/user namespaces, char device registration, Binder UAPI, and `binder_internal.h`. It calls `binder_add_device`, `binder_remove_device`, and uses `binder_fops` from Binder core.

## Integration Points
Android userspace mounts binderfs to get Binder device nodes. Binder core opens device nodes created here and uses their `binder_context`. Binder debugfs entries can be mirrored under `binder_logs` when global stats are requested. Feature files advertise support for oneway spam detection, extended errors, freeze notifications, and transaction reports.

## Risks
Minor accounting and device_count must stay balanced across create, ioctl copy failure, dentry creation failure, and inode eviction. User namespace mounting depends on careful device-node restrictions. Default device-name parsing must reject names longer than `BINDERFS_MAX_NAME`. Feature-file creation and inode eviction deserve build, mount, and lockdep coverage because small mistakes there can hide advertised features or leak minors.

## Test Signals
Mount binderfs in initial and non-initial user namespaces, use `BINDER_CTL_ADD`, verify max-device limits and minor reserve behavior, rename/unlink normal devices while protecting `binder-control`, read feature files, mount with and without `stats=global`, exercise default device creation from `binder_devices_param`, unmount under open devices, and run build/lockdep checks for the duplicate-lock anomaly.
