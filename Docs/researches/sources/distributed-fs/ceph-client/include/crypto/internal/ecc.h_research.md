# sources/distributed-fs/ceph-client/include/crypto/internal/ecc.h

Purpose: defines internal elliptic-curve arithmetic, key validation, ECDH, ECDSA formatting, and VLI helpers for NIST curves up to P-521.

Important APIs, types, and flow: constants define digit counts, byte limits, and point initialization. `struct ecdsa_raw_sig` stores raw `r` and `s` as native-endian VLI arrays. Conversion helpers (`ecc_swap_digits()`, `ecc_digits_from_bytes()`, `vli_from_be64()`, `vli_from_le64()`) normalize external byte encodings into little-endian digit arrays. Key and ECDH functions validate private keys, generate private keys, derive public keys, compute shared secrets, validate public keys partially or fully, allocate/free points, test the point at infinity, and perform Shamir multi-scalar multiplication for signature verification. VLI helpers provide zero check, comparison, subtraction, modular inverse, and slow modular multiplication.

State and persistence: all state is caller-owned key arrays, point allocations, and temporary arithmetic buffers. No persistence exists, but private keys and shared secrets are sensitive and require caller-side zeroization.

Dependencies and integration: depends on `crypto/ecc_curve.h`, unaligned access helpers, ECDSA crypto templates (`ecdsa_x962_tmpl`, `ecdsa_p1363_tmpl`), and KPP/signature implementations.

Risks and test signals: high-risk areas are endian conversion, curve-order bounds, point validation strength, scalar edge cases, timing behavior, and allocation cleanup. Signals include ECDH and ECDSA known-answer tests for P-192/P-256/P-384/P-521, invalid public/private key rejection, ASN.1/raw signature conversions, fuzzed point inputs, and constant-time/leakage review for secret-dependent arithmetic.
