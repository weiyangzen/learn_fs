# File Research: sources/block-storage/cryptsetup/lib/utils_benchmark.c

## Purpose
Implements public and internal benchmarks for ciphers and PBKDF settings.

## Key Responsibilities
- Allocates aligned benchmark buffers and random IV/key material.
- Measures kernel cipher encrypt/decrypt throughput through `crypt_cipher_perf_kernel()`.
- Benchmarks PBKDF2/Argon2 parameters through `crypt_pbkdf_perf()`.
- Lowers PBKDF memory cost when adjusted physical memory is below requested maximum.
- Raises process priority during PBKDF benchmarking and restores it afterward.
- Provides internal benchmark reuse rules for already-populated PBKDF settings.

## Important Details
- PBKDF2 is benchmarked for one second and then scaled to the requested target time.
- Argon2 benchmark results are reused if `iterations` is already set.
- `CRYPT_PBKDF_NO_BENCHMARK` requires explicit iterations or returns `-EINVAL`.
- The benchmark callback logs current memory, iteration, thread, and duration data.

## Dependencies
Uses crypto backend initialization, PBKDF limits/performance APIs, process-priority helper, and memory adjustment logic from `utils_pbkdf.c`.
