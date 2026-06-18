# sources/distributed-fs/ceph-client/drivers/net/phy/mxl-gpy.c

## Purpose
This file is the Linux phylib driver for MaxLinear GPY2xx, GPY11x/21x/24x, and MxL862xx Ethernet PHYs. It handles Clause 45 capability discovery, copper link negotiation, SGMII/2500Base-X in-band signaling, MDIX, Wake-on-LAN, LED controls, optional hwmon temperature reporting, loopback, interrupts, and ethtool PHY statistics.

## Important APIs, Types, and Functions
The main state type is `struct gpy_priv`, stored in `phydev->priv`. It contains a mailbox mutex, firmware major/minor values, WoL options, accumulated RX error count, and loopback disable timeout. Driver callbacks are registered through the large `gpy_drivers[]` table and exported with `module_phy_driver()`.

Key callbacks include `gpy_probe()`, `gpy_config_init()`, `gpy21x_config_init()`, `gpy_config_aneg()`, `gpy_read_status()`, `gpy_config_intr()`, `gpy_handle_interrupt()`, `gpy_set_wol()`, `gpy_get_wol()`, `gpy_loopback()`, `gpy115_loopback()`, LED callbacks, `gpy_update_stats()`, and `gpy_get_phy_stats()`. Optional hwmon paths are guarded by `CONFIG_HWMON`; `gpy_hwmon_read()` uses a polynomial conversion while MxL862x2 uses a signed-register linear conversion.

## Control Flow
Probe allocates `gpy_priv`, ensures Clause 45 IDs are populated for Clause 22 access, disables IRQ use unless the device property `maxlinear,use-broken-interrupts` is present, reads firmware version, registers hwmon, and logs firmware details. Init selects the RX error counter. GPY21x variants also mark `2500BASEX` and `SGMII` as possible interfaces.

Autonegotiation first handles forced mode, using Clause 22 forced setup for half duplex and Clause 45 PMA setup for full duplex. In autoneg mode it programs MDIX, Clause 45 advertisements, 1000BASE-T advertisements, restarts negotiation if needed, and may trigger a firmware-specific SGMII renegotiation workaround after polling link for up to four seconds. Status reading refreshes link, LPA, speed, duplex, dynamic SERDES interface, master/slave state, and MDIX.

Interrupt setup acknowledges pending status, enables link/speed/duplex/autoneg/downspeed events, and folds in WoL masks. The interrupt handler ignores unrelated status and uses a mailbox read workaround when link-state or speed changes can leave the interrupt line asserted. WoL writes the attached netdev MAC address into vendor registers and enables magic packet or link-change wake. LED callbacks translate netdev LED triggers to vendor LED registers and allow active high/low polarity control.

## State and Persistence
State is runtime-only in `phydev->priv` and hardware registers. `wolopts` mirrors ethtool WoL state, `rx_errors` accumulates an 8-bit read-clear hardware counter, firmware fields drive workarounds, and `lb_dis_to` prevents rapid loopback re-entry. Hardware state persists across callbacks until reset or reconfiguration.

## Dependencies and Integration Points
The file integrates with phylib, Clause 45 generic helpers, ethtool WoL/stats/LED APIs, Linux hwmon, device properties, netdev address storage, MMD register helpers, and optional firmware-specific behavior. It depends on PHY register definitions and kernel helpers such as `phy_modify_mmd()`, `genphy_c45_*()`, `linkmode_*()`, and `devm_hwmon_device_register_with_info()`.

## Risks
Important risks are hardware-specific timing and interrupt workarounds, read-clear error counter races, incorrect dynamic interface selection on MACs that cannot tolerate SGMII/2500Base-X changes, WoL programming without an attached netdev MAC, firmware-version workaround coverage, and LED trigger mappings that may not match every board design.

## Test Signals
Useful tests include probing every listed PHY ID, forced and autoneg link at 10/100/1000/2500, interface switching between SGMII and 2500Base-X, WoL magic/link-change wake, IRQ storm regression under link flaps, LED trigger/polarity ethtool tests, hwmon temperature reads, loopback timing, and RX error counter accumulation.
