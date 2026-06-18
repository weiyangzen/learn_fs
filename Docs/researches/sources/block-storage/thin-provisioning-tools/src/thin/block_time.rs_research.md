# File Research: sources/block-storage/thin-provisioning-tools/src/thin/block_time.rs

This file defines the on-disk value type for thin mapping btrees.

Key elements:
- `BlockTime { block: u64, time: u32 }` stores a data block number and a 24-bit mapping time.
- `Unpack::disk_size()` returns 8 bytes.
- `unpack()` reads a little-endian `u64`, extracts the high 40 bits as `block`, and the low 24 bits as `time`.
- `Pack::pack()` writes `(block << 24) | time`.
- `Display` formats as `<block> @ <time>`.

Interactions:
- Used throughout mapping tree traversal, dump, restore, check, ls, delta, rmap, and migration metadata iteration.

Risks and notes:
- `time` is not range-checked before packing; values above 24 bits would overlap the encoded block field.
- `block << 24` assumes block numbers fit in the remaining 40 bits of the on-disk format.
