# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/bcachefs.rs

- Includes generated bindgen output from `OUT_DIR/bcachefs.rs` with broad lint allowances for C naming and generated patterns.
- Adds Rust bitfield wrappers for crypt and scrypt flags.
- Extends generated superblock and superblock-handle types with typed field access, UUID, device count, nonce, members access, and RAII freeing.
- Implements partial equality for superblocks based on identity/version/sequence fields.
- Adds `bch_opt_strs` helpers to store strdup’d option strings, parse them into `bch_opts`, and free them.
- Declares opaque placeholders for blocked C types.
