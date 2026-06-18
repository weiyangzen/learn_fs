# sources/control-plane/mayastor/io-engine/src/rebuild/rebuild_map.rs

## Purpose
This file wraps a `SegmentMap` with device identity and exposes rebuild-specific dirty/clean segment operations.

## Important APIs, Types, And Functions
`RebuildMap::new` constructs the wrapper. `is_blk_clean` checks whether a logical block does not need transfer. `blk_clean` marks a block clean. `count_dirty_blks` counts remaining dirty blocks. `From<RebuildMap> for BitVec` consumes the segment map into a bit vector.

## Control Flow
Range walkers and partial copy wrappers query the map before copying. Successful partial-sequential copies call `blk_clean` to reduce future remaining work.

## State, Persistence, And Dependencies
State is in-memory `SegmentMap` bits plus `device_name` for diagnostics. Dependencies include `bit_vec` and core `SegmentMap`.

## Integration Points
Nexus partial rebuilds receive a `RebuildMap` from child dirty-bit state. `PartialSeqCopier` locks and mutates the map as segments are copied.

## Risks
Out-of-range map access logs an error and returns dirty/unclean semantics, which avoids data loss but can increase copy work. `blk_clean` assumes the map supports the requested block. Device name is diagnostic only and is not used to validate that the map matches a destination.

## Test Signals
Test clean/dirty queries, out-of-range behavior, dirty count updates after `blk_clean`, conversion to `BitVec`, and use with segment sizes larger than one block.
