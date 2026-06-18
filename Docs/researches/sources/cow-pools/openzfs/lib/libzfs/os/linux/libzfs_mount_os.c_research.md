# File Research: sources/cow-pools/openzfs/lib/libzfs/os/linux/libzfs_mount_os.c

Linux libzfs mount adapter. It maps ZFS mount options to Linux `MS_*` flags, performs direct `mount(2)` by default, supports an optional `/bin/mount` helper path, injects SELinux mount contexts, and updates namespace-sensitive flags with `mount_setattr(2)` when available.

Key interfaces:
- `zfs_parse_mount_options()` tokenizes comma-separated options, respecting quoted commas, and maps known names through `option_map`.
- `zfs_adjust_mount_options()` adds SELinux `context`, `fscontext`, `defcontext`, `rootcontext` options and a `mntpoint=` hint.
- `do_mount()` uses direct `mount(src, mntpt, "zfs", flags, opts)` unless `ZFS_MOUNT_HELPER` is set.
- `do_unmount()` uses `umount2()` unless helper mode is enabled.
- `zfs_mount_setattr()` selectively updates readonly/exec/setuid/devices/atime/relatime mount attributes for mounted datasets.

Legacy datasets require iterating `/proc/mounts` because they may be mounted in multiple locations. If `mount_setattr()` is missing and the dataset is not legacy, the code falls back to full remount.
