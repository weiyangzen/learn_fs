# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/data/extents.rs

- Rust iterators over bcachefs extent entries and extent pointers.
- Includes generated extent-entry type sizing from the C x-macro.
- Derives entry type from bit-position encoding and bounds iteration using bkey value size.
- Supports extent-entry iteration for `btree_ptr`, `extent`, `stripe`, `reflink_v`, and `btree_ptr_v2` typed bkeys.
- Provides pointer-only iterator that filters for `BCH_EXTENT_ENTRY_ptr`.
