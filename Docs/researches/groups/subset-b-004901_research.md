# Research Report: subset-b-004901

Grouped research for the Realtek `rtw88` core, PCI, PHY, and power-save files under `sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/main.c

## Purpose
`main.c` is the shared core for the Realtek `rtw88` wireless driver. It owns module parameters, supported channel/rate metadata, mac80211 registration, core lifecycle, firmware loading and recovery, station/rate setup, scan transitions, per-port register programming, watchdog work, and glue into PHY, firmware, coexistence, security, regulatory, debugfs, LED, SAR, and transport-specific HCI operations. It is transport-neutral: PCI/USB/SDIO call into this file through `rtw_core_init()`, `rtw_chip_info_setup()`, `rtw_register_hw()`, `rtw_core_start()`, and `rtw_core_stop()`.

## Important APIs, Types, and Functions
- Module parameters: `disable_lps_deep`, `support_bf`, and `debug_mask`; global `rtw_edcca_enabled` is shared with PHY debug behavior.
- Hardware capability metadata: `rtw_channeltable_2g`, `rtw_channeltable_5g`, `rtw_ratetable`, `rtw_band_2ghz`, `rtw_band_5ghz`, interface limits/combinations, and HT/VHT capability initializers.
- Lifecycle APIs: `rtw_core_init()`, `rtw_core_deinit()`, `rtw_chip_info_setup()`, `rtw_power_on()`, `rtw_power_off()`, `rtw_core_start()`, `rtw_core_stop()`, `rtw_register_hw()`, and `rtw_unregister_hw()`.
- Station and rate-control APIs: `rtw_sta_add()`, `rtw_sta_remove()`, `rtw_update_sta_info()`, `rtw_desc_to_bitrate()`, `rtw_set_ampdu_factor()`, and BA work scheduling.
- Channel and scan APIs: `rtw_get_channel_params()`, `rtw_update_channel()`, `rtw_set_channel()`, `rtw_core_scan_start()`, `rtw_core_scan_complete()`, and `rtw_core_fw_scan_notify()`.
- Firmware crash handling: `rtw_fw_recovery()`, `rtw_dump_fw()`, `rtw_dump_reg()`, coredump helpers, and reset iterators for keys, stations, and vifs.
- Port/AP helpers: `rtw_vif_port_config()`, `rtw_core_port_switch()`, `rtw_core_check_sta_active()`, and `rtw_core_enable_beacon()`.

## Control Flow
Probe code in a transport module first allocates `ieee80211_hw` and calls `rtw_core_init()`. Core init constructs lists, work items, queues, timers, mutexes, completions, default receive filter state, statistics EWMAs, and begins asynchronous firmware requests. The transport then sets up resources and calls `rtw_chip_info_setup()`, which reads chip parameters, briefly powers MAC/HCI to download firmware for efuse/hardware feature extraction, parses efuse, validates RFE support, normalizes efuse defaults, initializes board power tables, and loads regulatory power data. `rtw_register_hw()` advertises mac80211 capabilities and bands, initializes regulatory/LED/debugfs integration, and registers with mac80211.

Runtime start enters through `rtw_core_start()`: it powers on through the chip operation, enables the security engine, chooses firmware-supported LPS deep modes, writes RCR, schedules the watchdog, and marks `RTW_FLAG_RUNNING`. `rtw_power_on()` is the detailed bring-up: HCI setup, MAC power-on, firmware wait/download, MAC init/postinit, PHY parameter setup, HCI start, H2C general/PHYDM messages, and Bluetooth coexistence power-on configuration. Stop clears running/firmware flags, drops the mutex while synchronously canceling queued work that may need it, reacquires the mutex, and invokes chip power-off.

The watchdog runs every two seconds while running. It updates traffic counters/EWMAs, toggles busy-traffic state, skips dynamic PHY while scanning, forces LPS exit before PHY/coex work, runs coexistence status queries, executes `rtw_phy_dynamic_mechanism()`, adjusts HCI RX aggregation, iterates vifs for CSI rate and per-vif stats reset, checks software beacon loss, and may enter LPS when PS is enabled and traffic/beacon/AP conditions allow it.

Firmware recovery prepares a coredump buffer, dumps firmware crash TLV and chip-specific segments, submits a device coredump, clears MCU test state, clears security CAM entries, removes station/vif driver state, enters IPS, then asks mac80211 to restart hardware.

## State and Persistence Behavior
Most persistent state is in `struct rtw_dev`: firmware state, efuse, HAL, security CAM, traffic stats, regulatory state, coexistence state, dynamic mechanism state, work items, TX queues, LPS config, flags, hardware ports, MAC IDs, WoW state, and LED/debugfs state. This file mutates those fields under `rtwdev->mutex` for mac80211-visible lifecycle and power paths. Firmware objects persist from async request until `rtw_core_deinit()` releases them. Efuse-derived MAC address, RF paths, NSS, RFE, board options, power tables, and regulatory defaults persist for the device lifetime. Watchdog counters and stats are reset each interval. No filesystem persistence is performed; firmware coredumps are handed to the kernel devcoredump framework.

## Dependencies and Integration Points
`main.c` depends on mac80211/cfg80211, firmware loading, devcoredump, kernel workqueues/timers/completions, and many local modules: `fw`, `ps`, `sec`, `mac`, `coex`, `phy`, `reg`, `efuse`, `tx`, `debug`, `bf`, `sar`, `sdio`, and `led`. It calls transport hooks through `rtw_hci_*` and chip-specific hooks through `rtw_chip_ops`. mac80211 integration is via `rtw_ops`, `ieee80211_register_hw()`, vif/sta iterators, TX status, scan/offload features, TDLS flags, WoWLAN caps, and SAR caps.

## Risks
- Lifecycle ordering is fragile: firmware completion, temporary efuse power-on, HCI setup/start/stop, and MAC power transitions must remain synchronized with transport resources.
- `rtw_core_stop()` deliberately unlocks `rtwdev->mutex` around cancellation; changes in called work items can introduce deadlocks or races.
- Firmware recovery removes software state and enters IPS before `ieee80211_restart_hw()`, so missing cleanup can leak MAC IDs, security entries, TXQs, or vif port state.
- Channel/SAR/power-state updates are tightly coupled; invalid channel definitions can trigger warnings or wrong power table selection.
- `rtw_update_sta_info()` contains dense rate-mask logic across CCK/OFDM/HT/VHT, RSSI floors, configured bitrate masks, NSS, STBC, LDPC, and SGI. Regressions show up as poor connectivity rather than immediate crashes.
- The watchdog forces LPS leave before PHY/coex work; mistakes in scan or PS flags can cause power churn, firmware ack timeouts, or missed beacon-loss handling.

## Test Signals
- Probe/register/unregister on supported PCI/USB/SDIO devices without firmware-load leaks or warning splats.
- Association and disassociation with station/AP/TDLS paths, checking MAC ID allocation/release and firmware media status.
- 2.4 GHz and 5 GHz channel changes, including 40/80 MHz primary-center computations and SAR band assignment.
- Firmware crash injection or forced recovery path validating devcoredump creation and mac80211 restart.
- Scan start/complete with random MAC restoration, DIG disable/reset, IPS leave/re-enter, and firmware scan-density completion.
- Traffic watchdog behavior under idle, busy, beacon-loss, and PS-enabled station scenarios.
- Rate-control behavior with HT/VHT, bitrate masks, one-stream mode, STBC/LDPC/SGI capabilities, and RSSI changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/main.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/main.h

## Purpose
`main.h` is the central contract for the `rtw88` driver. It defines shared constants, enums, data structures, chip-operation callbacks, per-device state, per-vif/per-station private state, firmware state, coexistence state, PHY/dynamic-mechanism state, efuse/HAL state, power-save state, and core API prototypes. Nearly every implementation file in this subset includes it, and HCI-private data is embedded at the end of `struct rtw_dev`.

## Important APIs, Types, and Functions
- Core capability enums: HCI type, band, bandwidth, secondary-channel offset, network type, RF type/path, BB path, rate section, wireless set, chip type, TX/RX queue type, firmware type, descriptor rates, regulatory domain, flags, ports, WoW flags, and capability quirks.
- Power and packet descriptors: `struct rtw_tx_pkt_info`, `struct rtw_rx_pkt_stat`, `struct rtw_lps_conf`, `struct rtw_sec_desc`, `struct rtw_tx_report`, `struct rtw_sta_info`, and `struct rtw_vif`.
- Hardware abstraction: `struct rtw_chip_ops` and `struct rtw_chip_info` describe chip-specific hooks, table pointers, firmware names, FIFO layout, RF/BB parameters, power sequences, coexistence parameters, scan/WoW limits, and feature support.
- PHY/power state: `struct rtw_dm_info`, `struct rtw_efuse`, `struct rtw_hal`, `struct rtw_sar`, power-by-rate and power-limit arrays, DPK/IQK/GAPK/CFO state, and path-diversity state.
- Device root: `struct rtw_dev`, containing mac80211 handle, device handle, HCI ops/type, chip pointer, HAL/fifo/fw/efuse/security/stat/regd/BF/DM/coex state, locks, work items, queues, flags, ID bitmaps, WoW state, LED state, and flexible HCI-private storage.
- Inline helpers: vif/txq container conversions, efuse grant wrappers, WCPU checks, LDPC/STBC checks, MAC ID allocation/release, firmware crash hook, and band conversion.
- Exported prototypes for core lifecycle, channel setup, station/vif handling, firmware recovery/dump, port switching, beacon control, AMPDU factor, and scan notifications.

## Control Flow
The header establishes how the driver is assembled rather than executing logic itself. Transport drivers allocate `sizeof(struct rtw_dev) + private_hci_size`, then access `rtwdev->priv` through the flexible `priv[]` tail. Core code calls chip operations from `rtw_chip_ops` for power, MAC, PHY, RF, calibration, beamforming, coexistence, and LED behavior. Table-loading macros produce `struct rtw_table` instances consumed by PHY parsers. mac80211 private areas use `hw->sta_data_size`, `hw->vif_data_size`, and `hw->txq_data_size` to store `rtw_sta_info`, `rtw_vif`, and `rtw_txq`.

## State and Persistence Behavior
`main.h` defines all long-lived in-memory state for a device. `rtw_fw_state` persists firmware pointers and parsed feature/version fields until deinit. `rtw_efuse` persists factory/calibration values and hardware capabilities read from efuse and firmware feature reports. `rtw_hal` persists current channel/bandwidth/RF topology, RCR, TX power tables, SAR source, and chip-version fields. `rtw_dm_info` persists dynamic PHY metrics across watchdog intervals. `rtw_lps_conf` persists active/LPS/deep-LPS settings and backup policy flags. Bitmaps (`hw_port`, `mac_id_map`, CAM map, TX queue flags) are the persistent allocation state used by callbacks.

## Dependencies and Integration Points
The header includes mac80211, firmware, vmalloc, EWMA, bit operations, field helpers, I/O polling, interrupt, and workqueue APIs. It includes local `util.h` before later including `hci.h`, which relies on `struct rtw_dev`. It is consumed by core, PCI, PHY, PS, firmware, TX/RX, security, coexistence, efuse, regulatory, WoW, and chip-specific files. `struct rtw_chip_info` is the main integration point for per-chip modules: they provide tables, register descriptions, feature flags, and operation callbacks.

## Risks
- Layout stability matters: `struct rtw_dev` ends with flexible `priv[]`; transport private structures depend on correct allocation and alignment.
- Many fields are shared between interrupt, workqueue, mac80211 callback, and mutex-protected contexts. The header itself does not enforce locking, so readers must follow conventions from implementation files.
- Large multidimensional TX power arrays are indexed by regulatory domain, bandwidth, rate section, channel, path, and descriptor rate. Bad enum bounds or mismatched table sizes can corrupt behavior.
- Packed bitfield structs for efuse/power/PHY conditions depend on endianness guards; new fields or compiler assumptions can break table interpretation.
- `rtw_chip_ops` has many optional hooks. Call sites must check for NULL where appropriate; some hooks, such as power tracking or false-alarm statistics, are assumed present by core PHY logic.

## Test Signals
- Build coverage across all chip variants and HCI backends, catching structure/prototype drift.
- Probe with multiple chip infos validating `rtw_dev` private storage and `rtw_chip_ops` callback availability.
- Runtime association, AP, scan, WoW, coexistence, LPS, and firmware-recovery paths validating shared state transitions.
- KASAN/lockdep runs for struct lifetime, workqueue cancellation, and mixed interrupt/workqueue access.
- Regulatory and TX power tests confirming array bounds and table parser compatibility with `rtw_hal` definitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/main.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/pci.c

## Purpose
`pci.c` implements the PCIe HCI backend for `rtw88`. It maps device registers, allocates and programs DMA descriptor rings, implements register and packet I/O hooks for core/HCI, handles TX completion and RX NAPI, controls PCI interrupts, manages PCIe link power saving and deep power-save entry/exit, applies PCI PHY/DBI/MDIO configuration, handles suspend/resume quirks, registers PCI error handlers, and provides probe/remove/shutdown entry points.

## Important APIs, Types, and Functions
- Module parameters: `disable_msi` and `disable_aspm`; DMI quirks can also disable ASPM and deep LPS.
- MMIO hooks: `rtw_pci_read8/16/32()` and `rtw_pci_write8/16/32()` back `rtw_hci_ops`.
- Ring setup/teardown: `rtw_pci_init_trx_ring()`, `rtw_pci_init_tx_ring()`, `rtw_pci_init_rx_ring()`, `rtw_pci_free_trx_ring()`, and reset helpers.
- HCI lifecycle: `rtw_pci_setup()`, `rtw_pci_start()`, `rtw_pci_stop()`, `rtw_pci_deep_ps()`, `rtw_pci_link_ps()`, `rtw_pci_interface_cfg()`, and `rtw_pci_ops`.
- TX path: `rtw_pci_tx_write_data()`, `rtw_pci_tx_write()`, `rtw_pci_tx_kick_off_queue()`, `rtw_pci_tx_kick_off()`, reserved-page and H2C writers, queue flush helpers, and `rtw_pci_tx_isr()`.
- RX path: `rtw_pci_rx_isr()`, `rtw_pci_get_hw_rx_ring_nr()`, `rtw_pci_rx_napi()`, and `rtw_pci_napi_poll()`.
- IRQ path: `rtw_pci_request_irq()`, `rtw_pci_interrupt_handler()`, `rtw_pci_interrupt_threadfn()`, interrupt mask/recognition helpers.
- PCI configuration: `rtw_dbi_read8()`, `rtw_dbi_write8()`, `rtw_mdio_write()`, `rtw_pci_link_cfg()`, `rtw_pci_phy_cfg()`, `rtw_pci_claim()`, and resource mapping/destruction.
- Top-level exports: `rtw_pci_probe()`, `rtw_pci_remove()`, `rtw_pci_shutdown()`, `rtw_pm_ops`, and `rtw_pci_err_handler`.

## Control Flow
`rtw_pci_probe()` allocates `ieee80211_hw` with appended `rtw_dev` and `rtw_pci`, assigns the chip info and PCI HCI ops, checks DMI quirks, initializes core firmware/work state, enables and claims the PCI device, maps BAR 2, allocates rings, initializes NAPI, reads chip/efuse/board info, optionally marks `rx_no_aspm`, programs PCI PHY/link settings, registers mac80211 hardware, and requests a threaded IRQ. Error paths unwind NAPI, PCI resources, core state, and hardware allocation.

During HCI setup, `rtw_pci_reset_buf_desc()` writes DMA base addresses and descriptor counts for BCN, H2C, BK/BE/VO/VI/MGMT/HI0 TX rings and the MPDU RX ring, then clears read/write pointers. Start enables NAPI, marks the backend running, and enables interrupts under `irq_lock`. Stop disables interrupts, synchronizes IRQ, stops NAPI, resets rings, and frees queued TX SKBs.

TX prepares an SKB by pushing the chip TX descriptor, filling it with `rtw_tx_fill_tx_desc()`, mapping it for DMA, writing two PCI buffer descriptors for descriptor and payload, queueing the SKB, setting a pending queue bit, and later kicking hardware by writing the queue write pointer. If a ring runs low on descriptors, the corresponding mac80211 queue is stopped; TX ISR drains completed descriptors, unmaps DMA, wakes queues when space returns, forwards requested TX status to the TX report path, and otherwise reports ACK/NOACK to mac80211.

RX interrupt handling schedules NAPI. NAPI reads the hardware write pointer, syncs each RX buffer for CPU, parses the RX descriptor, copies the frame into a fresh SKB, routes C2H packets to firmware command handling, strips RX descriptors from data frames, updates invalid-channel frequency if needed, updates RX stats, passes packets to `ieee80211_rx_napi()`, then resyncs the original DMA buffer and advances ring indices. Interrupts are reenabled when NAPI completes; a race check reschedules NAPI if data appeared before completion.

## State and Persistence Behavior
`struct rtw_pci` persists the PCI device pointer, MMIO base, IRQ masks/enabled/running state, two spinlocks, NAPI netdev, RX tag counter, TX queued bitmap, TX/RX rings, PCIe link control, link power-save usage count, ASPM workaround flag, and NAPI-running bit. Descriptor rings and RX buffers are DMA allocations held from probe until remove. TX SKBs are queued until completion or stop; reserved-page beacon queue replaces its previous SKB. RX buffers are reused permanently and copied into fresh SKBs for upper layers.

## Dependencies and Integration Points
`pci.c` integrates Linux PCI, DMI, MSI/INTx vector allocation, threaded IRQs, DMA mapping, NAPI, and mac80211 TX/RX reporting. It depends on local core/HCI abstractions (`main.h`, `pci.h`, `tx.h`, `rx.h`, `fw.h`, `ps.h`, `debug.h`, `mac.h`). It exposes `rtw_hci_ops` to core and consumes chip descriptors sizes, WCPU type, interface PHY tables, firmware features, and power-save callbacks.

## Risks
- DMA descriptor ownership and ring indices are sensitive to ordering. A bad write pointer, descriptor size, or unmap length can corrupt TX/RX or leak DMA mappings.
- RX path copies from reusable DMA buffers; allocation failure drops frames and must still resync descriptors.
- Interrupt masking is deliberately split between hard handler, threaded handler, and NAPI. Incorrect reenable behavior can cause interrupt storms, missed RX, or MSI edge loss.
- Deep power save requires TX rings to be empty unless firmware supports TX wake; entering too early can strand DMA.
- ASPM/CLKREQ behavior is hardware/platform sensitive. DMI quirks, bridge vendor checks, and module parameters are required to avoid device loss on known systems.
- Probe/remove unwind order is nontrivial; IRQ freeing after resource teardown or NAPI cleanup out of order can race live handlers.

## Test Signals
- PCI probe/remove/reprobe with MSI enabled and disabled.
- High-throughput TX/RX with queue stop/wake behavior and no DMA API warnings.
- RX NAPI budget exhaustion and interrupt-race scenarios.
- H2C and reserved-page/beacon queue writes.
- Suspend/resume on affected 8822C RFE and 8821C/Intel bridge systems, with ASPM toggling.
- Firmware recovery through PCI AER slot reset.
- Deep LPS entry under idle TX rings and forced TX while leaving deep PS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/pci.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/pci.h

## Purpose
`pci.h` defines the PCIe backend contract for `rtw88`: descriptor counts and buffer sizes, PCI register offsets and bit fields, interrupt masks, ring structures, PCI-private device state, exported PCI entry points, and small helpers for descriptor availability, queue sizing, SKB-private TX data access, and TX buffer descriptor lookup.

## Important APIs, Types, and Functions
- Ring sizes and buffers: `RTK_DEFAULT_TX_DESC_NUM`, `RTK_BEQ_TX_DESC_NUM`, `RTK_MAX_RX_DESC_NUM`, and `RTK_PCI_RX_BUF_SIZE`.
- PCI register definitions: control, DBI, MDIO, link config, descriptor base/count/index registers, read/write pointer clear, H2C CSR, interrupt mask/status registers, and interrupt bit definitions.
- Descriptor/ring types: `struct rtw_pci_tx_buffer_desc`, `struct rtw_pci_rx_buffer_desc`, `struct rtw_pci_tx_data`, `struct rtw_pci_ring`, `struct rtw_pci_tx_ring`, and `struct rtw_pci_rx_ring`.
- PCI-private state: `struct rtw_pci` with PCI device, locks, masks, running/IRQ state, NAPI netdev, RX tag, queued TX bitmap, ring arrays, link state, ASPM workaround flag, flags bitmap, and MMIO pointer.
- Exports: `rtw_pm_ops`, `rtw_pci_err_handler`, `rtw_pci_probe()`, `rtw_pci_remove()`, and `rtw_pci_shutdown()`.
- Helpers: `avail_desc()`, `max_num_of_tx_queue()`, `rtw_pci_get_tx_data()`, and `get_tx_buffer_desc()`.

## Control Flow
This header provides compile-time data consumed by `pci.c`. `max_num_of_tx_queue()` gives BE a larger ring and BCN a single descriptor. `avail_desc()` reserves one descriptor slot so full and empty ring states are distinguishable. `rtw_pci_get_tx_data()` stores PCI DMA metadata in mac80211 SKB status driver data, guarded by a `BUILD_BUG_ON()`. `get_tx_buffer_desc()` computes the current write-pointer descriptor address from ring head and descriptor size.

## State and Persistence Behavior
The declared `struct rtw_pci` state lives in `rtw_dev->priv` for the lifetime of the PCI device. Ring heads point to coherent DMA memory; RX ring `buf[]` entries point to long-lived SKBs; TX rings maintain software SKB queues matching hardware descriptors. `link_usage` persists nested link-power requests, while `flags` records NAPI state. Register constants encode persistent hardware programming addresses rather than mutable state.

## Dependencies and Integration Points
The header includes `main.h`, so it inherits core driver state and queue enums. It integrates with Linux PCI through `struct pci_dev`, DMA types, NAPI/netdev types, and mac80211 SKB control blocks. Its register definitions must match the chip families supported by the PCI backend and are used by interrupt, DMA, ASPM, DBI, and MDIO code.

## Risks
- Descriptor counts must stay within `TRX_BD_IDX_MASK`; `pci.c` validates TX lengths, but changing constants can break hardware index fields.
- `struct rtw_pci_tx_data` must fit inside mac80211 `status_driver_data`; the build assertion catches size growth only at compile time.
- RX/TX descriptor layouts use little-endian fields and exact sizes expected by hardware.
- Register definitions are shared across chip generations with conditional handling in `pci.c`; accidental reuse for unsupported chips can cause silent hardware misconfiguration.

## Test Signals
- Compile-time assertions for SKB private data size.
- Ring wrap tests for `avail_desc()` and queue stop/wake behavior.
- Probe tests validating BE/BCN/default queue descriptor counts.
- DMA and interrupt tests confirming register constants program the expected hardware queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/pci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/phy.c

## Purpose
`phy.c` implements shared PHY and RF logic for `rtw88`: rate-section tables, dynamic mechanisms run by the watchdog, DIG/false-alarm/RSSI handling, CCK packet detection tuning, rate adaptation support, CFO parsing/tracking hooks, RF register access, conditional PHY table parsing, BB/RF/MAC/AGC table loaders, TX power by-rate and regulatory limit parsing, TX power index computation, thermal power tracking helpers, and TX path diversity.

## Important APIs, Types, and Functions
- Exported rate tables: `rtw_cck_rates`, `rtw_ofdm_rates`, HT/VHT 1SS-4SS arrays, `rtw_rate_section[]`, and `rtw_rate_size[]`.
- Initialization and dynamic mechanism: `rtw_phy_init()`, `rtw_phy_dynamic_mechanism()`, `rtw_phy_dig_write()`, `rtw_phy_dig_set_max_coverage()`, and `rtw_phy_dig_reset()`.
- RSSI/rate helpers: `rtw_phy_rf_power_2_rssi()`, RA info update, RRSR mask update, and CFO parsing via `rtw_phy_parsing_cfo()`.
- RF I/O: `rtw_phy_read_rf()`, `rtw_phy_read_rf_sipi()`, `rtw_phy_write_rf_reg_sipi()`, `rtw_phy_write_rf_reg()`, and `rtw_phy_write_rf_reg_mix()`.
- Table condition/config parsing: `rtw_phy_setup_phy_cond()`, `rtw_parse_tbl_phy_cond()`, `rtw_parse_tbl_bb_pg()`, `rtw_parse_tbl_txpwr_lmt()`, `rtw_phy_cfg_mac()`, `rtw_phy_cfg_agc()`, `rtw_phy_cfg_bb()`, `rtw_phy_cfg_rf()`, and `rtw_phy_load_tables()`.
- TX power APIs: `rtw_phy_init_tx_power()`, `rtw_get_tx_power_params()`, `rtw_phy_get_tx_power_index()`, `rtw_phy_set_tx_power_level()`, `rtw_phy_tx_power_by_rate_config()`, and `rtw_phy_tx_power_limit_config()`.
- Power tracking/path diversity: `rtw_phy_config_swing_table()`, thermal delta helpers, `rtw_phy_pwrtrack_need_lck()`, `rtw_phy_pwrtrack_need_iqk()`, and `rtw_phy_tx_path_diversity()`.

## Control Flow
`rtw_phy_init()` resets dynamic mechanism history, reads the initial IGI value, initializes CCK PD state, clears IQK completion, and invokes chip-specific adaptivity/CFO/path-diversity initialization. The core watchdog calls `rtw_phy_dynamic_mechanism()`, which first refreshes RSSI and false-alarm/rate counters, then runs DIG, CCK PD, RA/RRSR updates, TX path diversity, CFO tracking, DPK tracking, power tracking, and adaptivity either through firmware or chip callbacks.

DIG computes a new initial gain index from false-alarm counts, link state, minimum RSSI, previous IGI history, and damping detection. During scans, `main.c` disables normal DIG and sets max coverage; scan completion restores the previous IGI. CCK PD runs only on 2.4 GHz and chooses a level from CCK false-alarm average, IGI, RSSI, and association state before calling the chip hook. RA tracking periodically resends station RA info and writes `REG_RRSR` based on the minimum reported station rate.

PHY table loading uses conditional table rows. `rtw_phy_setup_phy_cond()` builds the active condition from chip cut/pkg/interface/RFE/efuse fields. `rtw_parse_tbl_phy_cond()` evaluates IF/ELIF/ELSE/ENDIF-style encoded rows and applies matching config rows through the table's `do_cfg()` callback. BB power-group tables are parsed into by-rate offsets; TX power limit tables populate regulatory/channel/bandwidth/rate-section arrays, fill missing domains from alternates or worldwide defaults, and cross-reference missing HT/VHT 5 GHz limits.

TX power computation starts from efuse base indexes by channel group, applies by-rate offsets, regulatory limits, SAR limits, remnant power-tracking offsets, optional DPD disable adjustments, and chip max-power clamping. `rtw_phy_set_tx_power_level()` recomputes all rates per RF path under `hal.tx_power_mutex` and calls the chip hook to write hardware TX AGC.

## State and Persistence Behavior
PHY state is stored primarily in `rtwdev->dm_info`, `rtwdev->hal`, and `rtwdev->efuse`. Dynamic state includes false-alarm counts, RSSI levels, IGI/FA histories, damping state, CCK PD averages, CFO sums, packet counters, thermal EWMAs, TX AGC remnants, DPK/IQK/GAPK backups, and path-diversity RSSI accumulators. Power tables persist in `rtw_hal` arrays after efuse/table parsing and are reused for every channel/power update. RF/BB writes are hardware state, not filesystem persistence.

## Dependencies and Integration Points
`phy.c` depends on local register definitions, firmware feature checks, debug logging, regulatory helpers, SAR queries, chip-operation callbacks, mac80211 station/vif iterators, and per-chip table data declared through `rtw_table`. It is called by core initialization, channel setting, watchdog work, scan start/complete, RX descriptor processing for CFO/RSSI stats, and chip-specific calibration/power-tracking code.

## Risks
- Table parsing is dense and hardware-specific; malformed condition rows or RFE matching errors can apply the wrong RF/BB/MAC values.
- TX power math spans efuse, regulatory domain, SAR, bandwidth, rate section, channel group, path, NSS, DPD, and thermal remnants. Regressions may violate regulatory limits or reduce range.
- DIG and CCK PD feedback loops can oscillate; damping history reduces this risk but changes should be validated under noisy RF conditions.
- RF register access checks only `rf_phy_num`; wrong chip data can still direct writes to invalid addresses.
- Several dynamic mechanisms rely on optional chip callbacks; missing hooks can be benign or fatal depending on the call site.
- Path diversity assumes two-path support and resets accumulated samples each watchdog interval; wrong RX path state can cause ineffective or unstable path switching.

## Test Signals
- PHY table loading on every supported RFE/cut/interface combination, including unsupported RFE rejection.
- TX power index comparison against known-good tables for 2.4 GHz, 5 GHz, 20/40/80 MHz, HT/VHT, SAR, and alternative regulatory domains.
- Noisy-environment tests watching DIG, CCK PD, EDCCA/adaptivity, beacon loss, and throughput.
- Thermal chamber or simulated thermal updates validating LCK/IQK trigger thresholds and swing table selection.
- RX status tests validating RSSI conversion across 1-4 RF paths and CFO accumulation only for matching BSSID frames.
- Path-diversity tests on supported 2SS hardware with asymmetric path RSSI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/phy.h

## Purpose
`phy.h` declares the shared PHY API, rate-section tables, PHY table declaration macros, RFE validation helpers, TX power data structures, CCK packet-detection levels, register masks, RF read constants, and power-tracking helpers used by core, chip-specific PHY files, firmware/RX code, and debug paths.

## Important APIs, Types, and Functions
- Extern rate arrays and `rtw_rate_section[]`/`rtw_rate_size[]` used by TX power and rate-section logic.
- Initialization/runtime declarations: `rtw_phy_init()`, `rtw_phy_dynamic_mechanism()`, DIG helpers, EDCCA/adaptivity helpers, CFO parsing, and TX path diversity.
- RF access declarations for direct, SIPI, and mixed RF register operations.
- Table parser/config declarations for conditional PHY tables, BB power-group tables, TX power limit tables, and MAC/AGC/BB/RF config callbacks.
- TX power declarations: `rtw_phy_init_tx_power()`, `rtw_phy_load_tables()`, `rtw_phy_get_tx_power_index()`, `rtw_phy_set_tx_power_level()`, by-rate/limit config, `struct rtw_power_params`, and `rtw_get_tx_power_params()`.
- Power tracking declarations: swing table config, thermal average/change/delta helpers, power index helper, and LCK/IQK trigger predicates.
- Table macros: `RTW_DECL_TABLE_PHY_COND_CORE`, `RTW_DECL_TABLE_PHY_COND`, `RTW_DECL_TABLE_RF_RADIO`, `RTW_DECL_TABLE_BB_PG`, and `RTW_DECL_TABLE_TXPWR_LMT`.
- RFE helpers: `rtw_get_rfe_def()` and `rtw_check_supported_rfe()`.

## Control Flow
Chip-specific table files use the declaration macros to build `struct rtw_table` objects with parser and configuration callbacks. Core chip setup calls `rtw_check_supported_rfe()` before board setup, then loads PHY PG and TX power limit tables. MAC/PHY initialization later calls `rtw_phy_load_tables()` and `rtw_phy_init()`. Runtime watchdog and scan paths call the dynamic/DIG APIs declared here. RX code can call `rtw_phy_parsing_cfo()` after descriptor parsing.

## State and Persistence Behavior
The header itself stores no state, but its APIs operate on `struct rtw_dev` state from `main.h`: `rtw_hal` power arrays, `rtw_dm_info` dynamic mechanism fields, efuse power/thermal values, SAR config, and chip table pointers. The RFE inline helper logs and returns an RFE table pointer based on `efuse.rfe_option`; unsupported RFE detection is an early persistent device setup gate.

## Dependencies and Integration Points
`phy.h` includes `debug.h`, which brings in driver logging and the core types needed by declarations. It integrates with chip-specific generated table files, regulatory/SAR code, RX PHY status parsing, firmware adaptivity support, and core channel/power setup. Register mask constants are shared by low-level BB/RF configuration and chip-specific code.

## Risks
- Duplicate mask definitions must stay compatible with other register headers.
- Table declaration macros encode parser choice at compile time; using the wrong macro silently sends data to the wrong parser/config path.
- `rtw_get_rfe_def()` returns NULL when no RFE table exists or the efuse option is out of range; callers must validate before dereferencing.
- TX power helper prototypes expose many raw `u8` indexes, so callers must pass valid path/rate/bandwidth/channel/regulatory values.

## Test Signals
- Build coverage for all chip-specific table declaration macros.
- Unsupported RFE probe failure with clear error logs.
- Unit-style or trace validation of TX power helper inputs and outputs.
- Runtime scan/channel/rate/power-tracking paths invoking the declared APIs without NULL table or callback dereferences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/ps.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/ps.c

## Purpose
`ps.c` implements idle power save (IPS), leisure power save (LPS), deep LPS coordination, firmware power-mode acknowledgement, and LPS recalculation for the `rtw88` core. It bridges core lifecycle (`rtw_core_start/stop()`), HCI link/deep power-save hooks, firmware H2C power-mode commands, coexistence notifications, port restoration, and mac80211 vif power-save state.

## Important APIs, Types, and Functions
- IPS APIs: `rtw_enter_ips()` and `rtw_leave_ips()`, with helper `rtw_ips_pwr_up()`.
- Firmware/HCI power toggle: `rtw_power_mode_change()`.
- LPS helpers: `rtw_enter_lps()`, `rtw_leave_lps()`, `rtw_leave_lps_deep()`, `rtw_get_lps_deep_mode()`, `rtw_enter_lps_core()`, `rtw_leave_lps_core()`, and deep LPS helpers.
- Firmware leave-LPS validation: register polling fallback and C2H completion path through `rtw_fw_leave_lps_check()`.
- LPS policy recomputation: `rtw_recalc_lps()` and vif iterator helpers.

## Control Flow
IPS entry checks `RTW_FLAG_POWERON`; if powered, it notifies coexistence, stops core, and allows HCI link power save. IPS leave disables HCI link power save, powers the device back up through `rtw_core_start()`, notifies coexistence, restores the operating channel, and rewrites all vif port configuration registers.

LPS entry is called with `rtwdev->mutex` held. It ignores requests when coexistence forces LPS control, sets `lps_conf.mode` and port, programs LPS state (`RTW_RF_OFF`, awake interval, RLBM, smart PS), notifies coexistence, sends firmware power mode, enters HCI link PS, sets `RTW_FLAG_LEISURE_PS`, and then optionally enters deep PS. Deep PS is allowed only after LPS and only when the selected firmware/chip deep mode is not `NONE`; PG mode sends page information before HCI deep PS.

LPS leave first leaves deep PS, then if LPS is active switches mode to active, sets all-on state and active firmware parameters, disables HCI link PS, prepares C2H completion if supported, sends firmware power mode, waits for firmware to complete leave-LPS either by C2H or by polling `REG_TCR`, clears `RTW_FLAG_LEISURE_PS`, and notifies coexistence. On timeout, it clears the firmware power-management bit directly and dumps firmware debug info.

`rtw_recalc_lps()` counts vifs, treating any non-station interface or more than one station as disqualifying. Only exactly one station vif with `cfg.ps` enables LPS; otherwise it disables PS and forces LPS leave.

## State and Persistence Behavior
`ps.c` mutates `rtwdev->lps_conf`, `rtwdev->ps_enabled`, `RTW_FLAG_LEISURE_PS`, `RTW_FLAG_LEISURE_PS_DEEP`, and HCI link/deep power-save state. IPS and LPS are runtime hardware/firmware states only. `lps_leave_check` is a completion reused across leave-LPS operations when firmware advertises C2H support. Port register configuration is restored from persistent `rtw_vif` fields after IPS leave.

## Dependencies and Integration Points
This file depends on core lifecycle (`main.c`), HCI power hooks, firmware H2C power-mode/page-info commands, register definitions, MAC port configuration, coexistence notifications, debug logging, and mac80211 vif iteration. PCI implements `deep_ps` and `link_ps`; USB/SDIO backends provide equivalent HCI hooks.

## Risks
- `rtw_power_mode_change()` uses RPWM/CPWM toggle semantics and atomic polling. A missed firmware ack indicates severe hardware/firmware lockup and currently triggers warnings plus debug dumps.
- Entering deep PS before LPS or with active TX/DMA is unsafe; transport backends must enforce their side of the contract.
- IPS leave restores port configuration after full core restart; missing vif fields or ordering bugs can leave MAC/BSSID/net type stale.
- `rtw_recalc_lps()` is conservative: AP or multiple station interfaces disable LPS. Changes to multi-vif support must revisit firmware constraints.
- Several public functions assert `rtwdev->mutex` is held. Calling them unlocked can race watchdog, scan, mac80211 callbacks, or transport IRQ paths.

## Test Signals
- Idle transition into IPS and wake from scan/association with channel and port config restored.
- Single station with PS enabled entering and leaving LPS under watchdog traffic thresholds.
- Multi-vif, AP, and non-station cases disabling LPS and forcing leave.
- Firmware variants with `FW_FEATURE_LPS_C2H` and without it, validating both completion and register-poll leave checks.
- Deep LPS modes `NONE`, `LCLK`, and `PG`, including WoWLAN firmware mode selection.
- Forced firmware ack timeout path producing warnings and debug dump without deadlocking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/ps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/ps.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/ps.h

## Purpose
`ps.h` declares the power-save API for `rtw88` and defines the constants used for LPS thresholds, RPWM/CPWM power-mode bits, and leave-LPS timeout behavior. It is the narrow header through which core, transport, and mac80211-facing code coordinate IPS, LPS, and deep LPS transitions.

## Important APIs, Types, and Functions
- Policy/timing constants: `RTW_LPS_THRESHOLD`, `LEAVE_LPS_TRY_CNT`, and `LEAVE_LPS_TIMEOUT`.
- RPWM power bits: `POWER_MODE_ACK`, `POWER_MODE_PG`, `POWER_TX_WAKE`, and `POWER_MODE_LCLK`.
- IPS declarations: `rtw_enter_ips()` and `rtw_leave_ips()`.
- LPS/deep LPS declarations: `rtw_power_mode_change()`, `rtw_enter_lps()`, `rtw_leave_lps()`, `rtw_leave_lps_deep()`, `rtw_get_lps_deep_mode()`, and `rtw_recalc_lps()`.

## Control Flow
The header is consumed by `main.c` watchdog and scan/IPS paths, by `pci.c` deep/link power-save handling, and by any chip/backend code that needs to request or exit power-save states. Callers use `rtw_recalc_lps()` to update policy from vif state, `rtw_enter_lps()`/`rtw_leave_lps()` for runtime station power save, and `rtw_enter_ips()`/`rtw_leave_ips()` for full idle power-down/up.

## State and Persistence Behavior
The constants in this header shape runtime state stored in `struct rtw_dev`: traffic thresholds decide whether watchdog can enter LPS, power bits are written to HCI RPWM registers, and leave timeout constants bound firmware wait behavior. The header itself has no storage.

## Dependencies and Integration Points
`ps.h` assumes `struct rtw_dev`, `struct ieee80211_vif`, bit helpers, and `msecs_to_jiffies()` are available through including context. It integrates power-save code with firmware feature checks, HCI backends, coexistence notifications, and mac80211 vif power-save settings.

## Risks
- Timeout and retry constants are policy choices; too low can force false firmware failure handling, while too high can stall callbacks.
- Bit definitions must match firmware RPWM/CPWM protocol. Incorrect bits can prevent wake or deep-sleep entry.
- Public APIs require the locking discipline implemented in `ps.c`; the header does not encode that requirement.

## Test Signals
- Build inclusion from core and HCI backends.
- LPS entry threshold behavior under watchdog traffic counters.
- Firmware wake/ack behavior using both C2H and register-poll leave checks.
- Deep LPS with PG and TX wake firmware features.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw88/ps.h -->
