# sources/distributed-fs/ceph-client/drivers/crypto/amcc/crypto4xx_trng.c

## Purpose

`crypto4xx_trng.c` provides optional hwrng support for PPC4xx true random generator blocks associated with the AMCC crypto engine.

## Important APIs, Types, And Functions

The main functions are `ppc4xx_trng_probe()`, `ppc4xx_trng_remove()`, `ppc4xx_trng_data_present()`, `ppc4xx_trng_data_read()`, and `ppc4xx_trng_enable()`. It defines local TRNG control/status/data offsets and matches `ppc4xx-rng`, `amcc,ppc460ex-rng`, and `amcc,ppc440epx-rng`.

## Control Flow

Probe finds an available matching TRNG node, maps resource 0, allocates an `hwrng`, assigns data-present/read callbacks, stores it in `core_dev`, enables TRNG in the crypto engine device-control register, writes the TRNG control mode, and registers with `devm_hwrng_register()`. Data-present polls the busy bit up to 20 times with 10 us delays when waiting. Read returns one 32-bit value from the data register. Remove unregisters, disables the TRNG bit, unmaps MMIO, and frees the hwrng object.

## State And Persistence Behavior

TRNG state is held in `dev->trng_base` and `core_dev->trng`. Hardware enablement persists in `CRYPTO4XX_DEVICE_CTRL` until remove disables it. The hwrng object uses `rng->priv` to point back to the crypto4xx device.

## Dependencies And Integration Points

It integrates with OF node lookup, MMIO mapping, hwrng, endian IO helpers, and the core crypto device's main MMIO register block. It is compiled only when `CONFIG_HW_RANDOM_PPC4XX` is enabled.

## Risks And Test Signals

Risks include manual freeing after devm hwrng registration, missing `dev->trng_base` null checks on partial failures, polling semantics that report present when `wait` is false even if busy, and cross-node assumptions between crypto and RNG blocks. Test hwrng registration/removal, absent or disabled TRNG nodes, repeated reads under rngtest, module unload, and busy-bit timeout behavior.
