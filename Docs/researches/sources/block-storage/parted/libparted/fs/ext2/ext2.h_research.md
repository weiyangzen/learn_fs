# File Research: sources/block-storage/parted/libparted/fs/ext2/ext2.h

Private ext2 support header. It includes libparted headers, `sys/types.h`, integer types, and either the system ext2 header if configured or the local `ext2_fs.h`.

It defines `blk_t` and `struct ext2_fs`, a richer state object inherited from older resize code. The structure carries a device handle, superblock, group descriptor table, buffer cache, metadata dirty state, feature booleans, block/group sizing, relocation pool, debug/safe/verbose options, and journal pointer.

In the current listed implementation, ext2 probing uses only the local superblock definitions through this header. The larger `struct ext2_fs` is mostly relevant to historical or external resize components not present in this file group.
