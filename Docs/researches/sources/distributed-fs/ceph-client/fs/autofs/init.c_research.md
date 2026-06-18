# sources/distributed-fs/ceph-client/fs/autofs/init.c

Purpose: Registers and unregisters the autofs filesystem type and its misc-device control interface.

Important APIs and functions: `autofs_fs_type` names the filesystem `autofs`, points mount setup at `autofs_init_fs_context`, exposes `autofs_param_specs`, and tears down superblocks with `autofs_kill_sb`. `init_autofs_fs()` initializes the ioctl misc device then registers the filesystem. `exit_autofs_fs()` deregisters both. Module aliases expose filesystem and module names.

Control flow: Module init calls `autofs_dev_ioctl_init()` first, then `register_filesystem()`. If filesystem registration fails, the misc device is cleaned up immediately. Module exit runs the reverse order: deregister misc device then unregister filesystem.

State and persistence: Runtime global state is the registered filesystem type and misc device registration. Mount-specific state lives in other autofs files.

Dependencies and integration points: Depends on module/init infrastructure, VFS filesystem registration, autofs fs-context parsing, superblock kill path, and device ioctl setup in `dev-ioctl.c`.

Risks: Init failure handling must not leave `/dev/autofs` registered without filesystem support. Exit ordering prevents new device ioctls before filesystem unregister completes.

Test signals: Built-in and module load/unload, registration failure injection, alias lookup by filesystem name, mount parameter parsing through `autofs_param_specs`, and clean misc-device deregistration.
