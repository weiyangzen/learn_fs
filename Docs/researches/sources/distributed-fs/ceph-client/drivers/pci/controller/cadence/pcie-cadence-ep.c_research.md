<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-ep.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-ep.c

Purpose: Cadence PCIe endpoint controller implementation for the Linux PCI EPC framework. It programs endpoint configuration headers, BAR apertures, inbound BAR translations, outbound mappings, MSI/MSI-X/INTx delivery, SR-IOV VF addressing, function enablement, and endpoint startup.

Important APIs/types/functions: EPC callbacks in `cdns_pcie_epc_ops`: `cdns_pcie_ep_write_header()`, `cdns_pcie_ep_set_bar()`, `cdns_pcie_ep_clear_bar()`, `cdns_pcie_ep_map_addr()`, `cdns_pcie_ep_unmap_addr()`, MSI/MSI-X setters/getters, `cdns_pcie_ep_raise_irq()`, `cdns_pcie_ep_map_msi_irq()`, and `cdns_pcie_ep_start()`. Public setup/teardown are `cdns_pcie_ep_setup()` and `cdns_pcie_ep_disable()`.

Control flow: setup maps `reg` and `mem`, reads outbound-region and function/VF counts, disables all but function 0, creates the EPC, initializes endpoint memory, allocates a 128 KiB IRQ scratch window, reserves outbound region 0 for IRQs, applies detect-quiet quirk, and notifies EPC init. BAR setup computes the next power-of-two aperture, writes local-management BAR control, resolves PF/VF hardware function numbers, and writes inbound BAR target addresses. Outbound map finds a free region and calls Cadence common translation programming. IRQ delivery reuses region 0 for normal messages, MSI writes, or MSI-X table target writes.

State/persistence: runtime state is `struct cdns_pcie_ep`: outbound region bitmap/address table, IRQ CPU/PCI mapping cache, pending INTx bitmap, spinlock, EPF BAR pointers, function/VF allocation, and quirk flags. Hardware state includes LM function enable bits, BAR config, inbound/outbound AT windows, PCI config capability fields, and interrupt status.

Dependencies/integration: Cadence common helpers, Linux `pci_epc`/`pci_epf`, endpoint memory allocator, PCI capability helpers, platform resources, and optional DT properties `cdns,max-outbound-regions`, `max-functions`, and `max-virtual-functions`.

Risks: outbound region allocation is limited by `BITS_PER_LONG` and reserves region 0, so high region counts need review. VF handling only programs VF BAR config for `vfn == 1`; other VFs rely on computed function mapping. MSI-X assumes the selected BAR pointer and table memory are valid. INTx status updates rely on a narrow spinlock because remote RC and local EP can both touch PCI status. The code does not range-check all capability offsets before using them.

Test signals: EPC function binding, PF and VF header writes, 32/64-bit and prefetch BAR sizing, BAR clear, outbound map exhaustion, INTx assert/deassert, MSI vector counts and writes, MSI-X table/PBA placement, SR-IOV VF #1 device ID, link start, and endpoint teardown freeing EPC memory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-ep.c -->
