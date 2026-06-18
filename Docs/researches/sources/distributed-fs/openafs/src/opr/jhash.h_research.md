# sources/distributed-fs/openafs/src/opr/jhash.h

Purpose: OpenAFS wrapper around Bob Jenkins lookup3 hash routines for integers and opaque byte buffers.

Important APIs/types/functions: macros `opr_jhash_size`, `opr_jhash_mask`, `opr_jhash_rot`, `opr_jhash_mix`, and `opr_jhash_final`; inline functions `opr_jhash`, `opr_jhash_int`, `opr_jhash_int2`, and `opr_jhash_opaque`.

Control flow: hash functions initialize Jenkins state, process input in 12-byte or three-word blocks, then use switch fallthrough to mix trailing input. Opaque hashing reads bytes little-endian into 32-bit accumulators.

State and persistence: pure functions with no global state.

Dependencies/integration: uses OpenAFS integer typedefs and `AFS_FALLTHROUGH`. `opr_cache` uses `opr_jhash_opaque` for keys; `uuid.c` uses it for UUID hashes.

Risks and test signals: not cryptographic. `opr_jhash` expects word-aligned `afs_uint32` input if the platform requires alignment; use `opr_jhash_opaque` for arbitrary buffers. Regression tests should use fixed vectors for stability.
