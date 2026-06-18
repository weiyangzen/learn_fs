<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tenxpress.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tenxpress.c

## Purpose
Implements the SFX7101/TenXpress 10GBASE-T PHY driver for Falcon boards, including MDIO probing, PHY initialization, reset sequencing, loopback, low-power control, link polling, LED control, BIST, and ethtool link settings.

## Important APIs, types, and functions
- Exports `falcon_sfx7101_phy_ops` and `tenxpress_set_id_led`.
- Private state is `struct tenxpress_phy_data`, tracking previous loopback mode, PHY mode, and bad link-partner tries.
- Core operations: `tenxpress_phy_probe`, `tenxpress_phy_init`, `tenxpress_phy_reconfigure`, `tenxpress_phy_poll`, `sfx7101_phy_fini`, `tenxpress_phy_remove`, `sfx7101_run_tests`, `tenxpress_get_link_ksettings`, and `tenxpress_set_link_ksettings`.
- Hardware helpers: `tenxpress_init`, `tenxpress_special_reset`, `sfx7101_check_bad_lp`, `tenxpress_ext_loopback`, and `tenxpress_low_power`.

## Control flow
Probe allocates private state, advertises Clause 45 MDIO support, declares required MMDs, loopback modes, and default 10GBASE-T advertisement. Init delegates board PHY setup, waits for required MMD reset/check unless in special mode, initializes clocks and LEDs, reconfigures flow control/autoneg, waits briefly, and resets XAUI. Reconfigure skips off/special modes, performs a special reset when leaving non-normal modes or changing external loopback, applies low power and transmit-disable state, reconfigures MDIO PHY/autoneg, sets PHYXS loopback, and snapshots state. Poll reads link from PMA/PCS/PHYXS, forces 10G full duplex, reads pause state, and flags bad non-10G link partners through logging and red LED flashing.

## State and persistence behavior
The only persistent driver state is heap-allocated `efx->phy_data` and `efx->link_state`. Hardware state is held in MDIO registers for LEDs, power, autonegotiation, loopback, and reset status. Fini powers down the LNPGA and waits before board power removal.

## Dependencies and integration points
Depends on Linux delay/rtnetlink/seq/slab support and driver MDIO helpers from `mdio_10g.h`, board hooks from `falcon_board(efx)`, XAUI reset/stat control from Falcon NIC code, and ethtool link-ksettings helpers.

## Risks and test signals
Risks include reset sequences glitching XGMAC stats, races in autoneg status sampling, link-partner false positives, and LED override state not being restored after errors. Test signals include PHY alive test, offline BIST after special reset, stable link polling, autoneg advertisement/lpa reporting, loopback self-tests, LED behavior, and bad link-partner logs after `MAX_BAD_LP_TRIES`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/tenxpress.c -->
