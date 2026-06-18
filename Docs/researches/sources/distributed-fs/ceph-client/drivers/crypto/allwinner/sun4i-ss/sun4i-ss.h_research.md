<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss.h

## Purpose

`sun4i-ss.h` is the shared private header for the sun4i Security System driver. It defines register offsets, control bits, FIFO helpers, device/algorithm/TFM/request contexts, and cross-file function prototypes.

## Important APIs, Types, And Functions

Register definitions include `SS_CTL`, key registers, IV registers, `SS_FCSR`, digest registers, and RX/TX FIFOs. Control bits describe PRNG mode, IV mode, ECB/CBC/CTS, AES key size, encrypt/decrypt, AES/DES/3DES/SHA1/MD5/PRNG operation, `SS_DATA_END`, and enable. Core types are `struct sun4i_ss_ctx`, `struct sun4i_ss_alg_template`, `struct sun4i_tfm_ctx`, `struct sun4i_cipher_req_ctx`, and `struct sun4i_req_ctx`.

## Control Flow

The header has no executable flow, but its constants drive how cipher, hash, PRNG, and core files program the hardware and share state. The `fallback_req` fields are deliberately last in request contexts to allow variable crypto request sizes.

## State And Persistence Behavior

It defines persistent device state, per-algorithm stats/back-pointers, per-TFM key and fallback state, per-request IV backup, and hash buffering/intermediate state. Optional PRNG seed state is included only when configured.

## Dependencies And Integration Points

It pulls in Linux crypto, skcipher, ahash, RNG, DES/AES/SHA/MD5, platform, reset, runtime PM, IO, scatterlist, and module interfaces.

## Risks And Test Signals

Risks include register bit drift from hardware documentation, mismatched context sizes with algorithm templates, and incorrect alignment or field ordering for fallback requests. Test through full driver builds, sparse/compile warnings, crypto manager tests, and hardware register traces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/sun4i-ss.h -->
