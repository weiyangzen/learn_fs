## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx-aes-ecb.c

Purpose: implements `ecb(aes)` through NX hardware.

Important APIs: `ecb_aes_nx_set_key` initializes key size, algorithm properties, CPB mode, and key bytes. `ecb_aes_nx_crypt` performs encrypt/decrypt hardware calls. `nx_ecb_aes_alg` exports the skcipher descriptor.

Control flow: setkey calls `nx_ctx_init`, maps AES key lengths to NX key size constants and property slots, sets `NX_MODE_AES_ECB`, and copies key bytes. Crypt takes the context lock, sets encrypt/decrypt direction in CPB flags, loops over request chunks bounded by OF limits and scatterlist capacity, issues synchronous hcalls, updates AES operation/byte counters, and releases the lock.

State and persistence: per-transform state is the CPB, key, selected algorithm properties, and stats pointer. ECB has no IV or request-persistent state.

Dependencies: uses NX core context initialization, scatterlist building, hcall submission, and crypto API registration performed in `nx.o`.

Risks: ECB is block-oriented and structurally simple, but it still depends on accurate scatterlist length trimming and nonzero hcall input/output lengths. The reused CPB must not be accessed concurrently without the spinlock. ECB mode has no semantic IV protection; it should be exposed only as the standard crypto API primitive.

Test signals: AES-ECB known-answer vectors for 128/192/256-bit keys, invalid key size rejection, large multi-page scatterlists, chunking at `databytelen`, hcall error propagation, and concurrent transform use.
