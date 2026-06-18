# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/printbuf.rs

- Rust RAII wrapper around C `printbuf`.
- Implements indentation guard, tabstop management, automatic aligned sub-buffer output, newline/tab helpers, unit/human-readable formatting, metadata version formatting, superblock printing, bitflag printing, and raw C access.
- Implements `fmt::Write`, `Default`, and `Display`.
