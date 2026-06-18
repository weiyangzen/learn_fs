# sources/control-plane/mayastor/jsonrpc/Cargo.toml

Purpose: crate manifest for the `jsonrpc` Rust library, version `1.0.0`, edition 2018.

Important APIs/types/functions: declares dependencies on workspace `nix`, `serde`, `serde_json`, `tonic`, `tokio` with `full` features, and `tracing`.

Control flow: no runtime flow; Cargo uses it to compile the JSON-RPC Unix-socket client and tests.

State/persistence: none directly. Dependency choices determine async socket behavior, serialization, errno mapping, and gRPC status conversion.

Dependencies/integration: integrated into the Mayastor workspace as a library crate that can bridge JSON-RPC errors to tonic status codes.

Risks: Tokio `full` expands dependency surface. Edition 2018 and crate version should stay aligned with workspace expectations.

Test signals: `scripts/cargo-test.sh` runs `cargo test` in this crate, covering manifest resolution and unit tests.
