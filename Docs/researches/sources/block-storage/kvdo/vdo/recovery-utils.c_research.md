# File Research: sources/block-storage/kvdo/vdo/recovery-utils.c

Read completely: 283 lines.

This file provides recovery-time utilities for loading and scanning the recovery journal. `vdo_load_recovery_journal()` allocates a full journal-sized buffer, creates enough multi-block metadata VIOs to read the journal partition in chunks of at most `MAX_BLOCKS_PER_VIO`, submits reads, and completes the parent when all reads finish. `journal_loader` owns the parent completion, original callback thread, VIO array, and completion counts.

`vdo_find_recovery_journal_head_and_tail()` scans every journal block read from disk, unpacks each header, checks that it is congruent with its circular offset, nonce, recovery count, and metadata type, then finds the highest valid sequence number plus maximum block-map and slab-journal head values. It returns false if no valid entries newer than the current journal tail are found.

`vdo_validate_recovery_journal_entry()` checks unpacked entries against VDO bounds: block-map page PBN, slot range, valid mapped location, physical data block membership, and special restrictions for block-map increment entries, which cannot be compressed or point at the zero block.

Dependencies: metadata VIO allocation/submission, partition layout offsets, packed recovery journal block headers, recovery journal entry unpacking, slab depot physical-block checks, VDO config bounds, completion framework, and metadata I/O error recording.

Security/reliability notes: a loader allocation failure after the journal data buffer is allocated finishes the parent without freeing that buffer in this function; ownership expectations around `journal_data_ptr` matter on that path. Scan logic ignores stale/unformatted/misplaced blocks and only trusts headers matching nonce and recovery count.
