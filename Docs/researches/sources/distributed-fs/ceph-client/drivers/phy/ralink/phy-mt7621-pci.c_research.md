# sources/distributed-fs/ceph-client/drivers/phy/ralink/phy-mt7621-pci.c

Purpose: Implements the MediaTek MT7621 PCIe PHY driver, including SSC/PLL setup for 20/25/40 MHz crystals, optional E2 revision pipe-reset bypass, and dual-port handling.

Important APIs/types/functions: `struct mt7621_pci_phy` holds regmap, PHY, system clock, MMIO base, dual-port state, and bypass quirk. Key helpers are `mt7621_phy_rmw()`, `mt7621_bypass_pipe_rst()`, `mt7621_set_phy_for_ssc()`, `mt7621_pci_phy_init()`, and power on/off ops. `mt7621_pcie_phy_of_xlate()` records whether the consumer selected a dual-port mode.

Control flow: Probe detects the MT7621 E2 quirk through `soc_device_match()`, maps MMIO, initializes a 32-bit regmap, creates a PHY, gets the system clock, and registers a custom OF xlate provider. Init optionally bypasses pipe reset, reads the XTAL clock rate, forces XTAL/PHY control fields, disables ports, programs PLL/DDS/SSC fields according to clock rate, and sets PLL current/divider controls. Power-on enables PHY and disables force mode for one or two ports; power-off disables PHY and re-enables force mode.

State and persistence: Driver state includes whether the selected consumer asked for dual-port operation and whether the E2 pipe-reset workaround is needed. PLL and force-mode register writes persist until reinitialized or reset by firmware/hardware.

Dependencies and integration points: Depends on generic PHY, regmap MMIO, system clock, platform OF, SoC revision matching, and `dt-bindings/phy/phy.h`. It is registered with `builtin_platform_driver()`, so it is intended for early built-in availability.

Risks: `has_dual_port` is set during OF xlate, so different consumers can alter shared state. Unsupported clock rates fall through to the 20 MHz setup. `mt7621_phy_rmw()` intentionally avoids `regmap_write_bits()` semantics; replacing it would risk PLL misprogramming.

Test signals: Boot MT7621 with 20/25/40 MHz crystals, probe E2 and non-E2 revisions, use one-port and dual-port PHY phandles, verify PCIe link training, inspect PLL register fields, and build as built-in under Ralink and compile-test configs.
