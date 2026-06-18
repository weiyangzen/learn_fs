## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-spear13xx.c

Purpose: SPEAr13xx DesignWare PCIe root-complex glue. It initializes the SPEAr application register block, PHY, clock, MSI interrupt path, and root-port DBI quirks for the ST SPEAr1340 compatible.

Important APIs, types, and functions: `struct spear13xx_pcie` stores a pointer to allocated `struct dw_pcie`, application register base derived from DBI plus `0x2000`, PHY, and clock. `struct pcie_app_reg` documents the app register layout. `spear13xx_pcie_probe()` allocates private and DWC objects, gets `"pcie-phy"`, initializes it, enables the clock, applies optional Gen1 restriction from `st,pcie-is-gen1`, and calls `spear13xx_add_pcie_port()`. `spear13xx_pcie_host_init()` limits Max Read Request Size to 128 bytes, programs vendor/device IDs, and enables MSI interrupt masking. `spear13xx_pcie_start_link()` writes RC mode, misc-control enable, LTSSM enable, and region translation enable. `spear13xx_pcie_irq_handler()` services `MSI_CTRL_INT` by calling `dw_handle_msi_irq()`.

Control flow: probe performs PHY/clock setup before DesignWare host init. Host init computes `app_base`, applies DBI changes, and unmasks app MSI. Link training starts when the DWC core calls `start_link()`. The single platform IRQ is requested with `IRQF_SHARED | IRQF_NO_THREAD`; the handler clears all seen app interrupt status bits.

State and persistence: hardware-only state includes app control bits, app interrupt mask/status, clock enable, PHY init, Gen1 limit in DWC state, DBI vendor/device IDs, and Max Read Request Size. No persistent state exists. There is no explicit remove path because the driver is built in and suppresses bind attributes.

Dependencies and integration points: platform DT match `st,spear1340-pcie`, DesignWare host core, `CONFIG_PCI_MSI` for MSI handling, PHY framework, clock framework, OF property parsing, and shared PCI IRQ behavior.

Risks: `phy_init()` return is ignored in probe, so PHY init failure can be hidden. Clock cleanup is only on add-port failure. The IRQ handler uses `BUG_ON(!IS_ENABLED(CONFIG_PCI_MSI))` if MSI status appears without MSI support, which is harsh. `app_base = dbi_base + 0x2000` assumes a fixed mapping.

Test signals: SPEAr1340 boot should show root port registration, a 128-byte read request setting, link-up from `XMLH_LINK_UP`, MSI interrupt delivery through DWC, behavior with `st,pcie-is-gen1`, and failure-path clock cleanup when IRQ or host init fails.
