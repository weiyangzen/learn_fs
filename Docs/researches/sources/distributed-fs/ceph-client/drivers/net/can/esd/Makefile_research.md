# sources/distributed-fs/ceph-client/drivers/net/can/esd/Makefile

Purpose: object composition for the esd electronics 402 PCI driver.

Important build targets: `esd_402_pci-objs := esdacc.o esd_402_pci-core.o` links shared ESDACC core behavior with PCI card glue. `obj-$(CONFIG_CAN_ESD_402_PCI) += esd_402_pci.o` emits the module or built-in object when configured.

Control flow and state: no runtime flow; the Makefile encodes the split between card resource management and CAN controller logic. Dependencies are the Kconfig symbol and exported-internal functions declared in `esdacc.h`. Risks are link breakage if either object is omitted because PCI code calls `acc_*` functions and core code relies on structures initialized by PCI code. Test signals include module build, modpost symbol resolution, and load-time module metadata.
