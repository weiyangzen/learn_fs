# File Research: sources/block-storage/kvdo/vdo/journal-point.h

Inline utilities and packed format for recovery/slab journal positions.

Key responsibilities:
- Defines `journal_entry_count_t`.
- Defines `struct journal_point` as sequence number plus entry count.
- Defines packed little-endian `struct packed_journal_point`.
- Provides inline advance, validity, ordering, equality, pack, and unpack helpers.

Important behavior:
- Packed encoding stores low 48 bits of sequence number shifted left 16 bits plus 16-bit entry count.
- `vdo_advance_journal_point()` wraps entry count to zero and increments sequence number at `entries_per_block`.
- Valid points require non-NULL pointer and sequence number > 0.

Dependencies:
- Includes numeric helpers and VDO types.

Notable risks:
- Header notes the packed format assumes top 16 bits of sequence number are zero long-term.
- Inline pack does not validate sequence-number width or entry-count bounds.
