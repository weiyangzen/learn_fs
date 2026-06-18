# sources/distributed-fs/ceph-client/fs/ubifs/ioctl.c

## Purpose

`ioctl.c` implements UBIFS file attribute handling and forwards fscrypt ioctls. It provides EXT2-compatible visible flags for compression, synchronous writes, append-only, immutable, directory sync, and encryption status while translating them to UBIFS private inode flags and VFS inode flags.

## Important APIs, Types, And Functions

`ubifs_set_inode_flags()` propagates `struct ubifs_inode::flags` to `inode->i_flags`. `ubifs_fileattr_get()` and `ubifs_fileattr_set()` are the modern fileattr handlers. `ubifs_ioctl()` handles encryption-policy/key ioctls, and `ubifs_compat_ioctl()` maps compat pointers for the same supported fscrypt commands. Internal converters `ioctl2ubifs()` and `ubifs2ioctl()` map `FS_*_FL` values to `UBIFS_*_FL` values and back. `setflags()` budgets and persists changed inode flags.

## Control Flow

Getting attributes rejects special dentries with `-ENOTTY`, converts stored UBIFS flags to ioctl flags, and fills `struct file_kattr`. Setting attributes rejects special dentries, unsupported fsx-style attributes, and unknown flags; masks the request to settable flags; removes `FS_DIRSYNC_FL` for non-directories; then calls `setflags()`.

`setflags()` reserves inode-dirty budget, takes `ui->ui_mutex`, replaces only UBIFS flags represented by the settable ioctl mask, updates VFS flags, updates ctime, marks the inode dirty synchronously, and unlocks. If the inode was already dirty, it releases the newly reserved budget because a previous dirty budget covers persistence. If the resulting inode is synchronous, it forces `write_inode_now()`.

`ubifs_ioctl()` is intentionally narrow: encryption policy setup first calls `ubifs_enable_encryption(c)`, then delegates to fscrypt. All other supported encryption ioctls are direct fscrypt forwards. Unsupported commands return `-ENOTTY`; compat unsupported commands return `-ENOIOCTLCMD`.

## State And Persistence Behavior

Persistent state is `ubifs_inode(inode)->flags`, plus ctime and dirty inode state. Attribute updates become durable through normal UBIFS inode writeback or immediate `write_inode_now()` for synchronous inodes. Encryption status is gettable through `FS_ENCRYPT_FL` but not settable through generic file attributes; actual encryption policy and key state are controlled by fscrypt ioctls.

## Dependencies And Integration Points

The file depends on VFS inode flags, Linux `fileattr` helpers, mount/idmap interfaces, fscrypt ioctls, UBIFS budgeting (`ubifs_budget_space()`, `ubifs_release_budget()`), UBIFS inode locking, and inode writeback. It is the bridge between userspace flag APIs and UBIFS journaled inode persistence.

## Risks And Edge Cases

The flag masks must remain consistent with the conversion functions. Allowing `FS_ENCRYPT_FL` to be set via fileattr would be wrong, so it is gettable but excluded from `UBIFS_SETTABLE_IOCTL_FLAGS`. Budget release depends on whether the inode was already dirty. Non-directory `FS_DIRSYNC_FL` must be stripped. Special files deliberately do not expose these fileattr operations.

## Test Signals

Test coverage should include `chattr`/`lsattr` style get/set for each supported flag, rejection of unknown or fsx fields, special-file `-ENOTTY`, non-directory dirsync masking, synchronous inode immediate writeback, encryption policy/key ioctl forwarding, compat ioctl pointer handling, and budget accounting when the inode is already dirty versus initially clean.
