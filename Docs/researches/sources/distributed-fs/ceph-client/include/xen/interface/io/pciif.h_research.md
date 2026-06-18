# sources/distributed-fs/ceph-client/include/xen/interface/io/pciif.h

Purpose: defines shared structures and constants for Xen PCI frontend/backend configuration-space access, MSI/MSI-X control, and PCIe AER handling.

Important APIs/types/functions: `XEN_PCI_MAGIC`, flags `XEN_PCIF_active`, `XEN_PCIB_AERHANDLER`, `XEN_PCIB_active`; commands `XEN_PCI_OP_conf_read`, `conf_write`, `enable_msi`, `disable_msi`, `enable_msix`, `disable_msix`, and AER operations; errors `XEN_PCI_ERR_*`; `SH_INFO_MAX_VEC`; `struct xen_msix_entry`, `struct xen_pci_op`, `struct xen_pcie_aer_op`, and `struct xen_pci_sharedinfo`.

Control flow: frontend writes a command into shared info, identifying PCI segment, bus, devfn, config offset/size, value, and optional MSI-X vectors. Backend performs the privileged PCI operation and writes `err` and output values. AER operations use the separate `aer_op` record.

State and persistence: `xen_pci_sharedinfo` persists as the command mailbox with active flags and operation payloads. MSI-X entry arrays persist only for an operation.

Dependencies and integration points: used by Xen pcifront/pciback drivers, PCI config space, MSI/MSI-X setup, PCIe AER recovery, and XenBus versioning via `XEN_PCI_MAGIC`.

Risks: single shared operation slots require external serialization. `SH_INFO_MAX_VEC` bounds MSI-X vectors at 128. Incorrect domain/bus/devfn or config offsets can target wrong hardware; backend permission checks are critical.

Test signals: config read/write round trips, denied access checks, MSI and MSI-X enable/disable with vector counts near limits, AER error/resume/slot reset paths, and protocol magic compatibility checks.
