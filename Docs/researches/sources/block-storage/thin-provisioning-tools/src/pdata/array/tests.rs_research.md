# File Research: sources/block-storage/thin-provisioning-tools/src/pdata/array/tests.rs

This file tests persistent array block pack/unpack round trips.

Important behavior:
- `mk_random_block()` creates an `ArrayBlock<u64>` with random values and a valid header.
- `pack_unpack_empty_block()` verifies empty array blocks preserve header and have no values.
- `pack_unpack_fully_populated_block()` verifies a full array block preserves header and all values.

Integration points:
- Exercises `pack_array_block()`, `unpack_array_block()`, and `calc_max_entries()`.

Risks and notes:
- Tests focus on valid round trips, not malformed header validation paths.
