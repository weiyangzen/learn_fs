<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.c

Purpose: shared classic Cadence PCIe core helpers. It implements capability search, link-up polling, detect-quiet tuning, outbound region programming, outbound reset, PHY lifecycle helpers, PHY discovery, and common noirq PM operations.

Important APIs/types/functions: `cdns_pcie_find_capability()`, `cdns_pcie_find_ext_capability()`, `cdns_pcie_linkup()`, `cdns_pcie_detect_quiet_min_delay_set()`, `cdns_pcie_set_outbound_region()`, `cdns_pcie_set_outbound_region_for_normal_msg()`, `cdns_pcie_reset_outbound_region()`, `cdns_pcie_init_phy()`, `cdns_pcie_enable_phy()`, `cdns_pcie_disable_phy()`, and exported `cdns_pcie_pm_ops`.

Control flow: outbound setup rounds size up, builds PCI target and descriptor registers, injects bus/devfn in RC mode or function only in EP mode, applies optional CPU address fixup, and writes CPU base registers. PHY init counts `phy-names`, gets each PHY, adds stateless device links, powers PHYs on, and unwinds on failure. PM suspend powers off/exits PHYs; resume reinitializes/powers them.

State/persistence: no independent global state. `struct cdns_pcie` stores register base, PHY arrays, device links, ops, and mode. Hardware state includes outbound windows, detect-quiet field, and PHY power/init state.

Dependencies/integration: Linux PHY framework, OF properties, device links, PCI capability walking macros, Cadence register definitions, and platform-specific `cdns_pcie_ops` for address fixup or link control.

Risks: `cdns_pcie_set_outbound_region()` assumes nonzero size and available region number. PHY init error unwinding starts from the current index and may not remove links already assigned if failure occurs after allocation but before all fields are stored. `cdns_pcie_init_phy()` treats missing `phy-names` as non-fatal, so boards relying on PHY power must provide correct DT.

Test signals: capability search on RP/EP config spaces, outbound MEM/IO/message TLPs, CPU address fixup platforms, multi-PHY init failure unwinds, no-PHY probe, suspend/resume PHY cycling, and detect-quiet quirk register update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/pcie-cadence.c -->
