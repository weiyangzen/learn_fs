# sources/distributed-fs/ceph-client/init/do_mounts.c

## Purpose
`do_mounts.c` implements early root filesystem selection and mounting. It parses root-related boot parameters, waits for devices, loads initrd when configured, mounts NFS/CIFS/generic/block/nodev roots, mounts devtmpfs, pivots into the new rootfs, and selects ramfs versus tmpfs rootfs backing.

## Important APIs, Types, and Functions
Important state includes `root_mountflags`, `saved_root_name`, `root_wait`, `root_mount_data`, `root_fs_names`, `root_delay`, and `ROOT_DEV`. Key functions include boot parsers for `ro`, `rw`, `root=`, `rootwait`, `rootwait=`, `rootflags=`, `rootfstype=`, and `rootdelay=`, plus `split_fs_names()`, `do_mount_root()`, `mount_root_generic()`, `mount_nfs_root()`, `mount_cifs_root()`, `mount_nodev_root()`, `mount_block_root()`, `mount_root()`, `wait_for_root()`, `parse_root_device()`, `prepare_namespace()`, `rootfs_init_fs_context()`, and `init_rootfs()`.

## Control Flow
`prepare_namespace()` applies root delay, waits for probe completion, runs RAID setup, parses `root=`, calls `initrd_load()`, optionally waits for root device discovery, mounts the selected root type, mounts devtmpfs, then pivots and unmounts old rootfs. Generic mounting tries requested or known block filesystems, retries read-only after writable failures, and panics with partition/filesystem diagnostics if no mount succeeds.

## State and Persistence Behavior
Boot parameter state lives in `__initdata` until init memory is freed. Successful mount updates `ROOT_DEV`, current working directory, root mount state, and rootfs backing choice. No durable storage is written except filesystem mount effects.

## Dependencies and Integration Points
It depends on init syscalls, VFS mount APIs, block device lookup, async/device probe completion, devtmpfs, RAID autodetect, NFS/CIFS root helpers, initrd loader, filesystem type registry, and rootfs ramfs/tmpfs implementations.

## Risks and Test Signals
Risks include invalid `root=` disabling `rootwait`, indefinite waits, root filesystem list handling with empty names, nodev root misclassification, panic diagnostics masking the original error, initrd interactions with `ROOT_DEV`, and pivot/unmount failures. Test signals include boots with block root, `rootfstype` lists, NFS/CIFS root retries, `rootwait` timeout, `rootdelay`, initrd present/absent, tmpfs rootfs selection, and missing-root panic output.
