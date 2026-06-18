# File Research: sources/block-storage/thin-provisioning-tools/src/utils/adjacent_chunks.rs

## Purpose
Provides an iterator that groups a sorted slice of `u64` block numbers into adjacent consecutive chunks capped by a maximum length.

## Main Components
- `AdjacentChunks<'a>` stores the input slice, `max_len`, and current start index.
- `AdjacentChunks::new()` constructs the iterator.
- `Iterator for AdjacentChunks` returns borrowed subslices `&'a [u64]`.
- `adjacent_chunks()` is a convenience constructor.

## Behavior
Each `next()` starts at the current position and extends while:
- the end index remains inside the slice,
- chunk length is less than `max_len`,
- the next value equals the previous value plus one using `saturating_add(1)`.

The iterator yields non-overlapping subslices and advances `start` to the end of the yielded chunk.

## Research Notes
This helper assumes caller-provided ordering when “adjacent” semantics are desired. A `max_len` of zero still yields one-element chunks because `end` is initialized to `start + 1` before the cap is checked.
