# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/sha.c

Purpose: implements SHA-1.

Important APIs/types/functions: `SHA1_Init`, private `calc` for the 80-round compression function, endian `swap_uint32_t` for little-endian/Cray handling, `SHA1_Update`, and `SHA1_Final`.

Control flow: initialization sets SHA-1 initial constants and clears bit count. Update tracks bit length, buffers data into 64-byte blocks, endian-swaps into 32-bit words when needed, and compresses. Final writes SHA-1 padding and big-endian length, processes it, and serializes five 32-bit words big-endian.

State and persistence: `struct sha` stores split bit count, five counters, and a 64-byte save buffer. Finalization does not explicitly zero the context.

Dependencies and integration points: depends on `hash.h` and `sha.h`; exposed through EVP SHA/SHA1 descriptors, HMAC-SHA1, PBKDF2-HMAC-SHA1, and validation.

Risks and test signals: SHA-1 is collision-broken for signatures but still appears in compatibility KDF/HMAC contexts. Alignment/endian paths require testing. Use FIPS/RFC SHA-1 vectors, segmented updates, large inputs, and HMAC/PBKDF2 integration signals.
