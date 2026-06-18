<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-imx6.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-imx6.c

Purpose: NXP/Freescale i.MX DesignWare PCIe driver for many generations in RC and EP modes: i.MX6Q/SX/QP, i.MX7D, i.MX8MQ/MM/MP/Q, and i.MX95. It centralizes variant-specific GPR/syscon programming, clocks, resets, regulators, PHY setup, LTSSM control, endpoint features, suspend/resume workarounds, and i.MX95 stream-ID LUT management.

Important APIs/types/functions: `struct imx_pcie_drvdata`, `struct imx_pcie`, `drvdata[]`, `imx_pcie_probe()`, `imx_pcie_host_init()`, `imx_pcie_host_exit()`, `imx_pcie_start_link()`, `imx_pcie_stop_link()`, `imx_add_pcie_ep()`, `imx_pcie_ep_raise_irq()`, PHY helpers `pcie_phy_read/write()`, reset/refclk helpers, `imx_pcie_add_lut_by_rid()`, `imx_pcie_suspend_noirq()`, `imx_pcie_resume_noirq()`, and `imx_pcie_quirk()`.

Control flow: probe allocates DWC and i.MX state, selects variant data, fetches optional PHY MMIO, reset GPIO, clocks, PHY driver, resets, GPR/regmap or SERDES app regmap, TX tuning properties, max speed, supplies, and power domains. EP mode runs `imx_add_pcie_ep()` and adds a default i.MX95 LUT entry. RC mode sets DWC PM/ATU flags, initializes the host, and enables MSI in the root port when available. Host init enables regulators, installs LUT callbacks when needed, asserts resets/PERST, initializes PHY and mode, enables clocks/refclk, powers PHY, disables LTSSM, deasserts reset/PERST, waits for PLL, and configures MPLL. Link start may force Gen1 first for old variants, then performs directed speed change.

State/persistence: state includes clocks, reset controls, GPIO, GPR regmap, regulators, PHY, power domains, MSI control save, i.MX95 LUT cache, controller ID, TX tuning, and variant flags. Hardware state spans IOMUXC GPRs, PHY registers, DWC DBI/ATU, LTSSM/app reset, PERST, refclk override, regulators, and i.MX95 LUTs. Suspend saves MSI/LUT state and either uses DWC suspend or a broken-suspend workaround; resume restores RC, LUT, and MSI state.

Dependencies/integration: DWC host/EP core, Linux PHY and PCIe PHY APIs, reset, regulator, clock, GPIO, regmap/syscon, power domains, OF ID mapping (`iommu-map`/`msi-map`), PCI endpoint framework, and ARM fault hooks for i.MX6 abort handling.

Risks: variant flags are dense and easy to combine incorrectly. Several helper return values from low-level PHY reads/writes are not always checked. `imx_pcie_start_link()` returns 0 after some speed-change failures after resetting PHY, which can mask link failure. i.MX95 LUT programming must reconcile IOMMU and MSI stream IDs and has only 32 entries with 6-bit SIDs. Broken-suspend paths require MSI and RC reinitialization.

Test signals: boot/enumeration across each compatible, endpoint function tests and BAR feature constraints, Gen1-to-Gen2 speed workaround, PERST timing, refclk/CLKREQ override clear after link, regulator and PHY sequencing, suspend/resume on broken and normal variants, i.MX95 LUT add/remove/save/restore with `iommu-map` and `msi-map`, MSI capability preservation, and i.MX6 config-size quirk behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-imx6.c -->
