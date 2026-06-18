# File Research: sources/block-storage/kvdo/vdo/index-layout.c

On-disk UDS index layout manager for block-device backed index storage, including superblock layout, region tables, two clean-save slots, save/load of index state, and volume-region access.

Key responsibilities:
- Defines the single-file index layout format: super/header/config/index/seal regions, one sub-index, a volume region, and two `RL_KIND_SAVE` regions.
- Defines save-region sublayout: save header, index page map, per-zone volume-index regions, saved open chapter, and optional free space.
- Computes required index size from `struct configuration` geometry via `compute_sizes()` and exports `uds_compute_index_size()`.
- Generates and validates nonces using `murmurhash3_128()`: primary superblock nonce, sub-index nonce, and per-save nonce.
- Encodes/decodes little-endian `region_header`, `layout_region`, superblock data, `index_save_data`, and versioned `index_state_data301`.
- Loads existing layout from storage, validates magic/version/config, reconstructs region boundaries, and loads valid save-region metadata.
- Creates new layouts, invalidates old save slots, writes the top-level layout header and config region.
- Selects latest valid save for load and oldest/invalid save for overwrite.
- Saves and loads clean index state by coordinating saved open chapters, volume index zones, and index page maps.
- Exposes `make_uds_index_layout()`, `free_uds_index_layout()`, `replace_index_layout_storage()`, `load_index_state()`, `save_index_state()`, `discard_index_state_data()`, `discard_open_chapter()`, `get_uds_volume_nonce()`, and `open_uds_volume_bufio()`.

Important behavior:
- The persistent format uses 4K `UDS_BLOCK_SIZE` blocks; region headers and regions begin on block boundaries.
- Supported superblock versions are 3 and 7; versions 4-6 are explicitly rejected.
- Version 7 represents converted layouts with `volume_offset`/`start_offset`; older versions treat both as zero.
- Save validity requires nonzero zone count, nonzero timestamp, and a save nonce matching the sub-index nonce plus save start block and timestamp.
- `save_index_state()` first invalidates the selected old slot, instantiates a fresh save layout, writes the open chapter, writes all volume-index zones, writes the page map, then writes the save header last to make the slot valid.
- `load_index_state()` selects the latest valid save slot and restores newest/oldest chapter numbers, last-save chapter, saved open chapters, volume index, and page map.
- `discard_open_chapter()` zeroes one block of the latest save's open-chapter region so later recovery knows a clean saved open chapter is no longer available.
- `open_uds_volume_bufio()` returns a dm-bufio client over the volume region, adjusted for converted-layout offsets.

Dependencies:
- Storage access is through `io_factory`, `buffered_reader`, `buffered_writer`, and dm-bufio.
- Relies on `configuration`, `geometry`, config serialization, open-chapter save/load, volume-index save/load, index-page-map save/load, random/time utilities, memory allocation, logging, and little-endian buffer helpers.
- Uses `linux/murmurhash3.h` for nonce hashing.

Notable risks:
- Region reconstruction is strict about offsets, kinds, instances, counts, and versions; minor layout drift becomes `UDS_CORRUPT_DATA` or unsupported-version failure.
- `discard_index_state_data()` stores the last failing result in `saved_result` but logs/returns `result` after the loop, which may not be the same variable value if multiple slots are attempted.
- `make_index_save_region_table()` stores `payload` and `type` as `size_t` before assigning to 16-bit fields; current values are small, but the type mismatch matters for future expansion.
- Clean-save atomicity depends on invalidating the old slot before writing a new one and committing the new save header last.
- Save arrays are bounded by `MAX_ZONES`; callers must keep `zone_count` within that contract.
