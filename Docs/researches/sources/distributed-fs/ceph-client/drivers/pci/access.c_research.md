# sources/distributed-fs/ceph-client/drivers/pci/access.c

Purpose: central PCI configuration-space access layer. It validates alignment, serializes config ops when configured, delegates to bus-specific `pci_ops`, exposes generic ECAM/MMIO accessors, implements user-access blocking around unsafe device states, and provides PCIe capability helpers.

Important APIs/types/functions: exports `pci_bus_read/write_config_{byte,word,dword}`, `pci_generic_config_read/write`, `pci_generic_config_read32/write32`, `pci_bus_set_ops()`, `pci_user_read/write_config_*`, `pci_cfg_access_lock/trylock/unlock()`, PCIe capability read/write/clear-set helpers, and device-level `pci_read/write_config_*`. `pci_lock` is the global raw spinlock unless `CONFIG_PCI_LOCKLESS_CONFIG` disables it.

Control flow/state: bus-level macros check offset alignment, lock, call `bus->ops`, and set error responses on failure. User accesses wait on `pci_cfg_wait` while `dev->block_cfg_access` is set. PCIe capability helpers synthesize zero or presence-detect defaults for unimplemented registers and protect selected read-modify-write paths with `dev->pcie_cap_lock`. 32-bit-only config write helpers warn once about adjacent RW1C corruption risk.

Dependencies/integration: depends on `struct pci_bus`, `struct pci_dev`, arch/controller `pci_ops`, wait queues, MMIO read/write primitives, and PCIe capability metadata. Risks include lock ordering, sleeping while dropping/reacquiring `pci_lock`, unsafe partial writes on 32-bit-only hardware, and callers ignoring PCIBIOS errors. Test signals include misaligned access rejection, disconnected-device error responses, config blocking during D-state/BIST transitions, PCIe register default behavior, and lockless-config builds.
