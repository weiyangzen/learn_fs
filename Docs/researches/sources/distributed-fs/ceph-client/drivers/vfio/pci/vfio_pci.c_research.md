# sources/distributed-fs/ceph-client/drivers/vfio/pci/vfio_pci.c

Purpose: implements the generic `vfio-pci` meta-driver that binds arbitrary PCI devices to VFIO using common VFIO PCI core operations.

Important APIs and functions: module parameters for dynamic IDs, INTx masking, VGA resource access, idle D3, SR-IOV, and denylist override; denylist checks for known unsafe Intel QAT/DSA/IAX devices; `vfio_pci_open_device()`, generic VFIO device ops, probe/remove, SR-IOV configure, dynamic id parser, init/exit.

Control flow: module init pushes parameters into VFIO PCI core, registers the PCI driver, and adds dynamic IDs from the `ids` module parameter. Probe rejects denylisted devices unless overridden, allocates a `vfio_pci_core_device`, attaches generic PCI ops including dmabuf physical lookup, and registers the VFIO device. Open enables VFIO core and optionally sets up Intel IGD-specific regions before finishing enable. SR-IOV configure is allowed only when the module parameter is enabled.

State and persistence: static module parameters govern runtime behavior. Per-device state is allocated in VFIO core and stored as driver data; no persistent storage is used.

Dependencies and integration: depends on VFIO PCI core/private helpers, PCI dynamic IDs, optional VGA/IGD support, iommufd attach/detach including PASID ops, and core error handlers.

Risks: disabling the denylist can expose devices with known stability/security errata to untrusted userspace. SR-IOV enablement without a PF userspace driver can create nonfunctional VFs. Dynamic ID parsing must reject malformed strings without corrupting the driver id table.

Test signals: module parameter matrix, denylist allow/block paths, dynamic id parsing, probe failure unwind, Intel IGD open path, SR-IOV configure with and without `enable_sriov`, iommufd attach/detach/PASID ops, and module unload cleanup.
