# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/crypto_kernel.c

Implements a Linux AF_ALG kernel crypto backend.

Key points:
- `crypt_backend_init()` requires Linux via `uname()`, builds a version string, and probes `AF_ALG` hash support with `sha256`.
- Supported hashes are table-driven with cryptsetup names, kernel names, digest lengths, and HMAC block lengths.
- Hash/HMAC contexts hold transform and operation sockets. `_get_alg()` maps cryptsetup names to kernel algorithm names.
- `crypt_kernel_socket_init()` creates/binds AF_ALG sockets, optionally sets the key, and accepts an operation fd.
- Hash and HMAC update with `send(..., MSG_MORE)` and finalize with `read()`.
- RNG is explicitly unavailable and returns `-EINVAL`.
- PBKDF2 delegates to generic `pkcs5_pbkdf2()` using each hash’s block size; Argon2 delegates to `argon2()`.
- Ciphers and BitLocker AES-CCM are kernel-only through `crypt_cipher_*_kernel()` and `crypt_bitlk_decrypt_key_kernel()`.
- Backend flags return `CRYPT_BACKEND_KERNEL`; FIPS status delegates to `crypt_fips_mode_kernel()`.

Storage relevance:
- Provides cryptsetup with a no-userspace-crypto path where hash/HMAC/cipher operations come from the Linux kernel.
- Timing code in `pbkdf_check.c` accounts for this backend by adding system CPU time.
