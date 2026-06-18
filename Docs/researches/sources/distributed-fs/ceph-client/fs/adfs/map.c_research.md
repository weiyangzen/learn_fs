# sources/distributed-fs/ceph-client/fs/adfs/map.c

## Purpose
`map.c` reads, validates, scans, and queries the ADFS free/object map. The map is a zone-based bitstream of variable-length fragments whose fragment IDs identify file and directory extents.

## Important APIs, types, and functions
Public functions are `adfs_read_map()`, `adfs_free_map()`, `adfs_map_lookup()`, and `adfs_map_statfs()`. Important helpers include `lookup_zone()`, `scan_free_map()`, `scan_map()`, `adfs_calczonecheck()`, `adfs_checkmap()`, `adfs_map_layout()`, `adfs_map_read()`, and `adfs_map_relse()`. `GET_FRAG_ID` extracts unaligned little-endian bitfields.

## Control flow
Mount passes a valid disc record to `adfs_read_map()`, which computes zone count, bits-per-map-block conversions, IDs per zone, the central map address, allocates descriptors, reads zone buffers, and validates per-zone and cross checksums. `adfs_map_lookup()` chooses a starting zone from the fragment ID, converts sector offset to map-bit offset, scans zones under `adfs_map_lock`, and returns a physical sector or reports corruption.

## State and persistence
The in-memory `adfs_discmap` array holds buffer_heads and zone bit ranges. On-disk map state persists as checksum-protected zone sectors. This file only reads and releases maps; allocation updates are not implemented here.

## Dependencies and integration points
It integrates with `adfs_fill_super()`, `adfs_get_block()`, statfs, buffer_head I/O, little-endian bit helpers, and ADFS disc-record fields such as `log2bpmb`, `zone_spare`, and `idlen`.

## Risks and test signals
Risks include malformed fragment chains, oversized fragments, invalid free-list links, id-length limits, shift/sign errors in map-to-sector conversion, and checksum false positives. Test signals include valid F/F+ images, corrupt zonecheck and crosscheck images, root fragment lookup, large fragmented files, free-space statfs accuracy, and out-of-range fragment IDs.
