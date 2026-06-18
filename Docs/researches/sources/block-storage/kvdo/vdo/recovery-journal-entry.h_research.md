# File Research: sources/block-storage/kvdo/vdo/recovery-journal-entry.h

Read completely: 110 lines.

This header defines the logical and packed recovery journal entry formats. A logical entry records the block-map slot being changed, the target data location mapping, and the journal operation. The packed on-disk entry uses bitfields for operation, slot, and the high nibble of the block-map-page PBN, a little-endian low 32-bit PBN word, and a packed block-map entry.

`vdo_pack_recovery_journal_entry()` converts a logical entry into the compact on-disk layout. `vdo_unpack_recovery_journal_entry()` reconstructs the operation, block-map slot, block-map page PBN, and data location.

Dependencies: block-map entries, journal operation enum, journal point/types, endian conversion helpers, and packed layout assumptions.

Security/reliability notes: the format stores a 36-bit block-map page PBN and a 10-bit slot. Correctness depends on callers validating bounds before trusting unpacked entries.
