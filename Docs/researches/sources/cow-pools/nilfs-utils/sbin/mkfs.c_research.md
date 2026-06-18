# File Research: sources/cow-pools/nilfs-utils/sbin/mkfs.c

## Scope

Implements `mkfs.nilfs2`, creating an initial NILFS2 filesystem image: superblocks, initial segment, root directory, ifile, cpfile, sufile, DAT, segment summary, super root, checksums, and device erase/write behavior.

## APIs And Behavior

- Option parsing supports block size, blocks per segment, badblocks scan, force overwrite, discard suppression, label, reserved-segment percentage, dry-run, quiet/verbose, feature set, passive creation time, and version.
- Device checks verify regular/block device, not currently mounted, optional blkid signature confirmation, and optional badblocks scan with dropped privileges.
- `init_disk_layout()` determines device size, block bits, creation time, random CRC seed, first segment block, segment count, and minimum segment requirement.
- Layout helpers count required blocks for block-grouped files, cpfile, sufile, and DAT, then place all initial files in the first segment.
- Disk buffering lazily allocates block-aligned blocks and preserves the disk header before writing superblock data.
- Erase logic optionally issues `BLKDISCARD`, skips zeroing if discard guarantees zeroes, otherwise wipes the beginning and end of the device while preserving a boot sector area when present.
- Metadata construction initializes root directory entries, reserved inodes, block-grouped allocation descriptors/bitmaps, ifile inodes, checkpoint state, segment usage state, DAT mappings, segment summary finfo/binfo records, super root, and on-disk inode bmaps.
- `fill_in_checksums()` computes segment summary, super root, and full segment data checksums.
- `commit_super_block()` fills last checkpoint/partial-segment/sequence/free-block fields and superblock CRC.
- `write_disk()` writes initial segment blocks, fsyncs, writes primary and secondary superblocks, and fsyncs again unless dry-run is set.

## State And Dependencies

Global option state controls formatting choices. `struct nilfs_disk_info`, `struct nilfs_segment_info`, `struct nilfs_file_info`, and global `struct nilfs_fs_info nilfs` track the planned filesystem image. Dependencies include NILFS on-disk structures, libuuid, optional libblkid, block-device ioctls, `check_mount`, CRC32, feature parsing, and local bitmap helpers.

## Risks And Invariants

Many validation failures terminate via `perr()`. The code assumes one initial segment in `seginfo[1]`. Block size must be a power of two, between 1024 and page size; blocks per segment must be a power of two and at least `NILFS_SEG_MIN_BLOCKS`. Superblock CRC is computed after `raw_sb` was zeroed and populated; checksum fields inside segment/super-root must be written after all metadata content is stable.
