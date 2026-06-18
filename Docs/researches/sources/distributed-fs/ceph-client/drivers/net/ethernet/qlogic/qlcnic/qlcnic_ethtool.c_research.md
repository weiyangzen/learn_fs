# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qlcnic/qlcnic_ethtool.c

## Purpose
This file implements the qlcnic `ethtool_ops` tables for PF/default, SR-IOV VF, and failed-adapter modes. It exposes driver/firmware identity, link settings, registers, EEPROM, ring parameters, channels, pause settings, diagnostics, strings/statistics, LED identification, Wake-on-LAN, interrupt coalescing, message level, and firmware dump/reset controls.

## Important APIs, Types, And Functions
- Statistics definitions: `struct qlcnic_stats`, `qlcnic_gstrings_stats`, queue stat strings, 83xx TX/MAC/RX stat strings, eSwitch stat strings, and diagnostic test strings.
- Capability/length helpers: `qlcnic_dev_statistics_len()`, `qlcnic_get_regs_len()`, `qlcnic_get_eeprom_len()`, and `qlcnic_get_sset_count()`.
- Link and port configuration: `qlcnic_get_link_ksettings()`, `qlcnic_82xx_get_link_ksettings()`, `qlcnic_set_link_ksettings()`, and `qlcnic_set_port_config()`.
- Register/EEPROM/ring/channel/pause paths: `qlcnic_get_regs()`, `qlcnic_get_eeprom()`, `qlcnic_get_ringparam()`, `qlcnic_set_ringparam()`, `qlcnic_get_channels()`, `qlcnic_set_channels()`, `qlcnic_get_pauseparam()`, and `qlcnic_set_pauseparam()`.
- Diagnostics: `qlcnic_reg_test()`, `qlcnic_eeprom_test()`, `qlcnic_irq_test()`, `qlcnic_loopback_test()`, `qlcnic_do_lb_test()`, and `qlcnic_diag_test()`.
- Stats: `qlcnic_get_strings()`, `qlcnic_update_stats()`, `qlcnic_get_ethtool_stats()`, `qlcnic_fill_stats()`, and `qlcnic_fill_tx_queue_stats()`.
- Firmware dump/reset: `qlcnic_enable_fw_dump_state()`, `qlcnic_disable_fw_dump_state()`, `qlcnic_check_fw_dump_state()`, `qlcnic_get_dump_flag()`, `qlcnic_get_dump_data()`, `qlcnic_set_dump_mask()`, and `qlcnic_set_dump()`.
- Exported operation tables: `qlcnic_ethtool_ops`, `qlcnic_sriov_vf_ethtool_ops`, and `qlcnic_ethtool_failed_ops`.

## Control Flow
Ethtool calls enter through one of the exported ops tables. Most operations branch by adapter generation: 83xx-specific helpers handle 83xx register dumps, link settings, pause, interrupt test, loopback, flash test, LED, and statistics, while this file directly implements 82xx/default behavior. Ring-size changes validate descriptor counts, update adapter fields, and call `qlcnic_reset_context()`. Channel changes require MSI-X, validate RX/TX queue counts, update RSS/TSS requested counts, set `QLCNIC_TSS_RSS`, and rebuild rings. Offline diagnostics run register/link checks for all requests and IRQ/loopback/EEPROM checks only for `ETH_TEST_FL_OFFLINE`.

Statistics collection first emits per-TX-ring software counters, then adapter software counters, then generation-specific firmware stats. 83xx stats are filled only when link is up. 82xx MAC stats use mailbox queries, and eSwitch stats are appended when eSwitch is enabled.

Firmware dump controls use ethtool dump flags. Force dump and force reset call `qlcnic_dev_request_reset()`. Enable/disable toggles either the local `fw_dump->enable` flag or, for 84xx, bits in `QLC_83XX_IDC_CTRL` under driver lock. Dump retrieval copies template header as little-endian words, appends captured data, frees the dump buffer, and clears the available flag.

## State And Persistence Behavior
This file reads and mutates adapter software stats, ring counts, RSS/TSS counts, link settings, pause bits in registers, diagnostic/reset bits, LED state, WOL register bits, coalescing settings, message level, and firmware dump state. Some changes persist only in adapter memory until reset/reopen, while others are written to firmware or CRB registers. Dump retrieval is destructive: it frees `fw_dump->data` and clears `fw_dump->clr` after successful extraction.

## Dependencies And Integration Points
It integrates with Linux ethtool, netdev open/stop, PCI identity, qlcnic mailbox/context reset, hardware register macros from `qlcnic_hdr.h`, 83xx-specific ethtool helpers, firmware dump/minidump infrastructure, diagnostics allocation/free, loopback packet TX/RX paths, DCB/eSwitch stats, and qlcnic reset request handling.

## Risks And Edge Cases
- Several ethtool operations can trigger context reset, netdev stop/open, firmware reset, or firmware dump; callers must expect disruptive side effects.
- `qlcnic_get_eeprom()` returns success without data for 83xx, while `qlcnic_eeprom_test()` delegates to 83xx flash test; this asymmetry can surprise consumers.
- Offline diagnostics manipulate `__QLCNIC_RESETTING`, ring counts, diagnostic resources, and loopback mode; unwind paths must restore counts and clear reset state.
- Stats string counts must stay exactly aligned with data fill order; adding/removing stats in one array requires updating count and fill paths together.
- `qlcnic_get_ethtool_stats()` skips 83xx firmware stats when link is down, leaving zeros for those slots.
- Firmware dump mask changes require dump support and enabled state; retrieving a dump clears the stored data, so repeated reads differ.

## Test Signals
Test with `ethtool -i`, `-k/-S/-g/-G/-l/-L/-a/-A`, register dumps, link setting changes, offline and online self-tests, LED identify, coalesce get/set, WOL get/set on supported 82xx hardware, firmware dump enable/disable/force/read, SR-IOV VF ethtool capability restrictions, and failed-adapter ops availability.
