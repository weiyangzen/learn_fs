# sources/distributed-fs/ceph-client/drivers/vfio/pci/ism/Kconfig

## Purpose

This Kconfig file enables the IBM ISM VFIO PCI variant driver for s390.

## Important APIs, Types, and Functions

`ISM_VFIO_PCI` is a tristate option depending on `S390` and selecting `VFIO_PCI_CORE`.

## Control Flow

When selected, the ISM variant driver builds and can bind IBM Internal Shared Memory PCI devices through VFIO.

## State and Persistence Behavior

Only build configuration state is represented.

## Dependencies and Integration Points

It integrates the variant with s390 zPCI behavior and VFIO PCI core.

## Risks and Edge Cases

The driver is architecture-specific because it relies on zPCI load/store instructions and ISM device constraints.

## Test Signals

Build on s390 with `ISM_VFIO_PCI=y/m` and verify the option is unavailable elsewhere.
