# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/mdio_10g.c

## Purpose
`mdio_10g.c` implements shared helpers for IEEE 802.3 Clause 45 10G PHY management. The code is not specific to one PHY model; it handles MMD reset, presence checks, link checks under loopback policy, low-power and TX-disable state, autonegotiation reconfiguration, ethtool link setting changes, pause resolution, and PHY liveness tests.

## Important APIs, Types, And Functions
`ef4_mdio_id_oui()` reorders PHY ID bits into conventional OUI form. Reset and discovery helpers include `ef4_mdio_reset_mmd()`, `ef4_mdio_wait_reset_mmds()`, and `ef4_mdio_check_mmds()`, with the internal `ef4_mdio_check_mmd()` validating `MDIO_STAT2_DEVPRST`. Link and mode helpers include `ef4_mdio_links_ok()`, `ef4_mdio_transmit_disable()`, `ef4_mdio_phy_reconfigure()`, and `ef4_mdio_set_mmds_lpower()`. User-facing configuration helpers include `ef4_mdio_set_link_ksettings()`, `ef4_mdio_an_reconfigure()`, `ef4_mdio_get_pause()`, and `ef4_mdio_test_alive()`.

## Control Flow
Reset routines write reset bits, sleep in bounded loops, and poll control/status registers until reset clears or times out. MMD checks read device-present bitmaps from `DEVS1`/`DEVS2`, compare against the expected mask, then validate each required MMD. Link checks first apply driver loopback and PHY-mode exclusions, then defer to `mdio45_links_ok()`. Link settings are accepted only when they differ from current settings, both old and new ports are twisted pair, autonegotiation remains enabled, and requested advertising is supported. Autonegotiation writes base-page pause capability, asks the PHY operation to set next-page advertising, then enables/restarts AN.

## State And Persistence
The code persists configuration in PHY MDIO registers: reset, low-power, transmit disable, loopback, AN advertisement, and AN restart bits. It reads and updates driver state such as `efx->link_advertising`, `wanted_fc`, `phy_mode`, `loopback_mode`, and `efx->mdio.mmds`. `ef4_mdio_test_alive()` serializes ID probing and MMD checks with `efx->mac_lock`.

## Dependencies And Integration Points
It depends on Linux MDIO, ethtool link mode conversion, MII flow-control resolution, sleep/delay APIs, driver logging, `net_driver.h`, `mdio_10g.h`, and loopback/workaround definitions. PHY-specific operation tables call these helpers for common behavior, while ethtool settings, link polling, and monitor paths use their results.

## Risks
Timeout constants are intentionally conservative but still represent hardware assumptions. Passing reset spins and sleep time in the wrong units is guarded only by a paranoid debug check. Some paths assume at least one MMD bit is present for `__ffs()`. `ef4_mdio_set_link_ksettings()` uses legacy advertising conversion, so unsupported combinations must be rejected carefully. MDIO read errors must stay negative; treating them as register values would corrupt state decisions.

## Test Signals
Test signals include PHY probe success, MMD presence errors on missing devices, reset timeout logs, ethtool speed/duplex/autoneg rejection and acceptance, pause resolution from AN partner state, loopback-specific link status, low-power/TX-disable behavior, and `test_alive` reporting invalid all-zero/all-ones PHY IDs.
