# File Research: sources/block-storage/kvdo/vdo/slab-journal-format.c

Implements decoding of one slab journal entry from a packed slab journal block.

Function:
- `vdo_decode_slab_journal_entry()`

Behavior:
- Starts with `vdo_unpack_slab_journal_entry()`, which decodes SBN and data increment/decrement from the packed entry.
- If the block header says the block has block-map increments, checks the entry-type bitmap.
- If the bitmap bit is set, overrides the operation to `VDO_JOURNAL_BLOCK_MAP_INCREMENT`.

This supports the dual slab-journal format: dense data-only entries and a lower-capacity “full” format that can distinguish block-map increments.
