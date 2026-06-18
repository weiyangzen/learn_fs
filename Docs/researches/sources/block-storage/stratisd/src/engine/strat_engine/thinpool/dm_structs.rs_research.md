# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/dm_structs.rs

## Purpose
Contains helper types and functions for interpreting device-mapper thin-pool status and constructing DM target tables.

## Main Components
- `ThinPoolStatusDigest` is a simplified equality-friendly digest of `ThinPoolStatus`.
- `impl From<&ThinPoolStatus> for ThinPoolStatusDigest` maps device-mapper status to stable categories.
- `thin_pool_status_parser::meta_lowater()` extracts metadata low-water mark from working status.
- `thin_pool_status_parser::used()` extracts used data and metadata blocks from working status.
- `thin_table::get_feature_args()` exposes thin-pool feature args from a target table.
- `linear_table::segs_to_table()` converts physical segments into linear target table lines.

## Behavior
`ThinPoolStatusDigest` collapses detailed status into:
- `Fail`
- `Error`
- `Good`
- `ReadOnly`
- `OutOfSpace`

The digest string names intentionally match kernel thin-pool state strings via `strum` serialization attributes.

`linear_table::segs_to_table()` accumulates logical offsets starting at zero while preserving each segment’s backing-device start offset and length.

## Research Notes
This file is a thin adapter around `devicemapper` crate types. It isolates low-level parsing/table-construction details from higher-level thinpool code.
