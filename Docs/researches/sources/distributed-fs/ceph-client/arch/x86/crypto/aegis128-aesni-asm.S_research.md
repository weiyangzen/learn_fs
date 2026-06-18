# sources/distributed-fs/ceph-client/arch/x86/crypto/aegis128-aesni-asm.S

## Purpose
AES-NI/SSE4.1 assembly implementation of the AEGIS-128 AEAD primitive. It provides state initialization, associated-data absorption, encryption/decryption, tail handling, and tag finalization for the C glue.

## Important APIs, Types, And Functions
Defines `aegis128_aesni_init()`, `aegis128_aesni_ad()`, `aegis128_aesni_enc()`, `aegis128_aesni_dec()`, `aegis128_aesni_enc_tail()`, `aegis128_aesni_dec_tail()`, and `aegis128_aesni_final()`. Macros `aegis128_update`, `load_partial`, `store_partial`, `encrypt_block`, and `decrypt_block` implement the repeated AESENC-based state transform and partial-block I/O.

## Control Flow And State
The state is five XMM blocks. Initialization mixes key, IV, and two constants through ten update rounds. AD and crypt loops process five blocks per unrolled iteration, rotating the logical state by storing different XMM registers on each exit path. Encryption computes keystream from state words, writes ciphertext, updates state with plaintext; decryption reverses keystream use and updates with plaintext. Tail decrypt masks unused bytes before state absorption. Finalization injects bit lengths, runs seven updates, XORs all state blocks into the caller-provided tag buffer.

## Dependencies And Integration
Called only under `kernel_fpu_begin()` from `aegis128-aesni-glue.c`. Requires AES-NI and SSE4.1 instructions, x86_64 ABI register conventions, and 16-byte-aligned constants.

## Risks And Test Signals
Risks include partial load/store overlap errors, tail decrypt authentication mismatch, state rotation mistakes, length block bit-count errors, ABI clobbering, and missing FPU protection in callers. Signals include AEGIS known-answer tests across AD/plaintext tail sizes, in-place encryption/decryption, truncated tags, crypto fuzzing, and SIMD register state tests.
