# sources/cloud-native/nydus/utils/Cargo.toml

Purpose: package manifest for `nydus-utils`, the shared utility crate used across Nydus.

Important APIs/types/functions: package version `0.5.1`, dual license `Apache-2.0 OR BSD-3-Clause`, edition 2021. Core dependencies include `arc-swap`, `thiserror`, `blake3`, `httpdate`, `lazy_static`, `libc`, `log`, `lz4-sys`, `lz4`, `serde`, `serde_json`, `sha2`, `tokio`, `zstd`, `nix`, `crc`, and local `nydus-api`. Optional `openssl` backs `encryption`; optional `libz-sys` backs `zran`. Target-specific flate2/libz choices use stock zlib on ppc64 and linux/aarch64, zlib-ng elsewhere. Dev dependencies include `vmm-sys-util`, `tar`, `futures`, and Tokio test features.

Control flow: Cargo feature resolution controls whether `compress::zlib_random` and `crypt` build. Target cfg selects zlib implementation.

State and persistence: none directly.

Dependencies and integration points: this manifest determines shared primitive availability for digesting, compression, logging, metrics, async helpers, and encryption across Nydus crates. Docs.rs builds all features for selected targets.

Risks: feature-gated modules can be under-tested in default builds. Vendored OpenSSL increases build time/complexity but improves portability. Target-specific zlib choices signal prior linking issues and should be maintained carefully.

Test signals: dev dependencies support unit and fixture tests throughout `utils/src`.
