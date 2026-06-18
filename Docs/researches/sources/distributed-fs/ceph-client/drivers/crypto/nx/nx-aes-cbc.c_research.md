## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-cbc.c

Purpose: registers and implements `cbc(aes)` using IBM Power NX symmetric encryption hardware through the shared NX crypto context.

Important APIs: `cbc_aes_nx_set_key` initializes the CPB for AES CBC, records the key size property slot, and copies the key. `cbc_aes_nx_crypt` performs encrypt/decrypt loops. `nx_cbc_aes_alg` is the exported `skcipher_alg` descriptor consumed by `nx.o`.

Control flow: setkey calls `nx_ctx_init`, maps key lengths to NX key-size fields, selects `nx_ctx->ap`, sets CPB mode `NX_MODE_AES_CBC`, and stores the key. Encryption/decryption acquire `nx_ctx->lock`, set or clear `NX_FDM_ENDE_ENCRYPT`, repeatedly build NX scatterlists from the request at the current offset, reject empty in/out lists, issue `nx_hcall_sync`, copy the chaining value back to `req->iv`, update stats, and continue until the request length is processed.

State and persistence: per-transform state is the aligned CPB, key material, selected OF algorithm properties, and shared stats pointer. Per-request mutable state is the IV, which is updated for CBC chaining. No persistent storage exists.

Dependencies: depends on `nx_build_sg_lists`, `nx_hcall_sync`, CPB definitions from `nx_csbcpb.h`, AES key constants, and registration in `nx.o`.

Risks: CBC requires block-aligned request lengths, so caller-side crypto API validation and scatterlist trimming matter. Incorrect IV update breaks multi-call chaining. The CPB is reused across requests, making the spinlock mandatory. Stats use the CSB processed-byte count and depend on successful hardware completion.

Test signals: AES-CBC encrypt/decrypt vectors for 128/192/256-bit keys, multi-page scatterlists, partial processing bounded by OF `databytelen`, IV mutation checks, busy/error hcall paths, and concurrent request serialization on one transform.
