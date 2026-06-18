# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/Kconfig

## Purpose

`amlogic/Kconfig` defines the build options for the Amlogic GXL crypto offloader and its debug stats support.

## Important APIs, Types, And Functions

`CRYPTO_DEV_AMLOGIC_GXL` is a tristate depending on `HAS_IOMEM`, defaulting to module on `ARCH_MESON`, selecting `CRYPTO_SKCIPHER`, `CRYPTO_ENGINE`, `CRYPTO_ECB`, `CRYPTO_CBC`, and `CRYPTO_AES`. `CRYPTO_DEV_AMLOGIC_GXL_DEBUG` is a debugfs-dependent bool for stats/debug output.

## Control Flow

There is no runtime flow. Config selection controls whether the driver is built and whether debug counters/debugfs stats are compiled.

## State And Persistence Behavior

No runtime state is held here. Build configuration persists into which symbols, debug counters, and module objects are present.

## Dependencies And Integration Points

It integrates the Amlogic driver into the crypto driver Kconfig hierarchy and ensures required CryptoAPI algorithm helpers are available. The module name documented here matches the Makefile output.

## Risks And Test Signals

Risks include missing dependency on clocks or OF/platform support, debug option enabled in production affecting timing, and default module selection surprises on Meson platforms. Test `allyesconfig`, `allmodconfig`, `ARCH_MESON`, and `COMPILE_TEST`-like builds if dependency policy changes.
