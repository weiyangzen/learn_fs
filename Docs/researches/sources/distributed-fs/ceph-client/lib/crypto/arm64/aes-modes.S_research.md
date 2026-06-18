# sources/distributed-fs/ceph-client/lib/crypto/arm64/aes-modes.S

## Purpose
This shared ARM64 assembly template implements AES modes over macro-provided block primitives. It is included by both Crypto Extension and NEON AES implementations.

## Important APIs, Types, And Functions
Template-emitted functions include AES ECB encrypt/decrypt, CBC encrypt/decrypt, ESSIV CBC encrypt/decrypt, CBC-CTS encrypt/decrypt, CTR, XCTR, XTS encrypt/decrypt, and optional `aes_mac_update`. Local helpers include 4x/5x block wrappers, `ctr_encrypt`, `next_tweak`, `xts_load_mask`, CTS permutation table logic, and CBC-MAC loops.

## Control Flow
ECB and CBC paths process multi-block chunks with 4x or 5x interleaving, then handle single-block tails. CTR/XCTR constructs counter vectors, encrypts them, xors input, updates IV/counter state, and handles partial final blocks with documented overlapping temporary buffers. XTS encrypt/decrypt maintain and store tweaks, handle first-tweak encryption, process 4-block groups, and perform ciphertext stealing for non-block-multiple lengths. MAC update xors blocks into a digest and conditionally encrypts before/after.

## State And Persistence
Persistent state is caller-owned IV, counter, tweak, digest, input/output buffers, and key schedules. The template itself has no globals except read-only permutation data.

## Dependencies And Integration Points
It depends on includer-provided macros: `AES_FUNC_START`, `enc_prepare`, `dec_prepare`, `encrypt_block`, `decrypt_block`, multi-block variants, key switching, and XTS mask handling. `arm64/aes-ce.S` and `arm64/aes-neon.S` are the direct includers.

## Risks And Edge Cases
Tail handling is the highest-risk area. CTR/XCTR requires at least 16-byte temporary buffers even for sub-block sizes, with data at the end of the buffer. XTS CTS uses overlapping stores and pointer rewinds. Macro contract drift can break both CE and NEON variants simultaneously.

## Test Signals
Mode vectors for all exported modes, partial block tests for CTR/XCTR and CTS, in-place encryption/decryption tests, IV/tweak continuation tests, and comparison between CE, NEON, and generic implementations are important.
