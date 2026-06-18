# File Research: sources/cow-pools/bcachefs-tools/include/crypto/sha2.h

Purpose: kernel-style SHA constants, state structs, and SHA helper declarations for tools builds.

Key contents:
- Defines digest and block sizes for SHA1, SHA224, SHA256, SHA384, and SHA512.
- Defines initial hash constants for SHA1/SHA224/SHA256/SHA384/SHA512.
- Declares zero-message hash arrays.
- Defines SHA1/SHA256/SHA512 state structures.
- Declares update/finup functions for SHA1/SHA256/SHA512.
- Provides inline `sha256()` backed by libsodium `crypto_hash_sha256()`.

Important interactions:
- Lets bcachefs code compile against kernel-like SHA names while delegating SHA256 one-shot hashing to libsodium.
