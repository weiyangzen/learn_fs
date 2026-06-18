<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Kconfig

## Purpose

`drivers/crypto/allwinner/Kconfig` declares the Allwinner crypto accelerator family and feature options for the sun4i Security System, sun8i Crypto Engine, and sun8i Security System.

## Important APIs, Types, And Functions

`CRYPTO_DEV_ALLWINNER` gates the submenu and defaults to yes on `ARCH_SUNXI`. `CRYPTO_DEV_SUN4I_SS` selects MD5, SHA1, AES, DES library, RNG, and skcipher support. Optional symbols enable sun4i PRNG and debugfs stats. `CRYPTO_DEV_SUN8I_CE` selects skcipher, crypto engine, ECB/CBC, AES, DES, and RNG; optional symbols add debug stats, hash, PRNG, and TRNG. `CRYPTO_DEV_SUN8I_SS` similarly controls the A80/A83T security system.

## Control Flow

Kconfig selection determines which subdirectories build and which optional source files are included. Feature booleans also guard code paths for PRNG, TRNG, hash registration, and debug statistics.

## State And Persistence Behavior

Selections persist in kernel configuration and decide runtime algorithm availability, module names, and debugfs/hwrng exposure.

## Dependencies And Integration Points

It depends on `ARCH_SUNXI` or `COMPILE_TEST`, PM, and crypto framework symbols. It integrates with the Allwinner Makefile and per-driver Makefiles.

## Risks And Test Signals

Risks include missing primitive selections, optional features enabled without matching source support, and dependencies that block compile-test coverage. Test with Allwinner defconfigs, compile-test builds, optional debug/hash/RNG combinations, and crypto self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/Kconfig -->
