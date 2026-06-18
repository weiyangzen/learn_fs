# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ss/sun8i-ss.h

## Purpose

`sun8i-ss.h` defines the shared register constants, algorithm bits, flow limits, state structures, algorithm templates, and cross-file prototypes for the Allwinner A80/A83T Security System driver.

## Important APIs, Types, And Functions

Important definitions include `SS_CTL_REG`, `SS_INT_*`, `SS_KEY_ADR_REG`, `SS_IV_ADR_REG`, `SS_SRC_ADR_REG`, `SS_DST_ADR_REG`, `SS_LEN_ADR_REG`, algorithm/mode constants, `MAXFLOW`, `MAX_SG`, and `MAX_PAD_SIZE`. Important types are `struct ss_variant`, `struct sginfo`, `struct sun8i_ss_flow`, `struct sun8i_ss_dev`, cipher/hash/RNG TFM and request contexts, and `struct sun8i_ss_alg_template`.

## Control Flow

The header has no direct runtime execution, but it defines the data contract: core code allocates `sun8i_ss_flow`, cipher/hash/PRNG populate request contexts, and all hardware users coordinate through the shared register offsets and flow state.

## State And Persistence Behavior

Persistent state includes device MMIO/clock/reset/flow/debug state, per-flow IV/pad/result buffers, cipher keys and fallback TFMs, hash fallback and HMAC pad/key material, and RNG seed material. Many structures hold DMA addresses or word-count lengths consumed by hardware.

## Dependencies And Integration Points

It integrates CryptoAPI AES/DES/skcipher/rng/hash headers, debugfs, atomics, scatterlists, MD5/SHA constants, and driver-internal function prototypes. It is included by all SS implementation files and must stay aligned with conditional object linkage.

## Risks And Test Signals

Risks include fixed limits that shape fallback behavior, missing include guards, packed hardware assumptions in plain `struct sginfo`, request context layout with fallback request at the end, and state fields shared across optional build configurations. Test all config combinations, structure-size expectations, fallback request sizing, and sparse/compile warnings.
