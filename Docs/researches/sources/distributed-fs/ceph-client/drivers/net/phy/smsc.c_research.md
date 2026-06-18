# sources/distributed-fs/ceph-client/drivers/net/phy/smsc.c

## Purpose
`smsc.c` supports SMSC/Microchip LAN83C185, LAN8187, LAN8700, LAN911x internal, LAN8710/LAN8720, LAN8740, and LAN8742 PHYs. It layers vendor interrupt handling, Energy Detect Power-Down tuning, MDIX policy, optional reference clock enablement, statistics, and LAN874x Wake-on-LAN filters on top of generic phylib behavior.

## Important APIs, Types, And Functions
`struct smsc_hw_stat` describes ethtool statistics, and `struct smsc_phy_priv` stores EDPD policy and whether the single WoL pattern is currently ARP or multicast. Exported helpers include `smsc_phy_config_intr()`, `smsc_phy_handle_interrupt()`, `smsc_phy_config_init()`, `lan87xx_read_status()`, `smsc_phy_get_tunable()`, `smsc_phy_set_tunable()`, and `smsc_phy_probe()`. LAN-specific helpers include `lan87xx_config_aneg()`, `lan95xx_config_aneg_ext()`, `lan87xx_phy_config_init()`, `lan874x_phy_config_init()`, `lan874x_get_wol()`, `lan874x_set_wol()`, and pattern/CRC helpers.

## Control Flow
Probe allocates private state, defaults EDPD to enabled with a 640 ms wait, honors `smsc,disable-energy-detect`, stores `phydev->priv`, and optionally enables a 50 MHz reference clock. Config init disables EDPD automatically when IRQ mode is used unless the user explicitly set a tunable. LAN87xx init forces a known Auto-MDIX default. Autoneg config selects fixed MDI for forced links unless users requested another MDIX mode, writes `SPECIAL_CTRL_STS`, then delegates to generic autoneg.

Status reads call `genphy_read_status()` and, when link is down with EDPD enabled in polling mode, temporarily disable EDPD, poll for energy, then re-enable EDPD. Interrupt config acks by reading `MII_LAN83C185_ISF`, writes the mask register, and triggers phylib on relevant interrupt status bits. LAN874x WoL programs unicast/broadcast/magic bits, one ARP or multicast filter pattern, optional destination MAC registers, and reads back enabled modes.

## State And Persistence
Private EDPD and WoL pattern state persists in `phydev->priv`; hardware state persists in vendor MII and PCS MMD registers. Statistics are read directly from the PHY symbol error counter. The driver does not persist configuration outside runtime PHY registers.

## Dependencies And Integration Points
The file depends on phylib, MII helpers, ethtool tunables/WoL/statistics, optional clocks, OF/device properties, CRC16, Ethernet address helpers, and `<linux/smscphy.h>` register definitions. It registers a `struct phy_driver` table and exports common SMSC helpers for other modules.

## Risks And Edge Cases
EDPD is unreliable with interrupts, and the driver only allows polling-mode wake probing for timed EDPD values. `lan87xx_config_aneg()` writes `SPECIAL_CTRL_STS` without checking the write return before continuing. LAN874x supports only one pattern filter, so ARP and multicast wake are mutually exclusive. WoL programming assumes an attached net device for MAC address access when magic or unicast wake is requested. Clock rate assumptions may expose board-DT issues.

## Test Signals
Cover each PHY ID match, optional clock probe-defer/failure, EDPD tunable values including invalid ranges and IRQ rejection, polling-mode cable insertion while in EDPD, forced 10/100 MDIX behavior, interrupt mask/status handling, symbol-error ethtool stats, LAN874x magic/unicast/broadcast/ARP/multicast WoL programming, and suspend/resume with WoL-enabled devices.
