# sources/distributed-fs/ceph-client/lib/crypto/arm/aes.h

## Purpose
This ARM arch header binds the generic AES library to the ARM scalar assembly block functions and handles unaligned buffers on systems without efficient unaligned access.

## Important APIs, Types, and Functions
It declares `__aes_arm_encrypt()` and `__aes_arm_decrypt()`, and defines `aes_preparekey_arch()`, `aes_encrypt_arch()`, and `aes_decrypt_arch()`.

## Control Flow
Key preparation delegates to `aes_expandkey_generic()`. Encryption/decryption check whether input or output is 4-byte aligned when unaligned access is inefficient; if not, they copy through a 16-byte aligned bounce buffer, call the assembly routine in-place, then copy to the destination. Aligned paths call assembly directly.

## State and Persistence
Prepared keys persist in caller-owned AES key structs. Bounce buffers are stack-local.

## Dependencies and Integration Points
It is included by `aes.c` when ARM arch AES is selected via Makefile include paths. It depends on AES types/macros and efficient unaligned-access configuration.

## Risks and Test Signals
Risks include bounce-buffer copy mistakes, in-place aliasing, and key layout mismatch with assembly. Test signals are AES vectors over aligned and unaligned in/out buffers, encryption-only keys, and decryption keys.
