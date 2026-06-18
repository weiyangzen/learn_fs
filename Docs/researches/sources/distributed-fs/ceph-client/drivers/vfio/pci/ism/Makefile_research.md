# sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/Makefile

## Purpose

This Makefile builds the IBM ISM VFIO PCI variant driver.

## Important APIs, Types, and Functions

`obj-$(CONFIG_ISM_VFIO_PCI) += ism-vfio-pci.o` enables the aggregate object, and `ism-vfio-pci-y := main.o` supplies its implementation.

## Control Flow

Kbuild compiles the ISM variant when the Kconfig symbol is enabled.

## State and Persistence Behavior

No runtime state exists in the Makefile.

## Dependencies and Integration Points

It maps Kconfig to the implementation file and relies on VFIO PCI core being selected.

## Risks and Edge Cases

Object-name drift would break module creation.

## Test Signals

Build as built-in and module on s390.
