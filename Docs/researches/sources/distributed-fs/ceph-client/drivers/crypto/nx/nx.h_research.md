## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx.h

Purpose: declares the shared interface and state model for the NX symmetric/hash crypto driver.

Important types: `struct nx_sg` is the packed scatterlist format expected by pHyp. `enum nx_status`, `struct msc_triplet`, `struct max_sync_cop`, `struct alg_props`, and `struct nx_of` represent parsed OpenFirmware capabilities. `struct nx_stats` stores operation, byte, sync-call, and error counters. `struct nx_crypto_driver` is the module-level VIO/debugfs state. AEAD and mode-specific private structs store GCM/CCM request IVs, nonces, tags, XCBC key, and CTR nonce. `struct nx_crypto_ctx` is the per-transform workspace with aligned CPBs, VIO operation structs, NX SG pages, properties, stats, and private mode state.

Control flow and integration: algorithm wrappers include this header to call context initializers, `nx_ctx_init`, `nx_hcall_sync`, and scatterlist builders. `nx.o` includes it to define the global `nx_driver` and register external algorithm descriptors. Debugfs init/fini macros compile to no-ops without `CONFIG_DEBUG_FS`.

State and persistence: structures describe runtime-only module, transform, request, and stats state. There is no persistent storage. Some fields hold key material and must be freed with sensitive cleanup by exit paths.

Dependencies: crypto internal AEAD/hash/skcipher APIs, CTR helper constants, Power VIO definitions, and CPB constants from `nx_csbcpb.h` via implementation files.

Risks: this header is the ABI between many NX files; changing `struct nx_crypto_ctx` layout affects every algorithm descriptor's `cra_ctxsize`. `NX_MAX_SG_ENTRIES` assumes a 4K page for SG pages. Private union fields must not overlap in ways that wrappers misuse across modes. Debugfs macros must match function declarations.

Test signals: compile all NX algorithms with debugfs on/off, validate `cra_ctxsize` users after structure changes, run all AES/SHA/AEAD vectors, and use KASAN/KMSAN-style tests for context allocation/free and key cleanup.
