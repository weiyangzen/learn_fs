# File Research: sources/block-storage/stratisd/src/engine/strat_engine/thinpool/thinids.rs

## Purpose
Provides `ThinDevIdPool`, a simple allocator for device-mapper thin device IDs.

## Main Components
- `ThinDevIdPool { next_id: u32 }`
- `new_from_ids(ids)` initializes the next ID to one greater than the maximum existing thin ID, or zero if no IDs exist.
- `new_id()` converts `next_id` into a `ThinDevId`, increments `next_id`, and returns the allocated ID.

## Behavior
The allocator does not verify duplicate input IDs. It is monotonic from the maximum existing ID and relies on `ThinDevId::new_u64()` for validity checking. A TODO notes that failure handling could be improved to guarantee failure only after all 24-bit IDs are exhausted.

## Research Notes
This is intentionally small allocation state used during thin filesystem creation/setup. Its main invariant is avoiding reuse of known existing IDs by starting above the maximum saved ID.
