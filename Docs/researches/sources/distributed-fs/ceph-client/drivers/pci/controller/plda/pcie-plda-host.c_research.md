# sources/distributed-fs/ceph-client/drivers/pci/controller/plda/pcie-plda-host.c

## Purpose
Provides the shared PLDA PCIe root-port host implementation used by platform-specific PLDA controllers. It handles ECAM mapping, MSI and INTx irq domains, local event irq domains, ATR window programming, host bridge allocation/probing, and common teardown.

## Important APIs, Types, And Functions
Exports `plda_pcie_map_bus()`, `plda_init_interrupts()`, `plda_pcie_setup_window()`, `plda_pcie_setup_inbound_address_translation()`, `plda_pcie_setup_iomems()`, `plda_pcie_host_init()`, and `plda_pcie_host_deinit()`. Internal irq handlers include `plda_handle_msi()`, `plda_handle_intx()`, and `plda_handle_event()`. `plda_allocate_msi_domains()` creates the parent MSI domain.

## Control Flow
Platform drivers populate `struct plda_pcie_rp`, then call `plda_pcie_host_init()`. The common path maps `apb` and `cfg` resources, allocates a host bridge, runs optional platform `host_init`, programs config and MEM ATR windows, sets default MSI metadata, initializes interrupts, assigns PCI ops/sysdata, and calls `pci_host_probe()`. Interrupt flow begins at the platform IRQ, chains into event demux, then dispatches INTx or MSI chained handlers as needed.

## State And Persistence
`struct plda_pcie_rp` stores bridge/config bases, irq domains, chained IRQ numbers, MSI bitmap/vector address/count, event bitmap, ops, and raw spinlock. MSI allocation state persists in `plda_msi.used`; ATR and interrupt masks persist in controller registers until deinit or reset.

## Dependencies And Integration Points
Depends on Linux PCI host bridge APIs, irq domains, generic MSI parent-domain helpers, device-tree child interrupt-controller nodes, platform resources named `apb` and `cfg`, and constants from `pcie-plda.h`.

## Risks
IRQ-domain cleanup must only run after all domains/handlers are initialized. `plda_irq_msi_domain_alloc()` allocates one vector regardless of `nr_irqs`, so callers expecting multi-vector atomic allocation need scrutiny. `plda_pcie_setup_iomems()` does not bound ATR index count. Locking around IMASK updates is central to race-free mask/unmask behavior.

## Test Signals
Build users include Microchip and StarFive PLDA controllers. Runtime signals are working ECAM config access, downstream enumeration, MSI allocation/free reuse, INTx interrupt handling, event interrupt masking/acking, host probe failure rollback, and clean root-bus removal.
