# sources/cloud-native/composefs-rs/crates/composefs-integration-tests/src/tests/mod.rs

Purpose: module index for the integration test suite, grouped by execution environment and feature area.

Important APIs/types/functions: exports submodules `cli`, `cstor`, `digest_stability`, `old_format`, `privileged`, and `varlink`.

Control flow: Rust module loading causes each submodule's `integration_test!` registrations to be linked into the distributed slice. There is no runtime logic in this file.

State and persistence: none directly.

Dependencies and integration points: ties `src/main.rs`'s `mod tests;` to all test categories. The presence of `varlink` means varlink tests are part of the same harness even though that file is outside this subset.

Risks: adding a new test file without listing it here means its registrations are not compiled. Removing or renaming a module silently drops that suite from the harness.

Test signals: coverage organization is explicit: fast host CLI, containers-storage, network digest stability, old-format compatibility, privileged kernel/mount behavior, and varlink RPC.
