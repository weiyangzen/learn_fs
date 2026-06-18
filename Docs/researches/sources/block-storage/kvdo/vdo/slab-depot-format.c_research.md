# File Research: sources/block-storage/kvdo/vdo/slab-depot-format.c

Implements encoding/decoding and layout calculation for the slab depot’s on-disk superblock component.

On-disk header:
- `VDO_SLAB_DEPOT_HEADER_2_0` identifies the slab depot component, version `2.0`, and payload size `sizeof(struct slab_depot_state_2_0)`.

Encoding/decoding:
- `encode_slab_config()` and `decode_slab_config()` serialize all `struct slab_config` fields as little-endian 64-bit values.
- `vdo_encode_slab_depot_state_2_0()` writes the component header, slab config, first/last block, and zone count.
- `vdo_decode_slab_depot_state_2_0()` validates the header, decodes fields, checks decoded size, and populates state.

Layout helpers:
- `vdo_compute_slab_count()` computes full slabs as `(last_block - first_block) >> slab_size_shift`.
- `vdo_get_slab_depot_encoded_size()` returns header plus state payload size.
- `vdo_get_saved_reference_count_size()` returns `DIV_ROUND_UP(block_count, COUNTS_PER_BLOCK)`.

Configuration:
- `vdo_configure_slab_depot()` computes how many whole slabs fit in the block range, rejects zero slabs and too many slabs, and records first/last block and zone count.
- Runt slabs are not allowed; leftover blocks below one slab are wasted.
- `vdo_configure_slab()` computes per-slab metadata and data capacity:
  - reference-count blocks are sized from data capacity minus slab-journal blocks,
  - metadata blocks are reference-count blocks plus slab-journal blocks,
  - very small unit-test slabs may round data blocks down to a power of two,
  - journal flush/block/scrub thresholds are derived from journal block count.

Threshold meanings:
- Flush threshold: starts writing reference blocks, roughly three quarters of the journal.
- Blocking threshold: stops admitting new journal entries until reference blocks drain.
- Scrubbing threshold: leaves enough extra journal space for recovery behavior.
