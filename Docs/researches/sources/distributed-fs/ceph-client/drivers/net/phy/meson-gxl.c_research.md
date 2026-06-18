# sources/distributed-fs/ceph-client/drivers/net/phy/meson-gxl.c

## Purpose
This file implements the Amlogic Meson internal PHY driver entries for Meson GXL and G12A internal PHYs. It programs Meson GXL private test banks for fractional PLL setup and works around a known GXL autonegotiation/LPA corruption condition; the G12A entry reuses SMSC/LAN87xx-style support.

## Important APIs, Types, and Functions
Private bank access uses `meson_gxl_open_banks`, `meson_gxl_close_banks`, `meson_gxl_read_reg`, and `meson_gxl_write_reg` through test registers `TSTCNTL`, `TSTREAD1`, and `TSTWRITE`. `meson_gxl_config_init` enables the fractional PLL and writes `FR_PLL_DIV1` and `FR_PLL_DIV0` in the BIST bank. `meson_gxl_read_status` wraps `genphy_read_status` with a pre-check for completed autonegotiation, WOL-bank `LPI_STATUS_RSV12`, `MII_LPA`, and `MII_EXPANSION` consistency. The `meson_gxl_phy` table registers exact IDs `0x01814400` and `0x01803301`.

## Control Flow
Bank reads and writes toggle `TSTCNTL_TEST_MODE` to open private bank access, issue a read or write command with bank and register fields, then always close the bank access before returning. GXL init writes the PLL sequence once during phylib config initialization. Status reads check whether autonegotiation is complete; if it is not complete, control falls through to the generic status read. If autoneg is reported complete but the WOL status bit is missing or the link partner never acknowledged while claiming autoneg support, the driver restarts autoneg instead of trusting the corrupted LPA state.

## State and Persistence Behavior
There is no private software allocation. Persistent state is the internal PHY register state: test-bank access mode, fractional PLL configuration, and autonegotiation state. `meson_gxl_close_banks` attempts to leave test mode disabled after every private access. For G12A, persistent behavior is mostly inherited from `smsc_phy_probe`, `smsc_phy_config_init`, `lan87xx_read_status`, SMSC interrupt handlers, and tunable callbacks.

## Dependencies and Integration Points
The file depends on phylib, MII definitions, ethtool types, bitfield helpers, netdevice headers, and `linux/smscphy.h`. It integrates with generic phylib for reset, suspend/resume, autoneg restart, and unsupported MMD callbacks. Interrupt handling for both entries uses SMSC helper functions, so the internal PHYs are treated as compatible with that interrupt model even though the GXL bank programming is Amlogic-specific.

## Risks and Test Signals
The GXL autoneg workaround depends on undocumented/private WOL-bank bit semantics and may cause repeated autoneg restarts if the bit is unreliable. Bank access is not protected by an explicit MDIO bus lock in these helpers, so correctness depends on phylib's callback serialization. `meson_gxl_config_init` comments label both divider writes as `FR_PLL_DIV1`, which is harmless but can confuse maintenance. Test signals include Meson GXL boot/link at 10/100, repeated autoneg with partners that do and do not support autoneg, forced modes, suspend/resume, interrupt-driven link changes via SMSC helpers, and G12A regression coverage for SMSC tunables.
