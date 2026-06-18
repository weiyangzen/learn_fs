# File Research: sources/block-storage/util-linux/libblkid/src/partitions/mac.c

## Purpose
Parses Apple Partition Map (Mac) partition tables.

## Main Components
- Packed `mac_partition` models partition map entries with signature, map count, start/count, name, type, status, and boot fields.
- Packed `mac_driver_desc` models the driver descriptor in block 0 and provides block size/count.
- `get_mac_block()` reads map blocks using the descriptor block size.
- `has_part_signature()` accepts modern and old Mac partition signatures.
- `probe_mac_pt()` reads descriptor block 0, validates block size, reads partition map block 1, validates signature, creates `mac` table, caps map count at 256, iterates map entries, and adds partitions with name/type strings.
- `mac_pt_idinfo` detects the big-endian driver descriptor magic `45 52`.

## Dependencies and Interactions
Uses public partition setters for names and type strings. It follows Linux kernel behavior by exposing all map entries rather than filtering Apple free/void entries.

## Research Notes
The sector-size factor is `block_size / 512`; partition start/count are converted from Mac blocks to 512-sector units.
