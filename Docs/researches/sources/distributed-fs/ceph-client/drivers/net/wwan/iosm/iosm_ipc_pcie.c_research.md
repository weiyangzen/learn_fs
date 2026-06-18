# sources/distributed-fs/ceph-client/drivers/net/wwan/iosm/iosm_ipc_pcie.c

Purpose: implements the IOSM PCI driver: probe/remove, BAR mapping, MSI setup, DMA helpers, ASPM/BIOS sleep policy, suspend/resume callbacks, hibernation unregister/re-register, and module registration.

Important functions: `ipc_pcie_probe`, `ipc_pcie_remove`, resource request/release helpers, `ipc_pcie_config_aspm`, `ipc_pcie_check_aspm_enabled`, `ipc_pcie_check_data_link_active`, `ipc_pcie_suspend/resume`, SKB/DMA helpers `ipc_pcie_addr_map/unmap`, `ipc_pcie_alloc_skb`, `ipc_pcie_alloc_local_skb`, `ipc_pcie_kfree_skb`, and module init/exit.

Control flow: probe allocates `iosm_pcie`, enables PCI, sets 64-bit DMA mask, reads ACPI WWAN RTD3 policy, maps BAR0 doorbells and BAR2 scratchpad, acquires MSI, and initializes imem. Remove cleans imem first, then IRQ/BAR/PCI resources. Suspend chooses force-sleep s2idle or host-sleep D3L2 path based on BIOS policy; resume reverses it. Hibernation unregisters the PCI driver around restore.

State/dependencies: `iosm_pcie` stores PCI device, BAR pointers, doorbell offsets, suspend bit, and RTD3 mode. Dependencies include PCI, ACPI DSM, PM notifier, rtnetlink include, local IRQ/imem/protocol, DMA mapping, and SKB allocation. Risks: unwind ordering, DMA mapping lifetime in SKB cb, ACPI object type assumptions, ASPM only logged not changed, and hibernation registration races. Test signals: probe failure injection at each step, DMA map error, remove after partial init, suspend/resume modes, hibernation notifier, and supported PCI IDs.
