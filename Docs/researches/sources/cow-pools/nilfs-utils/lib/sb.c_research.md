# File Research: sources/cow-pools/nilfs-utils/lib/sb.c

## Scope

Implements NILFS superblock access helpers for user-space tools: reading primary/secondary superblocks, validating magic/size, computing CRC32, and selectively writing mutable superblock fields.

## APIs And Behavior

- `nilfs_sb_check_sum()` temporarily clears `s_sum`, computes the little-endian CRC using `s_crc_seed` over `s_bytes`, then restores the stored checksum.
- `nilfs_sb_is_valid()` validates `NILFS_SUPER_MAGIC`, caps `s_bytes` at 1024 bytes, and optionally checks the checksum.
- `__nilfs_sb_read()` allocates two 1024-byte buffers, determines block-device or regular-file size, reads the primary superblock at `NILFS_SB_OFFSET_BYTES`, reads the secondary superblock at `NILFS_SB2_OFFSET_BYTES(devsize)`, and rejects a secondary superblock whose offset is smaller than the filesystem geometry implies.
- `nilfs_sb_read()` returns the first available valid superblock buffer and frees the other.
- `nilfs_sb_write()` rereads both existing superblocks, copies only fields selected by `NILFS_SB_*` mask bits, recomputes checksums, and writes each present copy back to its known offset.

## State And Dependencies

The file depends on NILFS on-disk structures, endian helpers, Linux `BLKGETSIZE64`, `pread`/`pwrite`, regular-file sizing through `fstat`, and `crc32_le`.

## Risks And Invariants

The code validates magic and size before trusting `s_bytes`; full checksum validation is available but internal reads here pass `check_crc=0`. Writes are copy-on-existing-copy: missing superblock replicas are not recreated. Short `pwrite()` counts are treated as failure only when less than 1024 bytes, but negative and short writes share the same path.
