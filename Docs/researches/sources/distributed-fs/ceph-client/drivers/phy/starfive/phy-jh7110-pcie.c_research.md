# sources/distributed-fs/ceph-client/drivers/phy/starfive/phy-jh7110-pcie.c

Purpose: StarFive JH7110 PCIe 2.0 PHY provider that can switch the shared PHY block between PCIe and USB3 modes using syscon bits and local PLL/KVCO registers.

Important APIs, types, and functions: `struct jh7110_pcie_phy` stores local registers, optional STG/sys syscon regmaps and offsets, current `enum phy_mode`, and PHY pointer. `phy_usb3_mode_set()` programs STG mode/bus width/enable, sys split, and spread-spectrum PLL enable. `phy_pcie_mode_set()` restores PCIe defaults. `phy_kvco_gain_set()` writes KVCO fine tune values. `jh7110_pcie_phy_set_mode()` dispatches mode changes.

Control flow: probe maps MMIO, creates PHY, optionally obtains syscon phandle args for system and STG registers, applies KVCO tuning, attaches driver data, and registers simple xlate. Set-mode accepts USB host/device/OTG as USB3 mode or `PHY_MODE_PCIE` as PCIe; repeated same mode is a no-op.

State and persistence: current mode is cached in `phy->mode`, initially zero. Hardware syscon and local register mode bits persist until changed.

Dependencies and integration points: generic PHY, syscon/regmap phandle args, StarFive PCIe/USB3 controller consumers.

Risks: USB3 mode requires both syscons; PCIe mode silently works without syscons because default is PCIe. `sys_phy_connect` and STG offsets depend on phandle arg order. The duplicate `PCIE_USB3_PHY_ENABLE` define is harmless but noisy.

Test signals: PCIe enumeration, USB3 mode switch from xHCI/dwc3 consumer, syscon readback, missing syscon DT behavior, and repeated set-mode transitions.
