## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/camellia.c

Purpose: OpenSSL-like Camellia compatibility wrapper over the NTT core.

Important APIs/functions: `CAMELLIA_set_key()` stores the bit length and calls `Camellia_Ekeygen()`. `CAMELLIA_encrypt()` and `CAMELLIA_decrypt()` call block encrypt/decrypt using `key->bits` and `key->key`. `CAMELLIA_cbc_encrypt()` implements CBC encryption/decryption with mutable IV and partial final block handling similar to `aes.c`.

Control flow: set-key expands raw user key into the `CAMELLIA_KEY` key table and returns `1` unconditionally. CBC encryption XORs plaintext with IV, encrypts, stores ciphertext, and updates IV; partial final encryption fills remaining block bytes from IV. CBC decryption saves ciphertext, decrypts, XORs with IV, emits requested bytes, and updates IV to ciphertext.

State and persistence: caller-owned `CAMELLIA_KEY` persists the key length and expanded table. CBC mutates caller IV. No global mutable state.

Dependencies: `config.h`, optional `krb5-types.h`, `<string.h>`, `camellia-ntt.h`, `camellia.h`, and `roken.h`.

Integration points: used by `evp-hcrypto.c` for Camellia CBC ciphers and by callers expecting OpenSSL-like `CAMELLIA_*` functions renamed to `hc_`.

Risks: `CAMELLIA_set_key()` does not validate key size and always returns success, even though the NTT core ignores unsupported bit lengths. Partial-block CBC behavior is not padding-compatible with all protocols. No null-pointer guards. IV mutation means callers must manage IV reset for separate messages.

Test signals: known-answer block tests, CBC round trips for aligned and partial lengths, IV mutation checks, invalid bit-length behavior, and EVP Camellia descriptor tests.
