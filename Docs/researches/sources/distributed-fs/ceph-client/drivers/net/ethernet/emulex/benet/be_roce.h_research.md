# sources/distributed-fs/ceph-client/drivers/net/ethernet/emulex/benet/be_roce.h

Purpose: this header defines the ABI shared between the be2net Ethernet driver and the ocrdma RoCE driver.

Important APIs, types, and functions: `BE_ROCE_ABI_VERSION` is the compatibility gate. `enum be_interrupt_mode` describes MSI-X, INTx, and MSI modes, though the implementation only supplies MSI-X or INTx. `struct be_dev_info` is the resource handoff object containing MMIO doorbell pointer, unmapped doorbell address and size, optional DPP region, PCI and net devices, MAC address, device family, interrupt mode, and up to `MAX_MSIX_VECTORS` vector numbers plus start index. `struct ocrdma_driver` is the callback table with driver name, ABI version, `add`, `remove`, and `state_change_handler`. `enum be_roce_event` currently exposes `BE_DEV_SHUTDOWN`. Exported APIs are `be_roce_register_driver`, `be_roce_unregister_driver`, and the mailbox helper declaration `be_roce_mcc_cmd`.

Control flow and integration: ocrdma fills `struct ocrdma_driver` and registers it with be2net. The NIC side supplies `struct be_dev_info` when adapters are added, then uses the callback table during remove and shutdown. `be_roce_mcc_cmd` is declared here so RoCE can issue mailbox commands through the NIC driver without depending on the wider private be2net command interface.

State and persistence: the header itself has no state; it defines the data copied or referenced across the driver boundary. The embedded `net_device`, `pci_dev`, and doorbell pointers remain owned by be2net and are valid only for the active NIC lifecycle.

Dependencies and integration points: includes Linux PCI and netdevice headers and relies on `ETH_ALEN`. It must stay synchronized with `be_roce.c` and the ocrdma consumer. The size and semantics of `struct be_dev_info` are ABI-sensitive because both drivers use this layout.

Risks: any field reorder, semantic change, or version mismatch can break RoCE initialization. `MAX_MSIX_VECTORS` caps what the NIC can expose even if more vectors are enabled. The declaration of `be_roce_mcc_cmd` means consumers may compile against a mailbox interface whose implementation must remain available elsewhere in the be2net source set.

Test signals: compile both be2net and ocrdma against the header, verify `BE_ROCE_ABI_VERSION` matches on module load, confirm MSI-X and INTx handoff structures are populated as expected, and run RoCE attach/detach and shutdown tests while the netdev is registered and while it is being removed.
