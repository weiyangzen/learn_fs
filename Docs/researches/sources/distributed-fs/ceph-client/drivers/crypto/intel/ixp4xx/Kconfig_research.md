# sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/Kconfig

## Purpose
This Kconfig file defines `CRYPTO_DEV_IXP4XX`, the build option for the Intel IXP4xx NPE crypto acceleration driver.

## Important APIs, Types, And Functions
The symbol is a tristate named "Driver for IXP4xx crypto hardware acceleration". It depends on `ARCH_IXP4XX` or `COMPILE_TEST`, and on the platform queue manager and NPE support symbols `IXP4XX_QMGR` and `IXP4XX_NPE`.

## Control Flow
Selecting the option pulls in crypto API dependencies used by `ixp4xx_crypto.c`, including AES, DES, ECB, CBC, CTR, DES library helpers, AEAD, AUTHENC, and SKCIPHER support.

## State And Persistence
No runtime state is stored here. The Kconfig choice controls whether the driver is built in, built as a module, or omitted.

## Dependencies And Integration Points
The option integrates with the `Makefile` in the same directory through `obj-$(CONFIG_CRYPTO_DEV_IXP4XX) += ixp4xx_crypto.o`.

## Risks
- The driver has hardware/platform dependencies, so `COMPILE_TEST` can prove build coverage but not runtime correctness.
- Selecting broad crypto dependencies can increase the kernel/module footprint.

## Test Signals
- Build with `CRYPTO_DEV_IXP4XX=m` and `=y` on IXP4xx-capable or compile-test configurations.
- Confirm the corresponding object is included only when the symbol is enabled.
