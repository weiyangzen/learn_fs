# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/inline_crypto/chtls/Makefile

## Purpose

This Makefile builds the Chelsio inline TLS TOE driver object `chtls.o` when `CONFIG_CRYPTO_DEV_CHELSIO_TLS` is enabled.

## Important APIs, Types, and Functions

- `ccflags-y` adds include paths for `drivers/net/ethernet/chelsio/cxgb4` and `drivers/crypto/chelsio`.
- `obj-$(CONFIG_CRYPTO_DEV_CHELSIO_TLS) += chtls.o` controls module/object inclusion.
- `chtls-objs := chtls_main.o chtls_cm.o chtls_io.o chtls_hw.o` defines the composite object members.

## Control Flow

Kbuild includes this directory's object only when the Chelsio TLS config option is selected. The resulting `chtls.o` links the main ULD registration code, connection manager, socket I/O paths, and hardware key/TCB helpers.

## State and Persistence Behavior

There is no runtime state in this file. Build state is derived from Kconfig and Kbuild.

## Dependencies and Integration Points

The include paths are required for Chelsio adapter/ULD headers and crypto helper headers used by the four C files. It integrates with the kernel build system and the `CONFIG_CRYPTO_DEV_CHELSIO_TLS` option.

## Risks and Edge Cases

Missing include paths would break access to cxgb4 and Chelsio crypto headers. Adding new source files to the driver requires updating `chtls-objs`; otherwise functions may compile individually but not link into the driver.

## Test Signals

Build tests with `CONFIG_CRYPTO_DEV_CHELSIO_TLS=m` and `=y` should produce `chtls.o` with all four member objects. A config with the option disabled should omit the driver.
