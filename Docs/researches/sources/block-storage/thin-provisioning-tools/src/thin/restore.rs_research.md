# File Research: sources/block-storage/thin-provisioning-tools/src/thin/restore.rs

This file restores thin metadata from XML/IR into an output metadata device.

Key elements:
- `MappingRC` implements `RefCounter<BlockTime>` backed by a data `SpaceMap`, maintaining data block reference counts while btrees are built.
- `MappedSection` identifies the current mapping section as a shared definition or device.
- `Restorer` implements `MetadataVisitor` and owns restore state:
  - write batcher
  - report
  - shared subtree definitions
  - current map builder
  - current device details
  - source superblock IR
  - built devices
  - data space map
  - parser section state
  - superblock overrides
- `begin_section()` creates a `NodeBuilder<BlockTime>` for a def or device.
- `end_section()` completes the current node builder into btree node summaries.
- `build_device_details()` builds details and top-level mapping btrees.
- `release_subtrees()` drops temporary references held by prebuilt shared definitions.
- `finalize()` builds data space map, metadata space map, writes final superblock, and marks restore finalized.
- Visitor methods enforce ordering: one superblock, defs/devices inside superblock, maps only inside def/device, refs only inside device sections, and EOF after finalization.
- `restore()` opens input XML, creates output engine and write batcher, constructs a restorer with overrides, and parses XML into it.

Interactions:
- Used directly by `thin_restore`, indirectly by `repair.rs`, and by devtools metadata generation.
- Depends on btree builders, write batcher, disk/metadata space map writers, XML parser, and superblock packing.

Risks and notes:
- `map()` expands each run one block at a time into the node builder, so very large runs rely on builder efficiency.
- Shared definitions are prebuilt then released after devices reference them.
- Invalid section nesting/order is detected explicitly.
- Data block size validation requires 128..=2,097,152 sectors and 128-sector alignment.
