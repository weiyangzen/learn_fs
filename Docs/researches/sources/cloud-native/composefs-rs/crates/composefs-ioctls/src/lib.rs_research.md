## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/lib.rs

Purpose: this is the crate root for `composefs-ioctls`. It documents the crate as the unsafe boundary for Linux ioctls used by composefs and exposes safe Rust modules to downstream crates.

Important APIs and modules: `fsverity` is always public. `loop_device` is public only when the `loop-device` feature is enabled. `test_utils` is private and compiled only for this crate's tests. `test_utils_pub` is public but hidden from docs so integration tests in other crates can reuse the unsafe test helper without making production APIs depend on it.

Control flow: there is no runtime control flow here; the file is a module export and safety policy boundary. It sets `#![deny(unsafe_code)]` at crate root, forcing all unsafe operations to live in submodules that explicitly allow unsafe code, such as the ioctl implementations and test helpers.

State and persistence: no runtime state. Feature flags control the exported module graph.

Dependencies and integration: the crate-level docs provide an example of enabling and measuring fs-verity. The primary integration point is downstream composefs code that needs fs-verity or loop-device functionality without weakening its own unsafe policy.

Risks and test signals: accidental unsafe in the crate root or non-allowed modules is rejected by the lint. The hidden public test module is a deliberate API escape hatch; because it is public, downstream users could technically depend on it despite doc hiding, so changes should still consider semver impact within the workspace.
