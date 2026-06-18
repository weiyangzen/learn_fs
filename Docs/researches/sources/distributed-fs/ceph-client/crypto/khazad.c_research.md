<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/khazad.c -->
# sources/distributed-fs/ceph-client/crypto/khazad.c

Purpose: Implements the generic Khazad 64-bit block cipher with a 128-bit key for the kernel crypto API.

Important APIs/types/functions: `struct khazad_ctx` stores encryption and decryption round-key arrays. Large `T0` through `T7` lookup tables and constants `c[]` implement the Khazad round transformations. `khazad_setkey()` derives encryption keys and inverse decryption keys. `khazad_crypt()` applies the 8-round table-based permutation. `khazad_encrypt()` and `khazad_decrypt()` select the round-key array. `khazad_alg` registers `khazad-generic`.

Control flow: Module init registers the cipher. Setkey reads two big-endian 64-bit halves, iterates constants to fill `E[]`, then derives `D[]` from reversed encryption keys through table substitutions. Runtime crypt XORs the initial round key, runs rounds 1 through 7 with full T-table mixing, performs a final masked table round, and writes the big-endian output block.

State and persistence behavior: Per-transform state is the expanded key schedule only. All T-tables and constants are static module data. There is no IV, request context, or durable state.

Dependencies and integration points: Uses the classic crypto cipher API, unaligned big-endian helpers, Linux module registration, and any mode wrapper that can use an 8-byte block cipher by name.

Risks: Khazad is a legacy/niche cipher and should not be selected for new designs without a protocol requirement. Table lookups are secret-dependent and may be side-channel relevant. Key length is fixed at 16 bytes and relies on the crypto API to enforce min/max sizes. The 64-bit block size limits safe data volume in block modes.

Test signals: Khazad known-answer vectors, encrypt/decrypt inverse tests, unaligned input/output tests, module registration by name, and mode-wrapper tests over 8-byte blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/crypto/khazad.c -->
