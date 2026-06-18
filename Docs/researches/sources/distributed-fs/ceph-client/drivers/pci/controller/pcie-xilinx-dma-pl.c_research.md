# sources/distributed-fs/ceph-client/drivers/pci/controller/pcie-xilinx-dma-pl.c

Purpose: Implements Xilinx PL XDMA/QDMA PCIe host bridge support. It provides config-space mapping, link validation, bridge enablement, MSI parent-domain support, separate low/high MSI status handlers, INTx and event irqdomains, and variant-specific register layout for QDMA.

Important APIs/types/functions: `struct pl_dma_pcie` holds register/config mappings, physical MSI base, IRQ domains, MSI state, locks, and variant data. `struct xilinx_msi` tracks MSI bitmap/domain and two MSI IRQ lines. Key paths include `xilinx_pl_dma_pcie_map_bus()`, `xilinx_pl_dma_pcie_init_port()`, `xilinx_pl_dma_pcie_init_irq_domain()`, `xilinx_pl_dma_pcie_init_msi_irq_domain()`, `xilinx_request_msi_irq()`, `xilinx_pl_dma_pcie_setup_irq()`, `xilinx_pl_dma_pcie_parse_dt()`, and `xilinx_pl_dma_pcie_probe()`.

Control flow: Probe allocates a host bridge, gets the bus range and variant, creates an ECAM window over the primary resource, optionally maps QDMA bridge registers from `breg`, requests `msi0` and `msi1`, initializes bridge status/masks/MSI decode mode, creates event/INTx/MSI domains, maps and requests event/error/INTx IRQs, then registers PCI host ops. Config mapping rejects downstream accesses when link is down and uses `cfg_base` for QDMA versus `reg_base` for XDMA. MSI handlers drain low/high status registers, clear bits, find mappings, and invoke generic IRQ handling.

State and persistence: State includes ECAM window mappings, MSI bitmap allocations, event/INTx irqdomains, interrupt masks, MSI base registers, MSI status masks, bridge-enable state, and physical register base used as MSI target.

Dependencies/integration: Depends on generic PCI/ECAM APIs, generic MSI parent domains, irqdomain, OF resources and named IRQs, and shared Xilinx interrupt constants.

Risks: Link-up checks reduce but cannot eliminate races before PIO config access; comments note link-down PIO can require controller reset. Probe assigns `err = xilinx_pl_dma_pcie_setup_irq(port);` but does not branch on that error before `pci_host_probe()`, so IRQ setup failures may be masked by later probe behavior. MSI bitmap memory is allocated with `kzalloc()` and domain cleanup does not visibly free it. QDMA uses an offset register accessor, so variant mistakes corrupt accesses.

Test signals: XDMA and QDMA DT probe, config-space enumeration, link-down config rejection, MSI low/high vector delivery including multi-MSI allocations, INTx delivery, event/error IRQ logs, QDMA `breg` mapping, bridge-enable register state, and IRQ setup failure injection.
