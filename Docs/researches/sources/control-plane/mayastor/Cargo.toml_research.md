# sources/control-plane/mayastor/Cargo.toml

## Purpose
Root Cargo workspace manifest for the Mayastor/io-engine repository.

## Important APIs and Data
Defines `[profile.dev] panic = "abort"`, workspace resolver `1`, and members including `jsonrpc`, `libnvme-rs`, `io-engine`, `io-engine-bench`, tests, `sysfs`, `spdk-rs`, and utility dependency crates. `[workspace.dependencies]` centralizes versions for async/runtime, tracing, serde, errors, URL/UUID/time, gRPC/protobuf, device/system crates, Docker/k8s, and NATS.

## Control Flow
Cargo uses this manifest to resolve workspace membership and shared dependency versions. Member crates inherit workspace dependency versions where configured.

## State and Persistence
No runtime state. It controls dependency resolution and build graph persisted in Cargo lock/build outputs elsewhere.

## Dependencies and Integration Points
Integrates many Rust crates: `tokio`, `futures`, `tracing`, `serde`, `snafu`, `tonic/prost`, `udev`, `bindgen`, `nix`, `bollard`, `kube`, `k8s-openapi`, and internal path dependency `prost-extend`.

## Risks
Resolver version `1` can have feature-unification behavior different from newer resolver 2. Centralized dependency versions simplify consistency but make upgrades broad. `panic = "abort"` in dev changes debugging and unwind behavior.

## Test Signals
Run `cargo metadata`, `cargo check --workspace`, and CI integration tests. Dependency updates should be validated across all workspace members.
