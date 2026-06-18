<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/ptm.c -->
# sources/distributed-fs/ceph-client/drivers/pci/pcie/ptm.c

## Purpose
`ptm.c` implements PCIe Precision Time Measurement support. It discovers PTM capabilities, determines root/requester/responder roles and effective granularity, reference-counts enablement along the upstream PTM path, saves/restores PTM control state, suspends/resumes enabled PTM, and optionally exposes PTM context debugfs files for controller-specific implementations.

## Important APIs, Types, and Functions
Key PCI APIs are `pci_ptm_init()`, `pci_save_ptm_state()`, `pci_restore_ptm_state()`, `pci_enable_ptm()`, `pci_disable_ptm()`, `pci_suspend_ptm()`, `pci_resume_ptm()`, and `pcie_ptm_enabled()`. Debugfs APIs under `CONFIG_DEBUG_FS` are `pcie_ptm_create_debugfs()` and `pcie_ptm_destroy_debugfs()`, driven by `struct pcie_ptm_ops` callbacks for context update, validity, clocks, and timestamps.

## Control Flow and State
Initialization finds `PCI_EXT_CAP_ID_PTM`, records `dev->ptm_cap`, resets `ptm_enable_cnt`, adds a saved-control buffer, reads local granularity, finds the upstream PTM partner while skipping switch downstream ports, determines whether the device is a root, requester, or responder, and propagates effective granularity from the upstream source. `pci_enable_ptm()` recursively enables upstream PTM before the target, increments `ptm_enable_cnt`, writes enable/root/granularity bits, and logs granularity. Disable decrements the counter and recursively disables the upstream partner. Suspend disables hardware while preserving the count; resume re-enables if the count is nonzero.

## Dependencies and Integration Points
PTM depends on PCIe extended capability access, upstream bridge topology, atomic counters in `struct pci_dev`, saved capability buffers, module exports used by network drivers, and debugfs integrations used by DesignWare PCIe controller debug code. Public declarations are in `include/linux/pci.h`, while private save/restore hooks are declared in `pci.h`.

## Risks and Test Signals
Risks include recursive enable/disable imbalance, enabling endpoints without a complete upstream PTM path, ambiguous RCiEP time source granularity, resume failing silently after topology changes, and debugfs callbacks racing hardware context updates. Tests should cover root and endpoint enablement, nested users of `pci_enable_ptm()`, suspend/resume, missing upstream PTM, switch downstream-port skipping, debugfs file visibility and locking, and drivers such as mlx5/igc/ice/idpf requesting PTM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/pcie/ptm.c -->
