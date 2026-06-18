# sources/cloud-native/composefs-rs/crates/composefs-http/Cargo.toml

Purpose: declares the `composefs-http` library crate for HTTP downloading of composefs repositories.

Important APIs/types/functions: package metadata is workspace-inherited. Runtime dependencies are `anyhow`, `bytes`, workspace `composefs`, `hex`, `reqwest` with `zstd`, `sha2`, and `tokio`. Dev dependency is `similar-asserts`.

Control flow: the library is asynchronous and built from `src/lib.rs`. The dependency set points to a downloader that fetches HTTP resources, stores them in composefs repositories, and verifies hashes.

State and persistence: the manifest configures code that writes downloaded objects into a local repository but does not itself define persistence.

Dependencies and integration points: integrates with `reqwest`/Tokio for network IO, `composefs` repository and splitstream APIs, and SHA-256 verification. The `zstd` feature suggests support for compressed HTTP responses through reqwest.

Risks: version changes in reqwest/Tokio can affect async behavior and defaults. This crate likely needs network/integration tests because correctness depends on HTTP status handling, symlink content types, and concurrent downloads.

Test signals: no direct tests are present in this subset. Verification should include recursive splitstream fetching, object checksum mismatch handling, and progress events.
