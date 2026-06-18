# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array_builder/tests.rs

Tests `ArrayBlockBuilder<V>` using `CoreIoEngine`, `CoreSpaceMap<u8>`, and `WriteBatcher`. The fixture builds array blocks, completes/flushed writes, validates block count, array-block headers, and stored values.

Coverage includes empty/single-block arrays, multiple fully populated blocks, leading/trailing default fill, sparse gaps inside and across blocks, out-of-order index rejection, recovery after rejected pushes, and out-of-bounds rejection/recovery. The expected behavior is ordered sparse writes with default-value materialization for untouched entries.
