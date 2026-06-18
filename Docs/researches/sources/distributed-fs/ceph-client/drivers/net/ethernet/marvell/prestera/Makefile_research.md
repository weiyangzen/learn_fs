# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/Makefile

## Purpose
`Makefile` wires Prestera source files into the kernel build, defining the core `prestera` composite module and optional `prestera_pci` module.

## Important APIs, Types, and Definitions
`obj-$(CONFIG_PRESTERA) += prestera.o` builds the aggregate driver from main, hardware, DSA, RX/TX, devlink, ethtool, switchdev, ACL, flow, flower, span, counter, router, router hardware, and matchall objects. `obj-$(CONFIG_PRESTERA_PCI) += prestera_pci.o` builds the PCI transport.

## Control Flow
There is no runtime flow. Build flow links all `prestera-objs` into one module/object when `CONFIG_PRESTERA` is enabled.

## State and Persistence
The persistent effect is the object composition used by the kernel build system. It determines which implementation files share one module namespace and init/exit lifecycle.

## Dependencies and Integration Points
It depends on the Kconfig symbols from the adjacent `Kconfig`. ACL and counter files in this subset are part of the `prestera.o` aggregate and integrate with flow/flower/matchall/router files not in this work item.

## Risks and Edge Cases
Adding/removing objects changes module link coverage. Because many subsystems are linked into one aggregate, missing object entries can appear as unresolved symbols only for specific configs.

## Test Signals
Run kernel builds for built-in and module variants, verify `prestera_acl.o` and `prestera_counter.o` are included, and test `CONFIG_PRESTERA_PCI` independently follows `CONFIG_PRESTERA`.
