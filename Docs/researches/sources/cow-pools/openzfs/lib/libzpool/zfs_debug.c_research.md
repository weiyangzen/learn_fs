# File Research: sources/cow-pools/openzfs/lib/libzpool/zfs_debug.c

In-memory debug-message support for libzpool. It keeps a bounded list of debug messages for later dumping.

Key behavior:
- `zfs_dbgmsg_init()` creates the list and mutex.
- `__set_error()` logs `SET_ERROR()` source locations when `ZFS_DEBUG_SET_ERROR` is enabled.
- `__zfs_dbgmsg()` allocates a timestamped variable-length message node and purges old entries past `zfs_dbgmsg_maxsize` defaulting to 4 MiB.
- `zfs_dbgmsg_print()` writes all messages to an fd with start/end tags, using `write()` so it is signal-handler-friendly.

The list is protected by `zfs_dbgmsgs_lock`.
