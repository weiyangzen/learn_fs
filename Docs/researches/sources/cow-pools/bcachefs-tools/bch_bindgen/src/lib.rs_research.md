# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/lib.rs

- Library root exporting bcachefs binding modules and re-exporting `paste`.
- Defines `c` facade module for generated C symbols.
- Provides constructors and constants for `bpos` sentinel positions.
- Implements ordering for `bpos` and `bbpos`.
- Adds btree-id raw conversion, iteration, Display, and FromStr via C string tables.
- Provides path-to-CString conversion and parse errors for btree ids, bkey types, bpos, and bbpos.
- Parses `bbpos` and bbpos ranges.
- Adds `printbuf::new`, Drop for generated C printbuf, Display for `bpos`, sentinel-aware bpos parsing, and a helper for printing C printbuf output into Rust formatters.
