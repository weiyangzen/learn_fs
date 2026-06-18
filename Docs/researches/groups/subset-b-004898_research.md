# subset-b-004898 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/rf.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/rf.c

## Purpose
Implements the RTL8821AE/RTL8812AE RF6052 radio power and RF-parameter setup path. It programs RF bandwidth bits, builds CCK and OFDM/MCS transmit-power register values from EEPROM/efuse tables and dynamic power tracking, clamps values to chip limits, and invokes the generated RF table loaders selected by hardware type and RF path.

## Important APIs, Types, And Functions
The external entry points are `rtl8821ae_phy_rf6052_set_bandwidth`, `rtl8821ae_phy_rf6052_set_cck_txpower`, `rtl8821ae_phy_rf6052_set_ofdm_txpower`, and `rtl8821ae_phy_rf6052_config`. Internal helpers are `rtl8821ae_phy_get_power_base`, `get_txpower_writeval_by_regulatory`, `_rtl8821ae_write_ofdm_power_reg`, and `_rtl8821ae_phy_rf6052_config_parafile`. The code depends on `struct rtl_priv`, `struct rtl_phy`, `struct rtl_mac`, `struct rtl_efuse`, `struct rtl_hal`, RF path IDs, baseband TX AGC registers, `RF_CHNLBW`, and `RF6052_MAX_TX_PWR`.

## Control Flow
Bandwidth setup switches on `HT_CHANNEL_WIDTH_20`, `HT_CHANNEL_WIDTH_20_40`, and `HT_CHANNEL_WIDTH_80` and writes RF channel-bandwidth bits on paths A and B. CCK power setup builds one packed byte-per-rate AGC word per RF path, using max scan power while scanning unless regulatory mode disables that behavior, adding original offsets in unrestricted mode, clamping every byte, applying `rtl8821ae_dm_txpower_track_adjust`, and writing the A/B CCK AGC registers. OFDM power setup first expands OFDM, HT20, and HT40 base power arrays into packed words, then for six OFDM/MCS register groups computes regulatory-adjusted write values and sends them through `_rtl8821ae_write_ofdm_power_reg`. RF config sets `num_total_rfpath` from `rf_type` and walks each active RF path, selecting RTL8812AE or RTL8821AE table configuration callbacks according to `rtlhal->hw_type`.

## State And Persistence
No durable storage is touched. Runtime state is programmed into RF and BB registers and into `rtlphy->num_total_rfpath`. TX power computation reads persistent calibration/regulatory state from efuse/EEPROM-derived fields such as `eeprom_regulatory`, `mcs_txpwrlevel_origoffset`, per-channel power groups, and dynamic TX high-power level.

## Dependencies And Integration Points
This file is called by the PHY channel/bandwidth/power routines, especially channel switching and RF initialization in `phy.c`. It consumes calibration arrays declared in `table.h` indirectly through the PHY table loaders, uses BB/RF register accessors from the rtlwifi HAL, and integrates with dynamic management through `rtl8821ae_dm_txpower_track_adjust`.

## Risks And Edge Cases
Per-byte arithmetic is packed in 32-bit words, so underflow from dynamic high-power backoff or power-tracking subtraction can wrap if the value is already low. Regulatory mode 3 indexes efuse arrays with `channel - 1`, so callers must pass valid 1-based channels. Path B is programmed in bandwidth and power functions even when `RF_1T1R` later limits `num_total_rfpath`. Invalid bandwidth only logs an error and leaves prior RF state in place. Power limit decisions depend heavily on efuse fields being initialized before calls.

## Test Signals
Useful validation is hardware bring-up on RTL8821AE and RTL8812AE, channel switching across 20/40/80 MHz, scan power behavior, regulatory modes 0 through 3, thermal power tracking, and RF path A/B transmit verification. Kernel logs should show no RF config failure messages, and over-the-air tests should confirm expected CCK/OFDM/MCS output power per channel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/rf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/rf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/rf.h

## Purpose
Declares the RTL8821AE RF6052 interface used by the PHY/HAL code to configure RF paths, set channel bandwidth, and program transmit power for CCK and OFDM/MCS rates.

## Important APIs, Types, And Functions
Defines `RF6052_MAX_TX_PWR` as `0x3F` and declares `rtl8821ae_phy_rf6052_set_bandwidth`, `rtl8821ae_phy_rf6052_set_cck_txpower`, `rtl8821ae_phy_rf6052_set_ofdm_txpower`, and `rtl8821ae_phy_rf6052_config`. All APIs operate on `struct ieee80211_hw *` and use rtlwifi-private state reached through that object.

## Control Flow
This header has no runtime control flow. It is included by RF/PHY implementation files so channel switch and initialization paths can call the RF6052 routines.

## State And Persistence
No state is stored here. The max TX power constant constrains register byte values in `rf.c`.

## Dependencies And Integration Points
Depends on the surrounding rtlwifi include order to provide `struct ieee80211_hw`, `u8`, and `bool`. It is part of the RTL8821AE chip-specific HAL boundary used by `phy.c`, `rf.c`, and driver initialization.

## Risks And Edge Cases
The header lacks direct includes for Linux integer and mac80211 types, so standalone inclusion depends on prior includes. Any signature change must be coordinated with `rtl8821ae/phy.c` and `rtl8821ae/rf.c`.

## Test Signals
Build coverage for the RTL8821AE module is the primary signal. RF bring-up and channel-switch tests indirectly validate that all declared functions match their implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/rf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/sw.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/sw.c

## Purpose
Provides the PCI module glue for RTL8821AE and RTL8812AE. It initializes software defaults, requests firmware, binds the chip-specific HAL operation table to the shared rtlwifi PCI core, exposes module parameters, and registers the PCI driver IDs.

## Important APIs, Types, And Functions
Key functions are `rtl8821ae_init_aspm_vars`, `rtl8821ae_init_sw_vars`, `rtl8821ae_deinit_sw_vars`, and `rtl8821ae_get_btc_status`. The central data objects are `rtl8821ae_hal_ops`, `rtl8821ae_mod_params`, `rtl8821ae_hal_cfg`, `rtl8821ae_pci_ids`, and `rtl8821ae_driver`. The HAL ops table wires callbacks for EEPROM, interrupts, hardware init/disable/suspend/resume, channel and bandwidth changes, TX/RX descriptor handling, security, H2C/C2H firmware commands, LED control, Bluetooth coexistence, and WoWLAN pattern support.

## Control Flow
PCI probe enters the shared `rtl_pci_probe` through `module_pci_driver`; that core uses `rtl8821ae_hal_cfg` and calls `rtl8821ae_init_sw_vars`. Initialization sets Bluetooth coexistence operations, dynamic-management defaults, HT/VHT capability fields, band defaults, receive and interrupt masks, WoWLAN mode flags, IPS/LPS options from module parameters, ASPM settings, and firmware buffers. It then selects firmware names based on `rtlhal->hw_type` and submits asynchronous normal and WoWLAN firmware requests. Deinit frees firmware buffers. Module parameters alter crypto, IPS/LPS, MSI, ASPM, interrupt-clear, watchdog, and debug behavior before probe.

## State And Persistence
State is stored in rtlwifi private structures: `rtlpriv->dm`, `rtlpriv->psc`, `rtlpriv->rtlhal`, `rtlpci`, `mac`, and firmware buffers allocated with `vzalloc`. Firmware loading is asynchronous and completes through callbacks outside this file. Module parameters persist for the module lifetime but not across unload/reload unless supplied again.

## Dependencies And Integration Points
Integrates with mac80211 through shared rtlwifi core ops, the PCI core through `rtl_pci_probe`/`rtl_pci_disconnect`, the power-management core through `SIMPLE_DEV_PM_OPS`, firmware loading through `request_firmware_nowait`, and chip-specific modules such as `hw.c`, `phy.c`, `dm.c`, `fw.c`, `trx.c`, `led.c`, and Bluetooth coexistence.

## Risks And Edge Cases
Firmware buffer cleanup is asymmetric: `rtl8821ae_deinit_sw_vars` only frees `wowlan_firmware` when `USE_SPECIFIC_FW_TO_SUPPORT_WOWLAN == 1`, while allocation always occurs here. The request-firmware error paths free buffers but do not always null both pointers. Because normal and WoWLAN firmware are requested asynchronously, remove paths must wait for completion before freeing. Incorrect `hw_type` detection selects the wrong firmware and RF/PHY tables. The default MSI and ASPM settings can expose platform-specific PCIe issues.

## Test Signals
Build the module with PCI support, verify both PCI IDs `0x8812` and `0x8821` bind, check firmware request success for normal and WoWLAN blobs, exercise suspend/resume, unload during firmware load, MSI on/off, ASPM on/off, IPS/LPS modes, TX/RX traffic, and WoWLAN wake patterns. Logs should show selected firmware names and no firmware allocation or request failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/sw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/table.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/table.c

## Purpose
Stores the generated hardware programming tables for RTL8812AE and RTL8821AE. These arrays provide PHY register initialization, per-rate power group values, RF radio path programming, MAC register setup, AGC tables, and regulatory TX power limit records consumed by `rtl8821ae/phy.c`.

## Important APIs, Types, And Functions
There are no functions. Exported data symbols include `RTL8812AE_PHY_REG_ARRAY`, `RTL8821AE_PHY_REG_ARRAY`, `RTL8812AE_PHY_REG_ARRAY_PG`, `RTL8821AE_PHY_REG_ARRAY_PG`, `RTL8812AE_RADIOA_ARRAY`, `RTL8812AE_RADIOB_ARRAY`, `RTL8821AE_RADIOA_ARRAY`, `RTL8812AE_MAC_REG_ARRAY`, `RTL8821AE_MAC_REG_ARRAY`, `RTL8812AE_AGC_TAB_ARRAY`, `RTL8821AE_AGC_TAB_ARRAY`, `RTL8812AE_TXPWR_LMT`, `RTL8821AE_TXPWR_LMT`, and their `ARRAY_SIZE` length variables.

## Control Flow
The file contributes static initialization data only. At runtime, `phy.c` selects arrays by hardware type and walks their register/value tuples. Several arrays contain conditional marker words such as `0x80000000`, `0x90000000`, `0xA0000000`, and `0xB0000000`; the PHY table parser interprets these as board/interface/platform conditions rather than direct register addresses. TX power limit string arrays are parsed as repeated regulation, band, bandwidth, rate section, RF path count, channel, and limit fields.

## State And Persistence
The arrays are compiled into the module image and are read-only by convention, although the `u32` arrays are not declared `const`. They represent persistent vendor calibration defaults until the module is rebuilt. Applying the tables mutates device registers but this file does not store runtime state.

## Dependencies And Integration Points
Depends on `<linux/kernel.h>` for `ARRAY_SIZE` and on `table.h` for declarations. The main consumer is `rtl8821ae/phy.c`, which loads MAC, BB, AGC, RF, power-group, and TX power limit tables during hardware initialization and regulatory setup. `rf.c` depends on the calibration results produced after these tables are applied.

## Risks And Edge Cases
The data is dense and hardware-specific; a single wrong tuple can break RF bring-up, calibration, receive sensitivity, or regulatory compliance. Length symbols are element counts, not tuple counts, so consumers must step with the correct stride for each table. Because the arrays are mutable globals, accidental writes from parser bugs would corrupt future reinitialization. TX power limit strings are untyped, so parser assumptions about seven-field records and channel names must remain aligned with this file.

## Test Signals
Primary signals are successful hardware initialization on both RTL8812AE and RTL8821AE, PHY/RF table load logs, channel scans on 2.4 GHz and 5 GHz, AGC sensitivity, RF path A/B operation for RTL8812AE, and regulatory TX power limit behavior across FCC/ETSI/MKK/WW. Static checks should verify length symbols match `ARRAY_SIZE` and consumers never step past array bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/table.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/table.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/table.h

## Purpose
Declares all generated RTL8812AE/RTL8821AE hardware table symbols consumed by PHY initialization and regulatory power parsing.

## Important APIs, Types, And Functions
The header declares length/data pairs for PHY register arrays, PHY power-group arrays, RF radio arrays, MAC register arrays, AGC tables, and TX power limit string arrays. It exposes both RTL8812AE and RTL8821AE variants, with RTL8812AE having Radio A and B arrays and RTL8821AE having Radio A data.

## Control Flow
No executable control flow is present. Inclusion allows table consumers to select the correct array and length according to hardware type and configuration.

## State And Persistence
No local state. The declared globals are defined in `table.c` and persist for the lifetime of the loaded module.

## Dependencies And Integration Points
Includes `<linux/types.h>` for `u32`. Integrated directly with `rtl8821ae/phy.c` table parser code and indirectly with RF/power initialization.

## Risks And Edge Cases
The declarations are non-`const` for the register arrays, matching their definitions but weakening compile-time protection. Any mismatch between declaration type and definition, especially for `const char *` TX power limit arrays, would be caught at build time but can break consumers if not updated with parser changes.

## Test Signals
Compile coverage is the direct signal. Runtime PHY table loading for both supported chip IDs validates that every declared symbol resolves and uses the intended length.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/table.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/trx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/trx.c

## Purpose
Implements RTL8821AE PCI TX/RX descriptor handling and PHY-status translation. It converts hardware RX descriptors into `rtl_stats` and `ieee80211_rx_status`, computes RSSI/EVM/CFO metrics, fills TX descriptors from mac80211 TX control state, maps bandwidth/subcarrier settings for 20/40/80 MHz operation, and exposes descriptor get/set helpers to the shared PCI core.

## Important APIs, Types, And Functions
External functions are `rtl8821ae_rx_query_desc`, `rtl8821ae_tx_fill_desc`, `rtl8821ae_tx_fill_cmddesc`, `rtl8821ae_set_desc`, `rtl8821ae_get_desc`, `rtl8821ae_is_tx_desc_closed`, and `rtl8821ae_tx_polling`. Key internal helpers include `_rtl8821ae_map_hwqueue_to_fwqueue`, `odm_cfo`, `_rtl8821ae_evm_dbm_jaguar`, `query_rxphystatus`, `translate_rx_signal_stuff`, `rtl8821ae_insert_emcontent`, `rtl8821ae_get_rxdesc_is_ht`, `rtl8821ae_get_rxdesc_is_vht`, `rtl8821ae_get_rx_vht_nss`, `rtl8821ae_bw_mapping`, and `rtl8821ae_sc_mapping`.

## Control Flow
RX processing starts in `rtl8821ae_rx_query_desc`: descriptor macros extract length, driver-info size, shift, CRC/ICV, rate, aggregation, timestamp, bandwidth, MAC ID, HT/VHT/NSS, report type, wake-match flags, and decryption status. It fills mac80211 status fields and, when PHY status is present, calls `translate_rx_signal_stuff`, which determines BSSID/self/beacon matches and then calls `query_rxphystatus`. CCK packets use AGC report formulas that differ between RTL8812AE and RTL8821AE; OFDM/HT/VHT packets compute per-path RSSI, SNR, CFO, EVM, and signal strength. TX processing starts in `rtl8821ae_tx_fill_desc`: it computes the TCB descriptor, optionally prepends early-mode content, DMA maps the skb, clears the descriptor, writes rates, SGI/preamble, aggregation, RTS/CTS, bandwidth, subcarrier, packet size, AMPDU density, security type, queue selection, fallback limits, rate ID, MAC ID, sequence handling, multicast/broadcast flags, and TX report fields. Command descriptors are a simpler one-segment 1 Mbps beacon-queue path.

## State And Persistence
The file mutates live descriptor rings, DMA mappings, skb data when early mode is enabled, `rtlpriv->stats`, `rtlpriv->dm` counters/CFO state, antenna diversity keep fields, and link statistics. No durable persistence exists. Descriptor OWN bits and DMA addresses persist only until consumed by hardware.

## Dependencies And Integration Points
Integrates with mac80211 frame/status structures, rtlwifi PCI ring management, shared stats helpers (`rtl_query_rxpwrpercentage`, `rtl_signal_scale_mapping`, `rtl_process_phyinfo`, `rtl_evm_db_to_percentage`), dynamic management (`rtl8821ae_dm_set_tx_ant_by_tx_info`), firmware TX reports, LED control via the caller, and register polling through `REG_PCIE_CTRL_REG`. Bit layout accessors and packed descriptor structs come from `trx.h`.

## Risks And Edge Cases
DMA mapping errors cause an early return after possible early-mode `skb_push`, leaving callers to handle an skb that may have been modified. `rtl8821ae_tx_fill_desc` writes DMA addresses through 32-bit descriptor fields, so address width assumptions must match the PCI DMA setup. RX robust-management decryption logic deliberately clears `RX_FLAG_DECRYPTED` for protected management frames. The stats code later smooths `rx_mimo_sig_qual`, while this file fills `rx_mimo_signalquality`, so link-quality smoothing may miss EVM values for this chip unless another compatibility path copies them. RX descriptor parsing assumes enough skb data exists after `rx_drvinfo_size` and `rx_bufshift`. Incorrect primary channel offset state creates wrong 20/40/80 subcarrier descriptor values.

## Test Signals
Exercise RX for CCK, OFDM, HT, and VHT 1SS/2SS rates, including CRC/ICV failures, protected robust management frames, WoWLAN wake reports, TX report 2 packets, and PHY-status-present/absent cases. TX tests should cover AMPDU, multicast/broadcast, hardware and software sequence paths, WEP/TKIP/CCMP keys, RTS/CTS, 20/40/80 MHz bandwidth, early mode, DMA mapping failure injection, and descriptor OWN polling. Traffic tests should validate RSSI, SNR, EVM, CFO, and rate reporting in mac80211.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/trx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/trx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/trx.h

## Purpose
Defines RTL8821AE descriptor sizes, descriptor bitfield accessors, PHY status structures, early-mode setters, packed TX/RX descriptor layouts, and the TX/RX descriptor API used by the chip-specific HAL operations.

## Important APIs, Types, And Functions
Important constants are `TX_DESC_SIZE`, `RX_DESC_SIZE`, `RX_DRV_INFO_SIZE_UNIT`, `TX_DESC_NEXT_DESC_OFFSET`, `USB_HWDESC_HEADER_LEN`, and `CRCLENGTH`. Inline setters and getters cover TX packet size, offset, BMC/HTC/segment/OWN, MAC ID, queue, rate ID, security, aggregation, RDG, fragmentation, sequence, RTS/CTS, bandwidth, SGI, buffer size/address, next descriptor address, RX length/errors/driver info/shift/PHY status/OWN/MAC ID/rate/bandwidth/timestamp/buffer address, TX report 2 masks, and early-mode lengths. Data types include `struct phy_rx_agc_info_t`, `struct phy_status_rpt`, `struct rx_fwinfo_8821ae`, `struct tx_desc_8821ae`, and `struct rx_desc_8821ae`.

## Control Flow
The header itself has inline register/descriptor field manipulation only. Runtime control flow is in `trx.c`, which calls these accessors while parsing RX descriptors and filling TX descriptors.

## State And Persistence
The accessors mutate little-endian descriptor memory supplied by ring or skb code. Packed structures describe hardware-owned memory layouts and do not allocate persistent state.

## Dependencies And Integration Points
Relies on Linux bit helpers such as `le32p_replace_bits`, `le32_get_bits`, `GENMASK`, `BIT`, and endian conversion helpers. It is included by `rtl8821ae/trx.c` and referenced through HAL ops registered in `sw.c`. The descriptor layout must match PCI hardware and firmware TX report expectations.

## Risks And Edge Cases
The packed bitfield structs are documentation-like and compiler-layout-sensitive; the inline little-endian accessors are the safer operational interface. Some names are USB-derived, such as `USB_HWDESC_HEADER_LEN`, even though this is the PCI chip path. Address setters/getters use 32-bit values, so they require compatible DMA constraints. Clearing a descriptor intentionally preserves bytes beyond `TX_DESC_NEXT_DESC_OFFSET` when a larger structure is passed, protecting next-descriptor pointers but requiring callers to understand the boundary.

## Test Signals
Compile tests catch accessor signature issues. Runtime signals include correct descriptor ownership transitions, valid TX DMA addresses, RX rate/bandwidth extraction, TX report 2 parsing, early-mode aggregation behavior, and successful traffic across all queues and bandwidths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8821ae/trx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/stats.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/stats.c

## Purpose
Provides shared rtlwifi receive signal conversion and smoothing. It converts hardware dBm/EVM values to percentages, maps raw signal percentages to UI-oriented strength values, and updates rolling RSSI, PWDB, link-quality, SNR, EVM, CFO, and per-station smoothed power statistics for packets that match the current BSSID.

## Important APIs, Types, And Functions
Exported functions are `rtl_query_rxpwrpercentage`, `rtl_evm_db_to_percentage`, `rtl_signal_scale_mapping`, and `rtl_process_phyinfo`. Internal helpers include `rtl_translate_todbm`, `rtl_process_ui_rssi`, `rtl_update_rxsignalstatistics`, `rtl_process_pwdb`, and `rtl_process_ui_link_quality`. The code operates on `struct rtl_stats`, `struct rtl_priv`, `struct rtl_phy`, `struct rtl_sta_info`, and the rolling-window state under `rtlpriv->stats`.

## Control Flow
Chip-specific RX code fills a `rtl_stats` instance and calls `rtl_process_phyinfo`. Non-BSSID packets are ignored. Matching packets update UI RSSI only for packets to self or beacons, then update smoothed PWDB either per station in AP/adhoc modes or globally in `rtlpriv->dm.undec_sm_pwdb`, and finally update UI link quality if the packet carries nonzero signal quality. RSSI uses a fixed-size sliding window; per-path RSSI, SNR, EVM, and CFO use exponential smoothing with `RX_SMOOTH_FACTOR`. Signal conversion helpers are exported for descriptor parsers.

## State And Persistence
All state is in memory: rolling-window arrays and indexes under `rtlpriv->stats`, smoothed per-station `drv_priv->rssi_stat.undec_sm_pwdb`, global `rtlpriv->dm.undec_sm_pwdb`, and latest receive signal power. No filesystem persistence exists.

## Dependencies And Integration Points
Integrated with every rtlwifi chip-specific RX descriptor parser. It depends on mac80211 station lookup under RCU, `rtl_find_sta`, the shared `rtl_stats` layout in `wifi.h`, and RF path counts from `rtlpriv->phy`. Exported symbols allow chip modules to link against these helpers.

## Risks And Edge Cases
`rtl_process_ui_link_quality` reads `rx_mimo_sig_qual`, while several newer chip paths, including RTL8821AE, fill `rx_mimo_signalquality`; that mismatch can leave per-stream EVM smoothing stale. `rtl_process_ui_rssi` ignores non-self non-beacon packets, so some traffic patterns update PWDB but not UI RSSI. The initial `recv_signal_power == 0` sentinel can be ambiguous if a legitimate computed value is 0 dBm. Per-station smoothing is skipped in station mode because the code only calls `rtl_find_sta` when the opmode is not station.

## Test Signals
RX tests should cover BSSID match/mismatch, to-self data, beacons, AP/adhoc station lookup, CCK versus OFDM/HT/VHT stats, sliding-window wraparound, rising and falling RSSI smoothing, and per-stream EVM updates. Cross-chip tests should verify whether `rx_mimo_sig_qual` or `rx_mimo_signalquality` is populated before link-quality smoothing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/stats.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/stats.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/stats.h

## Purpose
Declares shared rtlwifi receive-statistics helper APIs and smoothing-window constants used by chip-specific RX descriptor code.

## Important APIs, Types, And Functions
Defines `PHY_RSSI_SLID_WIN_MAX` as 100, `PHY_LINKQUALITY_SLID_WIN_MAX` as 20, `PHY_BEACON_RSSI_SLID_WIN_MAX` as 10, and `RX_SMOOTH_FACTOR` as 20. Declares `rtl_query_rxpwrpercentage`, `rtl_evm_db_to_percentage`, `rtl_signal_scale_mapping`, and `rtl_process_phyinfo`.

## Control Flow
No runtime control flow exists in the header. It enables descriptor parsers to call shared signal conversion and smoothing routines.

## State And Persistence
No state is stored here. The constants size and tune in-memory rolling windows maintained by `stats.c`.

## Dependencies And Integration Points
Depends on surrounding includes for `u8`, `s8`, `long`, and `struct ieee80211_hw`. It is included by rtlwifi chip RX paths and by `stats.c`.

## Risks And Edge Cases
Changing constants alters smoothing behavior across all rtlwifi chips. Like several rtlwifi headers, it does not include all type providers itself, so it assumes inclusion after `wifi.h` or equivalent kernel headers.

## Test Signals
Build all rtlwifi chip modules and run RX signal reporting tests. Any change to constants should be checked against UI RSSI/link-quality stability and roaming decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/stats.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/usb.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/usb.c

## Purpose
Implements the shared rtlwifi USB transport layer. It provides synchronous vendor control-message register I/O, discovers endpoints, initializes USB TX/RX queues and URBs, moves received bulk data into mac80211, submits transmitted skbs as bulk OUT URBs, and provides generic probe/disconnect glue for USB rtlwifi chip drivers.

## Important APIs, Types, And Functions
Exported entry points are `rtl_usb_probe` and `rtl_usb_disconnect`. Core helpers include `_usbctrl_vendorreq_sync`, `_usb_read_sync`, `_usb_write_sync`, `_usb_write_chunk_sync`, `_rtl_usb_io_handler_init`, `_rtl_usb_init`, `rtl_usb_init_sw`, `_rtl_prep_rx_urb`, `_rtl_rx_completed`, `_rtl_rx_work`, `_rtl_usb_rx_process_noagg`, `_rtl_usb_receive`, `rtl_usb_start`, `rtl_usb_stop`, `_rtl_usb_cleanup_rx`, `_rtl_usb_cleanup_tx`, `_rtl_usb_tx_preprocess`, `_rtl_usb_transmit`, `_rtl_tx_complete`, `_usb_tx_post`, and `rtl_fill_h2c_cmd_work_callback`.

## Control Flow
Probe allocates `ieee80211_hw` with USB private space, allocates a small synchronized control-transfer data ring, initializes locks/work items/completions, binds `rtl_hal_cfg` and `rtl_usb_ops`, installs USB register I/O callbacks, reads chip/eeprom data, discovers endpoints, initializes TX/RX transport state, initializes mac80211 core and chip software variables, then registers the hardware. Adapter start calls chip `hw_init`, initializes RX config, marks USB started, marks HAL started, and submits RX URBs. RX completion validates length and queue depth, allocates an skb with radiotap/alignment reserve, copies the coherent buffer, queues it, schedules a tasklet, and resubmits the URB. The tasklet parses descriptors through chip `query_rx_desc`, updates stats/LED/beacon state, and passes valid frames to mac80211. TX maps mac80211 queues to hardware queues, applies power-save/action/stat preprocessing, asks the chip to fill a TX descriptor, builds a bulk URB, and reports completion status back to mac80211. Disconnect waits for firmware loading, unregisters mac80211 if needed, stops/deinitializes transport/core/chip state, releases I/O, and frees `ieee80211_hw`.

## State And Persistence
State lives in `struct rtl_usb`, `struct rtl_usb_priv`, `rtlpriv->usb_data`, USB anchors for submitted and cleanup URBs, TX skb queues, RX skb queue, tasklets, work items, endpoint maps, interrupt masks, and USB/HAL start-stop flags. No durable persistence exists.

## Dependencies And Integration Points
Depends on the Linux USB core, mac80211, skbuff APIs, rtlwifi core/base/power-save code, chip-specific `rtl_hal_cfg`, chip `usb_interface_cfg`, firmware common address ranges, and shared LED/action/beacon/stat helpers. USB chip drivers such as rtl8192cu and rtl8192du call `rtl_usb_probe` and `rtl_usb_disconnect`.

## Risks And Edge Cases
Vendor register I/O uses a shared rotating `usb_data` buffer protected only for allocation of the slot; the USB control transfer then occurs after unlocking, so concurrent accesses rely on enough ring slots and no immediate reuse. Firmware download writes are not retried in the firmware address range. RX aggregation path logs unsupported after processing, and `_rtl_usb_rx_process_agg` does not itself submit to mac80211. `_rtl_tx_complete` returns without freeing/reporting the skb if USB is stopped, relying on broader teardown to own cleanup. Cleanup reports queued TX skbs as ACKed even though they were never transmitted. Endpoint discovery assumes the first bulk-IN endpoint is the main RX endpoint.

## Test Signals
USB probe/disconnect loops, firmware load/unload races, suspend-like stop/start, high-speed and full-speed devices, endpoint map validation, control transfer timeout injection, RX queue saturation, short RX packet handling, TX URB submission failures, unplug during active traffic, and mac80211 registration failures are key tests. Runtime signals include no leaked URBs/skbs, stable register I/O, correct RX status delivery, and TX status completion under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/usb.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/usb.h

## Purpose
Defines the shared rtlwifi USB transport interface, endpoint/queue constants, USB private state structures, skb transport metadata helper, start/stop state macros, and exported probe/disconnect declarations.

## Important APIs, Types, And Functions
Important constants are `RTL_RX_DESC_SIZE`, `USB_HIGH_SPEED_BULK_SIZE`, `USB_FULL_SPEED_BULK_SIZE`, `RTL_USB_MAX_TXQ_NUM`, `RTL_USB_MAX_EP_NUM`, `RTL_USB_MAX_BULKOUT_NUM`, and `RTL_USB_MAX_TX_URBS_NUM`. `RTL_USB_DEVICE` helps chip drivers build USB ID table entries that point to an `rtl_hal_cfg`. `enum rtl_txq` defines BK/BE/VI/VO/BCN/MGT/HI queues. `struct rtl_ep_map`, `struct rtl_usb`, and `struct rtl_usb_priv` hold endpoint maps, anchors, queues, tasklet, callbacks, and Bluetooth coexistence state. `_rtl_install_trx_info` stores the `rtl_usb` pointer and endpoint number in skb driver data for completion callbacks.

## Control Flow
The header has inline metadata installation and macros to set/test USB transport state. Runtime control flow is implemented in `usb.c` and chip USB drivers.

## State And Persistence
`struct rtl_usb` captures all live transport state: USB device/interface, start/stop state, beacon and interrupt masks, queue-to-endpoint mapping, TX/RX anchors, skb queues, tasklet, and chip-specific callback hooks. This is in-memory state attached to `ieee80211_hw` and released at disconnect.

## Dependencies And Integration Points
Depends on Linux skbuff and USB/mac80211 types supplied by surrounding includes. Integrated with chip USB modules via `RTL_USB_DEVICE`, with shared rtlwifi core through `rtl_usbpriv`/`rtl_usbdev`, and with `usb.c` through `rtl_usb_probe` and `rtl_usb_disconnect`.

## Risks And Edge Cases
The queue enum must stay consistent with `skb_get_queue_mapping`, as noted in the file, or TX traffic will go to the wrong endpoint. `rate_driver_data` slots are reused for transport metadata, so chip TX/report code must not assume those slots are free while USB owns them. Maximum endpoint constants constrain devices with unusual endpoint layouts.

## Test Signals
Build USB rtlwifi chip drivers, verify USB ID table matching through `RTL_USB_DEVICE`, exercise queue mapping for BK/BE/VI/VO/beacon/management/high queues, and test unplug/stop paths to ensure state macros and anchors coordinate with `usb.c` cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/usb.h -->
