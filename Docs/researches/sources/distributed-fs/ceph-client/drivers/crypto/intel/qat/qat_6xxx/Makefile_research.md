# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_6xxx/Makefile

## Purpose
This Kbuild fragment defines the QAT Gen6 PF module. It compiles `qat_6xxx.o` when `CONFIG_CRYPTO_DEV_QAT_6XXX` is enabled and links the PCI driver with Gen6 hardware metadata.

## Important APIs, Types, And Functions
The build declarations are `obj-$(CONFIG_CRYPTO_DEV_QAT_6XXX) += qat_6xxx.o` and `qat_6xxx-y := adf_drv.o adf_6xxx_hw_data.o`. There are no runtime functions in this file.

## Control Flow
Kbuild conditionally includes the module in the kernel build. At module load, runtime control begins in the linked `adf_drv.c` PCI driver.

## State And Persistence Behavior
The Makefile has no runtime state. It persistently controls whether Gen6 probe, hardware data, firmware declarations, and callbacks are present in the built kernel/module.

## Dependencies And Integration Points
It integrates with top-level QAT Kconfig and `qat_common`, including Gen6 shared helpers, firmware loading, PF/VF communication, and common accelerator lifecycle code.

## Risks
Omitting either object breaks the module: the PCI object needs `adf_init_hw_data_6xxx()` and the hardware-data object depends on the PCI module to call it. Incorrect config wiring would silently omit Gen6 hardware support.

## Test Signals
Build output should include a `qat_6xxx` module/object with no unresolved common QAT symbols. Runtime confirmation is a Gen6 PCI ID binding and firmware requests for `qat_6xxx.bin` and `qat_6xxx_mmp.bin`.
