# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/bitset/tests.rs

Builds serialized bitset array blocks with `ArrayBlockBuilder<u64>` and verifies `BitsetCollector` reconstruction. Tests cover single `usize` entry, multiple entries, multiple array blocks, and insufficient destination size.

The helper sets source `u64` words from `FixedBitSet::ones()`, reads back array blocks, feeds them to the collector, and compares raw `FixedBitSet` slices for exact layout equality.
