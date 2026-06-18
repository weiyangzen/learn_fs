# sources/distributed-fs/ceph-client/drivers/crypto/stm32/Makefile

## Purpose

This Makefile connects the STM32 crypto Kconfig symbols to their driver objects.

## Important APIs, types, and functions

There are no C APIs. The file has two object rules: `obj-$(CONFIG_CRYPTO_DEV_STM32_HASH) += stm32-hash.o` and `obj-$(CONFIG_CRYPTO_DEV_STM32_CRYP) += stm32-cryp.o`.

## Control flow, state, and persistence

Build control is entirely declarative. If a symbol is built-in, the object is linked into the kernel image; if it is a module, the corresponding `.ko` is produced; if disabled, the object is omitted. No runtime state or persistence exists here.

## Dependencies and integration points

The Makefile is paired with `drivers/crypto/stm32/Kconfig` and the parent crypto drivers Makefile. Its integration point is kbuild's `obj-*` expansion for `stm32-hash.c` and `stm32-cryp.c`.

## Risks and test signals

Risks are limited to stale object names or mismatched Kconfig symbols. Test by building the two symbols independently as modules and built-ins, confirming `stm32-hash.o` and `stm32-cryp.o` are included only under their configured options.
