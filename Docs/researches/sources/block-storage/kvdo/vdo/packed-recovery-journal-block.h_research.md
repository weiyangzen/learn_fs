# File Research: sources/block-storage/kvdo/vdo/packed-recovery-journal-block.h

## Purpose
Defines in-memory and packed on-disk layouts for VDO recovery journal blocks and sectors.

## Key Structures
- `struct recovery_block_header`: native CPU representation.
- `struct packed_journal_header`: packed little-endian on-disk header.
- `struct packed_journal_sector`: per-sector check/recovery bytes, entry count, and flexible packed entries.

## Constants
- `RECOVERY_JOURNAL_ENTRIES_PER_BLOCK = 311`.
- `RECOVERY_JOURNAL_ENTRIES_PER_SECTOR`: derived from sector size and entry size.
- `RECOVERY_JOURNAL_ENTRIES_PER_LAST_SECTOR`: remainder for the last sector.

## Inline Helpers
- `vdo_get_journal_block_sector`: computes a sector pointer from the packed header and 1-based sector number.
- `vdo_pack_recovery_block_header`: CPU-to-little-endian conversion.
- `vdo_unpack_recovery_block_header`: little-endian-to-CPU conversion.

## Integration Notes
Includes numeric helpers, constants, recovery journal entry definitions, and VDO types. The packed structures are ABI/on-disk format sensitive.
