# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md4.h

Purpose: declares the MD4 digest API and context shape.

Important APIs/types/functions: defines `MD4_DIGEST_LENGTH` as 16, `struct md4` with split size, four-word counter, and 64-byte save buffer, typedefs `MD4_CTX`, and renames `MD4_Init`, `MD4_Update`, and `MD4_Final` to hcrypto symbols.

Control flow: callers use init/update/final streaming semantics.

State and persistence: the context preserves bit count, compression state, and partial block across updates.

Dependencies and integration points: consumed by `md4.c` and provider EVP descriptors.

Risks and test signals: context layout and deprecated algorithm exposure are the key risks. Build coverage and MD4 known-answer vectors validate it.
