# sources/distributed-fs/ceph-client/include/crypto/ghash.h

Purpose: GHASH block and digest size constants.

Important APIs/types/functions: `GHASH_BLOCK_SIZE` and `GHASH_DIGEST_SIZE`, both 16 bytes.

Control flow: none.

State and persistence: none.

Dependencies and integration points: included by GHASH/POLYVAL and GCM code for common sizing.

Risks: consumers must still respect GHASH format and padding rules defined elsewhere; this header only provides sizes.

Test signals: compile-time size assertions in GHASH/GCM users and AEAD vectors.
