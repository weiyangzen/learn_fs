# File Research: sources/block-storage/vdo/utils/vdo/slabSummaryReader.c

Reads and merges the VDO slab summary from metadata storage.

Key details:
- `readSlabSummary()` returns success immediately if the slab depot has zero zones.
- Allocates one zone’s slab-summary blocks with the physical layer allocator.
- Locates `VDO_SLAB_SUMMARY_PARTITION` from decoded layout and reads the first zone.
- For multiple zones, reads each zone’s summary block set into a temporary buffer and copies interleaved entries into the primary entry array.

Risk notes:
- If `vdo_get_partition()` fails, the allocated `entries` buffer is not freed before returning.
- Multi-zone merge assumes entries are distributed by `entry_number = zone; entry_number < MAX_VDO_SLABS; entry_number += zones`.
