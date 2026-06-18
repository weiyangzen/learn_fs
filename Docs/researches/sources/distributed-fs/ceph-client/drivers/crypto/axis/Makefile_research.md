# sources/distributed-fs/ceph-client/drivers/crypto/axis/Makefile

## Purpose

This Kbuild file connects the Axis ARTPEC crypto driver to the kernel build. It builds `artpec6_crypto.o` when `CONFIG_CRYPTO_DEV_ARTPEC6` is enabled.

## Important APIs, Types, and Functions

There are no C APIs or runtime types in this file. Its only build rule is `obj-$(CONFIG_CRYPTO_DEV_ARTPEC6) := artpec6_crypto.o`, which tells Kbuild to compile and link the ARTPEC-6/ARTPEC-7 crypto platform driver into the crypto driver subtree according to the selected kernel configuration.

## Control Flow

Build-time control flow is entirely configuration driven. If `CONFIG_CRYPTO_DEV_ARTPEC6=y`, the object is linked into the built-in kernel image. If it is `m`, it is built as a module. If unset, the ARTPEC driver is omitted.

## State and Persistence Behavior

The Makefile has no runtime state. The persistent effect is the build artifact selected by Kconfig and the resulting availability of the `artpec6-crypto` platform driver.

## Dependencies and Integration Points

The rule depends on the corresponding Kconfig symbol and on `artpec6_crypto.c`. It integrates with the kernel crypto drivers directory so the platform driver can register ahash, skcipher, and AEAD algorithms when a matching Axis device tree node is present.

## Risks and Edge Cases

- If Kconfig dependencies for `CONFIG_CRYPTO_DEV_ARTPEC6` do not include required crypto API, DMA, platform, or OF support, compile or link failures would surface from `artpec6_crypto.c`.
- Because only one object is listed, any future split of the driver into helper files must update this Makefile or the build will silently miss code.

## Test Signals

Build tests should confirm that `CONFIG_CRYPTO_DEV_ARTPEC6=y` and `m` both produce `artpec6_crypto.o`, and that disabling the symbol omits it. Runtime smoke testing is covered by the ARTPEC driver research section.
