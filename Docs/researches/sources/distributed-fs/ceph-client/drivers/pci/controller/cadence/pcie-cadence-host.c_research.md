<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host.c

Purpose: classic Cadence PCIe host controller implementation. It maps PCI config space through outbound region 0, initializes the root port, programs outbound IO/MEM windows, configures inbound DMA BARs, starts the link, and registers the root bus.

Important APIs/types/functions: `cdns_pci_map_bus()`, `cdns_pcie_host_init_root_port()`, `cdns_pcie_host_bar_ib_config()`, `cdns_pcie_host_init_address_translation()`, `cdns_pcie_host_link_setup()`, `cdns_pcie_host_init()`, `cdns_pcie_host_disable()`, and `cdns_pcie_host_setup()`. It exports `cdns_pci_map_bus`, `cdns_pcie_host_bar_ib_config`, `cdns_pcie_host_init`, `cdns_pcie_host_link_setup`, `cdns_pcie_host_disable`, and `cdns_pcie_host_setup`.

Control flow: host setup maps `reg` and `cfg`, starts the link, marks all inbound BARs available, initializes root port IDs/class/ASPM quirks, reserves outbound region 0 for config cycles, maps bridge windows to outbound regions 1..N, maps DMA ranges through inbound BARs, installs pci_ops when the bridge has none, and calls `pci_host_probe()`. Config access to non-root buses rewrites region 0 bus/devfn/type registers per access.

State/persistence: state is held in `struct cdns_pcie_rc` and host bridge resources. Hardware persistence includes root-port config registers, BAR config, inbound and outbound AT windows, PTM response enable, and link-training bit controlled by platform ops. Disable removes the root bus, deinitializes AT/root-port state, stops link, and disables PTM response.

Dependencies/integration: PCI host bridge framework, Cadence common translation helpers, platform resources named `reg` and `cfg`, optional DT `vendor-id` and `device-id`, and platform-specific `cdns_pcie_ops`.

Risks: `cdns_pcie_host_link_setup()` returns 0 even when `cdns_pcie_host_start_link()` reports the link never came up, so enumeration may continue after link failure. In `cdns_pcie_host_unmap_dma_ranges()`, BAR config reset writes a complemented mask value rather than preserving unrelated bits, which needs hardware validation. Outbound region count is not checked against bridge window count here.

Test signals: root-only config access rejection for nonzero devfn, downstream config cycles, IO and MEM outbound windows, DMA inbound `dma-ranges`, ASPM L0s/L1 quirk masking, link timeout behavior, host disable/remove, and resume replay through users such as J721E.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence-host.c -->
