# sources/cloud-native/ostree/rust-bindings/src/auto/enums.rs

Purpose: Generated Rust enum mappings for libostree enum types, with conversion implementations between Rust variants and C integer values.

Important APIs: Enums include `DeploymentUnlockedState`, `GpgSignatureAttr`, `ObjectType`, `RepoCheckoutFilterResult`, `RepoCheckoutMode`, `RepoCheckoutOverwriteMode`, `RepoCommitFilterResult`, `RepoCommitIterResult`, `RepoMode`, `RepoRemoteChange`, and `StaticDeltaGenerateOpt`. Each is `#[non_exhaustive]`, copyable, comparable, hashable, and has hidden `__Unknown(i32)` preservation.

Control flow and state: Conversion is pure value mapping. `IntoGlib` maps Rust variants to FFI constants; `FromGlib` maps FFI constants back, retaining unknown values for forward compatibility.

Dependencies and integration points: These enums are used across repo checkout/commit/pull APIs, object parsing, deployment state, remote mutation, static delta generation, and GPG verification metadata.

Risks: Enum constant drift is a compatibility risk. The `__Unknown` variant prevents panics on newer libostree values but callers must handle non-exhaustive matches correctly. Feature gates such as `RepoCheckoutFilterResult` under `v2018_2` must align with symbol availability.

Test signals: Compile across feature gates, round-trip known values through `IntoGlib`/`FromGlib`, and include wildcard match coverage in downstream tests.
