
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/msi.c

Purpose: architecture MSI/MSI-X delegation layer that routes PCI MSI setup and teardown through the owning PowerPC PCI host bridge controller operations.

Important APIs/types/functions: `arch_setup_msi_irqs`; `arch_teardown_msi_irqs`; `pci_bus_to_host`; `pci_controller->controller_ops.setup_msi_irqs`; `teardown_msi_irqs`.

Control flow: setup maps the device's bus to its host bridge, rejects setup with `-ENOSYS` if either setup or teardown callback is absent, rejects multiple vector classic MSI requests by returning 1, and otherwise calls the controller setup hook. Teardown repeats the host lookup and calls teardown if present because teardown can be invoked even after `-ENOSYS` setup.

State and persistence: this file holds no state; MSI state is owned by PCI core and platform controller callbacks.

Dependencies and integration: integrates generic PCI/MSI code with platform-specific PowerPC PHB MSI backends.

Risks: multiple MSI vectors are unsupported for classic MSI in this architecture layer; missing controller callbacks leave devices without MSI; teardown must be null-safe for failed setup.

Test signals: PCI device MSI and MSI-X enable/disable on each PHB backend, no-callback fallback to INTx, multi-vector MSI rejection, and teardown after failed setup.
