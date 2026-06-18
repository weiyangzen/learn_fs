# sources/distributed-fs/ceph-client/include/linux/ext2_fs.h

Purpose: small ext2 on-disk constants and image-size helper.

Important APIs/types/functions: `EXT2_NAME_LEN`, `EXT2_LINK_MAX`, superblock offsets `EXT2_SB_MAGIC_OFFSET`, `EXT2_SB_BLOCKS_OFFSET`, `EXT2_SB_BSIZE_OFFSET`, and `ext2_image_size()`.

Control flow: `ext2_image_size()` treats the provided buffer as an ext2 superblock, verifies magic at offset `0x38`, then computes total bytes from block count shifted by block-size log.

State/persistence: reads persistent ext2 superblock fields. No runtime state.

Dependencies/integration: ext2/ext-family image probing, `linux/magic.h`, endian conversion helpers.

Risks/test signals: risks are unaligned superblock buffer access, trusting too-small buffers, overflow/invalid block-size values, and confusing ext2-compatible metadata with other filesystems. Test valid ext2 images, bad magic, large block counts, malformed block-size log, and unaligned buffers on strict architectures.
