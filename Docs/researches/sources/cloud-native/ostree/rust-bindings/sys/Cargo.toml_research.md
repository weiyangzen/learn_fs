# sources/cloud-native/ostree/rust-bindings/sys/Cargo.toml

## sources/cloud-native/ostree/rust-bindings/sys/Cargo.toml

Manifest for the low-level `ostree_sys` FFI crate. It declares build dependency `system-deps`, runtime dependencies on `libc`, `gio-sys`, `glib-sys`, and `gobject-sys`, dev dependencies `shell-words` and `tempfile`, package metadata, library name, and a long chain of libostree version features from `v2014_9` through `v2025_3` plus `dox`.

Control flow is Cargo feature resolution rather than code execution. Each newer feature generally depends on the previous feature, allowing consumers to opt into a minimum libostree API level and letting generated bindings conditionally compile symbols. Persistence is Cargo/build metadata only.

Integration points are `build.rs`, `system-deps`, docs.rs, and the safe wrapper crate's feature gates. Risks include feature-chain mistakes, version ordering issues (`v2025_1` depends on `v2024_7` after declaration), and mismatch between available system libostree and enabled Rust features. Tests are not in the manifest, but dev dependencies support build/test scripts.
