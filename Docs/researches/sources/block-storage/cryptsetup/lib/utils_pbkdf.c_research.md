# File Research: sources/block-storage/cryptsetup/lib/utils_pbkdf.c

## Purpose
Defines default PBKDF settings and validates/initializes cryptsetup PBKDF configuration.

## Key Responsibilities
- Provides default PBKDF2, Argon2i, and Argon2id parameter structs.
- Selects defaults by PBKDF type or device type.
- Calculates adjusted usable physical memory for Argon2.
- Validates PBKDF type, hash, target time, iterations, memory, and parallelism.
- Enforces LUKS1/FIPS PBKDF2 restrictions.
- Initializes a crypt device’s PBKDF configuration, including string ownership.
- Limits benchmarked threads to online CPUs and memory to adjusted physical memory.
- Exposes public setters/getters for PBKDF type and iteration time.

## Important Details
- Small systems without swap get a stricter free-memory-based Argon2 cap.
- Forced no-benchmark values are not reduced by CPU or memory availability.
- Changing iteration time clears `CRYPT_PBKDF_NO_BENCHMARK` and resets iterations.
- PBKDF2 rejects memory/thread settings; Argon2 requires nonzero memory/thread settings.

## Dependencies
Uses `internal.h`, crypto backend hash/PBKDF limit APIs, system memory helpers, FIPS mode, and crypt device PBKDF state.
