# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/sun8i-ce.h

## Purpose

`sun8i-ce.h` is the shared interface and hardware contract for the Allwinner CE driver. It defines register offsets, algorithm/control bits, error bits, descriptor layout, SoC variant description, device/flow/request/TFM state, address conversion helpers, and cross-file function prototypes.

## Important APIs, Types, And Functions

Important types include `struct ce_variant`, `struct ce_task`, `struct sginfo`, `struct sun8i_ce_flow`, `struct sun8i_ce_dev`, `struct sun8i_cipher_req_ctx`, `struct sun8i_cipher_tfm_ctx`, `struct sun8i_ce_hash_tfm_ctx`, `struct sun8i_ce_hash_reqctx`, `struct sun8i_ce_rng_tfm_ctx`, and `struct sun8i_ce_alg_template`. `desc_addr_val()` and `desc_addr_val_le32()` abstract H616-style word addresses. Prototypes connect the core, cipher, hash, PRNG, and TRNG implementation files.

## Control Flow

The header itself has no runtime flow, but it defines the descriptor and state fields consumed by all runtime paths: core code allocates flows and descriptors, cipher/hash fill `ce_task` source/destination entries, PRNG/TRNG use flow 3, and all paths call `sun8i_ce_run_task()`. Variant flags influence descriptor address encoding and length units.

## State And Persistence Behavior

The structures define all persistent driver state: device-level clocks/reset/MMIO/debug/hwrng state, per-flow completions and coherent descriptor memory, TFM-level keys or fallback TFMs, request-level DMA mappings, and RNG seed storage. Descriptor layout is packed and aligned to the hardware ABI.

## Dependencies And Integration Points

The header integrates CryptoAPI AES/DES/skcipher/hash/rng headers, debugfs, hwrng, atomics, and SHA/MD5 constants. Its constants bind driver code to CE register semantics, supported algorithm IDs, maximum scatterlist count, clock count, DMA timeout, and flow count.

## Risks And Test Signals

Risks include ABI drift in packed descriptor layout, wrong enum indexes into variant capability arrays, mismatched comments (`hash_t_dlen_in_bytes` vs `hash_t_dlen_in_bits`), address conversion mistakes for word-address SoCs, and request context sizing around fallback objects. Test by building all CE config combinations, running sparse/clang structure layout checks, exercising every variant flag, and verifying DMA descriptors against hardware traces.
