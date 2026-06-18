# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/bitset.rs

Converts on-disk array-of-`u64` bitsets into `FixedBitSet` or `CheckedBitSet`. `CheckedBitSet` stores two bits per logical bit: presence/validity and enabled state, allowing partially recovered bitsets.

`BitsetVisitor` expands every `u64` bit word into checked bits with bounds validation. `BitsetCollector` copies directly into `FixedBitSet`, using a fast unsafe `u64` to `usize` slice copy on 64-bit targets and explicit little-endian conversion on 32-bit targets. Public entry points are `read_bitset_checked`, `read_bitset_checked_with_sm`, and `read_bitset`.
