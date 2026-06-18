# sources/control-plane/mayastor/io-engine/src/core/segment_map.rs

## Purpose
Represents dirty/clean rebuild segments over a block device. It maps logical block ranges to fixed-size segment bits for rebuild tracking.

## Important APIs, Types, and Functions
- `SegmentMap<B: BitBlock = u32>` stores a `BitVec`, number of segments, device block count, block length, and segment size.
- `new(num_blocks, block_len, segment_size)` creates a zeroed bitmap.
- `set(lbn, lbn_cnt, value)` marks the segment range containing a block range.
- `get(lbn)` reads the bit for a block.
- `merge`, `count_dirty_blks`, `segment_size_blks`, and `size_blks` support rebuild consumers.
- `From<SegmentMap> for BitVec` exposes the underlying bitmap.

## Control Flow and State
The constructor computes segment count by ceiling-dividing total bytes by segment size. `set` maps the first and last logical blocks to segment indices and sets all bits in that inclusive segment range. Dirty block count multiplies set segment count by segment-size blocks.

State is in-memory bitmap state. Persistence, if needed, must be handled by consumers.

## Dependencies and Integration Points
Depends on `bit_vec`. Used by rebuild logic to track what replica segments need transfer.

## Risks and Test Signals
`set` asserts `num_blocks != 0` but does not validate `lbn_cnt > 0`, `segment_size > 0`, or block range bounds. Dirty block count may over-count at the tail because it multiplies full segments. Tests should cover tail segments, merge semantics, zero/invalid inputs, and conversion to `BitVec`.
