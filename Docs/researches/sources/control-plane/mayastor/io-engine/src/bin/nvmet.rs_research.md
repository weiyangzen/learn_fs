<!-- BEGIN_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/nvmet.rs -->
## sources/control-plane/mayastor/io-engine/src/bin/nvmet.rs

### Purpose
`nvmet.rs` is a test utility that starts a small io-engine environment, creates a fixed-name nexus over provided NVMe-oF target URIs, and shares it over NVMf. It is intended for manual or automated nexus behavior testing.

### Important APIs, Types, And Functions
The file defines a fixed `NEXUS` UUID/name, `Args` for size and URI list, `start_tokio_runtime`, `create_nexus`, and `main`. It uses `nexus_create`, `nexus_lookup_mut`, and the `Share` trait.

### Control Flow
`main` parses target URIs, builds default `MayastorCliArgs` with RPC address `0.0.0.0:10124` and reactor mask `0xF`, initializes logging and environment, starts a small Tokio runtime running the gRPC server, schedules `create_nexus` on the reactor, and polls. `create_nexus` converts MB to bytes, creates the nexus with the fixed name, looks it up, and shares it over NVMf.

### State, Persistence, And Dependencies
The utility mutates local SPDK/io-engine state by creating and sharing a nexus. It depends on reactor initialization, NVMf target support, provided remote NVMe targets, gRPC server startup, logger, and version info. It does not use persistent store or normal registration.

### Risks And Test Signals
The fixed nexus UUID can collide with an existing resource. Many operations unwrap and are expected to crash on setup failure. The header comments note limitations for rebuild tests. Validation should cover URI parsing, size conversion, gRPC availability, successful NVMf share URI, behavior on child connection failure, and fixed-name collision.
<!-- END_FILE_RESEARCH: sources/control-plane/mayastor/io-engine/src/bin/nvmet.rs -->
