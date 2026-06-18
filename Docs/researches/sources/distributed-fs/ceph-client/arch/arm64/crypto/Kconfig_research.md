# sources/distributed-fs/ceph-client/arch/arm64/crypto/Kconfig

## Purpose
This Kconfig menu exposes arm64 accelerated cryptographic algorithms to kernel configuration.

## APIs, Types, And Functions
It defines tristate options for GHASH with ARMv8 Crypto Extensions, AES CE block modes, AES NEON block modes, AES bit-sliced NEON modes, SM4 CE cipher, SM4 CE block modes, SM4 NEON block modes, AES CE CCM, SM4 CE CCM, and SM4 CE GCM. Options depend on `KERNEL_MODE_NEON` and select crypto core helpers such as `CRYPTO_SKCIPHER`, `CRYPTO_AEAD`, `CRYPTO_LIB_AES`, `CRYPTO_LIB_AES_CBC_MACS`, `CRYPTO_SM4`, and GF128 helpers.

## Control Flow, State, And Persistence
There is no runtime flow. Kconfig selection persists in `.config`, which drives compilation of the corresponding modules or built-in objects.

## Dependencies And Integration
The file integrates the arm64 crypto directory with the kernel crypto API and module build. It coordinates with the local Makefile object names and with CPU feature gating in the modules themselves.

## Risks And Test Signals
Risks are missing `select` dependencies, incorrectly broad CPU capability claims, and enabling code paths without kernel-mode SIMD support. Test signals include Kconfig dependency resolution, `allyesconfig`/`allmodconfig` builds, crypto selftests, and runtime algorithm registration on CPUs with and without relevant features.
