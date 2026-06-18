# File Research: sources/block-storage/kvdo/vdo/recovery-journal-format.h

Read completely: 82 lines.

This header defines the superblock-encoded recovery journal state: `journal_start`, `logical_blocks_used`, and `block_map_data_blocks`. It declares the versioned component header, encode/decode helpers, encoded-size helper, and journal operation name helper.

It also provides inline validation for packed journal sectors by comparing sector check byte and recovery count against the unpacked block header, and inline circular journal block-number computation using `sequence_number & (journal_size - 1)`.

Dependencies: buffer/header APIs, packed recovery journal block definitions, and VDO numeric types.

Security/reliability notes: the block-number helper assumes the journal size is a power of two.
