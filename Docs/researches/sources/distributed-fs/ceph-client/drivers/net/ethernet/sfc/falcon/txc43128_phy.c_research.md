<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/txc43128_phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/txc43128_phy.c

## Purpose
Implements the Falcon driver for the TranSwitch/Mysticom TXC-43128 CX4 retimer PHY, including reset, BIST, default analog tuning, GPIO helpers, power management, loopback reconfiguration, polling, and ethtool operations.

## Important APIs, types, and functions
- Exports `falcon_txc_phy_ops`, `falcon_txc_set_gpio_val`, and `falcon_txc_set_gpio_dir`.
- Private state is `struct txc43128_data`, tracking bug-reset timer, PHY mode, and loopback mode.
- Core PHY operations: `txc43128_phy_probe`, `txc43128_phy_init`, `txc43128_phy_reconfigure`, `txc43128_phy_poll`, `txc43128_phy_fini`, `txc43128_phy_remove`, `txc43128_run_tests`, and `txc43128_get_link_ksettings`.
- Hardware helpers: `txc_reset_phy`, `txc_bist_one`, `txc_bist`, `txc_apply_defaults`, `txc_set_power`, `txc_reset_logic`, and lane power helpers.

## Control flow
Probe allocates private state, declares required MMDs and Clause 45 plus emulated Clause 22 support, and publishes supported loopbacks. Init resets the PMA/PMD MMD, checks required MMDs, runs BIST, and reapplies board and analog defaults. Reconfigure performs a full reset/default/XAUI reset when transmit-disabled mode changes, updates transmit-disable and MDIO PHY configuration, applies low-power lane settings, and runs a limited logic reset only when loopback or mode changes. Poll reads aggregate MDIO link state, sets fixed 10G full-duplex flow-control state, and periodically performs logic reset every five seconds while link remains down outside loopback.

## State and persistence behavior
Driver state lives in `efx->phy_data` and `efx->link_state`; hardware state persists in vendor MDIO registers for amplitude, preemphasis, LEDs, BIST, low power, and GPIO. Removal frees private state; fini disables LASI link events.

## Dependencies and integration points
Uses MDIO helpers, Falcon board initialization, Falcon XAUI reset, Linux delay/slab support, and ethtool link setting helpers. It participates in `selftest.c` through `run_tests` and `test_name`.

## Risks and test signals
Risks include infinite waiting if the BIST STOP bit never clears, repeated reset storms while link is down, incorrect analog defaults after reset, and missing cleanup of LASI/event state. Test signals include BIST lane frame/error counts, link polling transitions, five-second bug workaround resets, GPIO register reads/writes on board users, and offline ethtool test result `bist`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/falcon/txc43128_phy.c -->
