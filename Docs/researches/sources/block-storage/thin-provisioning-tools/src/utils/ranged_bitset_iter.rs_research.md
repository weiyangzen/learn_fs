# File Research: sources/block-storage/thin-provisioning-tools/src/utils/ranged_bitset_iter.rs

## Purpose
Defines an iterator over set bits in a specified index range of a `FixedBitSet`.

## Main Components
- `RangedBitsetIter<'a>` stores a borrowed bitset, the target `Range<usize>`, and current index.
- `RangedBitsetIter::new()` initializes iteration at `range.start`.
- `Iterator` implementation returns set bit indexes as `u64`.
- Manual unsafe `Send` and `Sync` implementations are provided.

## Behavior
`next()` scans linearly from `current` to `range.end`, returning the next index whose bit is set. It advances past every checked index, so each set bit is yielded once.

## Safety Notes
The file states the unsafe impls are safe because `FixedBitSet` is already `Sync` and `Send`. Since the iterator only holds an immutable reference plus owned range/current values, cross-thread sharing follows from the underlying bitset reference being safe.

## Research Notes
This is a simple range filter over `FixedBitSet`; it does not use bitset-internal fast search primitives, so cost is proportional to the full range length, not the number of set bits.
