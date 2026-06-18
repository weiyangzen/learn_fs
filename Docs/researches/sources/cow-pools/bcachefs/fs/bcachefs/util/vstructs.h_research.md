# File Research: sources/cow-pools/bcachefs/fs/bcachefs/util/vstructs.h

## Summary
Defines macros for working with variable-sized bcachefs structures whose payload length is expressed as a count of u64 words.

## Main Contents
- `vstruct_u64s()`, `vstruct_bytes()`, `vstruct_blocks()`, `vstruct_blocks_plus()`, `vstruct_sectors()`.
- `vstruct_next()`, `vstruct_last()`, `vstruct_end()`.
- `vstruct_for_each()` and `vstruct_for_each_safe()`.
- `vstruct_idx()`.

## Important Behavior
The macros assume structures have an `_data` payload and often a `start` flexible element. Length fields may be `u64`, `u32`, `u16`, or `u8` and are converted as little-endian values.

## Risks
The file notes that `type_is` cannot distinguish `__le64` from `u64`, so u64 length fields are assumed little-endian. These macros are type/layout-sensitive and can silently produce bad pointer arithmetic if used on structures without the expected `_data` and `start` conventions.
