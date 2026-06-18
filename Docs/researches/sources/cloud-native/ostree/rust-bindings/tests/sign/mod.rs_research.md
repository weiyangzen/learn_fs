# sources/cloud-native/ostree/rust-bindings/tests/sign/mod.rs

Purpose: This integration module verifies the safe signing API wrappers, including dummy signer failure behavior and optional ed25519 signing/verification.

Important APIs, types, and functions: `sign_api_should_work` uses `Sign::by_name`, `SignExt::data`, `data_verify`, and GLib `Bytes`/variant conversion. `inner_sign_ed25519` accepts any `T: SignExt`, generates keys by sourcing `tests/libtest.sh`, calls `set_sk`, `add_pk`, `data`, and `data_verify`, and checks error cases for modified payloads and ill-formed signatures. `sign_ed25519` runs only when the ed25519 backend is available.

Control flow: The dummy test confirms lookup and expected failures. The ed25519 path creates a temp dir, runs bash to generate keys, reads secret/public material, configures the signer, signs a payload, verifies it, then tests invalid payload and malformed signature rejection.

State and persistence behavior: Temporary key files are written in a temp directory. Signer objects hold key material in memory through libostree. No repo commits are signed in this file.

Dependencies and integration points: Depends on feature gate `v2020_2` or `dox`, libostree sign backends, GLib prelude traits, bash, `tests/libtest.sh`, and environment variable `G_TEST_SRCDIR`.

Risks: The test shells out and sources shared shell test code, so it can fail if run from an unexpected directory or without required shell tooling. It skips ed25519 if the backend is unavailable, reducing coverage on minimal builds. It validates data signing, not commit/summary signing.

Test signals: Passing confirms signer discovery, key loading, data signing, successful verification, and failure reporting for bad signatures through Rust traits.
