# File Research: sources/cow-pools/bcachefs-tools/bch_bindgen/src/opts.rs

- Rust accessors for bcachefs option metadata and parsing.
- Wraps bindgen’s zero-length option table as a slice sized by `bch2_opts_nr`.
- Provides macros for setting, checking, and getting option fields with default fallback.
- Safely maps table indexes to `bch_opt_id`, wraps defined/get/set operations by id, and exposes default opts.
- Extends `bch_option` with safe string accessors for name, hint, help, and choices.
- Parses mount option strings or vectors through C `bch2_parse_mount_opts`.
