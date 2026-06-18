# subset-b-004856 research

Work item: `subset-b-004856`

This grouped report covers the MT7915/MT7916 MediaTek mt76 wireless driver files requested for this subset. Each file section is delimited for the reconciliation lane and preserves the source path in its section title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/main.c

## Purpose

`main.c` is the mac80211-facing control plane for the MT7915 family driver. It implements `const struct ieee80211_ops mt7915_ops`, translates mac80211 lifecycle and configuration callbacks into mt76 state changes and MCU commands, and coordinates per-phy, per-vif, and per-station runtime state. It is not the low-level DMA or firmware transport layer; instead, it sits above `mcu.c`, `mac.c`, mt76 common helpers, and MMIO bus operations.

The file owns user-visible wireless behavior such as device start/stop, interface allocation, BSS updates, AP start/stop, channel changes, key installation, rate-control updates, AMPDU aggregation, TSF operations, antenna selection, SAR power updates, ethtool statistics, TWT teardown requests, background radar, and WED forwarding path export.

## Important APIs, Types, and Functions

- `mt7915_ops` is the main exported mac80211 operation table. It wires local callbacks into mac80211 and delegates generic behavior to mt76 helpers for TX queues, scans, survey, station state transitions, txpower query, buffered frames, testmode, and WED TC setup.
- `mt7915_run()`, `mt7915_start()`, and `mt7915_stop()` control radio bring-up and shutdown for primary and secondary PHYs. They toggle MCU power management, MAC enable state, noise floor collection, thermal protection, RTS threshold, SKU power enforcement, RX path/channel setup, and watchdog work.
- `mt7915_add_interface()` and `mt7915_remove_interface()` allocate and release vif indices, OMAC slots, WMM index, WCIDs, BSS state, dev-info state, and the internal per-vif WCID used for non-station traffic.
- `mt7915_set_channel()` performs per-channel firmware and MAC reconfiguration: optional DPD calibration, MCU channel switch, MAC timing update, DFS radar detector initialization, CCA reset, MIB reset, noise reset, and watchdog scheduling.
- `mt7915_set_key()` validates cipher support, handles BIP key-index selection, updates per-vif cipher state, programs WCID key state through mt76, and sends MCU key records.
- `mt7915_bss_info_changed()`, `mt7915_start_ap()`, `mt7915_stop_ap()`, `mt7915_channel_switch_beacon()`, and `mt7915_update_bss_color()` coordinate BSS firmware records, virtual STA records, beacons, protection, slot timing, QoS/EDCA, OBSS PD, in-band discovery, and color-change state.
- `mt7915_mac_sta_add()`, `mt7915_mac_sta_event()`, and `mt7915_mac_sta_remove()` manage station WCIDs, firmware STA records, rate-control records, TWT cleanup, duplicate AP station pruning, and polling/rate-control lists.
- `mt7915_ampdu_action()` maps mac80211 AMPDU actions into mt76 RX aggregation state and MCU BA add/remove commands.
- `mt7915_get_tsf()`, `mt7915_set_tsf()`, and `mt7915_offset_tsf()` manipulate LPON TSF registers with chip-specific control registers.
- `mt7915_sta_statistics()`, `mt7915_get_et_strings()`, `mt7915_get_et_sset_count()`, and `mt7915_get_et_stats()` expose station and device counters, including WED offload counters and page-pool stats.
- `mt7915_set_radar_background()` controls background RDD state and `dev->rdd2_phy` ownership.
- `mt7915_net_fill_forward_path()` is compiled with WED support and exports hardware forwarding metadata to the networking stack.

## Control Flow

Startup begins in mac80211 `.start`, which flushes pending initialization work, locks `dev->mt76.mutex`, and calls `mt7915_run()`. `mt7915_run()` first detects whether any PHY is already running. If this is the first active PHY, it disables MCU power-save for the primary band, enables the MAC and RX header translation, and enables noise-floor collection. If the requested PHY is the extension PHY, it repeats the power/MAC/noise setup for that band. It then configures thermal throttling, thermal protection, RTS threshold, SKU power enforcement, and RX path channel information before marking the PHY running and queueing watchdog work.

Stop is the inverse at PHY granularity. `mt7915_stop()` cancels watchdog work, resets testmode, clears the running bit, disables the extension PHY if stopping it, and disables the primary PHY only if no PHY remains running. This shared-device check avoids powering down the shared hardware while a second band is still active.

Interface addition is allocation-heavy. `mt7915_add_interface()` resets testmode, records monitor vifs, picks a free `mvif->mt76.idx` from `dev->mt76.vif_mask`, picks an OMAC slot from `phy->omac_mask` based on interface type, chooses a WMM set, sends `mt7915_mcu_add_dev_info()`, marks masks, allocates a WTBL/WCID entry, initializes the per-vif `mt7915_sta`, clears admission counters, assigns the vif txq WCID, adjusts offload flags, initializes bitrate masks and capabilities, then creates BSS and STA records in firmware. Removal deletes firmware BSS/STA/dev-info records, clears masks, drops RCU WCID pointer, removes poll list entries, and calls `mt76_wcid_cleanup()`.

Station flow is split between mt76 station callbacks and mac80211 state events. `mt7915_mac_sta_add()` allocates a station WCID and sends a newly created disconnected STA record. On associate, `mt7915_mac_sta_event()` sends a connect STA record, tweaks WTBL DW30, installs rate control, and enables the WCID. On authorize, it disconnects matching STAs from other AP vifs before marking the current station port secure. On disassociate, it tears down all TWT flows under the mt76 mutex, sends a disconnect STA record, and disables the WCID.

BSS changes are handled under the mt76 mutex. BSSID changes, association changes, and non-AP beacon enable transitions decide whether to add or remove BSS and virtual STA firmware records. The same callback also updates protection mode, slot timing, EDCA/tx command mode, OBSS spatial reuse, BSS color, beacon templates, FILS discovery, and unsolicited broadcast probe responses.

## State and Persistence Behavior

State is in memory and hardware/firmware, not persisted to disk by this file. Durable calibration and EEPROM handling live elsewhere. Important state mutations include:

- `dev->mt76.vif_mask` and `phy->omac_mask` track allocated software vif indices and hardware OMAC slots.
- `dev->mt76.wcid_mask` and `dev->mt76.wcid[]` track allocated firmware/hardware station table entries; RCU protects readers of WCID pointers.
- `mvif->bitrate_mask`, `mvif->queue_params`, and `mvif->cap` cache mac80211 policy that later MCU commands use for rate control, EDCA, and beamforming.
- `msta->wcid` carries per-station firmware index, tx flags, aggregation state, header-translation flags, statistics, and key index state.
- `msta->twt.flow[]` and `dev->twt` state are cleaned up when stations disassociate.
- `phy->rxfilter`, `dev->monitor_mask`, `phy->slottime`, `phy->coverage_class`, `phy->noise`, `phy->throttle_state`, and channel-state/MIB structures represent live radio state.
- `dev->rdd2_phy` and `dev->rdd2_chandef` record which PHY owns background radar detection.

The file consistently uses `dev->mt76.mutex` for firmware and hardware configuration sequences, spinlocks for station poll/rate-control lists, and RCU for WCID pointer publication. Some MCU calls during teardown occur outside the mutex before later mask cleanup, so ordering depends on the higher mac80211/mt76 lifecycle.

## Dependencies and Integration Points

`main.c` depends on mac80211 and cfg80211 for callback contracts, vifs, stations, BSS configuration, channel definitions, SAR, radar, TWT, and statistics. It depends on mt76 common helpers for WCID allocation, TX, testmode, survey, scan, key setup, rate helpers, WED netdev hooks, and work scheduling. It depends heavily on `mcu.c` for firmware commands and on `mac.c` for WTBL updates, timing, counters, TXWI generation, and TWT teardown. It also touches MMIO registers via `mt76_rr/wr/rmw` macros backed by `mmio.c`.

WED integration is conditional on `CONFIG_NET_MEDIATEK_SOC_WED`; station statistics and forwarding path behavior change when WED is active. Debugfs station hooks are conditional on `CONFIG_MAC80211_DEBUGFS`. Testmode resets and antenna overrides are conditional on `CONFIG_NL80211_TESTMODE`.

## Risks and Edge Cases

- Interface allocation has several coupled resources. A failure after dev-info creation or mask updates can leave partial firmware or mask state if not carefully unwound; this path should be reviewed when changing allocation order.
- `get_free_idx()` uses `ffs()` on a generated mask and returns a 1-based index that callers subtract. Boundary changes to OMAC constants can break slot selection.
- `mt7915_set_key()` falls back for unsupported ciphers and per-STA RX GTK limitations; changing cipher handling risks hardware/software encryption mismatch.
- BSS change handling intentionally delays removals until the end of the callback; reordering can race beacon, BSS, and STA firmware records.
- Rate-control fixed-mask logic accepts only specific mask shapes. Multi-rate or mixed-preamble masks can silently fall back to firmware rate control.
- TSF register accesses are chip-specific and assume the mt76 mutex is held by the internal helper.
- Background radar state rejects concurrent ownership with `-EBUSY`; caller behavior must tolerate this.
- WED station statistics are partly queried from WA firmware and partly accumulated locally; counter freshness and overflow behavior differ from non-WED paths.

## Test Signals

Useful validation signals include successful interface create/remove cycles across AP, STA, monitor, mesh, and dual-band modes; `iw` association and AP bring-up; key install for CCMP/GCMP/TKIP/BIP; channel switch and DFS radar events; `iw station dump` TX/RX bitrate and ACK signal fields; ethtool stat count matching `MT7915_SSTATS_LEN + page_pool_ethtool_stats_get_count()`; AMPDU start/stop under traffic; TWT setup/teardown; SAR power updates; monitor filter behavior; WED forwarding path activation; and suspend/reconfig complete paths waking queues and restarting watchdog work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mcu.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mcu.c

## Purpose

`mcu.c` is the firmware command and event implementation for the MT7915 family. It encodes mt76/mac80211 state into MediaTek MCU TLVs, selects the correct MCU queue, downloads firmware, handles firmware ownership transitions, parses synchronous responses, dispatches unsolicited events, and exposes command helpers used by `main.c`, `mac.c`, DFS, debugfs, EEPROM, thermal, txpower, calibration, and WED paths.

The file is the primary contract boundary between Linux driver state and WM/WA firmware. Most functions allocate command SKBs, append fixed-format packed structures or nested TLVs, send them through `mt76_mcu_send_msg()` or `mt76_mcu_skb_send_msg()`, and optionally parse firmware replies.

## Important APIs, Types, and Functions

- `mt7915_mcu_init()` installs `struct mt76_mcu_ops` with MT7915-specific message send, response parse, timeout, and headroom behavior, then calls `mt7915_mcu_init_firmware()`.
- `mt7915_mcu_init_firmware()` obtains driver ownership, downloads ROM patch and WM/WA firmware, marks MCU running, disables firmware logs by default, clears WTBL, configures WA capability, MWDS, MURU platform mode, RX airtime, and RED.
- `mt7915_mcu_send_message()` routes firmware download traffic to `MT_MCUQ_FWDL`, post-boot traffic to WA, and pre-boot traffic to WM.
- `mt7915_mcu_parse_response()` handles timeouts, reset scheduling, sequence matching, command-specific response bodies, and special WA TX stat responses.
- Event handlers include CSA completion, thermal notifications, radar detection, firmware log routing, BSS color-change completion, and generic unsolicited event dispatch through `mt7915_mcu_rx_event()`.
- BSS helpers include `mt7915_mcu_add_bss_info()`, `mt7915_mcu_bss_rfch_tlv()`, `mt7915_mcu_bss_ra_tlv()`, `mt7915_mcu_bss_he_tlv()`, `mt7915_mcu_bss_hw_amsdu_tlv()`, `mt7915_mcu_bss_bmc_tlv()`, `mt7915_mcu_muar_config()`, `mt7915_mcu_update_bss_color()`, `mt7915_mcu_set_protection()`, `mt7915_mcu_add_beacon()`, and `mt7915_mcu_add_inband_discov()`.
- STA helpers include `mt7915_mcu_add_sta()`, BA add/remove, HT/VHT/HE/MURU/AMSDU/WTBL/beamforming TLVs, SMPS update, fixed-rate controls, and rate-control record generation.
- Channel/radar helpers include `mt7915_mcu_set_chan_info()`, background chain control, `mt7915_mcu_rdd_background_enable()`, and DFS threshold setters.
- EEPROM/calibration helpers include `mt7915_mcu_set_eeprom()`, `mt7915_mcu_get_eeprom()`, free-block query, group pre-cal upload, and per-channel DPD upload.
- Power and thermal helpers include SKU enable/table/query, per-station frame power limits, thermal query, duty-cycle throttling, and thermal protection thresholds.
- Debug/control helpers include firmware log control, firmware debug level, MURU debug stats, SER control, TXBF actions, OBSS spatial reuse, RX rate query, WED WA TX stats, RF register access, and generic WA parameter command.

## Control Flow

Firmware initialization starts by forcing normal operation mode in `MT_SWDEF_MODE`, requesting driver ownership for band 0 and optionally band 1, restarting MCU firmware, polling for firmware download state, loading the chip-specific ROM patch and WM/WA firmware names, polling for ready state, and cleaning firmware download TX queues. After `MT76_STATE_MCU_RUNNING` is set, later MCU messages route to WA instead of WM.

Response parsing is defensive. A missing response logs the command and sequence, sets `MT76_MCU_RESET` once, marks recovery restart, wakes MCU waiters, queues reset work, and returns `-ETIMEDOUT`. A mismatched sequence returns `-EAGAIN`, except for the special WA TX stat event. Some commands pull nonstandard response headers before returning a status word.

BSS updates use a station-request wrapper and a strict TLV order. `mt7915_mcu_add_bss_info()` optionally configures MUAR repeater entries, allocates a BSS update request, emits OMAC first, emits basic BSS state, skips most data for monitor interfaces, and then appends RF channel, BMC rate, RA, HW AMSDU, HE, and ext-BSS TLVs when enabling. Beacon and in-band discovery offload create nested `BSS_INFO_OFFLOAD` sub-TLVs and embed TXWI plus the generated template frame.

STA updates also rely on firmware ordering. `mt7915_mcu_add_sta()` always emits basic STA state. For connected real stations it appends beamformer, HT, VHT, and UAPSD TLVs before WTBL. It appends WTBL for new stations or non-disconnect state, skips later capability TLVs on disconnect, and for connected stations adds AMSDU, HE, MURU, and beamformee TLVs. It then sends a DRR group command and gives WED a chance to append/update station state before sending `STA_REC_UPDATE`.

Rate control starts with `STA_REC_RA`, encoding supported legacy/HT/VHT/HE rates after applying the vif bitrate mask, then optionally sends fixed-rate overrides for exact single-rate masks, GI, HE LTF, and SPE index. Fixed GI updates WTBL directly because firmware TXCMD changes do not fully update the hardware rate visible in WTBL.

Channel switching encodes channel number, center channels, bandwidth, TX path count, RX path/mask, band index, channel band, CAC/switch reason, and 80+80 secondary center. Scan, idle, DFS, monitor, and testmode paths alter the switch reason and path fields.

## State and Persistence Behavior

This file writes persistent hardware/firmware state but does not persist files. It uses:

- `dev->mphy.state` bits for MCU running and reset state.
- `dev->recovery` fields when MCU timeouts or command-status errors require restart.
- `dev->cal`, `dev->cur_prek_offset`, and DPD channel counts for pre-calibration upload.
- `dev->mt76.eeprom.data`, `dev->flash_mode`, and chip-specific EEPROM sizes for EFUSE/flash buffer mode.
- `phy->sku_limit_en`, `phy->sku_path_en`, `mphy->txpower_cur`, and regulatory power-limit tables for TX power.
- `phy->throttle_temp[]`, `phy->throttle_state`, and firmware thermal notifications for thermal behavior.
- `phy->state_ts` and `mphy->chan_state` for clear-on-read or delta channel busy counters.
- `dev->hw_pattern` incremented on radar events.
- `msta->wcid.amsdu`, `msta->wcid.stats`, `msta->changed`, TWT flow data, and beamforming/rate-related WCID fields.

Most wire structures are `__packed` and little-endian. This is a high-risk ABI with firmware; field order, alignment, length, and endian conversions are part of the contract.

## Dependencies and Integration Points

`mcu.c` depends on `mt76_connac_mcu.h` for common TLV builders, command IDs, STA/BSS structures, WTBL helpers, and firmware download helpers. It depends on mac80211/cfg80211 for capabilities, BSS config, chandefs, rates, DFS regions, and generated beacon/FILS/probe templates. It calls into `mac.c` for TXWI creation and WTBL address calculation, into EEPROM helpers for calibration size and power targets, into mt76 for MCU queues, worker control, RCU WCID lookup, WED station updates, and firmware load routines, and into debugfs for firmware log handling.

Firmware names are selected with chip and ADIE/SKU helpers from `mt7915.h`. WED support is conditional and uses `mtk_wed_device_update_msg()`, WA TX stat queries, and WED station append helpers. Several paths are build-time gated by testmode, WED, and debugfs features.

## Risks and Edge Cases

- TLV tag ordering is explicitly required by firmware in STA and BSS records. Reordering can produce firmware-side misconfiguration without compile-time failures.
- Packed request structures and manual SKB length calculations must match firmware exactly. Incorrect padding or length can corrupt subsequent TLVs.
- Firmware timeout handling schedules a reset and wakes waiters; callers must avoid retry loops that fight recovery.
- Clear-on-read MURU stats and channel MIB counters are accumulated locally. Missing a poll or reading during channel switch can distort reported statistics.
- DPD frequency index tables are chip-specific and reject 80+80; adding bands or widths requires careful table updates.
- Per-station TX power assumes HT/VHT/HE capability layout and can return `-EINVAL` for legacy-only stations.
- Beacon and in-band discovery offload enforce `MT7915_MAX_BEACON_SIZE`; template size regressions surface as runtime errors.
- `mt7915_mcu_sta_he_tlv()` appears to assign `he->dcm_rx_max_nss` twice, with the second assignment using DCM RU bits. Changes here need firmware-format validation.
- Background radar commands depend on cfg80211 DFS region and valid chandefs; unset regions and non-5GHz PHYs fail early.
- Firmware log routing treats debugfs WM logs specially and emits unknown sources through wiphy info logs.

## Test Signals

Strong test signals include firmware download success for MT7915, MT7916, MT7981, and MT7986 variants; MCU timeout recovery behavior; AP/STA BSS record programming; beacon, MBSSID, CSA, BCC, FILS discovery, and unsolicited probe response offload; HE/VHT/HT station association with rate-control and beamforming TLVs; AMPDU BA add/remove; DFS radar detection including background radar; thermal throttle notifications and protection thresholds; regulatory/SAR power table updates; EEPROM EFUSE and flash-mode paths; group and DPD calibration upload; MURU debug stat reads; WED WA TX stat reads; RF register set/query; and negative tests for oversized templates, invalid chandefs, unsupported widths, and bad firmware response sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mcu.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mcu.h

## Purpose

`mcu.h` defines MT7915-family firmware command payloads, event payloads, command constants, TLV structures, enum values, and size limits used by `mcu.c` and related driver files. It is a firmware ABI header: the packed layouts describe how Linux-side state is serialized for the WM/WA MCU and how firmware notifications are decoded.

## Important APIs, Types, and Definitions

- Thermal and event payloads: `mt7915_mcu_thermal_ctrl`, `mt7915_mcu_thermal_notify`, `mt7915_mcu_csa_notify`, `mt7915_mcu_bcc_notify`, and `mt7915_mcu_rdd_report`.
- Radar/background scan structure: `mt7915_mcu_background_chain_ctrl`, including serving and monitor channel fields, scan mode, band index, and monitor scan type.
- Spatial reuse and EEPROM payloads: `mt7915_mcu_sr_ctrl`, `mt7915_mcu_eeprom`, and `mt7915_mcu_eeprom_info`.
- Query/response payloads: `mt7915_mcu_phy_rx_info`, `mt7915_mcu_mib`, `mt7915_mcu_txpower_sku`, `mt7915_mcu_tx`, and `mt7915_mcu_muru_stats`.
- BSS TLV structures: BMC rate, RA, HW AMSDU, BSS color, HE, beacon wrapper, beacon countdown, MBSSID, beacon content, in-band discovery, and protection TLVs.
- Command enums cover ATE parameters, channel MIB offsets, firmware log source, TWT agreement operations, WA parameter operations, RED controls, MMPS modes, beacon sub-TLVs, rate parameters, txpower feature IDs, OBSS SPR operations, thermal protection actions, TXBF actions, MURU settings, MURU stats commands, and SER actions.
- Size macros such as `MT7915_MAX_BEACON_SIZE`, `MT7915_BEACON_UPDATE_SIZE`, `MT7915_MAX_BSS_OFFLOAD_SIZE`, and `MT7915_BSS_UPDATE_MAX_SIZE` bound SKB allocations in `mcu.c`.

## Control Flow Role

This header does not execute control flow directly. Its values drive the command-building branches in `mcu.c`. For example:

- `THERMAL_PROTECT_*` constants select which firmware thermal operation a packed `mt7915_mcu_thermal_ctrl` represents.
- `BSS_INFO_BCN_*` values select nested beacon-offload sub-TLVs.
- `RATE_PARAM_*` values select fixed-rate, GI, HE-LTF, MMPS, automatic, or SPE update behavior.
- `TX_POWER_LIMIT_*` values select SKU enable, rate/path power tables, power queries, and frame power limits.
- `SPR_*` values select spatial reuse enablement, dynamic PD behavior, SIG-A restrictions, SRG bitmaps, and OBSS PD parameters.
- `SER_*` values encode firmware recovery actions and system assert triggers.

## State and Persistence Behavior

All structures in this file represent transient firmware messages or replies. They do not store driver state by themselves, but the layouts govern how runtime state from `mt7915_dev`, `mt7915_phy`, `mt7915_vif`, and `mt7915_sta` is persisted into firmware tables. Many structures are marked `__packed`, and some beacon TLVs are also `__aligned(4)`, so alignment is part of the ABI.

The most state-sensitive layouts are radar reports with arrays of pulses, channel MIB counters, MURU clear-on-read statistics, BSS update TLVs, beacon offload sub-TLVs, and txpower tables. Changes to these definitions affect runtime hardware behavior across resets only after firmware is reprogrammed; they are not saved by the kernel.

## Dependencies and Integration Points

`mcu.h` includes `../mt76_connac_mcu.h`, so it extends the common connac MCU API with MT7915-specific structures. It depends on constants from mac80211/mt76 headers such as `IEEE80211_NUM_ACS`, `CMD_HE_MCS_BW_NUM`, `MT7915_SKU_RATE_NUM`, and common BSS/STA request headers. `mcu.c` is the main consumer, but `main.c`, debugfs, DFS, and EEPROM code use the exported command helpers whose payloads are defined here.

## Risks and Edge Cases

- Packed firmware ABI structures are easy to break by adding fields, changing enum values, or using host-endian fields where firmware expects little-endian.
- Several enums use sparse firmware-assigned values, for example rate parameters, WA parameter IDs, txpower format IDs, SPR actions, and SER actions. Renumbering is not safe.
- Size macros must remain consistent with TLV builders in `mcu.c`; underestimating sizes causes SKB tail overrun risk, and overestimating can hide layout regressions.
- Radar report pulse arrays are large and firmware-owned; decoders must validate context before trusting the radar index.
- `struct edca` mixes 8-bit and little-endian fields; queue, CW, and TXOP conversion must stay in the sender.

## Test Signals

Header changes should be validated by building the driver with sparse/endian checking, exercising firmware commands that use every modified structure, checking firmware acceptance of BSS/STA/beacon updates, verifying txpower and thermal commands with real firmware replies, and ensuring `sizeof()`-based allocation macros still cover emitted TLVs. Runtime signs of mismatch include MCU command timeouts, firmware asserts, invalid radar events, wrong EDCA behavior, missing beacons, rejected station records, and broken power limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mcu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mmio.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mmio.c

## Purpose

`mmio.c` provides the MT7915-family MMIO backend, register translation, WED attachment, interrupt handling, mt76 device allocation, and module registration. It selects chip-specific register tables for MT7915, MT7916, MT7981, and MT7986, wraps mt76 bus operations to remap large physical register addresses into accessible PCI/AXI windows, and connects the device to mt76 DMA/NAPI callbacks and mac80211 operations.

## Important APIs, Types, and Functions

- Chip tables `mt7915_reg`, `mt7916_reg`, and `mt7986_reg` provide revision-specific base addresses for interrupts, WFDMA, firmware crash/debug addresses, SWDEF, and WED rings.
- Offset tables `mt7915_offs` and `mt7916_offs` provide revision-specific register offsets for TMAC, MDP, ARB, RMAC/MIB, AGG, LPON, WTBL, PLE, and ETBF areas.
- Register maps `mt7915_reg_map`, `mt7916_reg_map`, and `mt7986_reg_map` translate high physical register ranges into mapped MMIO windows.
- `mt7915_mmio_init()` initializes mt76 MMIO, selects register descriptors by device ID, clones and overrides bus ops, records ASIC revision, and initializes the remap spinlock.
- `mt7915_rr()`, `mt7915_wr()`, `mt7915_rmw()`, and `mt7915_memcpy_fromio()` are the register access wrappers used through mt76.
- `mt7915_mmio_wed_init()` optionally attaches MediaTek WED and fills bus-specific WED register addresses, token sizes, RX buffer sizes, callbacks, IRQ, and DMA device.
- `mt7915_dual_hif_set_irq_mask()` manages shared IRQ masks across primary and secondary HIF.
- `mt7915_irq_handler()` is the top-half IRQ entry. `mt7915_irq_tasklet()` processes interrupt status, schedules NAPI, handles MCU command errors, and re-masks interrupts.
- `mt7915_mmio_probe()` allocates the mt76/mt7915 device and installs `struct mt76_driver_ops`.
- `mt7915_init()` and `mt7915_exit()` register and unregister PCI primary, PCI HIF, and optional platform WMAC drivers.

## Control Flow

Probe code from PCI or platform calls `mt7915_mmio_probe()` with a mapped base and device ID. That allocates an mt76 device with `mt7915_ops` and MT7915-specific `mt76_driver_ops`, initializes MMIO/register mapping through `mt7915_mmio_init()`, and sets up the IRQ tasklet.

`mt7915_mmio_init()` calls `mt76_mmio_init()` first, then chooses register and offset maps by device ID. It saves the original bus ops in `dev->bus_ops`, duplicates the bus ops, replaces `rr`, `wr`, and `rmw` with MT7915 remapping wrappers, and installs the clone back into `dev->mt76.bus`. Direct register offsets below `0x100000` pass through. High addresses are searched in `dev->reg.map`; if absent, the code programs layer-1 or layer-2 HIF remap registers under `dev->reg_lock` and accesses the remapped aperture.

Interrupt flow starts in `mt7915_irq_handler()`, which masks primary and optional secondary interrupt sources, rejects interrupts before initialization, and schedules `mt76.irq_tasklet`. The tasklet reads WED or raw interrupt status, combines secondary HIF status, traces it, disables RX done and MCU TX done bits, schedules TX NAPI and RX NAPI queues for main, band1, MCU, WA, and variant-specific WA queues, then checks MCU command status. Firmware error or watchdog bits set `dev->recovery.state` and call `mt7915_reset()`.

WED initialization is optional and gated by the `wed_enable` module parameter and build support. When active, it maps PCI BAR or platform resources, fills WPDMA/WED addresses from the selected register table, sets token and RX buffer parameters, registers offload and reset callbacks, attaches WED, replaces the IRQ with WED's IRQ, and switches DMA ownership to the WED device.

Module init registers the auxiliary HIF PCI driver before the primary PCI driver, then optional MT798x WMAC platform driver. Exit unregisters in reverse order.

## State and Persistence Behavior

`mmio.c` sets persistent runtime state inside `struct mt7915_dev` and `struct mt76_dev`:

- `dev->reg` stores selected register bases, offsets, map pointer, and map size.
- `dev->bus_ops` preserves original low-level MMIO operations while `dev->mt76.bus` points to remapping wrappers.
- `dev->reg_lock` serializes remap window programming and access.
- `mdev->rev` records device ID and hardware revision.
- `mdev->mmio.irqmask` is updated under `mmio.irq_lock`, and dual-HIF writes mirror masks into both interrupt controllers.
- `dev->mt76.mmio.wed` stores WED attachment state, register addresses, callbacks, token sizes, IRQ, and DMA device.
- IRQ/NAPI scheduling state lives in mt76 NAPI objects.

No file-backed persistence is performed. State is re-established on driver load/probe and torn down on remove/module exit.

## Dependencies and Integration Points

This file integrates with the Linux PCI, platform, module, DMA, IRQ, NAPI, RTNL, and optional WED subsystems. It depends on mt76 MMIO, DMA, bus, tracing, and allocation helpers. It exports functions declared in `mt7915.h` and consumes functions from `main.c`, `mac.c`, `mcu.c`, DMA code, and reset logic through the `mt76_driver_ops` table and interrupt recovery callouts.

WED reset integration calls `mt7915_mcu_set_ser()` and waits for `mdev->mmio.wed_reset`, temporarily dropping RTNL. Register remapping relies on definitions in `regs.h` and chip predicates from mt76.

## Risks and Edge Cases

- Register remap access is global-window based. Missing `dev->reg_lock` coverage or nested remap use can read/write the wrong physical register.
- `__mt7915_reg_addr()` returns `0` when a high address is not in the static map, causing dynamic remap. A legitimate mapped offset of zero is indistinguishable from "needs remap" by design and must remain compatible with the tables.
- WED attach changes IRQ and DMA device ownership; cleanup paths must detach WED instead of freeing PCI vectors when active.
- Interrupt masking must be balanced with NAPI poll completion. Missing re-enable causes stalls; premature re-enable can cause interrupt storms.
- Dual-HIF interrupt masks must update both primary and secondary controllers. Primary-only changes can leave band1 queues dead or noisy.
- `mt7915_irq_handler()` returns `IRQ_NONE` before initialization after masking interrupts; probe ordering must ensure interrupts are not lost permanently.
- Chip-specific register maps are large and manually maintained; wrong entries can cause silent hardware misconfiguration or firmware crash dump failures.

## Test Signals

Validation should cover probe for each supported device ID, direct and remapped register reads, firmware download through remapped MCU registers, interrupt delivery for TX done and every RX queue, NAPI poll completion re-enabling interrupts, dual-HIF operation, WED attach/detach and reset, crash/status register reads, module unload/reload, and negative tests for invalid device IDs. Useful runtime signals include ASIC revision logs, no IRQ storms, stable traffic under both bands, working MCU command error recovery, and WED counters advancing when offload is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mt7915.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mt7915.h

## Purpose

`mt7915.h` is the central private header for the MT7915-family driver. It defines firmware names, EEPROM defaults and sizes, ring sizes, token sizes, thermal/power constants, queue IDs, device/PHY/VIF/STA state structures, recovery state, TWT state, helper accessors, feature-gated stubs, and cross-file function prototypes. It is the main integration contract among `main.c`, `mcu.c`, `mmio.c`, PCI/platform probe code, MAC/DMA/debugfs/EEPROM/DFS/testmode code, and mt76 common infrastructure.

## Important APIs, Types, and Definitions

- Constants define interface limits, WTBL sizes, watchdog/reset timing, TX/RX/MCU ring sizes, firmware and ROM patch names for MT7915/MT7916/MT7981/MT7986, default EEPROM names, EEPROM sizes, token sizes, thermal limits, SKU table sizes, TWT limits, WED RX token size, and default RTS threshold.
- Queue enums `mt7915_txq_id`, `mt7915_rxq_id`, and `mt7916_rxq_id` map driver queue IDs to firmware/DMA rings.
- `struct mt7915_twt_flow` stores per-flow TWT agreement state used by MAC and MCU agreement update code.
- `struct mt7915_sta` extends `mt76_wcid` with vif pointer, rate-control list node, airtime counters, ACK signal EWMA, changed flags, key/BIP state, and per-station TWT flow table.
- `struct mt7915_vif_cap` caches per-vif negotiated LDPC and beamforming capabilities.
- `struct mt7915_vif` extends `mt76_vif_link` with capabilities, internal per-vif station/WCID, owning PHY, EDCA queue params, and bitrate mask.
- `struct mt7915_phy` stores per-radio mt76 phy pointer, hardware capability tables, monitor vif, thermal cooling state, rx filter, OMAC mask, noise, timing/coverage, MIB state, SKU flags, and testmode state.
- `struct mt7915_dev` embeds `mt76_dev/mt76_phy` as the first union member, then adds HIF2 pointer, register descriptor, queue mappings, WFDMA mask, bus ops, primary PHY, background radar state, chain information, work items, reset waitqueue, recovery fields, coredump data, station rate-control/TWT lists, register lock, feature flags, debugfs/relay state, calibration data, firmware debug flags, reset controls, and SoC MMIO pointers.
- Inline helpers include `mt7915_get_rdd_idx()`, `mt7915_hw_phy()`, `mt7915_hw_dev()`, `mt7915_ext_phy()`, `mt7915_check_adie()`, `mt7915_wtbl_size()`, `mt7915_eeprom_size()`, `mt7915_irq_enable()`, and `mt7915_irq_disable()`.
- Function prototypes expose registration, EEPROM, DMA, TXBF, TX power, reset, MCU, MAC, RX/TX, DFS, debugfs, WED, and MMIO services.

## Control Flow Role

The header does not execute main control flow, but it defines the state and call graph used by all implementation files. `mmio.c` allocates `struct mt7915_dev`, initializes `dev->reg`, and installs mt76 driver ops. `pci.c` stores HIF2 pointers and calls registration/unregistration. `main.c` uses the inline accessors to map mac80211 `hw` pointers to `mt7915_phy` and `mt7915_dev`, and mutates `mt7915_vif` and `mt7915_sta`. `mcu.c` consumes the prototypes, constants, and structures to build firmware commands. `mac.c`, DMA, DFS, testmode, EEPROM, and debugfs fill in the declared functions.

IRQ enable/disable helpers switch between single-HIF and dual-HIF implementations and schedule the IRQ tasklet after enabling. WTBL and EEPROM size helpers encapsulate MT7915 versus newer-family sizing differences.

## State and Persistence Behavior

This header defines almost all non-firmware persistent runtime state for the driver instance. The state persists for the lifetime of the kernel device object and is rebuilt on probe. Notable lifetime boundaries:

- `mt7915_dev` exists from `mt76_alloc_device()` until `mt76_free_device()`/unregister cleanup.
- `mt7915_phy` exists for primary and optional secondary PHYs while registered.
- `mt7915_vif` and `mt7915_sta` live in mac80211 private storage for interface and station lifetimes.
- `mt7915_hif` objects are registered by auxiliary PCI HIF probe and reference-counted when associated with a primary device.
- Calibration data and EEPROM data are memory-resident copies used to program firmware; this header only stores pointers and sizes.
- Recovery, coredump, debugfs, relay, TWT, and background radar fields hold live runtime state and must be synchronized by implementation code.

The comments "must be first" on embedded mt76 structures are ABI-like constraints for container casts. Changing structure order would break many `container_of()` and mt76 callback assumptions.

## Dependencies and Integration Points

`mt7915.h` includes Linux interrupt/ktime support, mt76 connac definitions, and `regs.h`. It declares external driver tables for mac80211 ops, testmode ops, PCI drivers, and optional platform WMAC driver. Conditional sections integrate with `CONFIG_MT798X_WMAC`, `CONFIG_NL80211_TESTMODE`, `CONFIG_DEV_COREDUMP`, `CONFIG_MAC80211_DEBUGFS`, and WED support.

Every source file in this subset includes this header. It is also used by sibling driver files outside the subset, including MAC, DMA, EEPROM, init, debugfs, DFS, testmode, and SoC WMAC code.

## Risks and Edge Cases

- Structure layout constraints are critical. `mt7915_sta.wcid`, `mt7915_vif.mt76`, and `mt7915_dev.mt76/mphy` must stay first as documented.
- Queue ID constants and ring sizes must match DMA initialization and firmware expectations.
- Firmware file-name macros must stay synchronized with `MODULE_FIRMWARE()` declarations and `mcu.c` chip-selection logic.
- WTBL and EEPROM size helpers use `is_mt7915()` as a binary split; new variants may need more granular sizing.
- `mt7915_check_adie()` reads SoC infrastructure registers only for MT798x; callers must not assume nonzero on PCI chips.
- Recovery, TWT, and background radar fields are shared across asynchronous work, IRQ recovery, and mac80211 callbacks, so implementation code must preserve locking discipline.
- Adding fields under config guards can create build-only failures in less common configurations.

## Test Signals

Header-level changes should be validated by building all relevant configuration combinations: PCI only, MT798x WMAC, WED, testmode, debugfs, and devcoredump. Runtime signals include successful container casts through mt76 callbacks, correct WTBL allocation limits on MT7915 versus MT7916-class chips, firmware file requests matching chip type, dual-HIF IRQ enable behavior, valid EEPROM sizing, and no structure offset regressions in station/vif private data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/mt7915.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/pci.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/pci.c

## Purpose

`pci.c` is the PCI probe/remove layer for MT7915/MT7916 primary devices and auxiliary HIF devices. It matches PCI IDs, enables and maps BAR0, configures DMA and IRQ resources, discovers/links the optional second HIF, initializes the MMIO device, optionally attaches WED, requests primary and secondary interrupts, enables PCIe interrupt master switches, and calls `mt7915_register_device()`.

## Important APIs, Types, and Functions

- `mt7915_pci_device_table` matches primary devices `0x7915` and `0x7906`.
- `mt7915_hif_device_table` matches auxiliary HIF devices `0x7916` and `0x790a`.
- Static globals `hif_list`, `hif_lock`, and `hif_idx` coordinate discovery of a second PCI function/device used as HIF2.
- `mt7915_pci_get_hif2()` scans registered HIF devices for a recognition ID, takes a device reference, and returns the matching `struct mt7915_hif`.
- `mt7915_pci_init_hif2()` increments a global recognition index, writes it to the primary BAR recognition register with semaphore bit, and tries to find the matching auxiliary HIF.
- `mt7915_pci_hif2_probe()` creates and registers a lightweight `mt7915_hif` object for auxiliary devices.
- `mt7915_pci_probe()` handles both auxiliary and primary probe paths.
- `mt7915_hif_remove()` removes auxiliary HIF objects from the global list.
- `mt7915_pci_remove()` releases HIF2 and unregisters the primary device.
- `mt7915_hif_driver` and `mt7915_pci_driver` are exported to `mmio.c` module init.

## Control Flow

Both PCI drivers use `mt7915_pci_probe()`. The function first enables the PCI device with managed helpers, maps BAR0, sets bus mastering, enforces a 32-bit DMA mask, and disables ASPM through mt76. If the matched ID is an auxiliary HIF ID, it stops there and calls `mt7915_pci_hif2_probe()` to allocate a list entry, record BAR0 and IRQ, and set drvdata.

For primary IDs, the probe calls `mt7915_mmio_probe()` to allocate and initialize the mt76/mt7915 device, resets WFSYS, and tries to initialize HIF2. It then calls `mt7915_mmio_wed_init()`. A positive return means WED attached and supplied an IRQ/DMA device. A zero return means normal PCI IRQ vectors are allocated and HIF2 detection is retried. The primary IRQ is requested with `mt7915_irq_handler`, PCIe MAC interrupts are enabled, and if HIF2 exists, `dev->hif2` is set, secondary interrupt masks are cleared, the correct secondary PCIe interrupt master switch is enabled, and a secondary IRQ is requested.

The final step is `mt7915_register_device(dev)`, which performs the broader driver registration outside this file. Error paths unwind in reverse: secondary IRQ/device reference, primary IRQ, WED detach or PCI vector free, and mt76 device free.

Remove is shorter. Auxiliary remove deletes the HIF list node. Primary remove drops the HIF2 device reference and calls `mt7915_unregister_device()`.

## State and Persistence Behavior

Persistent runtime state includes the global auxiliary HIF list and recognition index, `struct mt7915_hif` objects stored in managed PCI device memory, primary `dev->hif2` references, PCI drvdata, IRQ registrations, and WED/IRQ-vector state. None of this is stored across module unload or device removal.

`mt7915_pci_get_hif2()` uses `get_device()` to hold the auxiliary device while associated with a primary device; `mt7915_put_hif2()` releases it. The recognition ID written into primary BAR0 is a hardware coordination mechanism for matching the primary and auxiliary functions.

## Dependencies and Integration Points

`pci.c` integrates with Linux PCI core, DMA API, IRQ management, and module firmware declarations. It depends on `mmio.c` for `mt7915_mmio_probe()`, `mt7915_mmio_wed_init()`, and `mt7915_irq_handler()`, on reset/register helpers for `mt7915_wfsys_reset()`, on registration code for `mt7915_register_device()`/`mt7915_unregister_device()`, and on mt76 PCI helpers such as `mt76_pci_disable_aspm()`.

The file declares firmware dependencies for MT7915 and MT7916 primary devices through `MODULE_FIRMWARE()`. MT798x firmware declarations are handled outside this PCI-specific file.

## Risks and Edge Cases

- HIF2 pairing relies on a global incrementing `hif_idx` and recognition register value. Concurrent probes and stale auxiliary entries require correct locking and device references.
- `mt7915_hif_remove()` removes from `hif_list` without an explicit lock in this file, while lookup uses `hif_lock`; this deserves care if removal can race lookup.
- WED initialization changes the cleanup branch. If WED attaches, PCI IRQ vectors may not have been allocated and cleanup must call `mtk_wed_device_detach()`.
- HIF2 is attempted before and after WED initialization in the non-WED path; behavior depends on auxiliary device probe timing.
- Error labels must distinguish `dev->hif2` from local `hif2`; a local HIF reference that has not been assigned to `dev->hif2` can be leaked if future changes add failures between lookup and assignment.
- Interrupt master switch writes are chip-specific for secondary PCIe; using the wrong register on MT7916-class devices would break HIF2 interrupts.

## Test Signals

Validation should include primary-only probe, dual-HIF probe with auxiliary devices appearing before and after primary, WED-enabled and WED-disabled probe, IRQ delivery on primary and secondary HIF, clean failure injection at BAR map, DMA mask, WED init, IRQ request, and register-device stages, module unload/reload, and remove while associated stations/traffic exist. Expected signals are proper firmware requests, one registered mac80211 device per primary, no leaked HIF device references, no stale HIF list entries, traffic on both bands when HIF2 is present, and clean WED detach or PCI vector free on failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7915/pci.c -->
