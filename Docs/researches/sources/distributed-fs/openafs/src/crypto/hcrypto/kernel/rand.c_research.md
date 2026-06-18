# sources/distributed-fs/openafs/src/crypto/hcrypto/kernel/rand.c

This file implements the kernel-facing hcrypto RAND interface. It defines global `afs_kmutex_t hckernel_mutex`, initializes it in `init_hckernel_mutex`, optionally uses Heimdal Fortuna on AIX/DragonFlyBSD/HPUX/SGI, and otherwise reads random bytes through `osi_readRandom`.

Important functions are `RAND_seed`, which seeds Fortuna only under `USE_FORTUNA`, and `RAND_bytes`, which returns failure for zero-size requests, delegates to Fortuna when enabled, or calls `osi_readRandom` and returns success when that read succeeds. State is the mutex and, on selected platforms, Fortuna internal PRNG state.

Dependencies are kernel hcrypto headers, `heim_threads.h`, `osi_readRandom`, and platform macros. Integration is Kerberos/RFC3961 key generation and kernel crypto. Risks include interpreting `osi_readRandom` return semantics correctly, no explicit locking around `RAND_bytes` in this file, and platform divergence between Fortuna and direct kernel RNG. Test signals are kernel RNG availability tests, seeded Fortuna behavior on listed platforms, and encryption key generation tests under low-entropy boot conditions.
