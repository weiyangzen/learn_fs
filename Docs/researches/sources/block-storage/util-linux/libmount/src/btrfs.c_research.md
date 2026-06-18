# File Research: sources/block-storage/util-linux/libmount/src/btrfs.c

Btrfs helper for discovering a mounted volume's default subvolume ID.

Key responsibilities:
- Provides missing kernel-header definitions for older `linux/btrfs.h`.
- Opens a Btrfs mount path and issues `BTRFS_IOC_TREE_SEARCH`.
- Searches the root tree directory object for the `default` dir item.
- Returns the default subvolume object ID or `UINT64_MAX` on no default/error.

Important behavior:
- Uses `opendir()`/`dirfd()` so the ioctl is issued on the mounted directory.
- Limits search to root tree object/directory and one item.
- Interprets Btrfs little-endian disk key fields through helper accessors.
- Logs failures via Btrfs debug messages and preserves errno from failing syscalls/ioctls.

Dependencies:
- Linux Btrfs ioctl ABI, `mountP.h`, `bitops.h`, and endian conversion helpers.

Notable risks:
- Relies on kernel Btrfs search result layout and local fallback structure definitions.
- Compares `"default"` using `strncmp("default", name, name_len)`, so malformed shorter prefixes could be surprising if returned by the kernel.
