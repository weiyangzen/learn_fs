# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxx/Makefile

## Purpose
This Kbuild fragment defines the C3xxx QAT PF module. It compiles the PCI driver and C3xxx hardware-data implementation when `CONFIG_CRYPTO_DEV_QAT_C3XXX` is enabled.

## Important APIs, Types, And Functions
The file declares `obj-$(CONFIG_CRYPTO_DEV_QAT_C3XXX) += qat_c3xxx.o` and `qat_c3xxx-y := adf_drv.o adf_c3xxx_hw_data.o`. There are no runtime functions.

## Control Flow
Kbuild conditionally links `adf_drv.o` and `adf_c3xxx_hw_data.o` into one `qat_c3xxx` module/object. Runtime control starts in the module init function in `adf_drv.c`.

## State And Persistence Behavior
No runtime state exists in this file. Its persistent effect is build composition for C3xxx PF support.

## Dependencies And Integration Points
The resulting object depends on `qat_common` exports, Gen2 common helpers, firmware loading, PCI core, and Kconfig selection.

## Risks
Removing either object breaks symbol resolution or runtime probing. Incorrect config names would omit C3xxx support from builds.

## Test Signals
Build `CONFIG_CRYPTO_DEV_QAT_C3XXX=m/y` and confirm a `qat_c3xxx` object includes both the PCI module and hardware-data callbacks, then probe a C3xxx PCI device.
