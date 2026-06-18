## sources/distributed-fs/ceph-client/include/linux/brcmphy.h

**Purpose:** This header is the Broadcom Ethernet PHY register and identifier catalog used by PHY drivers. It contains no executable control flow; it defines constants that let MDIO/PHY code identify Broadcom devices, access vendor-specific register windows, configure LEDs, Wake-on-LAN, BroadR-Reach/LRE, EEE, SerDes, RGMII/SGMII modes, power states, and cable diagnostics.

**Important APIs/types/functions:** There are no structs or functions. Important exports are `BRCM_PSEUDO_PHY_ADDR`, many `PHY_ID_BCM*` values, OUI masks, `PHY_BRCM_*` driver flags, `MII_BCM54XX_*` register addresses, interrupt masks, shadow-register selection helpers, LED encodings, expansion-register selectors, WOL register fields, LRE control/status/advertisement masks, and ECD fault/length result definitions.

**Control flow, state, persistence:** Runtime state lives in PHY driver-private data and hardware registers, not this header. The constants encode hardware-visible persistent state such as WOL configuration, PHY power modes, advertised link modes, and diagnostic results; callers must write/read them through MDIO helper paths.

**Dependencies/integration:** Includes `linux/phy.h` and depends on kernel bit macros such as `BIT()` and `GENMASK()`. It integrates with Broadcom PHY drivers under the PHY library and switch drivers that use pseudo-PHY address 30.

**Risks and test signals:** Risks are wrong bit masks, wrong shadow-bank selection, or mixing RDB/expansion addressing paths, all of which can silently misconfigure link, WOL, LEDs, or diagnostics. Test signals are PHY probe ID matching, ethtool link-mode reporting, interrupt delivery, WOL suspend/resume, EEE behavior, cable-test output, and register traces from known Broadcom PHY variants.
