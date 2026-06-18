# File Research: sources/cow-pools/bcachefs-tools/Cargo.toml

- Top-level Rust workspace and package manifest for `bcachefs-tools` version `1.38.5`.
- Workspace members are the CLI crate, `bch_bindgen`, and `doc/docgen`; default members exclude docgen.
- Defines binary `bcachefs` from `src/bcachefs.rs`.
- Default feature enables FUSE through optional `fuser`.
- Depends on CLI, serialization, udev, uuid, rustix, terminal, HTTP, demangling, chrono, and in-tree `bch_bindgen`.
- Release profile preserves debug info and uses `panic = "abort"` so C fatal handling/backtraces are not hidden by Rust unwinding.
