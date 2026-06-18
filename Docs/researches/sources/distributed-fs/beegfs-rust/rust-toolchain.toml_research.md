<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/rust-toolchain.toml -->
# sources/distributed-fs/beegfs-rust/rust-toolchain.toml

Purpose: pins the Rust toolchain for the BeeGFS Rust workspace.

Important APIs/types/functions: TOML `[toolchain]` declares `channel = "1.94"` and `profile = "default"`.

Control flow: rustup uses this file when commands are run inside the workspace to select/download the specified compiler toolchain.

State and persistence: no application state. It affects developer/CI toolchain selection and reproducibility.

Dependencies and integration points: applies to all Rust crates in `beegfs-rust`, including mgmtd, shared, sqlite, protobuf, and derive crates.

Risks: channel `1.94` is a future or specific stable version relative to many environments; builds fail if rustup cannot resolve/install it. Pin updates should be coordinated with edition/style settings and dependency MSRVs.

Test signals: validated by successful `cargo` commands under rustup. No unit tests apply.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/rust-toolchain.toml -->
