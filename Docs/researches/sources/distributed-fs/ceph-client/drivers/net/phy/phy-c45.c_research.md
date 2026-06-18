# sources/distributed-fs/ceph-client/drivers/net/phy/phy-c45.c

## Purpose
This file implements generic Linux phylib helpers for IEEE Clause 45 PHYs. It covers PMA sleep/resume, forced PMA speed setup, BASE-T1 master/slave and autoneg advertisement, autoneg restart/status, link and partner advertisement reads, PMA ability discovery, EEE support, loopback, fast retrain, Open Alliance TC14 PLCA, Open Alliance cable test helpers, and OATC14 SQI/SQI+ reads.

## Important APIs, Types, and Functions
The file exports many helpers used by PHY drivers: `genphy_c45_pma_resume()`, `genphy_c45_pma_suspend()`, `genphy_c45_pma_setup_forced()`, `genphy_c45_an_config_aneg()`, `genphy_c45_an_disable_aneg()`, `genphy_c45_restart_aneg()`, `genphy_c45_check_and_restart_aneg()`, `genphy_c45_aneg_done()`, `genphy_c45_read_link()`, `genphy_c45_read_lpa()`, `genphy_c45_read_pma()`, `genphy_c45_read_mdix()`, `genphy_c45_read_eee_abilities()`, `genphy_c45_an_config_eee_aneg()`, `genphy_c45_pma_read_abilities()`, `genphy_c45_read_status()`, `genphy_c45_config_aneg()`, `genphy_c45_loopback()`, `genphy_c45_fast_retrain()`, PLCA get/set/status helpers, EEE ethtool helpers, OATC14 cable-test start/status helpers, and OATC14 SQI helpers.

Internal helpers include `genphy_c45_baset1_able()`, which caches `phydev->pma_extable`, `genphy_c45_pma_can_sleep()`, BASE-T1 LPA/status helpers, EEE capability readers, `oatc14_cable_test_get_result_code()`, and `oatc14_update_sqi_capability()`.

## Control Flow
Ability discovery reads PMA/AN/PCS MMD registers and populates `phydev->supported` and `phydev->supported_eee`. Autoneg configuration first constrains advertising to supported modes, configures EEE advertising, then selects BASE-T1 or conventional AN registers. Forced mode writes PMA CTRL1/CTRL2 speed/type and BASE-T1 master/slave/strap controls when applicable, then disables AN.

Status reading checks link across relevant MMDs while preserving latched-low semantics, resets speed/duplex/pause fields, reads LPA and BASE-T1 master/slave data for autoneg links, resolves link mode, or reads PMA speed for forced links. EEE ethtool set/get reads and writes EEE advertisement registers and restarts AN when changes require it.

PLCA helpers validate the OATC14 ID, read or modify control/timer/burst registers, disable before partial reconfiguration when requested, and enable at the end. OATC14 cable tests check HDD capability, set control/start bits, poll valid results, report ethtool pair-A results, and clear control. OATC14 SQI caches capability in `phydev->oatc14_sqi_capability` on first use and then reads SQI+ or SQI registers.

## State and Persistence
Most state is in `phydev`: supported link modes, EEE modes, link, speed, duplex, pause, partner advertising, master/slave fields, cached `pma_extable`, and cached OATC14 SQI capability. Hardware MMD registers persist forced speeds, AN advertisement, EEE advertisement, PLCA config, loopback, fast retrain, cable test, and low-power state.

## Dependencies and Integration Points
The file depends on MDIO/MII definitions, phylib internals, ethtool netlink constants, `mdio-open-alliance.h`, and exported symbol users throughout `drivers/net/phy`. Many device drivers in this subset call these helpers directly, including GPY, NCN26000, and NXP C45.

## Risks
Generic helpers must tolerate devices with incomplete or buggy optional registers. The file intentionally ignores some EEE capability read failures, which is pragmatic but can hide hardware issues. BASE-T1 and conventional Clause 45 paths share APIs but use different registers, so incorrect `pma_extable` detection can misconfigure devices. Latched-low link handling must remain consistent with polling vs IRQ behavior. PLCA partial updates must preserve unmodified fields correctly.

## Test Signals
Test with conventional Clause 45 copper, BASE-T1, and 10BASE-T1S/OATC14 PHYs. Cover forced speeds, autoneg restart/change detection, master/slave modes, LPA decoding, EEE enable/disable and advertised-mode validation, PMA suspend/resume unsupported cases, loopback, fast retrain, PLCA get/set/status, OATC14 cable tests, SQI/SQI+ capability caching, and exported-symbol build coverage.
