# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/memutils.c

Provides sensitive-memory helper primitives for the crypto backend.

Key points:
- Functions are marked noinline and optionally `zero_call_used_regs("used")` to reduce secret remnants in registers.
- `crypt_backend_memzero()` uses `explicit_bzero()` when available, except under MemorySanitizer workaround, otherwise volatile byte stores.
- `crypt_backend_memcpy()` uses volatile byte loads/stores to avoid extra register spilling of sensitive data.
- `crypt_internal_memeq()` performs constant-time XOR accumulation and returns zero on equality, nonzero on mismatch.

Storage relevance:
- Used throughout crypto code to copy and clear derived keys, hashes, HMAC outputs, PBKDF temporaries, and passphrase-derived buffers.
