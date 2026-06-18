# File Research: sources/block-storage/thin-provisioning-tools/src/thin/runs.rs

This file implements `Gatherer`, which decomposes sequences of block IDs into atomic shared/non-shared runs.

Key elements:
- Internal `Entry` stores neighbor blocks in a `BTreeSet`.
- `Gatherer` tracks:
  - previous block in current sequence
  - head and tail bitsets
  - adjacency entries
  - reverse predecessor map
  - shared heads
- `new_seq()` terminates the previous sequence.
- `next(b)` records adjacency from previous block to `b`, marks heads, detects multiple predecessors, and marks shared nodes.
- `complete_heads_and_tails()` marks extra tails for branches/cycles and marks following blocks as heads.
- `extract_seq()` follows first neighbors from a head until a tail.
- `gather()` finalizes the last sequence and returns `(Vec<u64>, shared)` atomic runs.
- Unit tests cover empty input, simple runs, prefix/suffix sharing, overlapping runs, branches, and cycles.

Interactions:
- Used by `metadata.rs` to identify shared leaf runs and create reusable metadata definitions during dump/repair.

Risks and notes:
- `extract_seq()` follows the first sorted neighbor, so branch handling depends on prior tail/head splitting.
- Bitsets are allocated with `nr_entries`; callers must provide a capacity covering all block IDs used.
