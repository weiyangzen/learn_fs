# sources/distributed-fs/ceph-client/rust/syn/sealed.rs

## Purpose
`sealed.rs` provides a tiny internal sealing trait for lookahead-related parsing APIs.

## Important APIs, types, and functions
Under `parsing`, module `lookahead` defines `pub trait Sealed: Copy {}`. There are no functions.

## Control flow
There is no runtime control flow.

## State and persistence behavior
No state and no persistence.

## Dependencies and integration points
The trait is used as a sealing bound by lookahead token machinery so only crate-approved types can participate while still allowing copyable lookahead markers.

## Risks
The only risk is API-boundary drift: if lookahead types need to be extensible outside the crate, this sealed trait prevents it by design.

## Test signals
Compile-time tests should verify intended lookahead types satisfy the bound and downstream crates cannot implement sealed internals.
