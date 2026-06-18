<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/Makefile

## Purpose

The sun8i Crypto Engine Makefile assembles the `sun8i-ce` driver from its core and optional algorithm implementation files.

## Important APIs, Types, And Functions

It builds `sun8i-ce.o` when `CONFIG_CRYPTO_DEV_SUN8I_CE` is enabled. Base objects are `sun8i-ce-core.o` and `sun8i-ce-cipher.o`. Optional objects are `sun8i-ce-hash.o`, `sun8i-ce-prng.o`, and `sun8i-ce-trng.o` under their corresponding Kconfig symbols.

## Control Flow

There is no runtime flow. Build-time composition determines whether hash, PRNG, and TRNG algorithm registration has implementation code available.

## State And Persistence Behavior

No runtime state is stored here. The selected object set persists in the built module or kernel image.

## Dependencies And Integration Points

It integrates with Allwinner Kconfig and parent Makefile selections for the sun8i CE driver.

## Risks And Test Signals

Risks include missing optional sources for enabled symbols or stale object names. Test by building all combinations of hash, PRNG, and TRNG options and loading the resulting module on supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun8i-ce/Makefile -->
