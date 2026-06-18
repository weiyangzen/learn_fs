## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-sha512.c

Purpose: implements the `sha512` shash algorithm using NX SHA hardware.

Important types and APIs: `struct sha512_state_be` stores big-endian SHA512 state and a two-word byte count. Lifecycle functions are `nx_crypto_ctx_sha512_init`, `nx_sha512_init`, `nx_sha512_update`, `nx_sha512_finup`, `nx_sha512_export`, and `nx_sha512_import`. `nx_shash_sha512_alg` is the exported descriptor.

Control flow: transform init selects SHA function/mode, property slot `NX_PROPS_SHA512`, and digest size `NX_DS_SHA512`. Init seeds SHA512 constants. Update locks the context, copies current digest into the CPB, marks intermediate/continuation, builds output scatterlist to descriptor state, processes full SHA512 blocks, increments a two-word byte counter on wrap, stores hardware digest output, and returns leftover bytes. Finup computes high/low bit length from the two-word count plus final bytes, builds input/output scatterlists, calls hardware, updates stats, and copies final digest.

State and persistence: descriptor state persists digest and 128-bit-ish byte count across updates and can be exported/imported with endian conversion. Transform CPB and scatterlists are runtime-only.

Dependencies: NX core helpers, SHA512 constants, unaligned access helpers, CPB SHA512 fields, and algorithm registration in `nx.o`.

Risks: high-count arithmetic is subtle; `count1` is incremented on update wrap and then shifted into bit length in final. Export/import must preserve both count words. As with SHA256, leftover return semantics and OF-limited chunking must match shash core behavior. The final path does not explicitly verify `len == SHA512_DIGEST_SIZE` after building the output SG, unlike SHA256.

Test signals: SHA512 known-answer vectors, split-update fuzzing around 128-byte block boundaries, very large simulated count/import cases, export/import round trips, zero-length digest, hcall error propagation, and output scatterlist length checks.
