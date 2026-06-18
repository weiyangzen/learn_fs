# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/accounting.rs

- Rust helpers for bcachefs disk accounting positions and display.
- Safely maps raw `u8` values to generated C enums with sentinel fallback.
- Defines `DiskAccountingPos` as transparent wrapper around `bpos`, with ordering and accounting-type extraction.
- Defines `DiskAccountingKind` variants for all expected accounting key types and asserts the C enum count is 11.
- Encodes/decodes accounting keys by reversing the 20-byte bpos representation used by the C accounting layout.
- Provides helpers for empty/hidden data types, C printbuf formatting of accounting-related enums, btree id names, and member state names.
