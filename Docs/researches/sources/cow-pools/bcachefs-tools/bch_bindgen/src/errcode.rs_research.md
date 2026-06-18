# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/errcode.rs

- Safe Rust error wrapper for bcachefs and errno values.
- Stores positive raw error codes without constructing invalid repr enum discriminants.
- Provides message lookup via `bch2_err_str`, class matching via `__bch2_err_matches`, errno-class extraction, Display/Debug/Error impls.
- Converts negative C returns and Linux errptr values into `Result`.
