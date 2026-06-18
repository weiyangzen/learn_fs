## sources/distributed-fs/beegfs-rust/shared/src/lib.rs

### Purpose
Defines the public module surface for the shared BeeGFS Rust crate.

### Important APIs, Types, and Functions
- Imports `impl_macros` with `#[macro_use]`.
- Exposes `bee_msg`, `bee_serde`, `conn`, `journald_logger`, `nic`, `parser`, `run_state`, and `types`.
- Exposes `grpc` only when the `grpc` feature is enabled.

### Control Flow and State
No runtime control flow or state. This file controls compilation visibility and feature-gated API availability.

### Dependencies and Integration Points
All downstream Rust crates use this root to access protocol messages, serialization, connection handling, logging, NIC discovery, parsers, run-state coordination, and shared type definitions.

### Risks and Edge Cases
Modules not listed here are inaccessible from downstream crates. In the inspected tree, `bee_msg/publish_capacities.rs` exists but is not exported by `bee_msg.rs`, so it may be orphaned even though `lib.rs` exposes `bee_msg` as a whole. Feature-gated `grpc` consumers must compile with matching protobuf dependencies.

### Test Signals
No tests. Compile checks with default and `grpc` features validate module exposure.
