# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/vfat.c

## Scope

Implements FAT12/FAT16/FAT32 probing and the internal `blkid_probe_is_vfat()` helper.

## Behavior

- Defines FAT boot sector variants, directory entries, and FAT32 FSInfo layout.
- `fat_valid_superblock()` validates boot signature when needed, rejects JFS/HPFS pseudo-headers, checks FAT count, reserved sectors, media byte, cluster power-of-two, sector size, cluster count, and BitLocker collision.
- FAT12/16 probing searches the fixed root directory for a volume-label entry, exports boot label, serial UUID, `SEC_TYPE=msdos`, and FAT version.
- FAT32 probing walks the root directory cluster chain, bounded by `maxloop`, and validates FSInfo signatures when present.
- Exports label, FAT boot label, UUID, version, filesystem block size, sector block size, and filesystem size.

## Dependencies And Risks

- Ambiguous boot-sector magics require strong BPB validation to avoid false positives.
- FAT32 root traversal reads FAT entries from calculated offsets and is bounded to prevent runaway loops.
- `blkid_probe_is_vfat()` shares validation logic for partition-table collision handling.
