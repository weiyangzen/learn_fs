<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/libfs.h -->
# sources/distributed-fs/openafs/src/vfsck/libfs.h

## Purpose
Defines return codes for HP-UX block-seek support used by the special `AFS_HPUX101_ENV` I/O path in `utilities.c`.

## Important APIs, Types, And Functions
The header includes `<sys/fs.h>` for UFS macros and defines `BLKSEEK_PROCESSING_ERROR`, `BLKSEEK_FILE_WRITEONLY`, `BLKSEEK_NOT_ENABLED`, and `BLKSEEK_ENABLED`.

## Control Flow
There is no runtime control flow. The constants classify `setup_block_seek_2` outcomes so `bread` and `bwrite` know whether `lseek` offsets are in DEV_BSIZE blocks or byte offsets.

## State And Persistence
No state is stored here. The constants influence persistent disk I/O behavior indirectly through global `seek_options`.

## Dependencies And Integration Points
`utilities.c` includes this file only under HP-UX 10.1-style builds. It ties OpenAFS fsck to the HP-UX `O_BLKSEEK` device flag.

## Risks And Test Signals
Risk is limited to mismatched constant meanings with `utilities.c`. Test by verifying HP-UX device and regular-file fsck reads/writes seek to the expected offsets, including write-only device descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/libfs.h -->
