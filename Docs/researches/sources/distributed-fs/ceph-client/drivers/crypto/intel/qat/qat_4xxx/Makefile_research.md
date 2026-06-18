# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_4xxx/Makefile

## Purpose
This Kbuild fragment builds the QAT 4xxx PCI physical-function module. It connects `CONFIG_CRYPTO_DEV_QAT_4XXX` to the `qat_4xxx.o` kernel object and declares that object as the combination of the PCI driver (`adf_drv.o`) and generation-specific hardware metadata (`adf_4xxx_hw_data.o`).

## Important APIs, Types, And Functions
There are no runtime APIs in the Makefile. The important build contract is `obj-$(CONFIG_CRYPTO_DEV_QAT_4XXX) += qat_4xxx.o` plus `qat_4xxx-y := adf_drv.o adf_4xxx_hw_data.o`.

## Control Flow
Kbuild includes this module only when the matching config symbol is enabled. At link time it combines the probe/remove module and the hardware-data callbacks into one loadable or built-in kernel object.

## State And Persistence Behavior
The file has no runtime state. Its persistent effect is the compiled module membership and therefore which initialization functions and firmware declarations are present in the kernel build.

## Dependencies And Integration Points
It integrates with the top-level QAT Kconfig/Makefile and with `qat_common`, which provides the shared symbols imported by `adf_drv.o` and `adf_4xxx_hw_data.o`.

## Risks
If either object is omitted, the module will either lack PCI binding or lack required `adf_init_hw_data_4xxx()` symbols. Incorrect config gating can build a driver for unsupported kernels or omit support for 4xxx hardware.

## Test Signals
Build signals are successful compilation with `CONFIG_CRYPTO_DEV_QAT_4XXX`, a resulting `qat_4xxx` module/object, and module metadata that includes the 4xxx firmware declarations from `adf_drv.c`.
