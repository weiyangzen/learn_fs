# sources/distributed-fs/ceph-client/crypto/md4.c

Purpose: implements the MD4 message digest as a synchronous hash (`shash`) algorithm named `md4`/`md4-generic`.

Important APIs, types, and functions: `struct md4_ctx` holds four hash words, a 16-word block buffer, and a byte counter. `md4_init()`, `md4_update()`, `md4_final()`, `md4_transform_helper()`, and `md4_transform()` implement the shash lifecycle. The algorithm is registered through `crypto_register_shash()`.

Control flow: init sets RFC 1320 IV constants. Update accumulates input into a 64-byte block, processes full blocks after little-endian conversion, and stores the trailing partial block. Final appends `0x80`, zero padding, and a 64-bit bit length, processes the final block(s), writes little-endian digest bytes, and clears the context.

State and persistence: digest state lives only in the shash descriptor context. Module registration persists the algorithm while loaded. Finalization zeroes the context to avoid retaining intermediate material.

Dependencies and integration points: uses `crypto/internal/hash.h`, endian helpers, and module registration. Consumers include legacy protocols that still need MD4, such as NTLM-related code.

Risks: MD4 is cryptographically broken and should not be used for new integrity designs. Padding and byte counter logic are sensitive around 56-byte and 64-byte boundaries. This implementation has no export/import state support, unlike newer hash wrappers in this subset.

Test signals: RFC 1320 vectors, partial update versus single-shot equivalence, boundary message lengths around block and padding sizes, and crypto API registration under `md4`.
