# sources/distributed-fs/ceph-client/drivers/crypto/amcc/Makefile

## Purpose

This Makefile builds the AMCC/PPC4xx crypto accelerator module and conditionally links the PPC4xx TRNG hwrng support.

## Important APIs, Types, And Functions

It declares `obj-$(CONFIG_CRYPTO_DEV_PPC4XX) += crypto4xx.o`, combines `crypto4xx_core.o` and `crypto4xx_alg.o`, and appends `crypto4xx_trng.o` when `CONFIG_HW_RANDOM_PPC4XX` is enabled.

## Control Flow

There is no runtime control flow. Build-time object selection decides whether `ppc4xx_trng_probe()` and `ppc4xx_trng_remove()` are real functions or inline no-ops from the header.

## State And Persistence Behavior

No runtime state is stored. The built composite object determines which algorithms and optional hwrng code are present.

## Dependencies And Integration Points

It integrates with kbuild and the `CRYPTO_DEV_PPC4XX` and `HW_RANDOM_PPC4XX` symbols. It must align with `crypto4xx_trng.h` conditional prototypes and calls from `crypto4xx_core.c`.

## Risks And Test Signals

Risks include optional TRNG linkage mismatch and missing core or algorithm symbols. Test base driver builds with and without hwrng, module and built-in builds, and link-time symbol resolution.
