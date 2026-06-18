# sources/distributed-fs/ceph-client/include/crypto/blake2b.h

Purpose: BLAKE2b hash library interface with keyed and unkeyed modes.

Important APIs/types/functions: `enum blake2b_lengths`, `struct blake2b_ctx`, IV constants, `__blake2b_init`, `blake2b_init`, `blake2b_init_key`, `blake2b_update`, `blake2b_final`, and one-shot `blake2b`.

Control flow: initialization seeds state with IV and parameter block; optional key is buffered as the first block; callers update with data and finalize to write `outlen` bytes while zeroizing context.

State and persistence: context stores hash state, counters, finalization flags, partial block buffer, buffer length, and output length.

Dependencies and integration points: depends on bug checks, types, and string helpers. Used by code needing a direct BLAKE2b primitive outside the crypto API tfm model.

Risks: debug `WARN_ON` checks do not enforce validity in production; callers must respect output/key length limits and non-null buffers. Context is sensitive and should not be copied after keying unless intended.

Test signals: BLAKE2b KATs, keyed/unkeyed vectors, split update tests, invalid-parameter debug tests, and context zeroization checks.
