# sources/distributed-fs/ceph-client/lib/crypto/powerpc/chacha.h

## Purpose
Provides the PowerPC ChaCha architecture hook, selecting Power10 VSX acceleration for large buffers and falling back to the generic ChaCha implementation otherwise.

## Important APIs, Types, and Functions
Declares `asmlinkage void chacha_p10le_8x(...)`, defines `chacha_p10_do_8x`, `chacha_crypt_arch`, `chacha_mod_init_arch`, and maps `hchacha_block_arch` to `hchacha_block_generic`. It maintains `static __ro_after_init DEFINE_STATIC_KEY_FALSE(have_p10)`.

## Control Flow
Module init enables `have_p10` when `CPU_FTR_ARCH_31` is present. `chacha_crypt_arch` uses generic code if Power10 is unavailable, the buffer is at most one block, or SIMD is not usable. Otherwise it processes up to 4 KiB per VSX critical section. `chacha_p10_do_8x` sends the largest 256-byte-aligned prefix to assembly, advances pointers, updates the ChaCha block counter by processed blocks, then uses generic code for the remaining bytes.

## State and Persistence
The static key persists CPU capability. The function mutates `state->x[12]` as data is encrypted/decrypted, matching stream cipher counter semantics. VSX use is enclosed by preemption-disabled `vsx_begin`/`vsx_end`.

## Dependencies and Integration Points
Depends on PowerPC CPU feature and VSX switching APIs plus `crypto_simd_usable()`. Integrated by the generic ChaCha library via `chacha_crypt_arch`.

## Risks
Counter accounting must stay synchronized with the assembly block count. The 4 KiB chunking bounds preemption-off windows, but any future change to chunk size should consider latency. HChaCha is explicitly not accelerated.

## Test Signals
Run ChaCha/XChaCha tests with hardware acceleration available and unavailable, with lengths below one block, one block, 255/256/257 bytes, and over 4 KiB to exercise chunk loops and generic tails.
