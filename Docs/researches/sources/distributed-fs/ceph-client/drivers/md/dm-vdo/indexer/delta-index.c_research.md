# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/delta-index.c

## Purpose
`delta-index.c` implements the compact UDS delta-index key/value store. It stores sorted addresses in delta lists using variable-length Huffman-coded deltas plus fixed-size payloads, supports collision entries containing full record names, provides mutable in-memory indexes and immutable packed page indexes, and saves/restores mutable indexes by zone.

## Important APIs, Types, And Functions
- Initialization and teardown: `uds_initialize_delta_index()`, `uds_initialize_delta_index_page()`, `uds_uninitialize_delta_index()`, and `uds_reset_delta_index()`.
- Page packing/loading: `uds_pack_delta_index_page()`, `verify_delta_index_page()`, immutable header helpers, and `struct delta_page_header`.
- Save/restore: `uds_start_restoring_delta_index()`, `uds_finish_restoring_delta_index()`, `uds_check_guard_delta_lists()`, `uds_start_saving_delta_index()`, `uds_finish_saving_delta_index()`, `uds_write_guard_delta_list()`, and `uds_compute_delta_index_save_bytes()`.
- Iteration/search: `uds_start_delta_index_search()`, `uds_next_delta_index_entry()`, `uds_remember_delta_index_offset()`, `uds_get_delta_index_entry()`, and `uds_log_delta_index_entry()`.
- Entry operations: `uds_get_delta_entry_collision()`, `uds_get_delta_entry_value()`, `uds_set_delta_entry_value()`, `uds_put_delta_index_entry()`, and `uds_remove_delta_index_entry()`.
- Sizing/stats: `uds_get_delta_index_stats()`, `uds_compute_delta_index_size()`, and `uds_get_delta_index_page_count()`.
- Internal bit utilities include `get_field()`, `set_field()`, `get_big_field()`, `set_big_field()`, `move_bits()`, `insert_bits()`, `delete_bits()`, and delta encode/decode helpers.

## Control Flow And Data Flow
A mutable index is divided into zones, each with a contiguous bit-memory allocation, `delta_list` descriptors, and temporary rebalance offsets. `uds_reset_delta_index()` spaces each list through the zone memory and installs head/tail guard lists; the tail guard is filled with ones so corrupted streams are less likely to run past allocated memory while decoding.

Search begins with `uds_start_delta_index_search()`, which selects the zone/list, optionally starts from a saved offset, and initializes a `delta_index_entry` iterator. `uds_next_delta_index_entry()` advances by the previous entry size, decodes payload/delta bits, updates the running key, detects collision entries as zero deltas after list start, and bounds-checks against list size. `uds_get_delta_index_entry()` walks until the target key or insertion point, remembers the offset, and if a key match exists scans following collision entries comparing full names.

Insertion handles three cases: collision entry after an existing same-key entry, append at end, or insertion before a following entry that requires rewriting the following delta. `insert_bits()` grows a list by shifting nearby bits into free space or rebalancing the whole zone when local gaps are insufficient. Removal similarly deletes bits and, for non-collision entries followed by another entry, merges deltas into the following entry.

Immutable pages are packed from a mutable index by writing a `delta_page_header`, a 19-bit-per-list offset table, list bitstreams, and guard bytes. Immutable page initialization verifies nonce, list-count capacity, offset monotonicity, page bounds, and guard bytes. It supports old big-endian page headers as a fallback.

Save/restore writes per-zone `DI-00002` headers, list sizes, list data descriptors, and guard records. Restore first validates headers and list coverage, resets the target index, assigns list sizes to destination zones, rebalances memory, then reads data blobs and moves their bits to the correct destination zone.

## State And Persistence Behavior
Mutable delta indexes are in-memory structures used by the volume index and open chapter indexes. Immutable delta-index pages are persistent chapter-index pages. Save/restore records are persistent volume-index state. Persistent formats include magic, zone identity, list ranges, record/collision counts, list sizes, bit offsets, byte counts, tags, and list data. Stats track records, collisions, discards, overflow count, rebalance count, and rebalance time.

The encoding is very space-sensitive: payload bits are fixed per index, delta bits are variable-length based on `mean_delta`, collision entries append `UDS_RECORD_NAME_SIZE` bytes, and list size is a `u16` bit count. Rebalancing preserves bit offsets and guard lists while distributing free space.

## Dependencies And Integration Points
The file depends on Linux bit/log2/unaligned primitives plus VDO CPU prefetch, error codes, logging, allocation, numeric helpers, assertions, string utilities, time utilities, config, indexer, and buffered I/O. It is used directly by chapter indexes and volume indexes; geometry sizing calls `uds_get_delta_index_page_count()`.

## Risks
- Bit-level movement and overlapping copies are fragile; off-by-one errors corrupt indexes silently.
- `u16` list sizes cap a single delta list at 65535 bits; overflow handling is required by callers.
- Decode of corrupt streams can run until guard bits; guard setup and page verification are critical.
- Saved offset acceleration must be invalidated after insert/delete before the saved point.
- Collision handling requires full-name comparison; callers passing NULL names for searches that may collide would get only key-level behavior.
- Save/restore distributes lists by zone and assumes headers cover exactly all lists in order.

## Test Signals
High-value tests include randomized insert/search/delete against a reference map, collision-heavy keys with full-name checks, list overflow and rebalance stress, save/restore round trips with multiple zones, immutable page pack/load/search round trips, corrupted magic/header/list-size/page-guard tests, endian fallback fixtures, and stats consistency after insertions/removals.
