# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/Makefile

## Purpose

This Makefile composes the Aspeed crypto driver objects based on selected HACE hash, HACE symmetric crypto, and ACRY RSA Kconfig features.

## Important APIs, Types, And Functions

It conditionally maps `hace-hash-y` to `aspeed-hace-hash.o`, `hace-crypto-y` to `aspeed-hace-crypto.o`, builds `aspeed_crypto.o` from `aspeed-hace.o` plus selected HACE objects, conditionally maps `aspeed_acry-y` to `aspeed-acry.o`, and adds both composite/base objects under `obj-$(CONFIG_CRYPTO_DEV_ASPEED)`.

## Control Flow

There is no runtime control flow. The Makefile determines whether the shared HACE platform object is linked with hash, cipher, both, or neither, and whether RSA ACRY support is also built.

## State And Persistence Behavior

No runtime state is stored here. The build artifact composition persists as available driver code in the kernel or module.

## Dependencies And Integration Points

It integrates with `CRYPTO_DEV_ASPEED`, `CRYPTO_DEV_ASPEED_HACE_HASH`, `CRYPTO_DEV_ASPEED_HACE_CRYPTO`, and `CRYPTO_DEV_ASPEED_ACRY` symbols. It must remain consistent with object filenames and Kconfig feature dependencies.

## Risks And Test Signals

Risks include building `aspeed_crypto.o` without feature objects when both HACE options are off, adding `aspeed-acry.o` under the base symbol rather than a separate object target, and object-name drift. Test all feature combinations and verify expected algorithms register for hash, cipher, and RSA configurations.
