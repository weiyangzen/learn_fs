# sources/distributed-fs/ceph-client/drivers/phy/samsung/phy-exynos-pcie.c

Purpose: Provides the Exynos5433 PCIe PHY provider. It programs PMU and FSYS sysreg bits plus the PCIe PHY MMIO register block to bring up a 24 MHz reference-clock PCIe PHY.

Important APIs and functions: `exynos_pcie_phy_probe()` maps MMIO, resolves `samsung,pmu-syscon` and `samsung,fsys-sysreg`, creates the generic PHY, and registers an OF PHY provider. PHY operations are `exynos5433_pcie_phy_init()` and `exynos5433_pcie_phy_exit()`. `exynos_pcie_phy_writel()` wraps MMIO writes with register index-to-byte offset conversion.

Control flow: Init enables PMU PHY control, disables L1 exit request and refclk gating, asserts common reset, deasserts MAC reset, selects 24 MHz refclk, clears global reset, writes a fixed tuning sequence into PHY registers, then releases common reset and asserts MAC reset bits. Exit re-enables refclk gating and clears PMU enable.

State and persistence: Driver state is `struct exynos_pcie_phy` with MMIO and two syscon regmaps. Hardware state persists in PMU isolation, FSYS reset/refclk/gating controls, and PHY tuning registers until reset or power loss.

Dependencies and integration points: Depends on generic PHY, syscon/regmap, OF platform matching, and the Exynos PCIe controller consuming the PHY. The driver is built in with `builtin_platform_driver()`, matching early PCIe availability expectations.

Risks: The tuning sequence is hard-coded and SoC-specific. Missing PMU or FSYS syscon phandles prevent probe. Reset ordering is sensitive; wrong values can leave PCIe link training dead or gate the reference clock under the controller.

Test signals: Exynos5433 PCIe probe, PHY init/exit call tracing, PMU/FSYS register dumps, stable PCIe link training, endpoint enumeration, suspend/resume or controller reset testing, and absence of refclk gating during active links.
