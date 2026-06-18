# sources/cloud-native/ostree/src/libostree/ostree-sign-ed25519.c

Purpose: implements the Ed25519 `OstreeSign` backend for commit, summary, and data signatures, including key loading from explicit variants or well-known trusted/revoked key files.

Important APIs/types/functions: `OstreeSignEd25519` stores backend state, one secret key buffer, trusted public keys, and revoked public keys. State values distinguish usable, unsupported, and failed crypto initialization. `validate_length` enforces exact key/signature sizes. `_ostree_sign_ed25519_is_initialized` gates crypto operations. `ostree_sign_ed25519_data` signs with libsodium or OpenSSL. `ostree_sign_ed25519_data_verify` validates signatures against trusted, non-revoked keys. Key-management functions clear sensitive memory, decode base64 strings or bytestring variants, deduplicate keys, and add revoked keys. Loading helpers read blobs and scan `trusted.ed25519`, `trusted.ed25519.d`, `revoked.ed25519`, and `revoked.ed25519.d`.

Control flow: object init detects crypto support and initializes the core crypto layer. Signing validates initialization and key presence, then signs raw `GBytes` with the compiled crypto backend. Verification rejects null data, missing signatures, or wrong metadata type; auto-loads default keyrings if no public keys were preloaded; iterates signatures and trusted keys; skips revoked keys; validates with `otcore_validate_ed25519_signature`; and succeeds on the first valid pair. Loading with `filename` reads one trusted file; without it scans default or custom base directories for trusted and revoked keys.

State/persistence: instance state contains secret material and keyrings. `clear_keys` explicit-bzeros the secret key and frees key lists. Signatures persist outside this backend through generic detached metadata key/type macros. Default key discovery reads host/system files but does not write them.

Dependencies/integration: depends on `otcore` crypto wrappers, OpenSSL or libsodium conditionals, GLib/GObject/GVariant/GBytes/GList, libglnx, base64 decoding, `OstreeBlobReader`, and checksum hex utilities. Registered by `ostree-sign.c` when `HAVE_ED25519` is defined. Used by CLI signing, composefs signed-commit validation, summary signing, delta signing, and SignAPI verification.

Risks: `set_sk` calls `clear_keys`, which also clears public and revoked keys. OpenSSL signing constructs the private key from the seed portion while validating combined secret-key length, so key format conversion must remain intentional. Verification is O(signatures * trusted keys * revoked keys). Auto-loading default keyrings makes host state part of validation behavior. Builds without crypto support produce runtime errors for the engine.

Test signals: `tests/test-signed-commit-ed25519.sh`, `tests/test-delta-ed25519.sh`, composefs signed tests, and generic signed pull/commit paths cover signing, verification, metadata storage, default key loading, and failures.
