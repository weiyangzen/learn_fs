## sources/distributed-fs/openafs/src/external/heimdal/hcrypto/aes.c

Purpose: OpenSSL-compatible AES wrapper over Heimdal's bundled Rijndael implementation. Provides key setup, single-block encrypt/decrypt, CBC mode, and CFB8 mode.

Important APIs/functions: `AES_set_encrypt_key()` and `AES_set_decrypt_key()` populate `AES_KEY.rounds` and `AES_KEY.key` via `rijndaelKeySetupEnc/Dec`, returning `-1` when the round count is zero. `AES_encrypt()` and `AES_decrypt()` call `rijndaelEncrypt/Decrypt`. `AES_cbc_encrypt()` implements encrypt/decrypt CBC with mutable IV. `AES_cfb8_encrypt()` implements byte-wise CFB8 using AES encryption for both directions.

Control flow: CBC encryption XORs each plaintext block with IV, encrypts, writes ciphertext, and updates IV to ciphertext. Partial final input is handled by XORing available bytes and filling the rest of the block from IV before encrypting a full block. CBC decryption saves the ciphertext block, decrypts, XORs with IV, and updates IV to the saved ciphertext; partial final input decrypts a full temporary block but emits only requested bytes. CFB8 loops one byte at a time, encrypts the IV, XORs the first keystream byte, and shifts either ciphertext input or output into IV depending on direction.

State and persistence: caller-owned `AES_KEY` persists expanded key material. CBC and CFB8 mutate caller-provided `iv` in place, so callers must preserve/reset IV externally for independent messages. No global state or files.

Dependencies: `config.h`, optional `krb5-types.h`, `<string.h>`, `rijndael-alg-fst.h`, and `aes.h`.

Integration points: used directly through the `hc_`-renamed AES symbols and indirectly by `evp-hcrypto.c` EVP cipher descriptors. Matches familiar OpenSSL function names through macros in `aes.h` while avoiding symbol collisions.

Risks: `AES_set_*_key()` does not validate null pointers. CBC partial-block behavior is non-standard for protocols requiring explicit padding; encryption emits a whole final block even when `size` is not a multiple of 16, while decryption emits only `size` bytes. The function signatures use `unsigned long size`, but CFB8 loop uses `int i`, which can overflow/truncate on very large sizes. In-place operation should be reviewed for each mode because some loops read/write advancing pointers.

Test signals: NIST AES known-answer vectors for 128/192/256 keys, CBC round trips with block-aligned and partial lengths, IV mutation checks, CFB8 vectors and encrypt/decrypt symmetry, invalid key-size path returning `-1`, and EVP integration through `EVP_hcrypto_aes_*`.
