# sources/distributed-fs/ceph-client/drivers/net/phy/vitesse.c

## Purpose
`vitesse.c` is the phylib driver collection for Vitesse/Microsemi PHYs including VSC82xx, VSC73xx, VSC86xx, and VSC8211/8221 devices. It provides model-specific initialization sequences, RGMII skew control, SGMII in-band configuration, downshift tunables, MDIX controls, interrupt handling, and forced-mode auto-crossover setup.

## Important APIs, Types, And Functions
Important helpers include `vsc824x_config_init()`, `vsc824x_add_skew()`, `vsc8662_inband_caps()`, `vsc8662_config_inband()`, `vsc73xx_read_page()`, `vsc73xx_write_page()`, `vsc73xx_get_downshift()`, `vsc73xx_set_downshift()`, `vsc73xx_config_init()`, `vsc738x_config_init()`, `vsc739x_config_init()`, `vsc73xx_mdix_set()`, `vsc73xx_read_status()`, `vsc8601_config_init()`, `vsc82xx_config_intr()`, `vsc82xx_handle_interrupt()`, `vsc8221_config_init()`, and `vsc82x4_config_aneg()`.

## Control Flow
Driver registration maps each PHY ID to the appropriate init and operation callbacks. VSC824x init writes auxiliary control/status and optionally applies TX/RX skew for `rgmii-id`. VSC8662 in-band config toggles MAC autoneg/bypass bits and soft-resets if the extended control bit changed. VSC738x/VSC739x init executes vendor application-note register sequences, then common VSC73xx setup configures receiver/LEDs, enables maximum downshift, and defaults MDIX to auto. VSC73xx autoneg writes MDIX policy then calls generic autoneg; status first reads current MDI/MDI-X indication, then delegates to `genphy_read_status()`. VSC82x4 forced 10/100 operation calls `genphy_setup_forced()` and writes extended reserved registers to keep auto crossover active.

## State And Persistence
There is no private allocation. Runtime policy persists in PHY registers and phylib fields (`mdix_ctrl`, `mdix`, interface mode, autoneg, speed). Page state is accessed through `read_page`/`write_page` callbacks for VSC73xx extended page operations.

## Dependencies And Integration Points
The driver depends on phylib, MII/ethtool constants, bitfield helpers, and module MDIO matching. Integration points include phylib config/init/aneg/status/interrupt callbacks, ethtool PHY downshift tunables, in-band negotiation callbacks, and page access callbacks.

## Risks And Edge Cases
Several initialization sequences are undocumented magic values from application notes, so revision-specific regressions are plausible. VSC738x revision 0 has a special sequence based on low PHY ID revision bits. Interrupt disable must read status before masking because some Vitesse parts cannot clear interrupts after disabling. `vsc73xx_mdix_get()` does not check for negative `phy_read()` return values before interpreting bits. Forced MDIX mode for VSC73xx cannot truly force MDIX and falls back to autoconfig.

## Test Signals
Test each matched PHY ID, RGMII-ID skew application and non-application, VSC8662 in-band enable/disable/bypass with reset behavior, VSC73xx downshift get/set including invalid counts, forced and autoneg MDIX modes, interrupt enable/disable and handler masks, VSC738x rev 0 and nonzero init paths, and forced 10/100 auto-crossover programming.
