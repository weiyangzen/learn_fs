# sources/distributed-fs/ceph-client/drivers/crypto/ccree/Makefile

## Purpose

This Makefile builds the Arm CryptoCell/CCREE crypto driver object composition under `drivers/crypto/ccree`.

## Important APIs, Types, And Functions

It declares `obj-$(CONFIG_CRYPTO_DEV_CCREE) := ccree.o` and composes `ccree-y` from core modules: driver, buffer manager, request manager, cipher, hash, AEAD, and SRAM manager. Optional objects are added for `CONFIG_CRYPTO_FIPS`, `CONFIG_DEBUG_FS`, and `CONFIG_PM`.

## Control Flow

Kbuild links the listed objects into `ccree.o` when CCREE support is enabled. Feature-specific files are included only when the corresponding kernel config symbols are set.

## State And Persistence Behavior

The Makefile has no runtime state. Its persistent effect is build composition and conditional inclusion of FIPS, debugfs, and power-management code.

## Dependencies And Integration Points

It integrates with Linux Kbuild and the CCREE source files in the same directory. Configuration symbols determine whether the driver and optional support paths are compiled.

## Risks And Test Signals

Risks include missing object entries when new CCREE source files are added or feature objects being omitted under their configs. Test by building with `CONFIG_CRYPTO_DEV_CCREE`, with and without `CONFIG_CRYPTO_FIPS`, `CONFIG_DEBUG_FS`, and `CONFIG_PM`, and checking link coverage for the resulting `ccree.o`.
