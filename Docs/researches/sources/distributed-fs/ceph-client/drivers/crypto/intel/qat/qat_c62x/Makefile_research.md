# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62x/Makefile

## Purpose
This Kbuild fragment builds the QAT C62x PF module when `CONFIG_CRYPTO_DEV_QAT_C62X` is enabled. It links the PF PCI driver with C62x hardware metadata.

## Important APIs, Types, And Functions
The declarations are `obj-$(CONFIG_CRYPTO_DEV_QAT_C62X) += qat_c62x.o` and `qat_c62x-y := adf_drv.o adf_c62x_hw_data.o`. There are no runtime APIs.

## Control Flow
Kbuild conditionally composes the module. Runtime control starts in `adf_drv.c` module init and PCI probe.

## State And Persistence Behavior
No runtime state exists. The file persistently controls object composition for C62x support.

## Dependencies And Integration Points
The module links against `qat_common`, Gen2 helpers, Linux PCI, firmware loader code, and top-level QAT Kconfig.

## Risks
Incorrect object membership causes missing PCI binding or missing `adf_init_hw_data_c62x()` callbacks.

## Test Signals
Build with C62x config and confirm a `qat_c62x` module/object exists and can bind `PCI_DEVICE_ID_INTEL_QAT_C62X`.
