# sources/distributed-fs/ceph-client/drivers/bus/mhi/host/Makefile

Purpose: builds host-side MHI objects and the optional generic PCI controller.

Important declarations: `mhi-y := init.o main.o pm.o boot.o`; `mhi-$(CONFIG_MHI_BUS_DEBUG) += debugfs.o`; `obj-$(CONFIG_MHI_BUS_PCI_GENERIC) += mhi_pci_generic.o`; `mhi_pci_generic-y += pci_generic.o`.

Control flow and state: build aggregation only. It ensures firmware boot support is always part of the host core and debugfs is conditional.

Dependencies and integration: driven by `CONFIG_MHI_BUS`, `CONFIG_MHI_BUS_DEBUG`, and `CONFIG_MHI_BUS_PCI_GENERIC`. Links with shared common headers and public MHI APIs.

Risks and tests: missing object entries would remove runtime functionality such as firmware loading or debugfs. Test signals include host core link, debugfs symbol inclusion/exclusion, and generic PCI module builds.
