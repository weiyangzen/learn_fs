<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-exynos.c

Purpose: Samsung Exynos DesignWare PCIe host driver. It sequences Exynos ELBI sideband DBI access, core resets, clocks, regulators, PHY power, IRQ pulse handling, link startup, host initialization, removal, and noirq suspend/resume.

Important APIs/types/functions: `struct exynos_pcie`, sideband helpers `exynos_pcie_sideband_dbi_w_mode()` and `_r_mode()`, reset helpers, `exynos_pcie_start_link()`, `exynos_pcie_read_dbi()`, `exynos_pcie_write_dbi()`, `exynos_pcie_host_init()`, `exynos_add_pcie_port()`, `exynos_pcie_probe()`, and PM callbacks.

Control flow: probe allocates driver state, gets PHY, enables all clocks, gets/enables `vdd18` and `vdd10`, then initializes the DWC host. Host init installs root-bus own-config ops, asserts core reset, powers PHY, deasserts reset, and enables pulse IRQs. DBI accesses temporarily set ELBI sideband bits before calling generic DWC read/write. Resume re-enables supplies, reruns host init, sets up RC registers, starts link, and waits for link.

State/persistence: runtime state holds embedded `struct dw_pcie`, clock bulk array, PHY, and regulators. Hardware state includes ELBI reset bits, sideband DBI enable bits, pulse interrupt enables/status, PHY power, DWC root-port registers, and regulator state. Suspend powers these down; resume reconstructs them.

Dependencies/integration: DWC host core, Exynos ELBI resource from DWC platform mapping, PHY framework, bulk clocks, regulators, IRQs, and DT compatible `samsung,exynos5433-pcie`.

Risks: `phy_init()` and `phy_power_on()` results in host init are not checked. Root-bus config ops only access the root port and return device-not-found for other slots; downstream config access is handled by DWC host machinery. Probe failure calls `phy_exit()` even if host init failed before PHY init. Regulator/PHY ordering is strict for suspend/resume.

Test signals: regulator and clock enable sequencing, sideband DBI read/write correctness, root-port config access, link-up bit polling, pulse IRQ clear, suspend/resume link restoration, and clean remove with supplies disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pci-exynos.c -->
