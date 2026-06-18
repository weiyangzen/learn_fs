# sources/distributed-fs/ceph-client/drivers/net/phy/broadcom.c

## Purpose
`broadcom.c` is the main Broadcom PHY driver collection for BCM54xx Gigabit PHYs, BCM54810/54811 BroadR-Reach PHYs, BCM54616S fiber/SerDes modes, Fast Ethernet BCM5221/5241/AC131 PHYs, and several internal switch PHY IDs. It centralizes Broadcom copper initialization, interrupt setup through shared helpers, RGMII delay handling, APD/IDDQ power management, Wake-on-LAN, PTP hook-up, statistics, link-change DAC wake tweaks, and BroadR-Reach status/autoneg support.

## Important APIs, Types, And Functions
`struct bcm54xx_phy_priv` stores stats, optional Broadcom PTP state, wake IRQ state, and BroadR-Reach mode. `struct bcm54616s_phy_priv` tracks whether the BCM54616S fiber path is 1000BASE-X. Init helpers include `bcm54xx_config_clock_delay()`, `bcm54210e_config_init()`, `bcm54612e_config_init()`, `bcm54616s_config_init()`, `bcm54xx_phydsp_config()`, `bcm54xx_adjust_rxrefclk()`, `bcm54811_config_init()`, and `bcm54xx_config_init()`.

Power/WoL functions are `bcm54xx_suspend()`, `bcm54xx_resume()`, `bcm54xx_iddq_set()`, `bcm54xx_phy_get_wol()`, `bcm54xx_phy_set_wol()`, and `bcm54xx_set_wakeup_irq()`. BroadR-Reach functions are `bcm5481x_set_brrmode()`, `bcm5481x_read_abilities()`, `bcm5481_config_aneg()`, `bcm54811_config_aneg()`, `bcm54811_read_status()`, and supporting LRE helpers. Fast Ethernet helpers are `brcm_fet_config_init()`, `brcm_fet_config_intr()`, `brcm_fet_handle_interrupt()`, `brcm_fet_suspend()`, `bcm5221_config_aneg()`, and `bcm5221_read_status()`.

## Control Flow
Common BCM54xx probe allocates stats, tries `bcm_ptp_probe()` for supported PTP-capable models, obtains an optional wake GPIO, requests a disabled wake IRQ if present, and marks the MDIO device wake-capable if either normal PHY interrupt or wake IRQ exists. Common config masks interrupts globally, programs the per-event interrupt mask, applies model-specific setup, runs PHY DSP workarounds, configures LEDs unless the PHY is on an SFP module, initializes PTP registers if present, and acknowledges Wake-on-LAN interrupt status.

RGMII delay setup updates the AUXCTL RX skew bit and shadow clock-control TX delay bit according to `phydev->interface`. BCM54210E can force master mode. BCM54612E/54811 can route CLK125 to LED4 when the reference clock is used. BCM54616S switches between SGMII and 1000BASE-X register sets by powering down SerDes, changing shadow mode, and powering interfaces back up. The PHY DSP path enables SMDSP, applies model-specific expansion register workarounds, and disables SMDSP again.

Suspend snapshots stats, stops active PTP workers, acknowledges WoL status, enables wake IRQ if WoL is active, otherwise powers down BMCR and optionally enters IDDQ. Resume disables wake IRQ, exits IDDQ, resumes BMCR, waits for internal reset to clear, optionally soft-resets, and reruns common config. Link-change notify adjusts DAC wake bits for 10M links when auto power down is enabled.

BroadR-Reach flow reads the `brr-mode` DT property, toggles the LRE overlay, switches supported link modes to single-pair/LDS capabilities, and uses LRE-specific autoneg/status functions. BCM54811 disables LDS autoneg in BRR mode because the datasheet requires a reserved bit to be cleared after reset. Fast Ethernet flow resets, programs interrupt masks, shadow LED/MDIX/APD state, and uses special suspend low-power writes; BCM5221 adds manual/auto MDIX programming and status decoding.

## State And Persistence
Driver state is held in `phydev->priv`, stats shadow arrays, optional PTP state owned by `bcm-phy-ptp.c`, wake IRQ enabled state, and BRR mode. Hardware state spans normal Clause 22 registers, Broadcom shadow registers, expansion registers, BMCR power state, WoL registers, and LRE registers. There is no filesystem persistence. Resume paths deliberately replay configuration because suspend/reset loses hardware state.

## Dependencies And Integration Points
The file depends on `bcm-phy-lib.h` for shared Broadcom register/stat/interrupt/WoL/LED helpers, `bcm-phy-ptp.c` exported helpers for PTP, phylib genphy/c37/LRE helpers, Linux GPIO/IRQ wake APIs, OF properties such as `brr-mode` and `enet-phy-lane-swap`, ethtool stats/WoL/LED interfaces, and Broadcom PHY IDs from `brcmphy.h`. It registers a large `phy_driver` array through `module_phy_driver()`.

## Risks And Edge Cases
Many branches are model-specific and register values are undocumented or errata-driven. SFP modules are deliberately excluded from LED reprogramming because LED pins may carry LOS signals. WoL support is suppressed unless an IRQ path exists, allowing MAC drivers to offer fallback wake. `bcm54xx_set_wakeup_irq()` calls IRQ wake helpers when `phy_interrupt_is_valid()` or `wake_irq` exists; platforms without a sideband GPIO but with normal PHY IRQ need valid IRQ wake behavior. Fast Ethernet reset tolerates `-EIO` on one read because of MDC turnaround limits. BroadR-Reach mode alters the meaning of supported, advertising, master/slave, and link partner data and must be kept separated from IEEE mode.

## Test Signals
Useful tests include probing each major model family, RGMII delay modes, CLK125 behavior with `PHY_BRCM_RX_REFCLK_UNUSED`, WoL enable/suspend/resume with main IRQ and wake GPIO, PTP exposure for BCM54210E, stats preservation across suspend, SFP LED non-reprogramming, BroadR-Reach DT mode supported/adverting/status paths, BCM54616S 1000BASE-X status, Fast Ethernet interrupt and suspend behavior, and BCM5221 MDIX manual/auto controls.
