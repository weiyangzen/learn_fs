# sources/distributed-fs/ceph-client/lib/crypto/mips/chacha.h

## Purpose
Declares MIPS-optimized ChaCha and HChaCha entry points for the generic ChaCha library.

## Important APIs, Types, and Functions
- Declares `asmlinkage void chacha_crypt_arch(...)`.
- Declares `asmlinkage void hchacha_block_arch(...)`.
- Uses `struct chacha_state`, `HCHACHA_OUT_WORDS`, and standard kernel integer types.

## Control Flow and State
This header has no runtime control flow. It supplies ABI declarations for assembly functions that mutate the ChaCha state counter and write output buffers.

## Dependencies and Integration Points
Included when `CONFIG_CRYPTO_LIB_CHACHA_ARCH` or the MIPS crypto path is enabled. It couples the generic C dispatch to `mips/chacha-core.S`.

## Risks and Test Signals
The declarations must match the assembly ABI exactly, including `asmlinkage` argument passing. Test signals come from successful MIPS builds, modpost symbol resolution, and generic-vs-arch ChaCha/HChaCha vectors.
