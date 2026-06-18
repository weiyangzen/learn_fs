# File Research: sources/block-storage/cryptsetup/lib/crypto_backend/pbkdf_check.c

Implements PBKDF parameter limits and benchmarking/calibration.

Key points:
- `crypt_pbkdf_get_limits()` defines hard limits for PBKDF2 and Argon2i/Argon2id.
- PBKDF2 minimum iterations are 1000; Argon2 has minimum time cost 4, memory 32 KiB, benchmark memory floor 64 MiB, max memory 4 GiB, and parallelism 1-4.
- CPU-time measurement uses `getrusage()` for PBKDF2, adding system time for kernel backend or broken user-time reporting.
- Argon2 benchmarking uses wall-clock `CLOCK_MONOTONIC_RAW` because parallel threads make CPU time inappropriate.
- `next_argon2_params()` adjusts time cost and memory cost toward target runtime, bounded by min/max.
- `crypt_argon2_check()` first finds parameters taking at least 250 ms, then iterates until within 95-110% of target or convergence.
- `crypt_pbkdf_check()` estimates PBKDF2 iterations for target runtime, scaling iterations up until a stable measurement over 500 ms.
- `crypt_pbkdf_perf()` selects the PBKDF2 or Argon2 calibration path and reports iterations and memory.

Storage relevance:
- Determines calibrated KDF strength for formatted volumes and passphrase operations.
- Progress callback can interrupt calibration with `-EINTR`.
