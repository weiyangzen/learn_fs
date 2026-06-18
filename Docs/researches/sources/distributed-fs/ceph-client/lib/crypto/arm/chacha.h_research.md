# sources/distributed-fs/ceph-client/lib/crypto/arm/chacha.h

## Purpose
This ARM arch header selects between scalar and NEON ChaCha/HChaCha implementations and updates the block counter for callers.

## Important APIs, Types, and Functions
It declares NEON and scalar assembly entry points, defines static key `use_neon`, helper `neon_usable()`, `chacha_doneon()`, `hchacha_block_arch()`, `chacha_crypt_arch()`, and `chacha_mod_init_arch()`.

## Control Flow
`hchacha_block_arch()` chooses scalar unless kernel-mode NEON is enabled and usable. `chacha_crypt_arch()` uses scalar for no NEON, unusable SIMD, or <=64-byte messages; otherwise it processes up to `SZ_4K` per SIMD section using `chacha_doneon()`. `chacha_doneon()` uses four-block NEON chunks and a one-block final path, including a bounce buffer for partial final blocks. Init enables NEON except on Cortex-A7/A5 where scalar is preferred.

## State and Persistence
Persistent state is the static key and caller-owned `struct chacha_state`, especially `x[12]` block counter, which the wrapper increments by blocks consumed.

## Dependencies and Integration Points
It depends on crypto SIMD helpers, ARM hwcap/cputype APIs, and the generic ChaCha library. The Makefile includes scalar and optional NEON objects for ARM.

## Risks and Test Signals
Risks include counter update mismatches between scalar and NEON paths, SIMD use in invalid contexts, CPU blacklist logic, and partial final-block copy handling. Test signals include ChaCha selftests over small/large lengths, Cortex feature-path coverage, and in-place encryption tests.
