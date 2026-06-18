# sources/distributed-fs/ceph-client/include/crypto/blake2s.h

Purpose: BLAKE2s hash library interface with keyed and unkeyed modes.

Important APIs/types/functions: `enum blake2s_lengths`, `struct blake2s_ctx`, IV constants, `__blake2s_init`, `blake2s_init`, `blake2s_init_key`, `blake2s_update`, `blake2s_final`, and one-shot `blake2s`.

Control flow: initialization configures IV-derived state and buffers an optional key block; update processes message bytes; finalization emits the configured digest length and zeroizes context.

State and persistence: context stores 32-bit state words, counters, finalization words, partial block, buffer length, and output length.

Dependencies and integration points: depends on kconfig, bug, types, and string helpers; used by in-kernel direct BLAKE2s users.

Risks: production callers must validate lengths because debug warnings are not hard errors. Keyed contexts contain secret material in the buffer until finalization.

Test signals: BLAKE2s KATs, keyed vectors, incremental update equivalence, and finalization zeroization tests.
