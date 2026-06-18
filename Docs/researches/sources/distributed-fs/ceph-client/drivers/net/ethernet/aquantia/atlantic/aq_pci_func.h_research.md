<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.h -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.h

Purpose: declares the PCI-facing interface used by NIC lifecycle code and module init/exit code.

Important APIs/types: `struct aq_board_revision_s` maps a PCI device/revision to `aq_hw_ops` and `aq_hw_caps_s`. Public functions allocate/free per-vector IRQs, query IRQ type, and register/unregister the PCI driver.

Control flow: `aq_nic_cfg_start` queries `aq_pci_func_get_irq_type`; `aq_nic_start` uses `aq_pci_func_alloc_irq`; `aq_nic_stop` uses `aq_pci_func_free_irqs`; module setup uses register/unregister. The board-revision structure is consumed internally by probe.

State and persistence: no storage beyond declarations. Runtime state is passed through `struct aq_nic_s` and maintained in the implementation.

Dependencies and integration: includes `aq_common` and `aq_nic`, tying PCI setup to the generic NIC object and hardware capability abstraction.

Risks: any change to IRQ helper signatures affects NIC start/stop paths; board table declarations must remain aligned with hardware ops/caps definitions. Test signals are compile coverage and successful probe/open/close across MSI-X, MSI, and legacy INTx variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/aquantia/atlantic/aq_pci_func.h -->
