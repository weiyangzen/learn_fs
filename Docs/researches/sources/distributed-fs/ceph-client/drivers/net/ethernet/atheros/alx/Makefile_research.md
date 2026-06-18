# sources/distributed-fs/ceph-client/drivers/net/ethernet/atheros/alx/Makefile

## Purpose
Builds the Qualcomm Atheros ALX PCIe Ethernet driver as a composite object.

## Important APIs, Types, and Functions
`obj-$(CONFIG_ALX) += alx.o` and `alx-objs := main.o ethtool.o hw.o` define module composition.

## Control Flow and State
No runtime control flow. The Makefile ensures that PCI/netdev orchestration (`main.o`), ethtool implementation (`ethtool.o`), and low-level hardware helpers (`hw.o`) link together.

## Dependencies and Integration Points
Selected by the parent Atheros Makefile and `CONFIG_ALX`. The object layout matches header boundaries: `alx.h` for driver state, `hw.h`/`reg.h` for hardware definitions, and the three C files for implementation.

## Risks and Test Signals
Build tests should verify that `alx.o` contains all exported symbols required across files, especially `alx_ethtool_ops` and hardware helper functions used by `main.c`.
