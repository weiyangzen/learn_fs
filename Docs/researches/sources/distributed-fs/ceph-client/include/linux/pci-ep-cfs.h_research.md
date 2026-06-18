# Research: sources/distributed-fs/ceph-client/include/linux/pci-ep-cfs.h

Purpose: `pci-ep-cfs.h` declares configfs group creation/removal helpers for PCI endpoint controllers and endpoint functions.

Important APIs/types/functions: when `CONFIG_PCI_ENDPOINT_CONFIGFS` is enabled, `pci_ep_cfs_add_epc_group()`, `pci_ep_cfs_remove_epc_group()`, `pci_ep_cfs_add_epf_group()`, and `pci_ep_cfs_remove_epf_group()` manage configfs groups. Disabled stubs return `NULL` or no-op.

Control flow and state: endpoint core or drivers create configfs groups by name, expose runtime configuration, and remove groups during teardown. State lives in configfs objects and the endpoint core.

Dependencies and integration points: depends on `linux/configfs.h`, PCI endpoint core, and userspace-driven endpoint configuration.

Risks and test signals: risks include group lifetime leaks, duplicate names, missing removal on probe failure, and callers not handling disabled stubs. Tests should cover configfs mount interactions, create/remove cycles, duplicate group names, disabled-config builds, and module unload.
