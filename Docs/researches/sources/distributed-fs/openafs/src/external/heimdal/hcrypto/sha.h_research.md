# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha.h

Purpose: declares SHA-1, SHA-256, SHA-384, and SHA-512 contexts, digest lengths, and streaming APIs.

Important APIs/types/functions: defines `SHA_DIGEST_LENGTH`, `SHA256_DIGEST_LENGTH`, `SHA384_DIGEST_LENGTH`, `SHA512_DIGEST_LENGTH`; declares `struct sha`, `struct hc_sha256state`, and `struct hc_sha512state`; typedefs `SHA_CTX`, `SHA256_CTX`, `SHA512_CTX`, and `SHA384_CTX`; and prototypes init/update/final functions with symbol renaming.

Control flow: consumers use init/update/final streaming calls; SHA384 reuses the SHA512 state shape.

State and persistence: contexts store bit counts, compression counters, and partial block buffers sized to the algorithm block size.

Dependencies and integration points: shared by SHA implementation files, Fortuna, EVP provider descriptors, HMAC, and PBKDF2.

Risks and test signals: layout compatibility and endian behavior are key. Known-answer vectors for all SHA variants plus segmented-update tests validate it.
