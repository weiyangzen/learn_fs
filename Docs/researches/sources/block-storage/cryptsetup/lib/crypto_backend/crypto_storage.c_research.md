# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_storage.c

Implements generic userspace storage encryption wrappers and dm-crypt-compatible IV generation.

Key points:
- `crypt_sector_iv` models IV modes: none, null, plain, plain64, ESSIV, BENBI, plain64be, and EBOIV.
- `crypt_storage` stores sector size, IV shift, main cipher, and IV helper state.
- Sector size must be a power of two from 512 through 4096 bytes.
- `crypt_storage_init()` accepts standard cipher/mode strings and `capi:` strings, splits cipher mode from IV suffix, initializes the main cipher, and initializes IV state.
- ESSIV derives an IV encryption key by hashing the data key and initializing an ECB cipher.
- EBOIV initializes an ECB cipher with the data key and shifts by sector-size log2.
- `crypt_sector_iv_generate()` writes endian-specific sector IVs and encrypts ESSIV/EBOIV IV blocks.
- Encrypt/decrypt functions require aligned lengths and IV offsets, then process sector-by-sector in place.
- `crypt_storage_kernel_only()` reports whether the underlying cipher is kernel-only.

Storage relevance:
- This is the userspace mirror of dm-crypt sector-IV handling, useful for metadata parsing, tests, and non-device-mapper transformations.
