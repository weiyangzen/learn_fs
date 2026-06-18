## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-sha256.c

Purpose: implements the `sha256` shash algorithm using NX SHA hardware.

Important types and APIs: `struct sha256_state_be` stores the big-endian hardware digest words and byte count. `nx_crypto_ctx_sha256_init`, `nx_sha256_init`, `nx_sha256_update`, `nx_sha256_finup`, `nx_sha256_export`, and `nx_sha256_import` implement the shash lifecycle. `nx_shash_sha256_alg` exports the descriptor.

Control flow: transform init allocates a SHA context through `nx_crypto_ctx_sha_init`, initializes HCOP SHA state, selects the SHA256 property slot, and sets digest size in CPB. Descriptor init seeds SHA256 initial constants in big-endian form. Update locks the context, copies current digest into the CPB, marks intermediate/continuation, builds output scatterlist to descriptor state, repeatedly processes full SHA256 blocks through hardware, updates count, stores the new digest, and returns leftover bytes. Finup copies partial digest, clears intermediate, sets total bit length, builds input/output lists, calls hardware, updates stats, and copies final digest.

State and persistence: descriptor state persists digest and byte count across shash updates and can be exported/imported in CPU-endian format. Transform state is runtime CPB/scatterlist memory.

Dependencies: NX core context/hcall/scatterlist helpers, SHA2 constants, unaligned access helpers, CPB SHA definitions, and registration in `nx.o`.

Risks: update returns leftover length and relies on the shash core to retain unprocessed bytes. Endianness conversion in import/export is critical. The message bit length is a 64-bit `sctx->count * 8`; overflow behavior should match shash expectations. Zero-length final and partial-block handling need vector coverage.

Test signals: SHA256 known-answer vectors, streaming split at every byte around block boundaries, export/import round trips, zero-length digest, large updates bounded by OF limits, hcall failure propagation, and stats increments.
