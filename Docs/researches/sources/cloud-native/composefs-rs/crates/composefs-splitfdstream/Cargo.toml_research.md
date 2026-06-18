# sources/cloud-native/composefs-rs/crates/composefs-splitfdstream/Cargo.toml

## Purpose
This manifest defines the unpublished `composefs-splitfdstream` library crate, which implements a binary format for streams that mix inline bytes with external file descriptor references.

## Important APIs, Types, and Functions
Cargo metadata names the crate, description, keywords, and `publish = false`. The runtime dependency is `rustix` with `fs` and `std` features. Dev dependencies are `proptest` and `tempfile`. Workspace lints are enabled.

## Control Flow
The manifest keeps the crate small and independent. Tests pull in property testing and temporary files, while production only needs standard IO and `rustix` support for fd-relative/positional reads used in test-only reconstruction helpers.

## State and Persistence
No runtime state is defined by the manifest. It controls whether the stream format implementation is included as a private workspace crate and ensures it is not published independently.

## Dependencies and Integration Points
`rustix` provides low-level file descriptor IO support used by the library's test adapters. `proptest` is important because the stream format has many chunk ordering and boundary cases. `tempfile` supports external fd reconstruction tests.

## Risks
Because `publish = false`, downstream users should depend on it through the workspace, not crates.io. The crate has no serde or async dependencies, which keeps the wire format implementation simple but means higher-level fd passing protocols must be implemented elsewhere.

## Test Signals
The manifest enables extensive unit and property tests in `src/lib.rs`, including arbitrary chunk sequence round trips, external fd reconstruction, same-fd reuse, bounds errors, and inline size limit checks.
