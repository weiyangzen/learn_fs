# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/shared.rs

Read status: complete, 317 lines.

## Purpose

`shared.rs` contains common backstore structures and helpers used by data and cache tiers: segment representation, devicemapper target construction, allocated-segment recording, block-size validation, and metadata segment reconstruction.

## Main Types

- `Segment`: continuous sector range on a concrete device number.
- `BlkDevSegment`: `Segment` plus Stratis device UUID.
- `AllocatedAbove`: ordered list of block-device segments allocated to a higher layer.
- `BlockDevPartition`: borrowed split of block devices into used and unused sets.
- `BlockSizeSummary`: used/unused block-size groups.
- `SectorSizes`: private helper grouping base and optional crypt sector sizes.

## Segment Recording

`AllocatedAbove` implements `Recordable<Vec<BaseDevSave>>`.

Each `BlkDevSegment` becomes a `BaseDevSave` containing:

- parent device UUID
- start sector
- length

This is the persistence form for upper-layer allocations.

## Devicemapper Mapping

`AllocatedAbove::map_to_dm` converts ordered segments into linear devicemapper target lines.

It:

- Preserves segment order.
- Builds `LinearTargetParams` from physical device and start offset.
- Tracks cumulative logical start offset.
- Emits `TargetLine<LinearDevTargetParams>` entries.

## Coalescing

`coalesce_blkdevsegs` appends new segments while merging adjacent segments only when:

- UUIDs match.
- The left segment end equals the right segment start.

It preserves order and does not attempt global sorting.

## Block Size Validation

`BlockSizeSummary::validate` checks whether current used and unused device sector sizes are safe for future extension.

Key behavior:

- If there are no used devices, more than one unused size group is an error.
- If there are used devices, unused logical sector sizes must not exceed the largest used logical sector-size tuple.
- Unused physical sector sizes must not exceed the largest used physical sector-size tuple.
- On success, it returns a representative `StratSectorSizes`.

This prevents adding larger-sector unused devices later in a way that could make filesystems unmountable after extension.

## Metadata Reconstruction

`metadata_to_segment` maps persisted `BaseDevSave` records back to `BlkDevSegment`.

It requires a UUID-to-device-number map and returns an error if metadata references a missing Stratis device UUID.

## Notable Dependencies

- `InternalBlockDev` for block-size extraction.
- `StratSectorSizes` and `BlockSizes`.
- devicemapper target types.
- serde save structs: `BaseDevSave`, `Recordable`.

## Important Assumptions

- Segment ordering in `AllocatedAbove` is meaningful and preserved.
- Coalescing is local to adjacent list entries.
- Sector-size validation is conservative because crypt and base sector sizes may differ.
