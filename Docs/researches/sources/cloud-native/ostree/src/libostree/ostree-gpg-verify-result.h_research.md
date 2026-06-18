# sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result.h

## Purpose
This public header declares the `OstreeGpgVerifyResult` boxed/GObject-style result API used by libostree callers to inspect GPG signature verification outcomes. It defines the signature attribute enum, formatting flags, validation helpers, and the GPG error domain.

## Important APIs, Types, and Control Flow
The central opaque type is `OstreeGpgVerifyResult`. Callers count signatures with `ostree_gpg_verify_result_count_all()` and `ostree_gpg_verify_result_count_valid()`, locate a signature by key id with `ostree_gpg_verify_result_lookup()`, and extract typed attributes with `ostree_gpg_verify_result_get()` or `ostree_gpg_verify_result_get_all()`. `OstreeGpgSignatureAttr` fixes the schema for validity, expired/revoked/missing-key status, fingerprints, timestamps, algorithm names, and user identity strings. Human-readable output flows through `ostree_gpg_verify_result_describe()` and `ostree_gpg_verify_result_describe_variant()`. `ostree_gpg_verify_result_require_valid_signature()` converts a result object into a boolean security gate.

## State, Dependencies, Integration, Risks, and Tests
The header stores no state itself; persistence is in the result object produced by GPG verification code elsewhere. It depends on GLib/GIO and `ostree-types.h`, exports `_OSTREE_PUBLIC` symbols, and integrates with repository pull/commit/signature verification paths. Risks concentrate around keeping `OstreeGpgSignatureAttr` ordering and `GVariant` typing compatible with implementations and bindings. Test signals should cover no signatures, invalid signatures, missing/expired/revoked keys, lookup by key id, and stable describe output.
