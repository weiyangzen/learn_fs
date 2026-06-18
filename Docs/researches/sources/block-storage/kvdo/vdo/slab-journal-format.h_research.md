# File Research: sources/block-storage/kvdo/vdo/slab-journal-format.h

Defines the on-disk format for slab journal blocks.

Key formats:
- `struct slab_journal_entry`: unpacked SBN plus journal operation.
- `packed_slab_journal_entry`: 24-bit packed offset with one bit used for increment/decrement.
- `struct slab_journal_block_header`: unpacked header with head, sequence number, nonce, recovery point, metadata type, block-map-increment flag, and entry count.
- `struct packed_slab_journal_block_header`: little-endian on-disk header.
- `struct full_slab_journal_entries`: packed entries plus bitmap for entries that are block-map increments.
- `slab_journal_payload`: union of full-entry layout, data-only dense layout, and raw payload space.
- `struct packed_slab_journal_block`: header plus payload.

Capacity constants:
- `VDO_SLAB_JOURNAL_PAYLOAD_SIZE`
- `VDO_SLAB_JOURNAL_FULL_ENTRIES_PER_BLOCK`
- `VDO_SLAB_JOURNAL_ENTRY_TYPES_SIZE`
- `VDO_SLAB_JOURNAL_ENTRIES_PER_BLOCK`

Helpers:
- `vdo_get_slab_journal_start_block()` computes journal origin inside a slab after data and reference-count blocks.
- `vdo_pack_slab_journal_block_header()` serializes header fields.
- `vdo_unpack_slab_journal_entry()` decodes data increment/decrement entries.
- `vdo_decode_slab_journal_entry()` handles the optional block-map-increment bitmap.

Design point:
- Most steady-state slab journal entries are data updates, so data-only blocks can store more entries. Blocks containing any block-map increments use the bitmap format.
