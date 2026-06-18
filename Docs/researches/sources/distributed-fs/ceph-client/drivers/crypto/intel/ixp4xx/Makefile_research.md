# sources/distributed-fs/ceph-client/drivers/crypto/intel/ixp4xx/Makefile

## Purpose
This Makefile wires the IXP4xx crypto driver object into Kbuild.

## Important APIs, Types, And Functions
It contains one build rule: `obj-$(CONFIG_CRYPTO_DEV_IXP4XX) += ixp4xx_crypto.o`.

## Control Flow
Kbuild compiles and links `ixp4xx_crypto.o` when the Kconfig symbol is enabled, either into vmlinux or as a module depending on the tristate value.

## State And Persistence
There is no runtime state. The file influences build output only.

## Dependencies And Integration Points
It is paired with `Kconfig` and the source file `ixp4xx_crypto.c`.

## Risks
Low risk. Any rename of the C file or Kconfig symbol must be mirrored here.

## Test Signals
Run a kernel build with `CONFIG_CRYPTO_DEV_IXP4XX=m` and confirm `ixp4xx_crypto.ko` is produced.
