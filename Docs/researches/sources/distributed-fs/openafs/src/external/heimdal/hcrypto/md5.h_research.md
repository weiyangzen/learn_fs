# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md5.h

Purpose: declares the MD5 digest API and context structure.

Important APIs/types/functions: defines `MD5_DIGEST_LENGTH` as 16, `struct md5` with split size, four counters, and 64-byte save buffer, typedefs `MD5_CTX`, and declares renamed `MD5_Init`, `MD5_Update`, and `MD5_Final`.

Control flow: consumers use standard init/update/final sequencing.

State and persistence: context persists partial input, bit counters, and compression state between updates.

Dependencies and integration points: included by `md5.c` and EVP provider descriptors.

Risks and test signals: layout drift and unsafe modern use are primary risks. MD5 known-answer and segmented-update tests validate implementation behavior.
