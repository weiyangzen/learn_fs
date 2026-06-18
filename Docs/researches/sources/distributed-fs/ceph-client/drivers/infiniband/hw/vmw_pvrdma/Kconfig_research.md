<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Kconfig

## Purpose

Adds the `INFINIBAND_VMWARE_PVRDMA` tristate option for the VMware Paravirtualized RDMA driver.

## Important APIs, Types, And Functions

The option depends on `NETDEVICES`, `ETHERNET`, `PCI`, `INET`, and `VMXNET3`. The help text documents that the driver provides low-level support for the VMware PVRDMA adapter and interacts with VMXNET3 for Ethernet capabilities.

## Control Flow

Kconfig selection controls whether the module is built. The VMXNET3 dependency mirrors runtime pairing in `pvrdma_main.c`, where the PVRDMA PCI function finds its sibling VMXNET3 netdev.

## State And Persistence Behavior

No runtime state exists in this file; it controls build configuration.

## Dependencies And Integration Points

Integrates with the RDMA hardware driver Kconfig hierarchy and the VMXNET3 network driver.

## Risks And Edge Cases

Incorrect dependencies can allow building a driver that cannot bind because paired network support is unavailable. Restricting to VMXNET3 is intentional for this paravirtual device.

## Test Signals

Kconfig tests should verify the symbol appears only when the network, PCI, INET, and VMXNET3 prerequisites are satisfiable and that module builds include all objects from the Makefile.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/Kconfig -->
