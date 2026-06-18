# File Research: sources/block-storage/kvdo/vdo/types.h

This header defines core VDO scalar types and persisted enums. Block, page, PBN/LBN, nonce, sequence, slab, slot, and zone count types are typedefs over fixed-width integers.

Persisted enums include:
- `enum vdo_state`: dirty/new/clean/read-only/force-rebuild/recovering/replaying/rebuild-for-upgrade.
- `enum journal_operation`: data/block-map increment/decrement operations.
- `enum partition_id`: block map, block allocator, recovery journal, slab summary.
- `enum vdo_metadata_type`: recovery journal and slab journal.

It also defines `struct block_map_slot`, `struct data_location`, and packed `struct slab_config`, which records slab total/data/ref-count/journal block counts plus journal flush/block/scrub thresholds. These definitions are shared across metadata, allocator, journal, and layout code.
