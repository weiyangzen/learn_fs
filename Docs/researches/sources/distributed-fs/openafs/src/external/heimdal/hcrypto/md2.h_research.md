# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md2.h

Purpose: declares the MD2 context, digest length, and init/update/final functions.

Important APIs/types/functions: defines `MD2_DIGEST_LENGTH` as 16, `struct md2` with length, partial data, checksum, and state arrays, typedefs `MD2_CTX`, and symbol-renames `MD2_Init`, `MD2_Update`, and `MD2_Final`.

Control flow: consumers use the standard streaming digest sequence init, one or more updates, then final.

State and persistence: the context carries partial block and checksum state across updates; finalization in `md2.c` clears it.

Dependencies and integration points: included by `md2.c` and EVP provider descriptors.

Risks and test signals: ABI/layout drift and accidental use for modern security are the main risks. Compile coverage and MD2 known-answer vectors validate behavior.
