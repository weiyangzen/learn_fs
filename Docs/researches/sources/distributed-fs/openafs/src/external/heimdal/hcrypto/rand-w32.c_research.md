# sources/distributed-fs/openafs/src/external/heimdal/hcrypto/rand-w32.c

Purpose: implements the Windows CryptoAPI-backed `RAND_METHOD`.

Important APIs/types/functions: `_hc_CryptProvider` lazily initializes a global `HCRYPTPROV`; method callbacks are `w32crypto_seed`, `w32crypto_bytes`, `w32crypto_cleanup`, `w32crypto_add`, `w32crypto_status`; `RAND_w32crypto_method` returns the descriptor.

Control flow: provider acquisition tries `CryptAcquireContext` variants and publishes the selected provider with `InterlockedCompareExchangePointer`. `w32crypto_bytes` calls `CryptGenRandom`; pseudo-random bytes share the same callback. Seed/add are no-ops. Cleanup attempts to release the provider.

State and persistence: global volatile `g_cryptprovider` caches the CryptoAPI provider handle for the process. No random state file is used.

Dependencies and integration points: depends on Windows `wincrypt.h`, `rand.h`, Heimdal threading headers, and `randi.h`. `rand.c` selects this method by default on `_WIN32`.

Risks and test signals: provider acquisition error logic and compare-exchange cleanup deserve review because small mistakes can leak or fail to release provider handles; seed/add ignore caller entropy; CryptoAPI provider availability varies by platform. Tests should cover first-use initialization, concurrent initialization, cleanup/reinit, `CryptGenRandom` failure, and status reporting.
