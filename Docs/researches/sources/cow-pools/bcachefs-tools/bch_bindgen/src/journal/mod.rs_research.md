# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/journal/mod.rs

- Rust pointer-arithmetic helpers and iterators for journal sets.
- Computes vstruct byte/sector sizes and `JSET_NO_FLUSH`.
- Iterates `jset_entry` records within a `jset` and bkeys within an entry, with bounds checks against computed end pointers.
- Converts journal entry type and btree id to known enums when possible.
- Extracts and compares trimmed log-entry message bytes.
