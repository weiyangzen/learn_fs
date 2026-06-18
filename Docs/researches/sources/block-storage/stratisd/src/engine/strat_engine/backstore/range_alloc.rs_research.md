# File Research: sources/block-storage/stratisd/src/engine/strat_engine/backstore/range_alloc.rs

Read status: complete, 631 lines.

## Purpose

`range_alloc.rs` implements a sector range allocator for block-device space. It tracks used ranges, coalesces adjacent ranges, rejects overlaps, computes complements, and allocates free space from the front or back of a device.

## Main Types

- `PerDevSegments`: ordered, coalesced used ranges for one device.
- `Iter`: double-ended iterator over `PerDevSegments`.
- `RangeAllocator`: allocation wrapper over `PerDevSegments`.

## PerDevSegments Invariants

The comments and tests enforce:

- No zero-length stored segment.
- No contiguous stored segments; adjacent ranges are coalesced.
- No overlapping segments.
- No segment extends beyond `limit`.

Ranges are stored in a `BTreeMap<Sectors, Sectors>` where the key is start offset and the value is length.

## Insert Logic

`insert`:

- Rejects starts past the limit.
- Ignores zero-length ranges.
- Locates previous and next candidate ranges with `locate_prev_and_next`.
- Uses `insertion_result` to detect overlap and decide whether to coalesce with left, right, or both neighbors.
- Removes merged neighbors and inserts the coalesced range.

`insert_all` is atomic:

- It first inserts into a temporary `PerDevSegments`.
- It then unions that temporary structure with `self`.
- `self` is only replaced after the union succeeds.

## Set Operations

`union` merges two `PerDevSegments` with the same limit. It rejects differing limits and inserts ranges into a new structure, preserving overlap detection.

`complement` returns the free ranges as another `PerDevSegments` with the same limit. Complement-of-complement is tested as an invariant.

## Allocation Behavior

`RangeAllocator::new` creates an allocator with initial used ranges.

`alloc_front`:

- Iterates free ranges from lowest offset.
- Allocates up to the requested amount.
- May return less than requested if insufficient space exists.
- Marks allocated ranges as used.

`alloc_back` does the same from highest offsets and is currently `#[allow(dead_code)]`.

`increase_size` raises the allocation limit and asserts the new size is larger.

## Tests

Tests cover:

- Basic allocation and exhaustion.
- Initial contiguous ranges coalescing into one range.
- Overlapping insertions on previous and next ranges.
- Full allocator overwrite failures.
- Limit overflow and `u64::MAX` arithmetic overflow.
- Empty and full search behavior.
- Searches past the limit.
- Zero-length insert behavior.
- Zero-sized allocator invariants.
- End-of-limit insertion rules.

## Notable Dependencies

- `devicemapper::Sectors`
- `metadata::BlockdevSize`
- `StratisError` and `StratisResult`

## Important Edge Cases

- `start + len` uses checked addition in `insertion_result`.
- A zero-length range at exactly the limit is accepted as a no-op.
- A nonzero range starting at the limit is rejected.
- Allocation can return fewer sectors than requested.
