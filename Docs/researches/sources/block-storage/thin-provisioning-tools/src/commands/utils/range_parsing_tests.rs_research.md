# File Research: sources/block-storage/thin-provisioning-tools/src/commands/utils/range_parsing_tests.rs

Unit tests for `RangeU64` parsing in `commands::utils`.

Covered cases:
- Valid full-range form: `0..18446744073709551615`.
- Missing separator: `0`, `0.10`.
- Separator without values: `..`.
- Extra characters or extra separators: `0..10,`, `0..10..`.
- Invalid begin/end tokens.
- Negative begin/end values.
- End not greater than begin, including `0..0`.

These tests verify that range parsing is strict and unsigned.
