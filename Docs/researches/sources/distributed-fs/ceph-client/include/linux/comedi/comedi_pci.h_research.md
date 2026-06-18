# sources/distributed-fs/ceph-client/include/linux/comedi/comedi_pci.h

Purpose: This header provides Comedi helper APIs for PCI-backed Comedi drivers.

Important APIs/types/functions: It defines several PCI vendor IDs not present in `pci_ids.h`, declares `comedi_to_pci_dev`, `comedi_pci_enable`, `comedi_pci_disable`, `comedi_pci_detach`, `comedi_pci_auto_config`, `comedi_pci_auto_unconfig`, `comedi_pci_driver_register`, `comedi_pci_driver_unregister`, and macro `module_comedi_pci_driver`.

Control flow: A PCI probe path calls Comedi PCI auto-config with the matched `pci_dev`, Comedi driver, and context. Register/unregister helpers pair a Comedi driver with a PCI driver, while enable/disable/detach manage PCI device resources.

State and persistence behavior: State lives in `struct comedi_device`, its `hw_dev`, PCI enable/resource state, and Comedi attachment state. The macro wires module init/exit to paired register/unregister calls.

Dependencies and integration points: It includes `<linux/pci.h>` and `comedidev.h`, integrating PCI bus probe/remove with Comedi core auto-configuration and low-level board drivers.

Risks: Resource enable/disable must be balanced. Auto-unconfig must run on remove to detach Comedi devices. Vendor IDs duplicated here should not conflict with future central definitions.

Test signals: PCI probe/remove, module load/unload, BAR/IRQ resource cleanup, Comedi minor creation, and hot-unplug or driver unbind tests are useful signals.
