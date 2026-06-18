# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/sb/io.rs

- Rust wrappers for reading bcachefs superblocks.
- `read_super_opts` and `read_super` return `anyhow::Result<bch_sb_handle>`.
- `read_super_silent` returns `Result<bch_sb_handle, BchError>`.
- Uses `MaybeUninit` and path-to-CString conversion around C read-super APIs.
