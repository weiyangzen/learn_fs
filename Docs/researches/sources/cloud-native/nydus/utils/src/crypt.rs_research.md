# sources/cloud-native/nydus/utils/src/crypt.rs

Purpose: feature-gated encryption utilities for Nydus data and metadata, supporting AES-128-XTS, AES-256-XTS, and AES-256-GCM through OpenSSL.

Important APIs/types/functions: constants define data unit, IV, key, tag, and padding sizes. `Algorithm` exposes cipher creation, encryption-enabled checks, AEAD checks, tag size, and key length. `Cipher` wraps OpenSSL cipher handles and supports `encrypt`, `decrypt`, `encrypt_aead`, `decrypt_aead`, `encrypted_size`, `tag_size`, `tweak_key_for_xts`, random key/IV generation, and internal `cipher`. `CipherContext` stores key, IV, convergent-encryption flag, and algorithm, with `new`, `generate_cipher_meta`, and `get_cipher_meta`. Top-level helpers `encrypt_with_context` and `decrypt_with_context` conditionally apply encryption based on a boolean.

Control flow: XTS encryption pads data shorter than 16 bytes to an 18-byte buffer containing a 16-byte CMS-like padded block plus a two-byte magic suffix, then decrypt trims only when this magic padding is present. AES-GCM is only available through AEAD-specific methods and returns/accepts a separate tag. `CipherContext::new` validates key length and rejects identical XTS key halves. Convergent metadata encryption can derive key material from data and substitutes default keys for symmetric halves. Random key generation uses OpenSSL RNG then tweaks XTS keys to avoid identical halves.

State and persistence: `CipherContext` stores key and IV in memory. Ciphertext/tag output may be persisted by callers. No key zeroization is visible.

Dependencies and integration points: depends on optional `openssl` feature, `std::sync::Arc`, and crate error macros. Used by encrypted blob/bootstrap metadata paths when `nydus-utils/encryption` is enabled.

Risks: `CipherContext::new` indexes `key[0..key_length >> 1]`; for `Algorithm::None` with zero-length key this is safe, but zero-length encryption context semantics should be reviewed. Internal `alloc_buf` does not handle allocation failure explicitly and creates a vector from possibly null pointer; unlike storage's allocator, it does not call `handle_alloc_error`. XTS padding returns 18 bytes for very small plaintext while `encrypted_size` reports 16 for plaintext smaller than 16, so callers relying on `encrypted_size` may under-allocate. AES-GCM uses 12-byte tags but tests pass 16-byte IVs; nonce policy must be enforced by callers. Error text for `decrypt_aead` says "failed to encrypt data".

Test signals: tests cover XTS encrypt/decrypt determinism, IV/data sensitivity, small and >16-byte data, AES-GCM encrypt/decrypt/tag behavior, key tweaking, algorithm attributes/parsing/conversions, context validation, optional encryption bypass, and convergent key generation.
