# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_gcrypt.c

Implements the libgcrypt backend for cryptsetup’s common crypto backend interface: hashes, HMACs, RNG, PBKDF, block ciphers, BitLocker AES-CCM key decrypt, constant-time compare, and FIPS detection.

Key points:
- `crypt_backend_init()` initializes libgcrypt, secure memory, backend version text, and runs a Whirlpool split-update compatibility test.
- Hash name compatibility maps BLAKE2 names and special `whirlpool_gcryptbug` handling through `crypt_hash_compat_name()`.
- Hash/HMAC contexts wrap `gcry_md_hd_t`; `*_final()` copies requested digest bytes and resets the context for reuse.
- RNG maps normal randomness to `GCRY_STRONG_RANDOM` and salt/key/default to `GCRY_VERY_STRONG_RANDOM`.
- PBKDF2 uses either internal `pkcs5_pbkdf2()` or `gcry_kdf_derive()`.
- Argon2 can use libgcrypt KDF support when available and not using internal Argon2; parallel mode supplies custom pthread dispatch/wait callbacks.
- Cipher initialization first tries libgcrypt ECB/CBC/XTS, then falls back to the kernel cipher backend.
- `crypt_bitlk_decrypt_key()` uses AES-CCM when `GCRY_CCM_BLOCK_LEN` exists, otherwise returns `-ENOTSUP`.
- `crypt_fips_mode()` is compiled out unless `ENABLE_FIPS`; enabled builds query `gcry_fips_mode_active()` after backend init.

Storage relevance:
- This is one selectable cryptsetup crypto provider used by LUKS, FileVault2, BitLocker, PBKDF calibration, and storage encryption helpers.
- Kernel fallback means algorithms unsupported by libgcrypt can still work through Linux crypto API where available.
