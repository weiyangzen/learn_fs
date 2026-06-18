# sources/distributed-fs/ceph-client/drivers/vfio/pci/hisilicon/Kconfig

## Purpose

This Kconfig file enables the HiSilicon ACC VFIO PCI variant driver, which adds live migration support for HiSilicon accelerator virtual functions.

## Important APIs, Types, and Functions

`HISI_ACC_VFIO_PCI` is a tristate option depending on ARM64 or 64-bit compile test, PCI MSI, and HiSilicon QM/HPRE/SEC2/ZIP crypto drivers. It selects `VFIO_PCI_CORE`.

## Control Flow

When selected, the hisilicon subdirectory builds `hisi-acc-vfio-pci.o`, allowing supported Huawei accelerator VFs to bind through driver override and reuse VFIO PCI core.

## State and Persistence Behavior

Only build configuration state is represented.

## Dependencies and Integration Points

It ties the variant to hardware crypto drivers that provide PF/QM access needed for migration, plus PCI MSI and VFIO PCI core.

## Risks and Edge Cases

Migration support depends on PF driver availability and hardware generation. Kconfig dependencies ensure compile-time access to PF helper symbols but do not guarantee runtime PF binding.

## Test Signals

Build on ARM64 and COMPILE_TEST 64-bit configs with required crypto drivers enabled, and verify unsupported architectures hide the option.
