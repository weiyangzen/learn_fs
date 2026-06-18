<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/Makefile -->
# sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/Makefile

## Purpose

The sun4i Security System Makefile assembles the `sun4i-ss` driver module or built-in object from its core, hash, cipher, and optional PRNG sources.

## Important APIs, Types, And Functions

It creates `sun4i-ss.o` when `CONFIG_CRYPTO_DEV_SUN4I_SS` is enabled. The base object list is `sun4i-ss-core.o`, `sun4i-ss-hash.o`, and `sun4i-ss-cipher.o`. `sun4i-ss-prng.o` is appended when `CONFIG_CRYPTO_DEV_SUN4I_SS_PRNG` is enabled.

## Control Flow

There is no runtime flow, but source composition determines which algorithm templates have implementations available at link time.

## State And Persistence Behavior

No runtime state is owned here. Build-time symbol selections persist in the module contents.

## Dependencies And Integration Points

It integrates with the Allwinner parent Makefile and Kconfig options for sun4i SS and PRNG support.

## Risks And Test Signals

Risks include enabling PRNG registration without linking the PRNG implementation or adding a source file without updating this list. Test by building with PRNG on and off and running module load plus crypto RNG self-tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/allwinner/sun4i-ss/Makefile -->
