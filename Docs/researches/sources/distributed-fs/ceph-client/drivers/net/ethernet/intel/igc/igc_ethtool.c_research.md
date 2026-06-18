# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/igc/igc_ethtool.c

## Purpose
`igc_ethtool.c` is the IGC driver's ethtool control and reporting surface. It exposes driver information, register and EEPROM access, WOL, message levels, link state, ring sizing, pause parameters, statistics, interrupt coalescing, RSS and n-tuple filtering, channel count, timestamp capabilities, private flags, EEE, MAC Merge/FPE controls, link settings, and self-tests.

## Important APIs, Types, And Functions
The public entry point is `igc_ethtool_set_ops()`, which assigns the static `igc_ethtool_ops`. Important data tables are `igc_gstrings_stats[]`, `igc_gstrings_net_stats[]`, `igc_gstrings_test[]`, and `igc_priv_flags_strings[]`. Major callbacks include `igc_ethtool_get_drvinfo()`, `get_regs()`, `get_wol()`/`set_wol()`, EEPROM get/set, ringparam get/set, pause get/set, strings/stats handlers, coalesce get/set, RXNFC add/delete/query, RSS indirection get/set via `igc_write_rss_indir_tbl()`, channel get/set, timestamp info, private flags, EEE get/set, MAC Merge get/set/stats, link ksettings get/set, and `igc_ethtool_diag_test()`.

## Control Flow
Most callbacks translate ethtool requests into adapter state changes or register reads. Setters validate user input, update cached adapter/hardware fields, then either write hardware directly or reinitialize the interface. Ring changes allocate temporary rings, bring the device down, swap resources, and bring it back up. Link and pause setters serialize with `__IGC_RESETTING`. RXNFC insertion builds an `igc_nfc_rule`, validates masks and duplicates under `nfc_rule_lock`, and delegates hardware programming to main-driver helpers. Offline self-test powers PHY, tests link, closes/resets, runs register and EEPROM tests, resets again, then reopens if needed.

## State And Persistence
The file changes persistent in-memory driver state such as `adapter->wol`, `msg_enable`, `rx_ring_count`, `tx_ring_count`, `fc_autoneg`, `hw->fc.*`, `rx_itr_setting`, `tx_itr_setting`, RSS flags and indirection table, `rss_queues`, private flags, `hw->dev_spec._base.eee_enable`, and FPE configuration. EEPROM writes can persist to flash through `hw->nvm.ops.update()`. WOL state is also pushed to device wakeup settings.

## Dependencies And Integration Points
It depends on Linux ethtool/netdevice APIs, runtime PM, MDIO definitions, `igc_diag.h` self-tests, `igc_tsn.h` TSN/FPE helpers, NVM ops from `igc_i225.c`, register constants from `igc_defines.h`, and main driver helpers such as `igc_up()`, `igc_down()`, `igc_reset()`, `igc_reinit_locked()`, `igc_reinit_queues()`, `igc_add_nfc_rule()`, and `igc_tsn_offload_apply()`.

## Risks
This file is a high-risk user-facing mutation surface. EEPROM writes can partially modify NVM before checksum/flash update failures. Ring, channel, pause, EEE, private flag, and link setters can disrupt traffic through reset/reinit. UDP RSS warns about fragmented packet reordering. NFC rules have strict mask support and duplicate detection requirements. The register dump ABI contains a compatibility workaround where RAL/RAH values are written again after earlier index overlap.

## Test Signals
Useful signals include `ethtool -i`, `-d`, `-S`, `-s`, `-g/-G`, `-a/-A`, `-c/-C`, `-l/-L`, `-x/-X`, `-n/-N`, `--show-eee/--set-eee`, `--show-mm/--set-mm`, WOL suspend/resume tests, EEPROM read/write with checksum validation, offline and online `ethtool -t`, queue reinit under traffic, RSS distribution tests, and TSN/FPE offload validation.
