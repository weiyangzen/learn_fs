# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/Makefile

## Purpose
This Kbuild fragment builds the C62x virtual-function module. It gates `qat_c62xvf.o` on `CONFIG_CRYPTO_DEV_QAT_C62XVF` and links VF PCI code with C62x VF hardware metadata.

## Important APIs, Types, And Functions
The declarations are `obj-$(CONFIG_CRYPTO_DEV_QAT_C62XVF) += qat_c62xvf.o` and `qat_c62xvf-y := adf_drv.o adf_c62xvf_hw_data.o`. There are no runtime functions.

## Control Flow
Kbuild conditionally composes the VF module. Runtime control starts in `adf_drv.c` when a matching VF PCI device is probed.

## State And Persistence Behavior
No runtime state exists. The file controls module composition.

## Dependencies And Integration Points
The module depends on `qat_common`, Gen2 VF helpers, PCI core, and PF/VF messaging support.

## Risks
Incorrect composition can omit the VF metadata required by probe or PF/VF notifications.

## Test Signals
Build with C62x VF config, create or assign VFs, confirm `qat_c62xvf` binds, and run basic crypto/compression operations through the VF.
