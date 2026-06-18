## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-xcbc.c

Purpose: implements the `xcbc(aes)` shash algorithm using NX AES-XCBC-MAC hardware, including a software-assisted hardware ECB sequence for the zero-length message case.

Important types and APIs: `struct xcbc_state` stores the current MAC state. `nx_xcbc_set_key`, `nx_xcbc_init`, `nx_xcbc_update`, `nx_xcbc_finup`, `nx_xcbc_empty`, and `nx_crypto_ctx_aes_xcbc_init2` implement the shash lifecycle. `nx_shash_aes_xcbc_alg` exports the algorithm descriptor.

Control flow: transform init allocates the shared NX SHA/AES context, calls `nx_ctx_init`, sets AES-128 key size, and selects `NX_MODE_AES_XCBC_MAC`. Setkey accepts only AES-128. Update copies previous state into the CPB, marks intermediate/continuation, builds input and output scatterlists for block-aligned data, invokes hardware, and returns leftover bytes to the shash core. Final processes the final nonzero block with intermediate cleared; zero-length final calls `nx_xcbc_empty`, which temporarily switches to ECB mode to derive K1/K3 and calculate the RFC3566 tag.

State and persistence: the descriptor state holds the running MAC. The transform CPB stores key and temporary CV/MAC fields. No durable storage exists.

Dependencies: NX core hcall/scatterlist helpers, AES constants, CPB mode definitions, shash block-only semantics, and algorithm registration in `nx.o`.

Risks: only AES-128 keys are valid. The algorithm declares `CRYPTO_AHASH_ALG_BLOCK_ONLY` and `FINAL_NONZERO`, so update/final contracts depend on the shash core supplying appropriate lengths. The zero-length special path changes CPB mode/key and must restore both. Nested calls under the same spinlock are notable because `nx_xcbc_finup` calls `nx_xcbc_empty` while already locked.

Test signals: RFC3566 vectors, zero-length vector, invalid key sizes, update/finup splits, block-only behavior, leftover return values, CPB mode restoration after empty digest, and concurrent transform serialization.
