# sources/distributed-fs/ceph-client/drivers/crypto/chelsio/Kconfig

## Purpose

`drivers/crypto/chelsio/Kconfig` exposes the Chelsio T6 crypto co-processor driver as `CONFIG_CRYPTO_DEV_CHELSIO`. It controls whether the `chcr` module is built and declares the crypto-library dependencies needed by that driver.

## Important APIs, Types, And Functions

The single symbol is `CRYPTO_DEV_CHELSIO`, a tristate named "Chelsio Crypto Co-processor Driver". It depends on `CHELSIO_T4` and selects `CRYPTO_LIB_AES`, `CRYPTO_LIB_GF128MUL`, SHA-1/SHA-256/SHA-512 libraries, and `CRYPTO_AUTHENC`. The help text identifies the module name as `chcr`.

## Control Flow

Kconfig evaluation determines whether the symbol is unavailable, built-in, or module. If enabled, the Makefile in the same directory builds the Chelsio crypto objects according to this symbol.

## State And Persistence Behavior

There is no runtime state. The selected symbol persists in kernel configuration and changes build output and module availability.

## Dependencies And Integration Points

The dependency on `CHELSIO_T4` ties this crypto driver to the Chelsio cxgb4 network adapter infrastructure. Selected crypto libraries provide AES, GF(2^128), SHA, and authenc support used by the implementation objects.

## Risks And Edge Cases

Using `select` forces library symbols on when the driver is enabled, so dependency correctness matters. If `CHELSIO_T4` is disabled, the crypto option is hidden even if crypto subsystem support is present. The help URLs are informational and not part of build behavior.

## Test Signals

Configuration tests should verify `CONFIG_CRYPTO_DEV_CHELSIO=m` builds `chcr.ko` when `CHELSIO_T4=m/y`. `scripts/config` or `make menuconfig` should show the symbol only with the dependency satisfied. Module load tests require compatible Chelsio hardware or graceful no-device behavior.
