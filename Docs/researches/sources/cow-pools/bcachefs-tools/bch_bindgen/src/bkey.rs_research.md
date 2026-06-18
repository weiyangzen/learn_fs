# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bkey.rs

- Defines `BkeySC`, a Rust split-const bkey/value reference tied to a btree iterator lifetime.
- Includes generated typed bkey dispatch from `bkey_types_gen.rs`.
- Provides conversion from inline and split C bkeys, value dispatch, and C text formatting through printbuf.
- Implements pure Rust `bpos` and bkey comparison helpers plus min/max helpers.
- Computes bkey start position from end position minus size.
