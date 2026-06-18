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
