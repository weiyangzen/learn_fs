# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_bus.h

Purpose: Declares the Ionic bus abstraction used by common driver code to hide PCI-specific IRQ, doorbell, and driver registration details.

Important APIs/types/functions: Exposes IRQ lookup/allocation/free (`ionic_bus_get_irq()`, `ionic_bus_alloc_irq_vectors()`, `ionic_bus_free_irq_vectors()`), bus name lookup (`ionic_bus_info()`), module bus registration (`ionic_bus_register_driver()`, `ionic_bus_unregister_driver()`), and doorbell page map/unmap helpers.

State and persistence: No state is defined here; implementation state is stored in `struct ionic` and its PCI BAR table.

Dependencies and integration: Implemented by `ionic_bus_pci.c` and consumed by LIF, debugfs, ethtool, devlink, and main module code.

Risks and test signals: Common code assumes the PCI implementation has mapped BARs and allocated MSI-X vectors before use. Test vector allocation failures, doorbell page map/unmap for queue counts, and module register/unregister paths.
