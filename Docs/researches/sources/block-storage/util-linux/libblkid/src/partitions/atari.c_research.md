# File Research: sources/block-storage/util-linux/libblkid/src/partitions/atari.c

## Purpose
Parses Atari partition tables, including primary, XGM extended, and optional ICD partition entries.

## Main Components
- Packed `atari_part_def` and `atari_rootsector` describe on-disk root/extended sector fields.
- Linux-compatible `_linux_isalnum` table matches kernel partition-ID validation.
- Validation helpers check active flags, three-character IDs, dimensions, common ICD IDs, and overflow.
- `parse_partition()` adds a partition, handles duplicate starts, and sets the type string from the three-byte Atari ID.
- `parse_extended()` follows XGM chains, parses data entries, validates next-link entries, and limits traversal to 100 iterations.
- `probe_atari_pt()` enforces 512-byte sectors and disk size constraints, validates root-sector size and bad-sector list, requires at least one valid primary entry, creates the `atari` table, parses primary/XGM entries, and optionally parses ICD entries when no XGM is present.
- `atari_pt_idinfo` has no fixed magic and relies on the prober.

## Dependencies and Interactions
Uses partition-list helpers from `partitions.c`, probe sector reads, endian helpers, and magic recording through `blkid_probe_set_magic()`.

## Research Notes
The parser follows Linux kernel behavior closely, including alphanumeric classification. Partition starts/sizes are stored in 512-sector units and duplicate starts do not create duplicate entries.
