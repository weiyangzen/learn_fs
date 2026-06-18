# File Research: sources/cow-pools/bcachefs-tools/fs/vfs/ioctl.c

Purpose: implements file-level bcachefs ioctls and compatibility ioctl dispatch.

Key behavior:
- Provides compatibility wrappers for path create/remove helper APIs before Linux 6.18.
- Supports reinheriting inode attributes from a parent directory.
- Implements get/set generation, filesystem label get/set, and `FS_IOC_GOINGDOWN`.
- Implements subvolume create/destroy, including snapshot creation, permission/security checks, idmap checks, VFS path locking, create-lock synchronization, and fsnotify events.
- Implements subvolume listing and subvolume-to-path queries with permission-aware traversal.
- Implements snapshot tree query, including snapshot accounting readout.
- Supports reflink option propagation and setting `REFLINK_P_MAY_UPDATE_OPTIONS`.
- Implements raw direct pread with optional poison-check bypass and structured error reporting.
- Implements unpoisoning extents, including reflink target extents.
- Dispatches known commands in `bch2_fs_file_ioctl()`, forwarding unknowns to generic `bch2_fs_ioctl()`.

Important interactions:
- Calls into `fs.c` create/unlink/VFS inode lookup helpers, snapshot/subvolume modules, btree transaction iteration, direct I/O read path, and reflink format helpers.
- Security-sensitive paths use capability checks, owner checks, VFS permissions, LSM hooks, mount write references, and idmapped mount helpers.
- `CONFIG_COMPAT` maps 32-bit flag/version ioctls to native commands where possible.
