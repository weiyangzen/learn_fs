# sources/distributed-fs/ceph-client/fs/hfsplus/ioctl.c

## Purpose
`ioctl.c` implements the HFS+-specific ioctl surface. The only local command is `HFSPLUS_IOC_BLESS`, which updates volume-header Finder metadata so platform firmware can locate the bootable system folder and bootloader.

## Important APIs, types, and functions
The public entry point is `hfsplus_ioctl(struct file *file, unsigned int cmd, unsigned long arg)`. The only helper is `hfsplus_ioctl_bless()`. The command code is declared in `hfsplus_fs.h` as `_IO('h', 0x80)`.

## Control flow
`hfsplus_ioctl()` switches on the command and dispatches `HFSPLUS_IOC_BLESS`; unknown commands return `-ENOTTY`. Blessing first requires `CAP_SYS_ADMIN`. It then locks `sbi->vh_mutex`, updates both primary and backup volume-header `finder_info` fields, and unlocks. `finder_info[0]` and `[5]` receive the parent directory inode, and `finder_info[1]` receives the CNID stored in `dentry->d_fsdata` so hard-link boot files use the hard-link file ID rather than the indirect inode.

## State and persistence behavior
The ioctl mutates in-memory primary and backup volume headers. Persistence is deferred to the normal superblock commit/sync path; this function does not call `hfsplus_mark_mdb_dirty()` or write the volume header itself. The state is protected by `vh_mutex`.

## Dependencies and integration points
It depends on VFS file/dentry/inode state, Linux capability checks, user ioctl dispatch, HFS+ private superblock state, and the volume-header commit logic in `super.c`. It is wired into regular-file operations through `hfsplus_file_operations.unlocked_ioctl`.

## Risks and test signals
Risks include blessing changes not being persisted until a later sync, stale or absent `d_fsdata` for hard links, allowing the ioctl on unsuitable inode types, and missing readonly/error checks in the ioctl itself. Test signals include permission checks, blessing normal files and hard links, fsync/sync/unmount persistence of Finder info, readonly mount behavior, and unknown ioctl return codes.
