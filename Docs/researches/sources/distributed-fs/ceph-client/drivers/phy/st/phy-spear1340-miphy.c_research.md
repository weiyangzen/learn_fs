# sources/distributed-fs/ceph-client/drivers/phy/st/phy-spear1340-miphy.c

Purpose: SPEAr1340 MiPHY provider for SATA and PCIe modes, programming misc syscon registers and SATA power/reset sequencing.

Important APIs, types, and functions: `struct spear1340_miphy_priv` stores mode, misc regmap, and PHY pointer. `spear1340_miphy_sata_init/exit()` select SATA mode, set PLL config, power SATA domain, and deassert/assert SATA reset. `spear1340_miphy_pcie_init/exit()` select PCIe mode and clear it on exit. PM sleep ops reinitialize SATA on resume and shut it down on suspend.

Control flow: probe gets `misc` syscon, creates one PHY, and registers custom xlate. Xlate records a one-cell mode. Init/exit switch on the stored mode. SATA path includes fixed `msleep(20)` delays around power/reset transitions; PCIe path is immediate syscon programming.

State and persistence: mode is mutable per PHY object. Syscon bits and SATA power domain state persist until exit/suspend. PM callbacks use the last selected mode.

Dependencies and integration points: generic PHY, syscon/regmap, platform PM, SPEAr1340 SATA/PCIe consumers.

Risks: conflicting consumers can race mode changes. Fixed sleep delays are coarse and may hide timing issues. PM callbacks only handle SATA, so PCIe suspend behavior relies on other layers or retention.

Test signals: SATA link after init/resume, PCIe enumeration, syscon register readback, suspend/resume SATA power-cycle tests, and invalid mode phandle tests.
