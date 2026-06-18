## sources/distributed-fs/ceph-client/drivers/crypto/nx/nx.c

Purpose: is the shared core for the pSeries NX symmetric/hash crypto driver. It parses VIO/OpenFirmware capabilities, registers supported algorithms, allocates aligned per-transform workspaces, builds NX scatterlists, submits synchronous hypervisor coprocessor calls, records debug stats, and owns the VIO driver lifecycle.

Important APIs and types: `nx_hcall_sync`, `nx_build_sg_list`, `nx_walk_and_build`, `nx_build_sg_lists`, `nx_ctx_init`, `nx_crypto_ctx_*_init`, and `nx_crypto_ctx_*_exit` are shared by algorithm wrappers. OF parsing is handled by `nx_of_update_status`, `nx_of_update_sglen`, `nx_of_update_msc`, and `nx_of_init`. Registration helpers gate algorithms on parsed properties. `struct nx_crypto_driver nx_driver` is the global driver state.

Control flow: module init registers a VIO driver for `ibm,sym-encryption`. Probe rejects multiple devices, records the VIO device, parses OF properties, and calls `nx_register_algs`. Registration validates status/max-sg/max-sync-cop, initializes stats/debugfs, sets status OK, then registers ECB, CBC, CTR, GCM, RFC4106 GCM, CCM, RFC4309 CCM, SHA256, SHA512, and XCBC in order with unwind paths. Each transform init allocates a 4K-aligned CPB plus input/output SG pages, optionally a secondary AEAD CPB, copies OF properties into the context, and attaches stats.

State and persistence: global state is `nx_driver` with OF properties, stats, debugfs root, and VIO device. Per-transform state is allocated `kmem`, aligned CPBs, SG pages, property slots, private nonce/tag state, and stats pointer. No persistent storage exists.

Dependencies: IBM VIO hcalls, OF properties `status`, `ibm,max-sg-len`, `ibm,max-sync-cop`, Linux crypto APIs, debugfs, PowerPC physical address helpers, and algorithm descriptors declared in `nx.h`.

Risks: scatterlist trimming is complex and uses negative lengths to signal SG lists to pHyp; arithmetic mistakes can underprocess data or violate block alignment. Remove unregisters SHA256/SHA512 with swapped property-slot constants, which should be reviewed. `nx_crypto_ctx_aead_exit` frees memory but does not null pointers like the generic exit. OF parsing must reject malformed variable-length `max-sync-cop` properties without reading past the property.

Test signals: VIO probe/remove, OF property parser fuzzing, registration unwind on each algorithm failure, algorithm selftests, debugfs stat visibility, SG building for vmalloc and highmem-like page boundaries, hcall busy retry behavior, and module unload with active transforms.
