# sources/distributed-fs/ceph-client/arch/arm64/crypto/aes-glue-neon.c

## Purpose
This wrapper builds the shared AES skcipher glue as the plain NEON implementation.

## APIs, Types, And Functions
It includes `aes-glue.c` without defining `USE_V8_CRYPTO_EXTENSIONS`. The shared code therefore sets `MODE` to `neon`, priority to 200, and binds operations to `neon_aes_*` backend routines.

## Control Flow, State, And Persistence
Runtime behavior is inherited from `aes-glue.c`. This wrapper contributes compile-time selection only; it has no mutable state.

## Dependencies And Integration
Kbuild uses this file for `CONFIG_CRYPTO_AES_ARM64_NEON_BLK`. It depends on shared glue and NEON backend symbols in the arm64 crypto directory.

## Risks And Test Signals
Risks are missing NEON symbols or algorithm registration conflicts with CE and bit-sliced implementations. Test by building `aes-neon-blk`, loading it on arm64 with kernel-mode NEON, and running AES skcipher selftests.
