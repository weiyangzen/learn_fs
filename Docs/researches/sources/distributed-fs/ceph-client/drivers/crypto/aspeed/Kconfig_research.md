# sources/distributed-fs/ceph-client/drivers/crypto/aspeed/Kconfig

## Purpose

`aspeed/Kconfig` defines the configuration surface for Aspeed crypto support, including the base HACE/crypto engine driver, optional debug messages, HACE hash support, HACE symmetric crypto support, and ACRY RSA support.

## Important APIs, Types, And Functions

The main symbol is `CRYPTO_DEV_ASPEED`, a tristate depending on `ARCH_ASPEED || COMPILE_TEST` and selecting `CRYPTO_ENGINE`. Optional symbols are `CRYPTO_DEV_ASPEED_DEBUG`, `CRYPTO_DEV_ASPEED_HACE_HASH`, `CRYPTO_DEV_ASPEED_HACE_CRYPTO`, and `CRYPTO_DEV_ASPEED_ACRY`, which select SHA/HMAC, AES/DES/ECB/CBC/CTR, or RSA dependencies as needed.

## Control Flow

There is no runtime flow. Config choices determine whether the shared Aspeed crypto module is built and which HACE hash, HACE cipher, and ACRY RSA implementation objects are linked.

## State And Persistence Behavior

No runtime state is stored here. Build-time state controls available algorithms and whether extra debug messages are compiled.

## Dependencies And Integration Points

It integrates Aspeed crypto drivers into the kernel crypto Kconfig tree and supplies dependency selection for downstream Makefile object composition. The help text documents HACE digest/cipher capabilities and ACRY RSA range.

## Risks And Test Signals

Risks include optional feature combinations that leave the base driver without any algorithms, debug messages affecting timing, and dependency omissions when algorithm coverage changes. Test all Aspeed config combinations, `COMPILE_TEST`, module/built-in builds, and Kconfig dependency resolution.
