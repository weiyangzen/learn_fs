## sources/cloud-native/composefs-rs/crates/composefs-ioctls/src/test_utils.rs

Purpose: this private test-only module re-exports unsafe-capable test utilities from `test_utils_pub` for internal crate tests.

Important APIs: it exposes whatever `crate::test_utils_pub::*` provides, currently the `CommandExt` trait for adding a pre-exec sleep to `std::process::Command`.

Control flow, state, and dependencies: there is no logic besides re-export. The module is compiled under `#[cfg(test)]` from `lib.rs`, allows unsafe code and unused imports, and keeps unsafe test support outside the crate root's `deny(unsafe_code)` policy.

Integration points: internal tests can import `crate::test_utils::*` without depending directly on the hidden public module. The split allows other workspace integration tests to use the same helper via `test_utils_pub` while keeping this module private.

Risks and test signals: because this file is only a re-export, risk is low. Its value is organizational: it preserves the unsafe boundary and avoids duplicating `pre_exec` helper code in tests.
