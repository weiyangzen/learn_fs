# sources/control-plane/mayastor/io-engine/src/lib.rs

## Purpose
This is the crate root for io-engine. It wires macro imports, declares the public module graph, re-exports SPDK FFI helpers, and provides C initialization hooks for SPDK subsystem/module registration.

## Important APIs, types, and functions
The file exposes major modules such as `core`, `bdev`, `grpc`, `host`, `jsonrpc`, `logger`, `lvm`, `lvs`, `pool_backend`, `replica_backend`, `rebuild`, `store`, `subsys`, and `target`. `pub use spdk_rs::ffihelper` makes SPDK callback helper utilities available through the crate.

`CPS_INIT!` exports a static function pointer in `.init_array` that points to `io_engine::cps_init`, allowing dependent binaries or modules to request early initialization. `cps_init()` registers the subsystem layer, nexus bdev module, and null-ng bdev module.

## Control flow
At library load or binary startup, users of `CPS_INIT!` arrange for `cps_init` to run before normal Rust main flow. That registration prepares SPDK-facing modules before runtime operations.

## State and persistence behavior
The file itself has no durable state, but `cps_init` mutates global SPDK/module registries. The module declarations define the crate's stable integration surface.

## Dependencies and integration points
It depends on macro crates (`ioctl_gen`, `tracing`, `serde`, `derive_builder`) and core external crates (`nix`, `serde_json`, `snafu`, `spdk_rs`). It is the integration root for all io-engine binaries and tests.

## Risks and test signals
Initialization order is the key risk: modules needing SPDK registration must be registered before use and must tolerate repeat or early calls. Tests are generally crate integration/build tests rather than local unit tests. Changes here have broad compile and startup impact.
