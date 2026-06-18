# sources/cloud-native/ostree/rust-bindings/src/auto/gpg_verify_result.rs

Purpose: Generated wrapper for `OstreeGpgVerifyResult`, exposing results from GPG signature verification.

Important APIs: `count_all`, `count_valid`, `all(signature_index)`, `lookup(key_id)`, and feature-gated `require_valid_signature` under `v2016_6`. Lower-level `get` with attribute arrays is left unimplemented due to unsupported C array conversion.

Control flow and state: The object stores verification results produced elsewhere. Methods read counts, retrieve a signature result as a `glib::Variant`, look up a signature index by key ID, or enforce at least one valid signature via a GLib error-returning call.

Dependencies and integration points: Depends on GPG verification paths in repo/commit/summary operations, GLib variants, and generated `GpgSignatureAttr` constants for interpreting variant data.

Risks: `all` returns an untyped variant, so callers must know the expected schema. Missing generated `get` means fine-grained typed access is unavailable. `lookup` uses `MaybeUninit` only if the C call succeeds, which is correct but relies on C API contract.

Test signals: Verification tests should cover no signatures, invalid signatures, valid signatures, `lookup` by key ID, and `require_valid_signature` error behavior.
