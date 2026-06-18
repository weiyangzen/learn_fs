# sources/distributed-fs/ceph-client/drivers/crypto/amlogic/Makefile

## Purpose

This Makefile builds the Amlogic GXL crypto offloader module from its core and cipher implementation files.

## Important APIs, Types, And Functions

It declares `obj-$(CONFIG_CRYPTO_DEV_AMLOGIC_GXL) += amlogic-gxl-crypto.o` and sets `amlogic-gxl-crypto-y := amlogic-gxl-core.o amlogic-gxl-cipher.o`.

## Control Flow

There is no runtime control flow. Build-time selection links the platform registration and AES cipher code into one module.

## State And Persistence Behavior

No runtime state is stored. The composite object determines which driver code is available.

## Dependencies And Integration Points

It integrates with kbuild and the `CRYPTO_DEV_AMLOGIC_GXL` Kconfig option. It must stay aligned with prototypes in `amlogic-gxl.h` and templates in `amlogic-gxl-core.c`.

## Risks And Test Signals

Risks are limited to object list drift and module-name mismatch. Test module and built-in builds with `CONFIG_CRYPTO_DEV_AMLOGIC_GXL`.
