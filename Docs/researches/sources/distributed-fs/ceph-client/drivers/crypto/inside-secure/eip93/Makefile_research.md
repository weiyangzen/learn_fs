# sources/distributed-fs/ceph-client/drivers/crypto/inside-secure/eip93/Makefile

## Purpose
This Makefile builds the EIP93 hardware crypto accelerator as a composite object when `CONFIG_CRYPTO_DEV_EIP93` is enabled.

## Important APIs, Types, And Functions
There are no runtime APIs. Kbuild creates `crypto-hw-eip93.o` from `eip93-main.o`, `eip93-common.o`, `eip93-cipher.o`, `eip93-aead.o`, and `eip93-hash.o`.

## Control Flow
The first line conditionally adds the composite object to the build. Subsequent `crypto-hw-eip93-y += ...` lines list mandatory objects for the composite driver.

## State And Persistence
No runtime state exists. This file only affects kernel build artifacts.

## Dependencies And Integration Points
The object split indicates major implementation areas: main platform/device code, shared helpers, skcipher, AEAD, and hash support. It is included from the parent Inside Secure Makefile.

## Risks
Object ordering and completeness matter for link success. If a new algorithm file is added without updating this list, the Kconfig symbol may enable an incomplete driver.

## Test Signals
Build `CONFIG_CRYPTO_DEV_EIP93=y` and `=m`, inspect that the resulting object/module contains all five implementation units, and run modpost for unresolved symbols.
