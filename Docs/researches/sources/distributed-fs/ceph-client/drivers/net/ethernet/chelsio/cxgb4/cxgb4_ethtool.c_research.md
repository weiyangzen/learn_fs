# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/cxgb4_ethtool.c

## Purpose

`cxgb4_ethtool.c` implements the ethtool operations for Chelsio `cxgb4` net devices. It exposes driver/firmware information, string sets, port and adapter statistics, register and EEPROM access, link mode and FEC configuration, pause and coalescing settings, ring sizing, RSS indirection and hash fields, n-tuple filter management, firmware/PHY/boot flashing, timestamp information, debug dumps, module EEPROM access, private flags, and offline loopback self-test support.

It is the main bridge between generic Linux ethtool requests and the driver's adapter, port, SGE, firmware, filter, cudbg, and hardware access helpers.

## Important APIs, Types, And Functions

- String and count tables: `stats_strings`, `adapter_stats_strings`, `loopback_stats_strings`, `cxgb4_priv_flags_strings`, `cxgb4_selftest_strings`, and `get_sset_count()`.
- Basic info: `get_drvinfo()`, `get_regs_len()`, `get_regs()`, `get_eeprom_len()`, `get_msglevel()`, `set_msglevel()`.
- Statistics: `collect_sge_port_stats()`, `collect_adapter_stats()`, and `get_stats()`.
- Link and media mapping: `from_fw_port_mod_type()`, `speed_to_fw_caps()`, `fw_caps_to_lmm()`, `lmm_to_fw_caps()`, `get_link_ksettings()`, and `set_link_ksettings()`.
- FEC translation: `fwcap_to_eth_fec()`, `cc_to_eth_fec()`, `eth_to_cc_fec()`, `get_fecparam()`, `set_fecparam()`.
- Pause/ring/coalesce: `get_pauseparam()`, `set_pauseparam()`, `get_sge_param()`, `set_sge_param()`, `set_rx_intr_params()`, `set_adaptive_rx_setting()`, `set_dbqtimer_tick()`, `set_dbqtimer()`, `set_dbqtimer_tickval()`, `set_coalesce()`, `get_coalesce()`.
- EEPROM: `eeprom_rd_phys()`, `eeprom_wr_phys()`, `get_eeprom()`, `set_eeprom()` with `EEPROM_MAGIC`.
- Flashing: `cxgb4_validate_fw_image()`, `cxgb4_validate_phy_image()`, `cxgb4_validate_boot_image()`, `cxgb4_validate_bootcfg_image()`, `cxgb4_ethtool_get_flash_region()`, `cxgb4_ethtool_flash_region()`, `set_flash()`.
- RSS: `get_rss_table_size()`, `get_rss_table()`, `set_rss_table()`, `cxgb4_get_rxfh_fields()`.
- Filters: `cxgb4_init_ethtool_filters()`, `cxgb4_cleanup_ethtool_filters()`, `cxgb4_get_filter_entry()`, `cxgb4_fill_filter_rule()`, `cxgb4_ntuple_get_filter()`, `cxgb4_ntuple_set_filter()`, `cxgb4_ntuple_del_filter()`, `get_rxnfc()`, `set_rxnfc()`.
- Debug dumps: `set_dump()`, `get_dump_flag()`, `get_dump_data()`.
- Module EEPROM: `cxgb4_get_module_info()` and `cxgb4_get_module_eeprom()`.
- Private flags and self-test: `cxgb4_get_priv_flags()`, `cxgb4_set_priv_flags()`, `cxgb4_lb_test()`, `cxgb4_self_test()`.
- `cxgb_ethtool_ops` is the operation table installed by `cxgb4_set_ethtool_ops()`.

## Control Flow

During netdev setup, `cxgb4_set_ethtool_ops(netdev)` installs `cxgb_ethtool_ops`. Ettool callbacks then enter this file with a `struct net_device *`, recover `struct port_info` and `struct adapter`, and delegate to common-code helpers or update driver state.

Information and statistics paths are mostly read-only. `get_drvinfo()` copies driver, bus, firmware, TP, and expansion-ROM versions. `get_stats()` first asks hardware for port stats with baseline offsets, then appends aggregated SGE queue counters, adapter doorbell/write-combine counters, the port id, and loopback stats. `get_regs()` returns a full hardware register dump using the adapter-version tag.

Link configuration paths translate between ethtool link masks and firmware capability bits. `get_link_ksettings()` refreshes port info if the netdev is down, fills supported/advertising/lp masks, speed, duplex, autoneg, MDIO fields, and port type. `set_link_ksettings()` validates full duplex, maps either a forced speed or an advertised mode mask into firmware capabilities, saves the old link config, calls `t4_link_l1cfg()`, and restores old config on firmware failure.

Coalescing combines RX interrupt settings and TX SGE doorbell queue timers. RX holdoff changes are applied to each response queue. TX doorbell timer tick is global to the adapter, so `set_dbqtimer_tickval()` records timer values for all ports, changes the global tick, rereads dependent timer values, and then reapplies closest timer values to all ports.

EEPROM access translates physical offsets to per-PF VPD offsets. Reads allocate an EEPROM-sized buffer and read aligned words. Writes require `EEPROM_MAGIC`, enforce PF partition bounds for non-PF0, perform read-modify-write for unaligned endpoints, disable EEPROM write protection, write words, and re-enable protection on success.

Flashing loads firmware data by name through `request_firmware()`. If the request targets all regions, it repeatedly identifies each image by signature and size, flashes the specific region, advances by the image size, and stops on errors. Explicit region flashing dispatches directly to firmware, PHY, boot, or bootcfg loaders. Firmware flashing requires the cxgb4 driver to be the PCIe firmware master when a master is already valid.

RSS and filter control are stateful. RSS table changes require a supported hash function/key combination and `CXGB4_FULL_INIT_DONE`, update `pi->rss[]`, and push to hardware. Ettool n-tuple filters use an allocated per-port bitmap and location-to-TID array. Insert validates initialization, range, and duplicate location, converts ethtool flow rule into a Chelsio filter specification through `cxgb4_flow_rule_replace()`, records the adjusted TID, and marks the bitmap. Delete validates location, fetches the filter, converts absolute TID to the appropriate namespace, destroys the flow rule, and clears bookkeeping.

Debug dump control stores the requested cudbg flag and computed length in `adapter->eth_dump`; data collection later calls `cxgb4_cudbg_collect()`. Module EEPROM reads use firmware I2C helpers and choose SFF-8079, SFF-8472, SFF-8436, or SFF-8636 metadata based on port/module type and transceiver bytes.

## State And Persistence

Persistent runtime state modified by ethtool includes:

- `adapter->msg_enable` for driver message level.
- Per-port `struct link_config` fields: speed caps, advertised caps, autoneg, requested pause, requested FEC.
- SGE queue sizes before full initialization; ring size changes are rejected after `CXGB4_FULL_INIT_DONE`.
- RX response queue interrupt parameters and adaptive RX flags.
- Adapter global SGE DBQ timer tick and per-Ethernet-TXQ timer indices.
- EEPROM/VPD contents and flash/firmware/PHY/boot images in nonvolatile adapter storage.
- `pi->rss[]` and hardware RSS indirection table.
- `adapter->ethtool_filters`, including per-port bitmaps, location arrays, and in-use counts.
- `adapter->eth_dump` cudbg flag/length/version.
- `adapter->eth_flags` and `pi->eth_flags` private flags.

Some values are hardware-derived snapshots rather than software state, such as register dumps, stats, module EEPROM contents, and firmware versions.

## Dependencies And Integration Points

- Includes Linux firmware and MDIO headers plus `cxgb4.h`, `t4_regs.h`, `t4fw_api.h`, `cxgb4_cudbg.h`, `cxgb4_filter.h`, and `cxgb4_tc_flower.h`.
- Uses Linux ethtool core types and helpers, including link ksettings, RSS parameters, FEC parameters, EEPROM, flash, RX flow rules, timestamp info, and dump APIs.
- Integrates with Chelsio common-code functions for hardware register reads, firmware mailbox operations, link L1 configuration, EEPROM/VPD access, firmware upgrades, I2C reads, RSS writes, SGE timers, cudbg collection, and self-test packet loopback.
- Filter support bridges ethtool n-tuple flow rules into the driver's tc-flower/filter path using `cxgb4_flow_rule_replace()` and `cxgb4_flow_rule_destroy()`.
- Optional TLS-device counters are included in stats when `CONFIG_CHELSIO_TLS_DEVICE` is enabled.

## Risks And Edge Cases

- Flashing and EEPROM writes are high-impact operations. Incorrect firmware region detection, bad image sizes, or power loss can leave adapter firmware/storage inconsistent.
- `cxgb4_validate_fw_image()` reads at a fixed signature offset; callers must ensure firmware data is large enough before validation to avoid short-buffer assumptions.
- `set_eeprom()` disables write protection and only re-enables it on the no-error write path; failures after disabling protection are a sensitive area to audit.
- `set_link_ksettings()` and `set_fecparam()` mutate `link_config` before firmware calls and restore on failure. Any future side effects before restore must preserve rollback semantics.
- Ring size changes are only allowed before full initialization; user expectations may differ if they attempt runtime resizing.
- RSS table changes require the interface to have completed full initialization at least once and reject unsupported key/hash-function changes.
- `get_rxnfc()` assumes `adap->ethtool_filters` is valid for rule-count paths; initialization failure or unsupported filters must be handled by setup.
- Filter bookkeeping must stay synchronized with the underlying filter tables; failures after hardware insertion but before bitmap update, or vice versa, would leak or hide rules.
- Coalescing DBQ tick is adapter-global; changing it for one netdev changes timing scale for all ports.

## Test Signals

Recommended signals include:

- `ethtool -i`, `-S`, `-d`, `-g`, `-c`, `-k`, `--show-fec`, `--show-pause`, and module EEPROM reads on supported hardware.
- Link mode set tests for autoneg on/off, unsupported speeds, full-duplex validation, FEC changes, and firmware rejection rollback.
- Ring parameter tests before and after full initialization to verify `-EBUSY` behavior.
- Coalesce tests covering RX usecs/count, adaptive RX, DBQ timer tick/value changes, and multi-port preservation.
- EEPROM read/write tests with magic validation, unaligned writes, PF partition bounds, and write-protect behavior.
- Flash tests with valid individual images, all-region concatenated images, bad signatures, non-master PF, and firmware-loader failures.
- RSS indirection get/set tests, including unsupported key/hash changes.
- Ettool n-tuple insert/get/delete tests for IPv4/IPv6 TCP/UDP, duplicate locations, out-of-range locations, and cleanup on adapter teardown.
- Cudbg dump set/get/data collection tests for buffer sizing and no-dump `-ENOENT`.
