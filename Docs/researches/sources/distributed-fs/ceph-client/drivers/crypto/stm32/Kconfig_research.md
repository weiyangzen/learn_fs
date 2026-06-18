# sources/distributed-fs/ceph-client/drivers/crypto/stm32/Kconfig

## Purpose

This Kconfig file defines the build-time configuration switches for the STM32 crypto accelerator drivers: `CRYPTO_DEV_STM32_HASH` for HASH hardware and `CRYPTO_DEV_STM32_CRYP` for CRYP AES/DES/TDES hardware.

## Important APIs, types, and functions

There are no functions or runtime types. `CRYPTO_DEV_STM32_HASH` is a tristate option named "Support for STM32 hash accelerators"; it depends on `ARCH_STM32 || ARCH_U8500` and `HAS_DMA`, selects the hash algorithms and infrastructure it may register (`CRYPTO_HASH`, `CRYPTO_MD5`, `CRYPTO_SHA1`, `CRYPTO_SHA256`, `CRYPTO_SHA512`, `CRYPTO_SHA3`, and `CRYPTO_ENGINE`). `CRYPTO_DEV_STM32_CRYP` is a tristate option named "Support for STM32 cryp accelerators"; it depends on `ARCH_STM32 || ARCH_U8500` and selects `CRYPTO_HASH`, `CRYPTO_ENGINE`, and `CRYPTO_LIB_DES`.

## Control flow, state, and persistence

Kconfig only controls compilation. When enabled as built-in or module, the corresponding Makefile entries build `stm32-hash.o` and/or `stm32-cryp.o`. There is no runtime state in this file and no persistence beyond the kernel configuration.

## Dependencies and integration points

The dependencies align the drivers with STM32 and Ux500 SoC families. HASH explicitly requires DMA support because the driver contains DMA code paths and registers algorithms that use crypto engine request routing. CRYP selects DES library support because its skcipher registrations validate DES and 3DES keys. Both options integrate with the crypto subsystem through `CRYPTO_ENGINE`.

## Risks and test signals

The main configuration risk is dependency drift: `stm32-hash.c` also supports polling and CPU paths, but the Kconfig still requires `HAS_DMA`; `stm32-cryp.c` can continue without DMA channels at runtime but still depends on platform support and selected libraries. Test signals are successful builds for `m`, `y`, and disabled configurations on STM32/Ux500 defconfigs, correct module objects being emitted, and no unresolved crypto symbols when either option is selected independently.
