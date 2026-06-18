# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/index-layout.c

## Purpose
Implements the on-disk layout manager for a UDS index. It computes the fixed block layout for the superblock, configuration block, volume region, alternating save regions, and seal block; creates new layouts; validates existing layouts; and saves or loads volatile index state through `index_save_layout` slots.

## Important APIs, Types, And Functions
The file defines private layout metadata structures: `region_header`, `layout_region`, `region_table`, `super_block_data`, `index_save_layout`, `sub_index_layout`, `index_layout`, and `save_layout_sizes`. Public entry points are `uds_compute_index_size()`, `uds_make_index_layout()`, `uds_free_index_layout()`, `uds_replace_index_layout_storage()`, `uds_load_index_state()`, `uds_save_index_state()`, `uds_discard_open_chapter()`, `uds_open_volume_bufio()`, and `uds_get_volume_nonce()`.

Key helpers include `compute_sizes()`, `initialize_layout()`, `create_index_layout()`, `save_layout()`, `load_index_layout()`, `find_latest_uds_index_save_slot()`, `setup_uds_index_save_slot()`, `load_super_block()`, `reconstitute_layout()`, `load_index_save()`, and `verify_uds_index_config()`. Nonces are generated with MurmurHash3-derived `generate_primary_nonce()` and `generate_secondary_nonce()`.

## Control Flow
Creation starts from `uds_make_index_layout(config, true, ...)`, builds an `io_factory`, checks backing-device capacity, computes region sizes, allocates save-slot metadata, writes empty save headers, writes configuration contents, and writes the superblock layout header. Loading follows `uds_make_index_layout(config, false, ...)`, reads the superblock, validates version/magic/nonce/region positions, validates saved configuration against the requested configuration, and loads each save slot header.

State load chooses the latest valid save slot by timestamp and nonce, restores index chapter counters, loads the saved open chapter, opens per-zone volume-index readers, restores the volume index, then reads the index page map. State save chooses the oldest save slot, invalidates it first, instantiates a fresh save layout with timestamp and nonce, writes open-chapter data, volume-index zones, and page-map data, then writes the save header last so incomplete saves are not selected later.

## State And Persistence
The storage format is block-aligned at 4 KiB. There are two alternating save regions so a previous clean save survives a failed newer save. Superblock versions 3 and 7 are accepted, versions 4 through 6 are explicitly rejected, and converted version 7 layouts carry `volume_offset` and `start_offset`. Save validity depends on nonzero zone count, nonzero timestamp, and a nonce derived from the volume nonce and save offset. `uds_discard_open_chapter()` zeroes the saved open-chapter block to force rebuild after a new chapter has been committed.

## Dependencies And Integration Points
Depends on `config`, `open-chapter`, `volume-index`, `index-page-map`, `io-factory`, `numeric` encoding helpers, `murmurhash3`, allocation helpers, logging, and time/random APIs. It integrates upward with `index.c` during `uds_make_index()`, `uds_save_index()`, and rebuild/no-rebuild open modes, and downward with dm-bufio through `io-factory`.

## Risks
Region offset arithmetic is correctness-critical, especially converted layouts using start and volume offsets. Save-slot invalidation-before-write protects against torn saves, but any future change that writes the header before all payloads would corrupt clean-load detection. Version and payload-size checks are strict; changing serialized structures requires explicit compatibility handling. The code allocates per-zone reader/writer arrays sized by `MAX_ZONES`, so geometry and zone-count validation elsewhere must remain aligned.

## Test Signals
Useful tests include create/load/no-rebuild/rebuild open paths, simulated interrupted saves, corrupted magic/version/nonce/region tables, converted version 7 layouts, backing device too small, storage replacement followed by save, and round trips that verify open chapter, page map, and volume index restore to the same chapter counters.
