# sources/distributed-fs/ceph-client/rust/kernel/num.rs

Purpose: defines shared numeric marker traits and re-exports bounded-number helpers for the Rust kernel crate.

Important APIs/types/functions: `pub mod bounded`, `pub use bounded::*`, marker enums `Unsigned` and `Signed`, trait `Integer`, and macro `impl_integer!` implementing the trait for Rust primitive integer types.

Control flow: there is no runtime control flow. The macro expands trait implementations that associate each primitive integer with signedness and expose `BITS`.

State and persistence behavior: none. This is compile-time type metadata.

Dependencies and integration points: depends on `core::ops` arithmetic/bitwise traits. It is intended for generic numeric code, especially bounded integer abstractions that need primitive integer capabilities and signedness information.

Risks: the `Integer` trait bundles many operator traits; adding/removing bounds affects all generic users. It does not encode overflow semantics, so generic code must still choose checked/wrapping/saturating behavior explicitly. Signedness marker enums are type-level only and have no values.

Test signals: compile tests should verify every primitive implements `Integer`, associated `BITS` matches primitive constants, signedness is correct, and bounded-number users compile for signed and unsigned types.
