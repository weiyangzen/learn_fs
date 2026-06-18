# sources/distributed-fs/ceph-client/crypto/serpent_generic.c

Purpose: implements the generic Serpent block cipher and exports core setkey/encrypt/decrypt helpers for other architecture-specific or mode code.

Important APIs, types, and functions: exported functions are `__serpent_setkey()`, `serpent_setkey()`, `__serpent_encrypt()`, and `__serpent_decrypt()`. The implementation uses `struct serpent_ctx` from `<crypto/serpent.h>`, S-box macros `S0` through `S7`, inverse S-boxes `SI0` through `SI7`, linear transform macros, and key schedule helpers.

Control flow: setkey pads keys up to 256 bits with a `1` byte then zeros, loads little-endian words, expands 132 prekeys with the PHI recurrence, and applies S-boxes to produce round keys. Encryption reads a 16-byte little-endian block, applies initial key xor, 32 Serpent rounds with S-boxes and linear transforms, final key xor, and writes output. Decryption performs inverse rounds in reverse order.

State and persistence: expanded round keys persist in the tfm context. No request state is retained. Core helpers are exported for reuse.

Dependencies and integration points: depends on unaligned little-endian helpers, crypto cipher registration, and public Serpent header definitions. Registers as `serpent`/`serpent-generic`.

Risks: macro-heavy bit-sliced code is hard to review and vulnerable to compiler behavior; the key S-box phase is deliberately marked `noinline` due to past misoptimization. Key padding and round-key indexing are correctness-critical. Serpent is secure but less common than AES, so test coverage matters.

Test signals: official Serpent known-answer vectors for 128/192/256-bit keys, random encrypt/decrypt inverse tests, exported helper users, compiler matrix coverage, unaligned buffers, and module alias lookup.
