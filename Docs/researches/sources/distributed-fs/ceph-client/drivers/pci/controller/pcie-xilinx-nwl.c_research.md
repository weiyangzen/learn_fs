# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-nwl.c

Purpose: Implements the Xilinx NWL PCIe bridge host controller. It manages bridge/config/ECAM mappings, PHY and clock enablement, bridge translation setup, link waiting, misc/INTx/MSI interrupt handling, and PCI host registration.

Important APIs/types/functions: `struct nwl_pcie` stores bridge, PCIe, and ECAM bases/physical addresses, PHY array, IRQs, MSI state, INTx domain, clock, and legacy mask lock. `struct nwl_msi` tracks 64 MSI vectors and two MSI IRQ lines. Key functions include `nwl_pcie_bridge_init()`, `nwl_pcie_parse_dt()`, `nwl_pcie_phy_enable()`, `nwl_pcie_init_irq_domain()`, `nwl_pcie_enable_msi()`, `nwl_pcie_map_bus()`, `nwl_pcie_misc_handler()`, `nwl_pcie_leg_handler()`, and MSI high/low handlers.

Control flow: Probe maps `breg`, `pcireg`, and `cfg`, chains INTx, obtains PHYs and clock, enables PHYs, initializes bridge windows and message filtering, waits for PHY link, enables ECAM, requests misc IRQ, clears/enables misc and legacy masks, creates INTx/MSI domains, configures MSI if enabled, then calls `pci_host_probe()`. Config mapping returns ECAM addresses only for root devfn 0 or downstream buses with link up.

State and persistence: Persistent hardware state includes egress bridge and ECAM base registers, ingress subtractive decode, message filters, MSI base/masks, misc/legacy masks, and bridge config interrupt enable. Driver state includes PHY/clock power, chained IRQ handlers, MSI bitmap, and irqdomains.

Dependencies/integration: Uses Linux PCI host bridge and ECAM helpers, PHY and clock frameworks, OF resources/IRQs, generic MSI parent domains, and chained irqdomain handling.

Risks: `nwl_pcie_phy_enable()` loops over the whole four-element PHY array and can call PHY helpers on NULL after DT ends early unless platform data guarantees all entries are valid or helper behavior tolerates it. Error paths after IRQ-domain/MSI setup do not remove domains before PHY cleanup. MSI setup uses chained handlers for named IRQs and assumes MSII capability is present. ECAM size is forced to max.

Test signals: Probe on `xlnx,nwl-pcie-2.11`, clock/PHY enable and disable, link wait timeout, ECAM enumeration, misc error interrupts, INTx delivery, MSI low/high vectors, DMA-coherent path setting, remove/unbind, and link-down config access handling.
