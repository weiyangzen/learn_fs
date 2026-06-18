# File Research: sources/block-storage/thin-provisioning-tools/src/pack/delta_list.rs

This file converts u64 sequences into compact delta runs.

`Delta` variants:
- `Base { n }`
- `Const { count }`
- `Pos { delta, count }`
- `Neg { delta, count }`

`to_delta()` emits a base value and then compresses constant, increasing, and decreasing arithmetic runs using wrapping arithmetic where needed.

Integration points:
- Used by `pack::vm` to encode numeric arrays such as B-tree keys and values.

Test coverage:
- Empty and single-element sequences.
- Positive/negative arithmetic progressions.
- Constant runs.
- Mixed patterns.
- Wrapping edge cases around `u64::MAX`.
- Round-trip through a local `from_delta()` helper.

Risks and notes:
- Count semantics represent additional emitted values after the base/current value.
