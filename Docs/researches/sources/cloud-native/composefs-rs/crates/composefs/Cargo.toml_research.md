# sources/cloud-native/composefs-rs/crates/composefs/Cargo.toml

Purpose: Defines the `composefs` Rust library crate metadata, feature flags, dependencies, development dependencies, and workspace lints.

Important APIs and types: This manifest does not export Rust APIs, but it controls compile-time feature surfaces. Features are `pre-6.15` and `test` for `tempfile`, `rhel9` for pre-6.15 plus `composefs-ioctls/loop-device`, and `varlink` for optional `zlink-core`.

Control flow: Cargo resolves core dependencies for EROFS read/write, dumpfile parsing, hashing, async process support, serialization, and zerocopy layout handling. Optional dependencies are activated through features, while dev-dependencies enable capability-safe temp dirs, snapshots, property testing, and executable-gated tests.

State and persistence: The manifest persists crate configuration and participates in workspace inheritance for edition, license, readme, repository, rust-version, version, and lints.

Dependencies and integration: Runtime dependencies include `anyhow`, `composefs-ioctls`, `serde`, `serde_repr`, `fn-error-context`, `hex`, `log`, `once_cell`, `rustix`, `serde_json`, `sha2`, `thiserror`, `tokio`, `xxhash-rust`, `zerocopy`, `zstd`, `rand`, and `tokio-stream`. It integrates with optional `zlink-core` and feature-gated `tempfile`.

Risks: Feature names encode kernel or distribution assumptions; downstream builds must select compatible flags. `rand = 0.10.0` and `sha2 = 0.11.0` may imply newer APIs than older distributions carry. Optional feature coupling should stay aligned with code-level `cfg` gates.

Test signals: Dev-dependencies indicate snapshot, property, async, and external executable tests. The fuzz crate depends on this package by path.
