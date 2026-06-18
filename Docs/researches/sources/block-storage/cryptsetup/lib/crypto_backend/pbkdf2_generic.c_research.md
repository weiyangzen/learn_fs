# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/pbkdf2_generic.c

Implements generic PKCS#5 PBKDF2 using cryptsetup’s HMAC interface.

Key points:
- `hash_buf()` hashes a buffer with a named cryptsetup hash.
- `pkcs5_pbkdf2()` implements PBKDF2 block derivation: compute `U_1...U_c`, XOR into `T`, and copy blocks into the derived key.
- Validates HMAC size, nonzero iteration count, nonzero output length, and bounded digest length by `MAX_PRF_BLOCK_LEN`.
- Optional `hash_block_size` pre-hashes long passwords before HMAC setup to avoid backend limitations or repeated long-key processing.
- Uses `alloca()` for salt-plus-block-index temporary and clears sensitive buffers before returning.
- Returns negative errno-style values.

Storage relevance:
- Fallback PBKDF2 core used by kernel/NSS and optionally gcrypt/OpenSSL builds.
- Directly affects passphrase-derived keys for LUKS and FileVault2 when internal PBKDF2 is selected.
