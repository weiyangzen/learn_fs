# File Research: sources/block-storage/thin-provisioning-tools/src/thin/rmap.rs

This file implements reverse mapping from physical data block ranges back to thin device/logical ranges.

Key elements:
- `RmapRegion` stores data begin/end, device ID, and thin begin.
- `RmapRegion::adjacent()` extends the current region only when device ID, data block, and thin block are contiguous.
- `RmapRegion::compare()` sorts output by data begin, data end, device ID, and thin begin.
- `RmapVisitor` implements `NodeVisitor<BlockTime>`:
  - current device ID is set before walking each device tree
  - mapping entries outside requested regions are ignored
  - adjacent entries are coalesced
- `ThinRmapOptions` carries input path, engine options, requested data regions, and report.
- `rmap()` reads the superblock, loads top-level mapping roots, walks each mapping tree with a restricted metadata space map, sorts completed reverse-map regions, and prints lines to stdout.

Interactions:
- Uses `btree_to_map::<u64>()` to find per-device roots.
- Uses `BTreeWalker::new_with_sm()` to avoid repeated metadata traversal issues.

Risks and notes:
- Region membership is checked by linear scan over requested ranges for every mapping entry.
- Output is text-only and sorted after collection.
- TODO notes mention possible multithreading; current implementation walks devices serially.
