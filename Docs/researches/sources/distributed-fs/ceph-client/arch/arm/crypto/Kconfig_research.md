<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/crypto/Kconfig

## Purpose
Kconfig menu for ARM accelerated cryptographic algorithms using kernel-mode NEON, ARMv8 Crypto Extensions, and PMULL.

## Important APIs/types/functions
- `CRYPTO_GHASH_ARM_CE`: AES-GCM AEAD using ARMv8 Crypto Extensions/PMULL; selects AEAD, AES library, and GF128 multiplication.
- `CRYPTO_AES_ARM_BS`: bit-sliced NEON AES for ECB/CBC/CTR/XTS; selects SKCIPHER and AES library.
- `CRYPTO_AES_ARM_CE`: ARMv8 Crypto Extensions AES for ECB/CBC/CTS/CTR/XTS; selects SKCIPHER and AES library.

## Control flow
Menu selections gate objects in `arch/arm/crypto/Makefile`. All options depend on `KERNEL_MODE_NEON`.

## State and persistence behavior
Selections persist in `.config` and determine algorithm registration availability at boot/module load.

## Dependencies and integration points
Integrates with the Linux CryptoAPI, module autoload aliases, CPU feature checks in module init, and ARM NEON/SIMD context management.

## Risks and edge cases
Enabling code on CPUs lacking runtime features must fail gracefully in module init. NEON use requires correct `kernel_neon_begin/end` pairing to avoid corrupting user/kernel SIMD state.

## Test signals
Build with each config as built-in and module; run `crypto/testmgr`, `tcrypt`, AF_ALG users, and CPU-feature-negative boot tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/crypto/Kconfig -->
