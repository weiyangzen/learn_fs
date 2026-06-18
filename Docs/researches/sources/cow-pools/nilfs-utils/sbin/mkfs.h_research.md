# File Research: sources/cow-pools/nilfs-utils/sbin/mkfs.h

## Scope

Defines constants and small helpers used by `mkfs.nilfs2`.

## API Surface

- Defines disk header/erase sizes, default block size, default blocks per segment, default check interval, reserved segment percentage, minimum block size, minimum user segments, and initial inode bounds.
- Aliases ext2-style bit operations to NILFS bitmap helper names.
- Provides fallback `BLKGETSIZE64`.
- Defines directory file-type constants matching Linux mode file type bits.
- Provides `nilfs_rec_len_from_disk()` and `nilfs_rec_len_to_disk()` conversions for directory entry record lengths, including the NILFS max-record-length sentinel for 64 KiB.

## Dependencies And Risks

The header includes NILFS on-disk structures through `compat.h`. The record length conversion asserts lengths are not above 64 KiB; callers must validate directory record sizing before writing.
