# sources/distributed-fs/ceph-client/fs/ext2/ioctl.c

Purpose: Implements ext2 file attribute get/set support and legacy ioctls for inode generation and reservation-window size.

Important APIs/types/functions: Public functions are `ext2_fileattr_get`, `ext2_fileattr_set`, `ext2_ioctl`, and `ext2_compat_ioctl`. Commands include `EXT2_IOC_GETVERSION`, `EXT2_IOC_SETVERSION`, `EXT2_IOC_GETRSVSZ`, `EXT2_IOC_SETRSVSZ`, and 32-bit aliases for get/set version.

Control flow: Fileattr get returns user-visible ext2 flags through `fileattr_fill_flags`. Fileattr set rejects fsx attributes and quota files, updates user-modifiable ext2 flags, reapplies VFS inode flags, updates ctime, and dirties the inode. `GETVERSION` returns `i_generation`; `SETVERSION` requires ownership/capability and a writable mount, copies a user value, updates ctime and generation under inode lock, and dirties the inode. Reservation-size ioctls operate only on regular files when reservation mount option is enabled; set clamps to `EXT2_MAX_RESERVE_BLOCKS` and lazily initializes allocation info under `truncate_mutex`.

State and persistence behavior: Attribute and generation changes persist through dirty inode writeback. Reservation size is in-memory allocation policy state, not an on-disk field; it changes future block allocation behavior for the open inode.

Dependencies and integration points: Used by file and directory file operations. Depends on VFS permission helpers, mount write guards, user copy helpers, fileattr API, and allocator reservation structures from `balloc.c`/`ext2.h`.

Risks: Reservation-size ioctl has a documented locking question but uses `truncate_mutex`, matching block allocation synchronization. Quota files must remain protected from flag changes. Compat ioctl only translates version commands; unsupported compat commands return `-ENOIOCTLCMD`.

Test signals: chattr/lsattr behavior; setting immutable/append/nodump/noatime flags; generation get/set permission and read-only mount failures; reservation ioctl on regular/non-regular files with reservation on/off; compat 32-bit ioctl tests.
