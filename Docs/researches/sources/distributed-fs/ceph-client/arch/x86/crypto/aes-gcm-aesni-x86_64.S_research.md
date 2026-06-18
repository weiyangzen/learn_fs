# sources/distributed-fs/ceph-client/arch/x86/crypto/aes-gcm-aesni-x86_64.S

## Purpose
AES-NI/PCLMULQDQ x86_64 assembly implementation of AES-GCM for CPUs with SSE4.1 or AVX. It provides GHASH precomputation, AAD update, encrypt/decrypt update, and final tag generation/verification.

## Important APIs, Types, And Functions
Exports non-AVX and AVX variants: `aes_gcm_precompute_aesni[_avx]()`, `aes_gcm_aad_update_aesni[_avx]()`, `aes_gcm_enc_update_aesni[_avx]()`, `aes_gcm_dec_update_aesni[_avx]()`, `aes_gcm_enc_final_aesni[_avx]()`, and `aes_gcm_dec_final_aesni[_avx]()`. Macros implement PCLMUL abstraction, byte swap, partial block load/store, single-block GHASH multiply, Karatsuba multi-block GHASH, 8-block CTR generation, update loops, and final tag logic.

## Control Flow And State
Precompute encrypts zero to obtain H, byte-reflects and adjusts it for GHASH arithmetic, stores H powers H^1..H^8, XORed halves, and H*x^64 in `struct aes_gcm_key_aesni`. AAD update GHASHes full and partial AAD blocks. Encrypt/decrypt update loads the little-endian counter and GHASH accumulator, processes 8-block chunks by interleaving AES rounds and GHASH multiplication, then handles 1-block and partial tails. Encryption GHASHes ciphertext after producing it; decryption GHASHes source ciphertext before/while writing plaintext. Final builds the length block, multiplies by H, AES-encrypts counter block 1, returns the tag for encryption or constant-time compares a truncated tag for decryption.

## Dependencies And Integration
Integrated into `aesni-intel.o`; callers provide an expanded key layout with offsets matching this file, manage FPU/SIMD state, buffer non-final updates to multiples of 16 where required, and dispatch based on AES/PCLMUL/SSE4.1 or AVX features.

## Risks And Test Signals
Risks include key-struct offset drift, GHASH bit-reflection/reduction errors, AES key-length branch mistakes, counter increment overflow, partial final block masking, constant-time tag check regressions, and AVX/non-AVX macro divergence. Signals include AES-GCM known-answer tests for all key sizes, AAD-only and plaintext-only cases, truncated tags 4-16 bytes, in-place decrypt, unaligned buffers, cross-boundary lengths around 16 and 128 bytes, and crypto fuzz tests versus generic GCM.
