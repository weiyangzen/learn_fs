# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/trng/Makefile

## Purpose
This Makefile wires the HiSilicon TRNG v2 driver into the kernel build. When `CONFIG_CRYPTO_DEV_HISI_TRNG` is enabled, it builds the module/object named `hisi-trng-v2` from `trng.o`.

## Important APIs, Types, And Functions
There are no C APIs here. The important build variables are `obj-$(CONFIG_CRYPTO_DEV_HISI_TRNG)` and `hisi-trng-v2-objs`.

## Control Flow
Kbuild includes `hisi-trng-v2.o` only when the config symbol is enabled. The composite object consists solely of `trng.o`.

## State And Persistence
No runtime state exists. The file affects build artifacts and module composition only.

## Dependencies And Integration Points
It depends on the enclosing crypto driver Kbuild and the Kconfig symbol for HiSilicon TRNG. It integrates `trng.c` as the implementation unit.

## Risks
The risk is low. A mismatch between object name and module metadata would prevent the driver from building or loading under the expected module name.

## Test Signals
Build with `CONFIG_CRYPTO_DEV_HISI_TRNG=y` and `=m`, and verify that `hisi-trng-v2` is linked and contains `trng.o`.
