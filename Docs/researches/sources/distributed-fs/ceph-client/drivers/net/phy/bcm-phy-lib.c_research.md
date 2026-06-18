# sources/distributed-fs/ceph-client/drivers/net/phy/bcm-phy-lib.c

## Purpose
Provides shared helper code for Broadcom PHY drivers. It abstracts Broadcom expansion, shadow, misc, and RDB register access; interrupt handling; APD and EEE control; downshift; statistics; AFE calibration; jumbo mode; cable diagnostics; Wake-on-LAN; LED brightness; and BroadR-Reach/LRE advertisement.

## Important APIs, Types, and Functions
Exported accessors include `bcm_phy_write_exp`, `bcm_phy_read_exp`, `bcm_phy_modify_exp`, `bcm54xx_auxctl_read/write`, `bcm_phy_write_misc/read_misc`, `bcm_phy_write_shadow/read_shadow`, and RDB read/write/modify helpers. Functional exports include `bcm_phy_ack_intr`, `bcm_phy_config_intr`, `bcm_phy_handle_interrupt`, `bcm_phy_enable_apd`, `bcm_phy_set_eee`, `bcm_phy_downshift_get/set`, `bcm_phy_get_sset_count`, `bcm_phy_get_strings`, `bcm_phy_get_stats`, `bcm_phy_update_stats_shadow`, `bcm_phy_r_rc_cal_reset`, `bcm_phy_28nm_a0b0_afe_config_init`, `bcm_phy_enable_jumbo`, cable-test helpers, `bcm_phy_set_wol`, `bcm_phy_get_wol`, `bcm_phy_wol_isr`, `bcm_phy_led_brightness_set`, `bcm_setup_lre_master_slave`, `bcm_config_lre_aneg`, and `bcm_config_lre_advert`.

## Control Flow and State
The access helpers select an indirect register window, optionally take the MDIO bus lock, read or write data, and often restore default selection. Interrupt config toggles the global ECR interrupt mask and acknowledges pending ISR. APD and EEE perform read-modify-write on shadow and C45 vendor registers, with EEE advertisement based on supported link modes. Downshift maps ethtool counts to Broadcom wirespeed bits and retry fields. Stats add clear/freeze-style hardware counters into caller-provided shadow storage. Cable tests force autoneg with no capabilities, optionally switch RDB devices to legacy access, start ECD, poll completion, report per-pair result and lengths, then restore RDB access. WOL programs pattern/mask registers and wake IRQ behavior. LRE helpers translate linkmode advertisements and master/slave settings to Broadcom registers.

## Dependencies and Integration Points
Depends on `linux/brcmphy.h` register definitions, phylib MDIO locking and MMD helpers, ethtool tunables/stats/netlink cable test/WOL data, netdevice MAC address helpers, and exported symbols consumed by Broadcom-specific PHY drivers such as Cygnus, Broadcom 54xx, 7xxx, 54140, and related modules.

## Risks and Test Signals
Risks include indirect-access helpers being called under the wrong lock variant, failure to restore RDB access after cable-test errors, APD/EEE policy surprises under forced mode, downshift range arithmetic around `DOWNSHIFT_DEV_DISABLE`, WOL pattern masking mistakes, stat accumulation over saturating counters, and shared magic AFE values impacting unrelated PHY revisions. Test signals include lockdep under nested MDIO operations, interrupt enable/disable and ISR delivery, APD wake, EEE advertisement reads, downshift ethtool tunables, cable-test result/length reporting with and without RDB, WOL magic/unicast/multicast/broadcast wake, LED brightness control, jumbo packet reception, and BroadR-Reach autoneg tests.
