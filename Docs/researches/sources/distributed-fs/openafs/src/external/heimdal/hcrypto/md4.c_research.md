# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/md4.c

Purpose: implements the legacy MD4 digest primitive.

Important APIs/types/functions: `MD4_Init`, private `calc` for the three MD4 rounds, endian `swap_uint32_t` on big-endian builds, `MD4_Update`, and `MD4_Final`. Round macros implement F/G/H functions and left rotations via `cshift`.

Control flow: update maintains a 64-bit bit count split across `sz[0]`/`sz[1]`, fills the 64-byte save buffer, transforms complete blocks, and handles endian conversion when needed. Final writes MD4 padding and little-endian length, feeds it through update, and serializes the four 32-bit state words little-endian.

State and persistence: context state consists of bit count, four counters, and one partial block. Unlike MD2, finalization does not explicitly zero the context after emitting output.

Dependencies and integration points: depends on `hash.h` and `md4.h`; exposed through deprecated EVP MD4 provider descriptors and used for compatibility protocols.

Risks and test signals: MD4 is broken cryptographically and should be compatibility-only. Alignment-sensitive casts to `uint32_t *` and bitfield helper structs need platform coverage. Test with standard MD4 vectors, segmented updates, big-endian behavior, and exact 55/56/64-byte padding boundaries.
