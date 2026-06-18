# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_trng.h

## Purpose

`crypto4xx_trng.h` conditionally exposes TRNG probe/remove hooks to the crypto4xx core while compiling them away when PPC4xx hwrng support is disabled.

## Important APIs, Types, And Functions

It declares `ppc4xx_trng_probe()` and `ppc4xx_trng_remove()` under `CONFIG_HW_RANDOM_PPC4XX`, otherwise provides inline no-op definitions with `__maybe_unused` parameters.

## Control Flow

The header itself has no runtime flow. It lets `crypto4xx_core.c` call the TRNG hooks unconditionally from probe/remove without requiring conditional code in the core file.

## State And Persistence Behavior

No state is stored here. State effects depend on whether the real implementation is linked.

## Dependencies And Integration Points

It depends on `struct crypto4xx_core_device` from `crypto4xx_core.h` and the `HW_RANDOM_PPC4XX` Kconfig symbol. The Makefile conditional object must match this header's conditions.

## Risks And Test Signals

Risks include config mismatch between header and Makefile, missing forward declarations if include order changes, and silent no-op behavior when users expect hwrng. Test builds with `HW_RANDOM_PPC4XX=y/m/n` and probe logs on systems with TRNG nodes.
