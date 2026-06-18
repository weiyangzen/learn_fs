# sources/distributed-fs/openafs/src/opr/ffs.h

Purpose: portable fallback implementations for finding first and last set bits in a 32-bit integer.

Important APIs/types/functions: `opr_ffs(int value)` returns one-based index of the least significant set bit or 0. `opr_fls(int value)` returns one-based index of the most significant set bit or 0.

Control flow: each function casts to unsigned 32-bit to avoid signed-shift undefined behavior, then loops until a set bit is found.

State and persistence: no state.

Dependencies/integration: depends on OpenAFS integer typedefs being visible. Installed as `opr/ffs.h`.

Risks and test signals: assumes 32-bit `afs_uint32` semantics and returns positions in the BSD convention. Unit tests should cover 0, powers of two, negative `int`, and all-bits-set values.
