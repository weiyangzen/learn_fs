# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_420xx/Makefile

## Purpose
This Makefile defines the module composition for the Intel QAT 420xx device family.

## Important APIs, Types, And Functions
It builds `qat_420xx.o` when `CONFIG_CRYPTO_DEV_QAT_420XX` is enabled, with constituent objects `adf_drv.o` and `adf_420xx_hw_data.o`.

## Control Flow
Kbuild links the family PCI driver and hardware-data table into a single module or built-in object.

## State And Persistence
No runtime state is stored here.

## Dependencies And Integration Points
The file integrates with the parent QAT Makefile and the hardware-data implementation in this directory.

## Risks
Low risk. Object-name drift would break the family module build.

## Test Signals
Build `CONFIG_CRYPTO_DEV_QAT_420XX=m` and confirm `qat_420xx.ko` includes both objects.
