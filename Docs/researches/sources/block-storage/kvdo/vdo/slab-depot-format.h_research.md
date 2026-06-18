# File Research: sources/block-storage/kvdo/vdo/slab-depot-format.h

Declares the slab depot persisted state format and configuration helpers.

Key type:
- `struct slab_depot_state_2_0`: packed on-disk state containing `slab_config`, first data block, last block, and zone count.

Exports:
- Format header: `VDO_SLAB_DEPOT_HEADER_2_0`.
- Slab count and encoded-size helpers.
- Encode/decode functions for version `2.0`.
- Depot/slab configuration functions.
- `vdo_get_saved_reference_count_size()` for sizing persisted refcount storage.

This header connects superblock state to runtime `slab_depot` construction.
