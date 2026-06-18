# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/cipher_check.c

## Purpose
Measures Linux kernel crypto cipher throughput.

## Key Content
Uses the kernel AF_ALG cipher wrapper to encrypt and decrypt a caller-supplied buffer in 64 KiB chunks. `cipher_measure()` times one full buffer pass with `CLOCK_MONOTONIC_RAW`, rejects too-small timings, and `crypt_cipher_perf_kernel()` repeats encryption and decryption until each exceeds roughly one second, then reports MiB/s.

## Dependencies and Coupling
Depends on `crypto_backend_internal.h` kernel cipher APIs. Intended for benchmarking kernel implementations used by dm-crypt.

## Invariants and Risks
This is a CPU/kernel crypto benchmark, not a storage benchmark. It mutates the supplied buffer in place during measurement.
