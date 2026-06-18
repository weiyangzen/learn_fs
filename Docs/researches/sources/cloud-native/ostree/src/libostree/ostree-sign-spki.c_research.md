# sources/cloud-native/ostree/src/libostree/ostree-sign-spki.c

Purpose: implements the SPKI `OstreeSign` backend using OpenSSL primitives. It signs data with DER private keys and verifies signatures against DER SubjectPublicKeyInfo public keys loaded from explicit variants or trusted/revoked key files.

Important APIs/types/functions: `OstreeSignSpki` stores support state, a `GBytes` secret key, trusted public keys, and revoked keys. `_ostree_sign_spki_is_initialized` gates operations. `ostree_sign_spki_data` decodes a private key with `d2i_AutoPrivateKey`, signs with `EVP_DigestSign`, and returns variable-length signature bytes. `ostree_sign_spki_data_verify` checks signatures with `otcore_validate_spki_signature`. Key setters accept base64 string or bytestring variants. Loading helpers use `ostree_sign_read_pk` and scan `trusted.spki`, `trusted.spki.d`, `revoked.spki`, and `revoked.spki.d`.

Control flow: init marks the engine unsupported unless OpenSSL is compiled and initialized. Signing validates initialization and key presence, decodes private key DER, probes signature length, signs into an allocated buffer, and returns failure if no signature is produced. Verification validates input and metadata type, auto-loads keys if needed, iterates signatures and trusted keys, skips revoked entries, and returns success on the first valid signature. Loading with `filename` reads one trusted file; otherwise it scans default or custom base directories.

State/persistence: instance key state is in memory. `clear_keys` attempts to zero secret-key data and unrefs key lists. Signatures persist through generic detached metadata key/type macros. Default keyrings are read-only inputs.

Dependencies/integration: depends on OpenSSL EVP/DER decoding, `otcore` SPKI validation/init, GLib/GObject/GBytes/GVariant/GList, libglnx, PEM parsing through `ostree_sign_read_pk`, and checksum hex utilities. Registered when `HAVE_SPKI` is defined.

Risks: arbitrary SPKI DER has no simple length validation, so invalid material fails during OpenSSL decode/verify. `_spki_add_revoked` appears to call `g_list_find_custom` with raw key data while using `g_bytes_compare`, which expects `GBytes` values and deserves review. `clear_keys` zeroes data from `g_bytes_unref_to_data` but does not free it afterward, which may leak storage. Auto-loading host keyrings makes verification environment-dependent.

Test signals: `tests/test-signed-commit-spki.sh` covers SPKI builds. Generic summary/pull signature tests also apply when SPKI is selected. Additional targeted tests should cover revoked SPKI matching and malformed DER/PEM keys.
