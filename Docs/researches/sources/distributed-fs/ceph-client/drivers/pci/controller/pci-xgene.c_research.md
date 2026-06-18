# sources/distributed-fs/ceph-client/drivers/pci/controller/pci-xgene.c

## Purpose
`pci-xgene.c` drives APM X-Gene PCIe root complexes for OF systems and supplies ACPI ECAM ops for X-Gene v1/v2 quirks. It programs controller CSR/CFG windows, outbound and inbound address translations, DMA ranges, root-port IDs, config access behavior, and link status reporting.

## Important APIs, Types, And Functions
`struct xgene_pcie` stores OF/device pointers, clock, CSR/config bases, config physical address, link state, and IP version. PCI operations are `xgene_pcie_map_bus()`, `xgene_pcie_config_read32()`, and generic writes. `xgene_pcie_setup()` clears firmware mappings, writes vendor/device IDs, programs outbound ranges via `xgene_pcie_map_ranges()`, maps inbound DMA ranges via `xgene_pcie_parse_map_dma_ranges()`, and reports link status. ACPI paths export `xgene_v1_pcie_ecam_ops` and `xgene_v2_pcie_ecam_ops`.

## Control Flow, State, And Persistence
Config access rejects nonzero devfn on the root bus and hides root BAR0/BAR1 because they are used for PCI-to-native translation. It writes `RTDID` before each config access so hardware emits the right BDF. Root-bus reads clear the v1 RRS Software Visibility bit to avoid endless retries on nonexistent devices. Probe defers until the X-Gene MSI domain is ready when `CONFIG_PCI_XGENE_MSI` and the MSI node exist. Hardware translation state is built at probe and not persisted; the in-memory state records only mapping bases, clock, and link status.

## Dependencies, Integration Points, Risks, And Test Signals
The driver uses OF/ACPI PCI helpers, generic ECAM for ACPI, clocks, host bridge resource windows, `dma-ranges`, X-Gene MSI readiness detection, and generic PCI host probing. It expects named OF resources `"csr"` and `"cfg"` for platform mode. Risks include invalid inbound DMA range sizing, exceeding three inbound regions, hidden root BAR diagnostic confusion, and v1 RRS retry regressions. Test deferred probe until MSI is present, `RTDID`-based config access, endpoint DMA through PIMs, root BAR hiding, and accurate link-up lane/speed messages.
