# sources/distributed-fs/ceph-client/tools/perf/util/blake2s.h

Purpose: declares the BLAKE2s context, IV constants, inline initialization helpers, and streaming API.

Important APIs and types: `struct blake2s_ctx` stores hash state, counters, finalization flags, buffer, buffer length, and output length. `enum blake2s_iv` provides the eight 32-bit IV constants. `blake2s_init()` initializes unkeyed hashing, `blake2s_init_key()` initializes keyed hashing, and `blake2s_update()`/`blake2s_final()` complete the streaming API.

Control flow: initialization sets the parameter block into `h[0]`, clears counters and flags, sets output length, and, for keyed hashing, preloads a full padded key block so the first update/final path processes it correctly.

State and persistence: context state is caller-owned. The header does not allocate or persist anything globally.

Dependencies and integration points: depends on Linux integer types and string routines. Consumers include code that needs a compact in-tree hash without linking external crypto libraries.

Risks: no explicit validation enforces maximum BLAKE2s digest or key sizes; misuse can overrun `ctx->buf` during keyed init if caller passes an invalid key length. The inline init is part of each translation unit and must stay in sync with the compression implementation.

Test signals: compile with all consumers, run known-answer vectors through both keyed and unkeyed init paths, and test invalid or boundary sizes where callers constrain inputs.
