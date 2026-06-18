# File Research: sources/block-storage/kvdo/vdo/delta-index.c

## Purpose
Implements UDS/VDO’s delta index: a compact key-value store where sorted integer keys are represented as deltas and values are fixed-width payloads. It supports mutable in-memory indexes, immutable packed chapter-index pages, persistence save/restore, collision records containing full chunk names, and statistics/logging.

## Main Concepts
- `delta_zone` owns a contiguous bitstream arena containing many `delta_list` streams plus guard lists at both ends.
- Delta entries store value bits followed by Huffman-style variable-length delta bits.
- Collision entries are encoded as `delta == 0` after the first list entry and carry a 256-bit full chunk name.
- Mutable indexes have allocated list headers and temporary offset arrays; immutable page indexes infer list boundaries from a packed page header table.
- Guard bytes at the tail are set to all ones to prevent corrupted variable-length decode from scanning into unsafe memory.

## Key Behavior
- Initialization: `initialize_delta_index()` allocates zones, divides list ranges across zones, computes coding constants, and initializes evenly spaced empty lists.
- Bit operations: `get_field()`, `set_field()`, `get_big_field()`, `move_bits()`, and helpers manipulate unaligned little-endian bit ranges.
- Page support: `pack_delta_index_page()` packs mutable lists into immutable pages; `initialize_delta_index_page()` validates page nonce, list ordering, guard bytes, and endian format.
- Persistence: `start_saving_delta_index()` writes a zone header and per-list sizes; `finish_saving_delta_index()` writes non-empty list payloads. Restore mirrors this through `start_restoring_delta_index()` and `finish_restoring_delta_index()`.
- Search/iteration: `start_delta_index_search()` initializes an iterator, `next_delta_index_entry()` decodes entries, and `get_delta_index_entry()` searches through possible collision chains.
- Mutation: `put_delta_index_entry()` inserts normal or collision entries, updating neighbor deltas and expanding/rebalancing zones as needed. `remove_delta_index_entry()` deletes entries and repairs the following delta.
- Accounting: stats aggregate allocated memory, records, collisions, discards, overflows, and rebalance time.

## Dependencies
Uses VDO/UDS support for buffers, buffered readers/writers, allocation, assertions, logging, endian unaligned access, hashing constants, timing, and CPU prefetching.

## Invariants and Risks
- The implementation assumes native little-endian behavior for hot bitstream utilities.
- Delta list size is capped by `uint16_t`; insertion sets overflow state and returns `UDS_OVERFLOW`.
- Correctness depends on guard list placement and tail bytes remaining all ones.
- Restore validates zone order, list count, tag, list size, and collision count before loading data.
- `write_guard_delta_list()` writes the in-memory save-info struct directly rather than using the endian helper used elsewhere, which is safe only if the packed layout and endian expectations match the reader’s assumptions.
