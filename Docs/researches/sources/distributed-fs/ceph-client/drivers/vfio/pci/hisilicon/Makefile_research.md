# sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/Makefile

## Purpose

This Makefile builds the HiSilicon ACC VFIO PCI variant driver.

## Important APIs, Types, and Functions

`obj-$(CONFIG_HISI_ACC_VFIO_PCI) += hisi-acc-vfio-pci.o` enables the aggregate object, and `hisi-acc-vfio-pci-y := hisi_acc_vfio_pci.o` supplies its implementation.

## Control Flow

Kbuild compiles the driver when the Kconfig symbol is enabled.

## State and Persistence Behavior

No runtime state exists here.

## Dependencies and Integration Points

The Makefile maps Kconfig to the single implementation file and depends on VFIO PCI core being selected by Kconfig.

## Risks and Edge Cases

Filename or symbol drift would break the variant build.

## Test Signals

Build `CONFIG_HISI_ACC_VFIO_PCI=y` and `m`.
