# sources/distributed-fs/ceph-client/drivers/net/phy/aquantia/aquantia_main.c

## Purpose
Implements the main Aquantia PHY driver for many AQ/AQR devices. It handles feature discovery, autonegotiation, forced modes, interrupts, link/status decoding, interface and rate-matching discovery, firmware-load probe path, statistics, downshift tunables, suspend/resume, LED and HWMON integration, and in-band host-interface configuration.

## Important APIs, Types, and Functions
The driver table matches AQ1202, AQ2104, AQR105, AQR106, AQR107, AQCS109, AQR405, AQR111/B0, AQR112, AQR412/C, AQR113/C, AQR114C, AQR115/C, and AQR813. Key functions include `aqr107_probe`, `aqr_config_aneg`, `aqr105_config_aneg`, `aqr105_setup_forced`, `aqr_read_status`, `aqr_gen1_read_status`, `aqr_gen2_read_status`, `aqr_gen1_read_rate`, `aqr_translate_interface`, `aqr_wait_reset_complete`, `aqr_build_fingerprint`, `aqr_gen1_config_init`, `aqr_gen2_read_global_syscfg`, `aqr_gen2_fill_interface_modes`, `aqr_gen4_config_init`, `aqr107_get_tunable`, `aqr107_set_tunable`, `aqr107_get_stats`, `aqr107_link_change_notify`, `aqr_gen2_inband_caps`, and `aqr_gen2_config_inband`.

## Control Flow and State
Probe allocates `aqr107_priv`, loads firmware if needed, and registers HWMON. Gen1 config validates the requested host interface, waits for firmware readiness, builds a firmware fingerprint when available, sets default downshift, applies optional MDI pair order, and restores saved LED polarity. Gen2/gen4 config additionally reads per-speed global system configuration and possible interfaces, with gen4 polling global config registers and clearing PMA TX disable. Autoneg writes standard C45 advertisement plus vendor 1000/2500/5000 bits and MDIX mode. Status reads LP 1000Base-T bits, MDIX state, standard C45 status, vendor host-interface type, vendor line speed, and rate-matching mode from cached global config. In-band configuration toggles USXGMII AN or per-speed global config AN bits.

## Dependencies and Integration Points
Depends on phylib C45 helpers, ethtool stats/tunables, LED callbacks from `aquantia_leds.c`, firmware and HWMON helpers, device-tree property `marvell,mdi-cfg-order`, MDIO vendor MMDs, PMA/AN/PHYXS registers, and host MACs consuming `possible_interfaces`, `rate_matching`, and in-band capabilities.

## Risks and Test Signals
Risks include incorrect device-table callback selection across many variants, firmware fingerprint based 10G-QXGMII translation being too narrow, global config reads racing firmware readiness, stale cached rate adaptation after firmware changes, autoneg vendor bits diverging from standard linkmode state, and LED polarity restoration only after driver-managed resets. Test signals include link tests at 10M through 10G, forced AQR105 modes, USXGMII/10G-QXGMII/SGMII/2500BASE-X interface reporting, downshift tunables, interrupts, suspend/resume processor-intensive operation waits, ethtool SGMII stats, HWMON registration, LED callbacks, and in-band enable/disable behavior.
