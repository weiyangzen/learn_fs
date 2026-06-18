# File Research: sources/block-storage/thin-provisioning-tools/src/thin/metadata.rs

This file builds and optimizes an in-memory representation of thin metadata from on-disk or rebuilt superblock state.

Key elements:
- `Entry` is either a concrete mapping leaf block or a shared-definition reference.
- `Mapping` holds a `KeyRange` and ordered entries.
- `Device`, `Def`, and `Metadata` model devices, shared definitions, and full metadata.
- `CoreSuperblock` represents a rebuilt in-core superblock with explicit device mapping/detail data.
- `ThinSuperblock` is either `OnDisk(Superblock)` or `InCore(CoreSuperblock)`.
- `CollectLeaves` implements `LeafVisitor<BlockTime>`, recording leaf visits and repeated visits as `Entry::Ref`.
- `collect_leaves()` walks mapping roots with a `RestrictedSpaceMap` to detect reused leaves.
- `build_metadata_with_dev()` loads device roots/details from on-disk btrees or in-core devices, optionally filtering selected devices.
- `build_metadata_without_mappings()` emits device details with empty maps.
- `Gatherer` from `runs.rs` is used to identify shared atomic leaf runs.
- `optimise_metadata()` builds shared `Def` entries and rewrites device entry lists to use refs for shared runs.

Interactions:
- Used by dump and repair.
- Depends on btree walkers, leaf walkers, space maps, `BlockTime`, `DeviceDetail`, and superblock types.

Risks and notes:
- Several `FIXME` comments note incomplete `KeyRange` handling.
- `entry_map.get(&root).unwrap()` assumes every mapping root was successfully collected.
- Optimization is leaf/run based; actual map content emission still happens later when dump reads those leaf blocks.
