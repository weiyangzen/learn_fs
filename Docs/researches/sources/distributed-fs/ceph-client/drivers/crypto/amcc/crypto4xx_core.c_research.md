# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_core.c

## Purpose

`crypto4xx_core.c` is the platform driver, descriptor-ring manager, interrupt/tasklet completion engine, algorithm registrar, and PRNG provider for AMCC/PPC4xx crypto hardware.

## Important APIs, Types, And Functions

Important functions include `crypto4xx_probe()`, `crypto4xx_remove()`, `crypto4xx_hw_init()`, `crypto4xx_build_{pdr,gdr,sdr}()`, descriptor get/put helpers, `crypto4xx_build_pd()`, `crypto4xx_cipher_done()`, `crypto4xx_aead_done()`, `crypto4xx_bh_tasklet_cb()`, interrupt handlers, `crypto4xx_register_alg()`, `crypto4xx_unregister_alg()`, `crypto4xx_sk_init()`, `crypto4xx_aead_init()`, and `crypto4xx_prng_generate()`. `crypto4xx_alg[]` registers AES skciphers, CCM/GCM AEAD, and `stdrng`.

## Control Flow

Probe resets supported PPC405EX/460EX/460SX crypto blocks through DCR registers, detects revision quirks, allocates core/device state, initializes locks and ratelimit, allocates SDR/PDR/GDR rings plus shadow SA/state pools, maps MMIO, requests IRQ, initializes hardware registers, registers algorithms, and probes optional TRNG. Request submission reserves contiguous gather/scatter/packet descriptors under spinlock, copies the requested SA into the packet's shadow SA, inserts IV and state-record pointers, maps source/destination or sets scatter buffers, marks the PD host-ready, and rings `CRYPTO4XX_INT_DESCR_RD`. IRQ clears status and schedules the tasklet; the tasklet walks completed PDs from tail, calls cipher or AEAD completion, frees ring descriptors, and completes CryptoAPI requests.

## State And Persistence Behavior

Persistent device state includes PDR/GDR/SDR rings, scatter bounce buffers, shadow SA and state-record pools, ring heads/tails, per-PD metadata, registered algorithm list, revision flag, PRNG/TRNG bases, locks, tasklet, IRQ, and hwrng pointer. Packet descriptors own temporary mappings until completion. PRNG generation reads hardware PRNG registers under `rng_lock`; seed callback is a no-op because hardware is seeded in `crypto4xx_hw_init()`.

## Dependencies And Integration Points

The file integrates OF platform probing, PowerPC DCR reset registers, DMA coherent/page mapping, scatterwalk, CryptoAPI skcipher/AEAD/RNG registration, tasklets, IRQs, optional TRNG, and AMCC-specific register/SA headers. Algorithm operations in `crypto4xx_alg.c` are thin wrappers over `crypto4xx_build_pd()`.

## Risks And Test Signals

Risks include descriptor-ring wrap bugs, DMA map leaks on partial setup failure, source mappings not explicitly unmapped in visible completion paths, `crypto4xx_get_n_sd()` comparing against `gdr_tail`, interrupt coalescing revision handling, AEAD tag copy/check offsets, busy/backlog return semantics, and optional TRNG lifetime. Test high-concurrency dm-crypt/IPsec workloads, ring exhaustion/backlog behavior, SG wrap-around, AEAD error tags, module remove, interrupt coalescing on RevA/RevB, PRNG reads, and DMA API debugging.
