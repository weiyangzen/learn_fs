# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/hash.h

Purpose: provides small shared helpers for MD4, MD5, SHA1, SHA256, and SHA512 implementations.

Important APIs/types/functions: defines `min(a,b)`, `CRAYFIX()` for platforms where 32-bit arithmetic needs masking, `cshift(uint32_t,unsigned int)` for 32-bit rotates, and `cshift64(uint64_t,unsigned int)` for 64-bit rotates.

Control flow: digest compression functions call these inline rotate helpers inside round macros. There is no standalone runtime flow.

State and persistence: no state is stored. All helpers operate on values passed by caller.

Dependencies and integration points: includes `krb5-types.h` under `KRB5` and `roken.h` for portable integer and platform support. It is shared by the hash implementation files and centralizes portability behavior.

Risks and test signals: rotate helpers assume nonzero rotation counts less than word width as used by the digest algorithms. Tests are indirect: known-answer vectors for MD4/MD5/SHA1/SHA2 on little-endian, big-endian, and unusual integer platforms.
