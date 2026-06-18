# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/Makefile

## Purpose
This Kbuild fragment builds the C3xxx virtual-function driver. It gates `qat_c3xxxvf.o` on `CONFIG_CRYPTO_DEV_QAT_C3XXXVF` and links VF PCI code with VF hardware metadata.

## Important APIs, Types, And Functions
The declarations are `obj-$(CONFIG_CRYPTO_DEV_QAT_C3XXXVF) += qat_c3xxxvf.o` and `qat_c3xxxvf-y := adf_drv.o adf_c3xxxvf_hw_data.o`. No runtime code is present.

## Control Flow
Kbuild includes the VF module only when configured. Runtime control starts in `adf_drv.c`, which registers a PCI VF driver for `PCI_DEVICE_ID_INTEL_QAT_C3XXX_VF`.

## State And Persistence Behavior
There is no runtime state in this file. It persistently controls module composition.

## Dependencies And Integration Points
The linked module depends on `qat_common`, Gen2 VF CSR/PFVF helpers, Linux PCI, and the matching PF driver when VFs are hosted locally.

## Risks
Incorrect object composition would omit VF-specific callbacks such as `adf_vf2pf_notify_init()` or break PCI binding.

## Test Signals
Build with C3xxx VF config, create SR-IOV VFs from a C3xxx PF or pass a VF into a guest, and confirm the `qat_c3xxxvf` driver binds and starts.
