# sources/distributed-fs/lustre-release/lustre/ptlrpc/gss/gss_sk_mech.c

Purpose: implements Lustre's shared-key (`sk`) GSS mechanism, supporting null/auth/integrity/privacy subflavors with HMACs and optional encrypted message/bulk payloads.

Important APIs/types/functions: `struct sk_ctx` stores selected crypt/hash algorithms, expiry, host/peer random nonces, IV counter, HMAC key, and session keyblock. `struct sk_hdr` carries message version and IV. `sk_fill_context()` parses user-space serialized shared-key context data. `sk_fill_header()`, `sk_verify_header()`, and `sk_construct_rfc3686_iv()` manage IV/nonce construction. MIC operations use `sk_make_hmac()` and `sk_verify_hmac()`. Message privacy uses `gss_wrap_sk()`/`gss_unwrap_sk()`. Bulk privacy uses `gss_prep_bulk_sk()`, `sk_encrypt_bulk()`, `sk_decrypt_bulk()`, `gss_wrap_bulk_sk()`, and `gss_unwrap_bulk_sk()`. `init_sk_module()` registers `skn`, `ska`, `ski`, and `skpi`.

Control flow: import validates interface version, HMAC algorithm, encryption algorithm, expiry delta, random nonces, HMAC key length, and optional session key; privacy initializes a skcipher transform. Reverse copy duplicates keys but starts IVs at `SK_IV_REV_START` so forward and reverse contexts do not reuse counter ranges with the same key. Wrap pads plaintext, fills a header, encrypts with an RFC3686-style IV, and HMACs header/GSS header/ciphertext. Unwrap validates the header and HMAC before decryption. Bulk HMAC verification hashes only the sender's declared byte count rather than all allocated encrypted pages.

State/persistence: per-context keys, algorithm ids, expiry, random nonces, and atomic IV counter are in memory. No disk persistence. IV monotonicity is critical security state.

Dependencies/integration: compiled only when SSK support is enabled. Uses Lustre crypto algorithm name mapping, `gss_crypto.c`, Linux skcipher/ahash, PTLRPC bulk descriptors, and GSS mechanism dispatch.

Risks/test signals: IV reuse is explicitly fatal; counter wrap returns failure. Header stores use `be64_to_cpu()` when filling and `cpu_to_be64()` when verifying, which should be tested for endian correctness. Tests should cover malformed serialized contexts, unsupported algorithms, short HMAC keys, privacy absent/present, reverse IV range, MIC mismatch, token shortness, block padding, bulk byte-count HMAC, adjusted vectors, and counter wrap.
