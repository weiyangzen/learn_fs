# File Research: sources/block-storage/thin-provisioning-tools/src/run_iter.rs

This file provides `RunIter`, a compact iterator over boolean runs in a `RoaringBitmap`.

Key elements:
- `RunIter { len, current, bits }` walks the index space `0..len`.
- Each `next()` returns `(bool, Range<u32>)`, where the boolean is whether the range is present in the bitmap.
- Consecutive equal membership values are coalesced into one range.
- Unit tests cover empty input, all-false input, alternating false/true regions, and trailing false runs.

Interactions:
- This is a general utility for converting sparse bitmap state into contiguous runs.
- It depends on the `roaring` crate.

Risks and notes:
- The iterator checks `bits.contains()` at every position, so runtime is linear in `len`, not in compressed bitmap cardinality.
- It assumes `len` fits in `u32`, matching `RoaringBitmap`’s key type.
