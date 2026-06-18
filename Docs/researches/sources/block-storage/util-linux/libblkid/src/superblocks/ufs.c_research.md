# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ufs.c

## Scope

Implements UFS/UFS2 probing across multiple historic superblock locations and endiannesses.

## Behavior

- Scans offsets 0, 8, 64, and 256 KiB for known UFS magic values in both endian forms.
- Classifies UFS2 vs UFS1, exports UFS2 volume name, and formats UUID from `fs_id` when present.
- Records the magic offset and exports fragment size as filesystem block size/block size.
- Exports filesystem endianness.

## Dependencies And Risks

- Uses manual scanning instead of a large static magic table.
- The detected magic/endian controls all later field interpretation.
- UFS variants share a large packed structure with unions for vendor/version-specific fields.
