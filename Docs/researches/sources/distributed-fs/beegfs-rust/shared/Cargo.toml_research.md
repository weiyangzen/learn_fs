<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/Cargo.toml -->
# sources/distributed-fs/beegfs-rust/shared/Cargo.toml

Purpose: manifest for the `shared` crate, which contains reusable BeeGFS protocol, networking, parsing, logging, type, and optional gRPC support used by mgmtd and other crates.

Important APIs/types/functions: declares package metadata inherited from the workspace, dependency on local `bee_serde_derive`, workspace dependencies such as `anyhow`, `libc`, `log`, `regex`, `ring`, `serde`, `thiserror`, and `tokio`, plus optional `protobuf`, `tonic`, and `tokio-stream`. Feature `grpc` enables those optional gRPC dependencies. Clippy lint `undocumented_unsafe_blocks = "deny"` is set.

Control flow: Cargo resolves optional gRPC dependencies only when the `grpc` feature is enabled.

State and persistence: no runtime state; it defines build graph and lint policy.

Dependencies and integration points: mgmtd uses shared BeeMsg, connection, NIC, parser, run-state, and type modules. Optional protobuf/tonic integration supports management API code paths.

Risks: `ring` is pulled for hashing with a comment noting licensing/indirect dependency concerns. Feature-gated code must compile both with and without `grpc`. Workspace dependency versions control compatibility.

Test signals: crate-level `cargo check/test` across feature combinations, especially default and `--features grpc`, validate this manifest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/beegfs-rust/shared/Cargo.toml -->
