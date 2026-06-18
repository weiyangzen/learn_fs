# File Research: sources/block-storage/parted/libparted/fs/amiga/affs.c

AFFS and muFS filesystem probe implementation. `_generic_affs_probe()` accepts a boot-block DOS type (`DOS\0` through `DOS\7`, `muFS`, and `muF\0` through `muF\5`) and returns a duplicate of the input geometry if the boot block and root block validate.

The probe is restricted to 512-byte device sectors. It optionally locates the matching Amiga RDB partition block via `amiga_find_part()` to derive reserved block count and block size. Without RDB data it defaults to reserved `2` and block size `1` sector. It reads the boot block at the partition start and checks the big-endian kind value. It then computes the AFFS root block near the middle of the filesystem, reads it, and validates root block type, tail marker, and checksum.

The file defines one `PedFileSystemOps` and `PedFileSystemType` per AFFS/muFS variant. It does not inspect directory trees or allocation maps; detection is signature/checksum based. Errors during reads/allocation throw libparted exceptions and return no match.
