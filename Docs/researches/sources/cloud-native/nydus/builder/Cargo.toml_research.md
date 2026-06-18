# sources/cloud-native/nydus/builder/Cargo.toml

Purpose: package manifest for the `nydus-builder` crate, version `0.2.0`, edition 2021, with metadata pointing to the Nydus project.

Important APIs/types/functions: not Rust code, but it defines the dependency surface used by builder modules. Core external dependencies include `anyhow`, `serde`, `serde_json`, `sha2`, `tar`, `xattr`, `gix-attributes`, `parse-size`, and system helpers such as `nix`, `libc`, and `vmm-sys-util`. Internal path dependencies are `nydus-api`, `nydus-rafs`, `nydus-storage` with `backend-localfs`, and `nydus-utils`.

Control flow: Cargo resolves these dependencies and workspace settings before compiling the builder. `package.metadata.docs.rs` enables all features and lists Linux and macOS ARM/x86 targets for documentation builds.

State and persistence: the manifest controls build graph persistence through Cargo lock/resolution and package metadata. It does not itself create runtime state.

Dependencies and integration points: this crate is integrated tightly with RAFS metadata, storage backend, utility digest/compression/crypto modules, and API configuration types. The `gix-attributes` dependency backs `attributes.rs`; `tar` backs tar header and conversion paths; `sha2` backs blob hashing.

Risks: path dependency versions must stay synchronized with sibling crates. `nydus-storage` feature selection affects available backends. Since this manifest has no feature section, conditional behavior largely comes from dependencies and higher-level workspace configuration.

Test signals: Cargo compilation and crate tests provide validation. Manifest-specific signals include dependency resolution and docs.rs target builds.
