# sources/distributed-fs/openafs/src/external/heimdal/roken/ct.c

Purpose: implements a constant-time memory equality check.

Important APIs/types/functions: `ct_memcmp(const void *p1, const void *p2, size_t len)` returns 0 if equal and nonzero otherwise.

Control flow: iterates over all bytes, ORs every XOR difference into an accumulator, and returns `!!r`. It does not early-exit on the first difference.

State and persistence behavior: stateless and read-only over the input buffers.

Dependencies and integration points: used by krb5 checksum verification paths and `krb5_data_ct_cmp()` to avoid leaking the position of the first mismatching byte.

Risks: the return value is equality-oriented, not lexicographic like `memcmp()`, and the comments warn it must not be used for ordering. Constant-time behavior still depends on compiler code generation but the source avoids data-dependent branches.

Test signals: equal/unequal buffers, zero length, differing first and last byte, and consumers that expect only zero/nonzero semantics.
