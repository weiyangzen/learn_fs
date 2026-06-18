# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/amlogic-gxl.h

## Purpose

`amlogic-gxl.h` defines the shared descriptor format, mode bits, flow/device/TFM/request state, algorithm template, and prototypes for the Amlogic GXL crypto driver.

## Important APIs, Types, And Functions

Key constants include key modes, encrypt/decrypt values, ECB/CBC modes, `MAXFLOW`, `MAXDESC`, and descriptor status bits `DESC_LAST`, `DESC_ENCRYPTION`, and `DESC_OWN`. Key types are `struct meson_desc`, `struct meson_flow`, `struct meson_dev`, `struct meson_cipher_req_ctx`, `struct meson_cipher_tfm_ctx`, and `struct meson_alg_template`.

## Control Flow

The header has no executable flow. Core code allocates flows and descriptor lists; cipher code fills `meson_desc` entries according to the bit layout documented here and submits them by writing flow registers.

## State And Persistence Behavior

Persistent state defined here includes per-device MMIO/clock/flow/IRQ/debug state, per-flow coherent descriptor memory and completion state, per-request direction/flow/fallback storage, and per-TFM key/fallback state.

## Dependencies And Integration Points

It integrates CryptoAPI AES/skcipher/engine headers, debugfs, scatterlists, and driver-internal prototypes. The descriptor layout is based on reverse-engineered or undocumented fields noted in comments, making it the local hardware ABI reference.

## Risks And Test Signals

Risks include undocumented descriptor bits, fixed descriptor count, no include guard, fallback request placement, and key pointer typed as `u32 *` while allocated from byte keys. Test build warnings, descriptor dumps against hardware behavior, all AES key sizes, and request-size calculations.
