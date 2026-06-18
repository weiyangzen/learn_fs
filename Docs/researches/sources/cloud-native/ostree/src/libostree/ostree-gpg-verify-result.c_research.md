# sources/cloud-native/ostree/src/libostree/ostree-gpg-verify-result.c

## Purpose
This file implements public inspection and reporting APIs for GPG detached-signature verification results.

## Important APIs, Types, And Functions
`signature_is_valid()` treats GPGME `VALID`, `GREEN`, or status-ok/no-summary signatures as valid. `signing_key_is_revoked()` works around GPGME revoked-key reporting. The GObject implements `GInitable` to allocate a GPGME context and finalizes by releasing context/details. `ostree_gpg_verify_result_count_all()` and `_count_valid()` walk `details->signatures`. `ostree_gpg_verify_result_lookup()` canonicalizes a key ID via GPGME and compares primary key fingerprints. `ostree_gpg_verify_result_get()` builds a tuple for requested `OstreeGpgSignatureAttr`s, including validity, expiry/revocation/missing flags, fingerprints, timestamps, algorithm names, user ID fields, and key expiry fields. `get_all()` uses a synchronized attribute list. `describe()` and `describe_variant()` format human-readable status. `require_valid_signature()` enforces at least one valid signature and maps the last failed signature to `OstreeGpgError`.

## Control Flow, State, And Persistence
Attribute extraction walks a selected signature, lazily looks up the signing key only for key-dependent fields, and returns a floating `GVariant` tuple. Description validates the exact all-attributes tuple type `(bbbbbsxxsssssxx)`. Error construction for invalid results iterates signatures newest-last-to-first and strips trailing newlines.

## Dependencies And Integration Points
It depends on GPGME, GLib/GObject/GVariant, libglnx, and the private result layout. Repository verification APIs return these objects to callers who need either boolean acceptance or detailed diagnostics.

## Risks And Test Signals
Signature validity policy is security-critical and intentionally includes “valid with caveats” and “not certified but cryptographically OK” cases. Tuple order must stay synchronized with the enum. Tests should cover valid, bad, missing-key, revoked, expired-key, expired-signature, subkey versus primary fingerprint lookup, unknown algorithm fallbacks, invalid timestamps, `require_valid_signature()` error-code selection, and backwards-compatible tuple type/order.
