# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bitmask.rs

- Pure Rust implementation of little-endian u64 bitmask get/set behavior equivalent to C `LE64_BITMASK`.
- Exposes `le64_bitmask_get` and `le64_bitmask_set`.
- Defines `bitmask_accessors!` macro to generate typed getter/setter methods for struct fields or array elements using exported bindgen constants.
