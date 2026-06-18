# Group Research: thin-provisioning-tools pdata and random subset A

Scope: `sources/block-storage/thin-provisioning-tools` persistent-data helpers for array blocks, btrees, space maps, walkers, serialization, and deterministic test data.

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder/tests.rs

Tests `ArrayBlockBuilder<V>` using `CoreIoEngine`, `CoreSpaceMap<u8>`, and `WriteBatcher`. The fixture builds array blocks, completes/flushed writes, validates block count, array-block headers, and stored values.

Coverage includes empty/single-block arrays, multiple fully populated blocks, leading/trailing default fill, sparse gaps inside and across blocks, out-of-order index rejection, recovery after rejected pushes, and out-of-bounds rejection/recovery. The expected behavior is ordered sparse writes with default-value materialization for untouched entries.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_walker.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_walker.rs

Implements `ArrayWalker` and `ArrayVisitor<V>`. It walks the btree that maps array indices to array-block locations, then reads and unpacks each `ArrayBlock<V>` through `BlockValueVisitor`.

The walker verifies contiguous array indices, validates array block checksum type, increments a supplied or restricted metadata space map for visited array blocks, and accumulates array plus btree errors into `ArrayError::Aggregate` when needed. It also provides `collect_array_blocks_with_path`, which returns index-to-`(path, block)` mappings without reading array block payloads.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_walker.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_walker/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_walker/tests.rs

Uses mock `ArrayVisitor` expectations to validate that `ArrayWalker` visits all undamaged array blocks in order. The fixture builds large arrays via `array_builder::test_utils`, tracks damaged btree nodes and array blocks, and computes expected surviving values.

Coverage includes clean arrays, trashed root, first/last damaged leaf, first/last damaged array block, damaged array-block ranges, and combined btree-node plus array-block damage. Tests emphasize partial traversal: good blocks are still delivered while affected ranges are skipped.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/array_walker/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/bitset.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/bitset.rs

Converts on-disk array-of-`u64` bitsets into `FixedBitSet` or `CheckedBitSet`. `CheckedBitSet` stores two bits per logical bit: presence/validity and enabled state, allowing partially recovered bitsets.

`BitsetVisitor` expands every `u64` bit word into checked bits with bounds validation. `BitsetCollector` copies directly into `FixedBitSet`, using a fast unsafe `u64` to `usize` slice copy on 64-bit targets and explicit little-endian conversion on 32-bit targets. Public entry points are `read_bitset_checked`, `read_bitset_checked_with_sm`, and `read_bitset`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/bitset.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/bitset/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/bitset/tests.rs

Builds serialized bitset array blocks with `ArrayBlockBuilder<u64>` and verifies `BitsetCollector` reconstruction. Tests cover single `usize` entry, multiple entries, multiple array blocks, and insufficient destination size.

The helper sets source `u64` words from `FixedBitSet::ones()`, reads back array blocks, feeds them to the collector, and compares raw `FixedBitSet` slices for exact layout equality.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/bitset/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree.rs

Defines on-disk btree node format: `NodeHeader`, `Node<V>::Internal`, and `Node<V>::Leaf`. Supports packing/unpacking little-endian keys and values using `Pack`/`Unpack`.

Validation checks value size, max-entry capacity against block size, entry count, optional non-fatal invariants such as `max_entries % 3 == 0` and minimum non-root occupancy, sorted keys, checksum type, and block-number match. `calc_max_entries<V>()` computes the kernel-compatible fanout rounded down to a multiple of three.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree/tests.rs

Tests `pack_node` and `unpack_node` round trips for empty and fully populated leaf nodes with random keys/values. It verifies header preservation, key preservation, and value preservation for `u64` leaves.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder.rs

Builds persistent btrees from sorted key/value streams and optional shared prebuilt leaves. `RefCounter<Value>`, `NoopRC`, and `SMRefCounter` manage referenced values, while metadata blocks are allocated through `WriteBatcher`.

`NodeBuilder` buffers values, writes balanced leaves/internal nodes through `NodeIO`, imports underfull shared nodes when needed, increments metadata refs for reused nodes, and unshifts prior nodes to avoid underfull final nodes. `BTreeBuilder` builds leaves then calls `build_btree` to add internal layers. `release_leaves` drops temporary shared leaf references and decrements contained values when leaves become unreferenced.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder/test_utils.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder/test_utils.rs

Provides test-only layout introspection for btrees. `NodeInfo` and `BTreeLayout` record block numbers, key ranges, entry ranges, and node heights as builders emit nodes.

Helpers build leaves and complete btrees from mappings, track root/leaf/node slices by height, calculate first leaf under a node, and expose `push_values`. This allows walker tests to know exact expected visitation and affected ranges after corrupting specific nodes.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder/test_utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder/tests.rs

Exercises `NodeBuilder` balancing and shared-node import behavior. Tests verify empty, underfull-root, full-root, two-leaf, balanced, and three-leaf construction; pushing regular shared nodes; unpacking first regular shared node when buffered entries are insufficient; handling underfull shared roots; and unshifting regular/underfull previous nodes.

It also validates residency with `EntriesCounter`, verifies serialized leaf contents, checks reused block numbers for shared leaves, expects panic for multiple underfull nodes pushed at once, allows underfull roots one by one, and rejects unordered keys.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_builder/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_error.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_error.rs

Centralizes btree error context. `KeyRange` models half-open key ranges and can split around child keys. `split_key_ranges` derives child ranges for internal nodes.

Also implements compact encoded node paths using VM-packed u64s plus base64 for diagnostics. `NodeError` covers IO, checksum/type, block mismatch, value-size, occupancy, ordering, and incomplete-data errors. `BTreeError` wraps node/value/context errors with key range, path, or aggregate context. Embedded tests cover key-range splitting and path encode/decode round trips.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_error.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_iterator.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_iterator.rs

Implements sorted in-order iteration over btree leaf entries. `BTreeIterator<V>` keeps a traversal stack of `Frame<V>` objects plus a path, descends to the leftmost leaf at construction, exposes current `(key, &value)` via `get`, and advances with `step`.

It reads nodes from an `Arc<dyn IoEngine + Send + Sync>` and unpacks with non-fatal checks ignored. Embedded tests build btrees of 0, 16, and 10240 entries and assert iteration returns the original ordered mappings.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_iterator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_layer_walker.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_layer_walker.rs

Provides batched/layered btree reading backed by `Aggregator`. `read_internal_nodes` walks internal levels breadth-first using `BufferPool`, marks nodes through `Aggregator::test_and_inc`, and avoids revisiting already-seen children. `LeafHandler` then reads leaf nodes and forwards them to a `NodeVisitor`.

`read_nodes` combines both phases, and `btree_to_map_with_aggregator` collects leaf key/value pairs using `ValueCollector`. This is optimized for loading space maps and large trees with fewer duplicate reads.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_layer_walker.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_leaf_walker.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_leaf_walker.rs

Walks only btree leaf blocks while tracking references in a mutable `SpaceMap`. `LeafVisitor<V>` receives key ranges and leaf block locations, with a `visit_again` hook for shared nodes.

`LeafWalker` computes tree depth, increments metadata counts, avoids repeated leaf IO via a `FixedBitSet`, validates node checksum and structure, and returns the collected leaf bitset. It is stricter about uniform depth and reports contextual btree errors on IO/checksum/layout failures.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_leaf_walker.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_lookup.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_lookup.rs

Implements simple point lookup. Starting at root, it unpacks each node, binary-searches internal keys to choose the greatest lower-bound child, and binary-searches leaf keys to return `Option<V>`.

It clones returned values and intentionally unpacks full nodes, which the comments call acceptable for low-frequency lookups such as device details.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_lookup.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_merge.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_merge.rs

Skeleton for non-destructive btree merge. It defines a private leaf-summary collector that walks multiple roots with `BTreeWalker`, verifies subtree ordering, and records leaf block, entry count, and low/high keys.

The intended algorithm is documented: collect all leaves, optimize/merge underpacked leaves, then rebuild upper layers. `optimise_leaves` is currently a pass-through and `merge` ends in `todo!()`, so this module is not complete production behavior.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_merge.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_utils.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_utils.rs

Contains `get_depth_` and `get_depth`, returning btree depth where `0` means root is a leaf. It reads/checks nodes, recurses through the first non-looping child that can reach a leaf, and skips path loops.

If all children fail, it returns the first captured error or a `NumEntriesTooSmall` node error. This utility is used by layered walkers to determine how many internal levels must be read.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_utils.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_walker.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_walker.rs

General recursive btree walker. `NodeVisitor<V>` receives leaf path, key range, header, keys, values, repeated-node callbacks, and end-walk callback. `BTreeWalker` tracks visited blocks through a `SpaceMap`, caches failures by block, batches child reads, and aggregates child errors.

Utility collectors convert btrees to maps, maps with paths, key sets, value vectors, or just block counts. Shared nodes are not reread; visitors receive `visit_again` if clean, or cached errors if bad. Error paths and key ranges are preserved for diagnostics.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_walker.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_walker/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/btree_walker/tests.rs

Uses a mock `NodeVisitor` plus `BTreeLayout` metadata to verify traversal and error reporting. The fixture builds large btrees, corrupts selected blocks with `trash_block`, computes unaffected leaves, and checks visited key ranges, headers, and mappings.

Coverage includes empty tree, clean large tree, trashed root, first/last leaf damage, damaged leaf sequence, damaged internal node, and combined internal/leaf damage. Error assertions inspect aggregate structure, key context, path last block, and node-error wrapping.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/btree_walker/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/mod.rs

Module index exporting persistent-data submodules: array, array builder/walker, bitset, btree core/build/error/iterator/layer/leaf/lookup/merge/utils/walker, space map, and unpack primitives.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/aggregator.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/aggregator.rs

Defines a concurrent, region-based reference-count aggregator. `Region` abstracts increment, lookup, set, test-and-inc, memory sizing, and allocation count. `U32Region` stores counts adaptively as `NoCounts`, `Bits`, `U8s`, `U16s`, or `U32s`, upgrading when duplicate hits or count overflows require wider representation.

`RestrictedTwoRegion` stores saturated 0/1/2 counts using two bits per entry. `AggregatorImpl<R>` shards entries into 1024-block mutex-protected regions, batches sorted increments by region, supports `lookup`, `test_and_inc`, `set_batch`, `diff`, representation-size accounting, and `RefCount` integration. `SpaceMap` allocation APIs are stubbed with `todo!()`.

Tests cover representation upgrades, single/multi-region increments, concurrent increments, lookup bounds/partial reads, test-and-inc seen-bit behavior, set upgrades/allocation tracking, mixed operations, and restricted-two saturation semantics.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/aggregator.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/aggregator_load.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/aggregator_load.rs

Loads serialized disk or metadata space maps into `Aggregator`. `SmType` selects data-space-map index gathering through a btree or metadata-space-map index gathering through the metadata index block.

`read_space_map` gathers index entries, reads bitmap blocks with `BufferPool` and `IndexHandler`, sets nonzero small counts in an aggregator, then walks the overflow ref-count btree with layered `read_nodes` to patch large counts. It also increments metadata-sm counts for index/bitmap metadata blocks. Public wrappers are `read_data_space_map` and `read_metadata_space_map`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/aggregator_load.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/allocated_blocks.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/allocated_blocks.rs

Builds a `RoaringBitmap` of allocated metadata blocks from a metadata space-map root. It loads the metadata index, sorts bitmap locations by physical block for read locality, reads each bitmap, and inserts any entry that is not `Small(0)`.

The returned roaring bitmap uses logical block numbers derived from index position times `ENTRIES_PER_BITMAP` plus bitmap entry offset.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/allocated_blocks.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/base.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/base.rs

Defines `RefCount`, `SpaceMap`, and shared `ASpaceMap`. `CoreSpaceMap<T>` is an in-memory vector-backed refcount map with typed counters, allocation count tracking, round-robin allocation, bounds checks, and overflow checks.

Also provides `RestrictedSpaceMap` for 0/1 visited tracking, `RestrictedTwoSpaceMap` for 0/1/2 saturated counts, and `NoopSpaceMap`. Factory helpers choose `u8`, `u16`, or `u32` core maps based on maximum count. Restricted maps are used heavily by walkers to avoid duplicate visits without full refcount precision.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/base.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/checker.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/checker.rs

Validates serialized data and metadata space maps against expected in-core counts. `OverflowChecker` walks overflow ref-count btrees and compares each stored count with a supplied `SpaceMap`.

`check_low_ref_counts` reads bitmap blocks, verifies bitmap checksum/type, detects leaks where on-disk count is 1 but expected is 0, reports fatal mismatches, and returns `BitmapLeak` records for repair. Public `check_disk_space_map` and `check_metadata_space_map` gather index entries, count referenced metadata blocks, check overflow trees, and validate low-count bitmaps.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/checker.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/common.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/common.rs

Defines shared on-disk space-map structures. `IndexEntry` maps a bitmap index entry to bitmap block location plus free-count metadata. `Bitmap` packs 2-bit reference states for `Small(0)`, `Small(1)`, `Small(2)`, and `Overflow`, using the device-mapper bit ordering.

`SMRoot` stores total blocks, allocated blocks, bitmap root, and overflow ref-count root. `write_common` serializes normal space maps into bitmap blocks plus overflow btree. `write_metadata_common` handles metadata-space-map serialization using `WriteBatcher` allocations and writes zero-filled remaining bitmaps.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/common.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/disk.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/disk.rs

Serializes a data-space map. `write_disk_sm` calls `write_common`, builds a btree of `IndexEntry` values keyed by bitmap index, flushes writes, and returns `SMRoot` populated from the input `SpaceMap`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/disk.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/metadata.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/metadata.rs

Implements metadata-space-map index block format. `MetadataIndex` stores its own block number and up to 255 `IndexEntry` records in a single metadata index block. Loading verifies checksum/type and block number, then truncates entries to the number required by `nr_blocks`.

Helpers map blocks to bitmap indexes. `write_metadata_sm` writes bitmap/overflow data, allocates the metadata index block, patches bitmap counts for blocks consumed by the space map itself, writes checksum-tagged index data, flushes, and returns `SMRoot`. `core_metadata_sm` caps metadata maps at `MAX_METADATA_BLOCKS`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/metadata.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/mod.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/mod.rs

Module index for space-map code: aggregator, aggregator loader, allocated-block extraction, base traits/maps, checker, common serialization, disk writer, metadata writer/loader, repairer, and tests. Re-exports `space_map::base::*`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/mod.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/repairer.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/repairer.rs

Repairs leak-only space-map bitmap errors. `repair_space_map` rereads bitmap blocks identified by `BitmapLeak`, unpacks each bitmap, changes entries from `Small(1)` to `Small(0)` where expected refcount is zero, repacks, rewrites bitmap checksums, and writes all repaired blocks.

It assumes leaks are the only corruption class; reread or write failures abort with errors.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/repairer.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/tests.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/tests.rs

Shared tests for `SpaceMap` behavior: block count, allocated count tracking, out-of-space, inc/dec to 255, no duplicate allocation, `set` allocation effects, and wraparound allocation. Applies these to `CoreSpaceMap<u8>`.

Additional metadata-space-map tests verify index-entry count/free-count invariants for single and multiple bitmap cases and tolerate junk bytes in unused metadata-index entries. Disk-space-map tests serialize data maps and verify btree index entry counts and free/allocated totals.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/space_map/tests.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/unpack.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/unpack.rs

Defines `Unpack` and `Pack` traits for fixed-size on-disk values. Provides helper `unpack<U>` converting nom parse failures to `io::ErrorKind::InvalidData`.

Implements little-endian packing/unpacking for `u64` and `u32`, which are the primitive value types used throughout btree, bitmap, and array structures.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/pdata/unpack.rs -->

<!-- BEGIN FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/random.rs -->
# File Research: sources/block-storage/thin-provisioning-tools/src/random.rs

Implements deterministic test-data generation with a linear congruential generator. `Generator::fill_buffer` writes little-endian `u64` words seeded by caller and stepping with fixed `a`/`c` constants; `verify_buffer` replays the sequence and returns false on first mismatch.

Both methods require buffer length to be a multiple of eight. `Default` delegates to `new`.
<!-- END FILE RESEARCH: sources/block-storage/thin-provisioning-tools/src/random.rs -->