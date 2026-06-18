# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_core.h

## Purpose

`crypto4xx_core.h` defines the shared state, ring sizes, descriptor metadata, context structures, prototypes, and endian-copy helpers for the PPC4xx crypto driver.

## Important APIs, Types, And Functions

Key definitions include ring sizes (`PPC4XX_NUM_PD/GD/SD`), descriptor states, reset constants, `union shadow_sa_buf`, `struct pd_uinfo`, `struct crypto4xx_device`, `struct crypto4xx_core_device`, `struct crypto4xx_ctx`, `struct crypto4xx_aead_reqctx`, `struct crypto4xx_alg_common`, and `struct crypto4xx_alg`. It declares `crypto4xx_build_pd()`, SA allocation/free, AES/AEAD operations, and endian helpers `crypto4xx_memcpy_{to,from}_le32()`.

## Control Flow

The header has no standalone runtime flow. It defines how algorithm code calls core packet submission and how core code tracks rings, requests, algorithm registration, PRNG/TRNG integration, and fallback cipher state.

## State And Persistence Behavior

Persistent state includes ring memory, ring heads/tails, shadow SA/state pools, per-PD async request metadata, algorithm list, ratelimit state, revision flag, hwrng pointer, tasklet, spinlock, and RNG mutex. `struct crypto4xx_ctx` persists per TFM SA buffers and fallback algorithm handles.

## Dependencies And Integration Points

It includes CryptoAPI internal skcipher/AEAD/RNG headers, scatterlists, mutexes, ratelimit, and the driver register/SA headers. The GCC access attribute on `crypto4xx_build_pd()` helps static checking of IV buffer length.

## Risks And Test Signals

Risks include fixed ring sizes and 256-byte shadow SA pool assumptions, packed SA aliasing, endian helper use on unaligned buffers, missing source DMA fields in `pd_uinfo`, and context union misuse between skcipher and AEAD. Test compile with GCC/Clang, sparse, DMA API debugging, all algorithm init/exit paths, and high descriptor pressure.
