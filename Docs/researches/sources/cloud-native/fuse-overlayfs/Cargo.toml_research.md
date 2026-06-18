<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/Cargo.toml -->
# sources/cloud-native/fuse-overlayfs/Cargo.toml

Purpose: Rust crate manifest for the fuse-overlayfs binary.

Important structure: package `fuse-overlayfs` version `2.0.0`, edition 2024, Rust 1.85 minimum, GPL-2.0-or-later metadata, and excludes CI/tests/containerfiles from packaging. Dependencies include `fuser` with ABI 7.40, `rustix`, `libc`, `signal-hook`, `parking_lot`, `log`, `env_logger`, `thiserror`, and `rustc-hash`; dev dependency is `tempfile`. Release profile enables LTO and stripping.

State and integration: controls build graph and published crate metadata. Risks include requiring recent Rust, FUSE ABI compatibility, and release builds optimized/stripped making debugging harder. Test signal is Cargo unit/build jobs in CI.
<!-- END_FILE_RESEARCH: sources/cloud-native/fuse-overlayfs/Cargo.toml -->
