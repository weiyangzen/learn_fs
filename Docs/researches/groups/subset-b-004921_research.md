# Research Report: subset-b-004921

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/coex.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/coex.h

## Purpose

`coex.h` is the public coexistence interface for the Realtek `rtw89` driver. It defines the WLAN/BT coexistence vocabulary shared by the core driver, firmware command path, radio calibration code, packet-notification logic, and debug/reporting paths. The header is intentionally state-heavy: most declarations are enums, register constants, bit masks, work periods, and small inline helpers that let other driver modules encode coexistence state into firmware-facing formats.

The file also declares the notification entry points implemented by the coexistence engine. Those functions let the rest of the driver report power transitions, scan state, band changes, special packets, role changes, radio/LPS state, WLAN RF calibration phases, station traffic state, BT C2H messages, and diagnostic dumps.

## Important APIs, Types, and Constants

The mode and RFK enums define the high-level coexistence state machine:

- `enum btc_mode` distinguishes normal, WLAN-only, BT-only, and WLAN-off operation.
- `enum btc_wl_rfk_type` names WLAN RF calibration operations (`IQK`, `LCK`, `DPK`, `TXGAPK`, `DACK`, `RXDCK`, `TSSI`, `CHLK`).
- `enum btc_wl_rfk_state` marks RFK start/stop and one-shot transitions.
- `BTC_RFK_PATH_MAP`, `BTC_RFK_PHY_MAP`, and `BTC_RFK_BAND_MAP` define the packed PHY/path/band encoding used by `rtw89_btc_phymap()`.

Packet and role notification types connect `core.c` TX/RX and mac80211 lifecycle events to BTC:

- `enum btc_pkt_type` covers DHCP, ARP, EAPOL start/end, ICMP, and sentinel `PACKET_MAX`.
- `enum btc_role_state` reports station/AP role starts, stops, type changes, association phases, and disconnects.
- `enum btc_rfctrl` and `enum btc_lps_state` map driver radio and low-power states to BTC decisions.

Hardware control enums and register constants model coexistence knobs:

- `enum btc_pri`, `enum btc_bt_trs`, `enum btc_bt_btg`, `enum btc_ant`, `enum btc_switch`, `enum btc_ant_div_pos`, and status enums encode antenna, priority, traffic, and BTG/pre-AGC control dimensions.
- `R_BTC_BB_BTG_RX`, `R_BTC_BB_PRE_AGC_S0/S1`, `B_BTC_BB_GNT_MUX`, and `B_BTC_BB_PRE_AGC_*` identify baseband fields used by coexistence status/control code.
- Zigbee/LTE/3CX and workaround feature bits are represented by `enum btc_3cx_type`, `enum btc_wa_type`, and `enum btc_chip_feature`.

The declared public functions are the integration surface:

- Lifecycle: `rtw89_btc_ntfy_poweron()`, `rtw89_btc_ntfy_poweroff()`, `rtw89_btc_ntfy_init()`, `rtw89_coex_power_on()`, `rtw89_coex_recognize_ver()`.
- Scan/channel/role: `rtw89_btc_ntfy_scan_start()`, `rtw89_btc_ntfy_scan_finish()`, `rtw89_btc_ntfy_switch_band()`, `rtw89_btc_ntfy_role_info()`.
- Packet notifications: `rtw89_btc_ntfy_specific_packet()` and the workqueue callbacks for EAPOL, ARP, DHCP, and ICMP.
- RF/LPS/calibration: `rtw89_btc_ntfy_radio_state()`, `rtw89_btc_ntfy_wl_rfk()`, `rtw89_btc_ntfy_conn_rfk()`, `rtw89_btc_ntfy_preserve_bt_time()`.
- Firmware/debug: `rtw89_btc_c2h_handle()`, `rtw89_btc_dump_info()`, `rtw89_btc_set_policy()`, `rtw89_btc_set_policy_v1()`, periodic work callbacks.

Inline helpers:

- `rtw89_btc_phymap()` packs RF path bits, PHY index bits, and current channel band from `rtw89_chan_get()` into the BTC RFK map.
- `rtw89_btc_path_phymap()` is a single-path wrapper.
- `rtw89_coex_query_bt_req_len()` returns `rtwdev->btc.bt_req_len`, currently ignoring `phy_idx`.
- `rtw89_get_antpath_type()` combines a PHY map and antenna-path type into a 16-bit style key.
- `_slot_set_le()`, `_slot_set()`, `_slot_set_dur()`, `_slot_set_type()`, and `_slot_set_tbl()` write firmware coexistence slot tables in little-endian format, selecting either `btc->dm.slot.v1` or `btc->dm.slot.v7` according to `btc->ver->fcxslots`.

## Control Flow

This header itself does not run a full state machine, but it defines the cross-module control flow:

1. Core lifecycle code powers MAC/HCI/PHY and calls BTC power/init/radio notifications.
2. mac80211 scan/channel/association paths report scan starts, scan completion, band switches, and role transitions.
3. TX code recognizes EAPOL, ARP, DHCP, and ICMP packets and queues the corresponding `wiphy_work` callbacks declared here.
4. RF calibration and dynamic-maintenance paths pass packed PHY/path/band maps into BTC notification APIs.
5. Coexistence policy code writes slot tables through the inline setters, which abstract firmware table version differences.

The slot setters are the most direct state mutation in the header. They require a valid `btc->ver` and a supported `fcxslots` value. Unsupported values silently leave the slot unchanged, which makes version recognition a prerequisite for correct policy programming.

## State and Persistence Behavior

There is no external persistence. Runtime state lives in `struct rtw89_dev`, especially `rtwdev->btc`, and in nested coexistence decision-management fields (`btc->dm.slot.*`, `btc->bt_req_len`, version metadata). Slot mutations persist only in driver memory until firmware H2C policy programming consumes them or the device is reinitialized.

RSSI state helpers (`BTC_RSSI_HIGH`, `BTC_RSSI_LOW`, `BTC_RSSI_CHANGE`) encode hysteresis-like state classes. They are pure macros but preserve an important convention: "stay" states count as high/low while only non-stay states count as a change.

## Dependencies and Integration Points

`coex.h` includes `core.h`, so it depends on core driver types such as `struct rtw89_dev`, `struct rtw89_btc`, channel contexts, PHY/path enums, and kernel bitfield helpers. It is consumed by `core.c`, PHY/RFK code, firmware C2H/H2C code, debugfs/reporting paths, and chip-specific coexistence policy implementations.

Major integration points:

- mac80211-facing core lifecycle and TX/RX code in `core.c`.
- Firmware command/event handling through `fw.h`/C2H callbacks.
- Channel context and multi-PHY state through `rtw89_chan_get()` and PHY index/path maps.
- Baseband/MAC register programming through constants defined here and used by coexistence implementation files.

## Risks and Edge Cases

- `rtw89_coex_query_bt_req_len()` ignores `phy_idx`; this is safe only while BT request length is device-global. Multi-PHY/MLO changes could need per-PHY request length.
- Slot setter helpers do not validate `sid` bounds. Callers must ensure the slot id is valid for the selected firmware coexistence slot version.
- Slot setter helpers silently do nothing for unexpected `btc->ver->fcxslots` values. Version-recognition failures can therefore degrade coexistence policy without an immediate local error.
- `rtw89_btc_phymap()` assumes `rtw89_chan_get()` returns a valid channel for the passed channel context and that `phy_idx`, path bits, and band type fit the declared masks.
- Because this header bridges firmware ABI versions (`fcxslots == 1` versus `7`), layout drift in the corresponding `struct rtw89_btc` slot definitions is high risk.

## Test Signals

Useful validation signals include:

- Build coverage for all BTC users after enum/API additions, especially sparse/endian warnings around slot table writes.
- Runtime BTC debug dumps from `rtw89_btc_dump_info()` showing recognized coexistence version and expected slot contents.
- Scan, association, RFK, LPS, and power-cycle tests with Bluetooth active to verify notification ordering.
- Packet-trigger tests for EAPOL/ARP/DHCP/ICMP confirming the work callbacks fire and policy changes are visible in debug logs.
- MLO/DBCC tests that exercise `rtw89_btc_phymap()` across PHY indices and bands.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/coex.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/core.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/core.c

## Purpose

`core.c` is the central mac80211-facing implementation for the Realtek `rtw89` wireless driver. It defines supported channels/rates/capabilities, converts cfg80211 channel definitions into hardware channel state, prepares TX descriptors, parses RX descriptors and PHY status reports, manages NAPI and TXQ scheduling, tracks traffic and beacon timing for power-save decisions, handles station/vif/link lifecycle, initializes chip and firmware-derived capabilities, and registers/unregisters the `ieee80211_hw` device.

The file is also the integration hub for chip-specific operations (`chip->ops`), HCI transport operations, firmware H2C/C2H flows, coexistence (`btc`) notifications, channel context management, power save, RF calibration, regulatory/SAR data, debugfs, WoWLAN, and MLO/MLSR support.

## Important APIs, Types, and Data

Static regulatory/radio definitions:

- `rtw89_channels_2ghz`, `rtw89_channels_5ghz`, and `rtw89_channels_6ghz` enumerate supported channels.
- `rtw89_bitrates` maps legacy hardware rate indexes to mac80211 bitrate values.
- `rtw89_sband_2ghz`, `rtw89_sband_5ghz`, and `rtw89_sband_6ghz` are duplicated and filled during registration.
- `rtw89_iface_combs` declares single-channel and MCC interface combinations.
- `rtw89_overlapping_6ghz` and `rtw89_get_6ghz_span()` map specific 6 GHz center frequencies to SAR/ACPI/antenna-gain subband spans.

Channel and RF setup APIs:

- `rtw89_get_default_chandef()` and `rtw89_get_channel_params()` translate cfg80211 channel definitions to `struct rtw89_chan`.
- `rtw89_set_channel()` recalculates entity mode, programs MAC/PHY channel state for one or two PHYs, updates TX power, notifies BTC of band changes, and triggers RFK when needed.
- `rtw89_chip_rfk_channel()` and pure-monitor helpers coordinate RF calibration with channel state and firmware-feature constraints.
- `rtw89_core_set_chip_txpwr()` applies chip TX power on active PHY entities.

TX path APIs:

- `rtw89_core_tx_write()` selects the designated vif/station link and delegates to `rtw89_core_tx_write_link()`.
- `rtw89_core_tx_update_desc_info()` classifies firmware, management, and data packets, fills `struct rtw89_tx_desc_info`, registers TX status waits, handles MLO MAC IDs, and invokes security/AMPDU/HTC/special-packet logic.
- `rtw89_h2c_tx()` sends firmware commands through the HCI command queue.
- `rtw89_core_tx_kick_off()` and `rtw89_core_tx_kick_off_and_wait()` ring transport queues and optionally wait for TX completion.
- `rtw89_core_fill_txdesc*()` and `rtw89_core_fill_txdesc_fwcmd*()` serialize descriptor fields for AX/BE and descriptor-generation variants.
- `rtw89_core_get_ch_dma*()` map queue selectors to HCI DMA channels.

RX path APIs:

- `rtw89_core_query_rxdesc()`, `_v2()`, and `_v3()` parse AX/BE RX descriptor layouts into `struct rtw89_rx_desc_info`.
- `rtw89_core_rx()` routes non-Wi-Fi reports to C2H/PPDU handlers and normal Wi-Fi packets to mac80211, with PPDU-status buffering when needed.
- `rtw89_core_rx_process_ppdu_sts()` parses MAC/PHY PPDU status, updates RSSI/SNR/EVM and per-station PHY status, then flushes pending SKBs with enriched radiotap/status data.
- `rtw89_core_update_rx_status()` converts hardware rates, bandwidth, GI/LTF, encryption flags, RSSI, scan frequency, and MAC time into `ieee80211_rx_status`.
- `rtw89_core_rx_to_mac80211()` finalizes stats/radiotap/frequency corrections and calls `ieee80211_rx_napi()`.

Work and lifecycle APIs:

- NAPI: `rtw89_core_napi_init()`, `rtw89_core_napi_start()`, `rtw89_core_napi_stop()`, `rtw89_core_napi_deinit()`.
- TXQ/BA: `rtw89_core_ba_work()`, `rtw89_core_txq_work()`, `rtw89_core_txq_schedule()`, `rtw89_core_set_tid_config()`, BA CAM acquire/release helpers.
- Remain-on-channel: `rtw89_roc_start()`, `rtw89_roc_end()`, `rtw89_roc_work()`.
- Periodic tracking: `rtw89_track_work()` and `rtw89_track_ps_work()` drive traffic stats, LPS entry, beacon tracking, RFK tracking, RA, CFO, antenna diversity, EDCCA, SAR, chanctx, rfkill, and MLO link decisions.
- Core lifecycle: `rtw89_core_init()`, `rtw89_core_deinit()`, `rtw89_core_start()`, `rtw89_core_stop()`, `rtw89_chip_info_setup()`, `rtw89_core_register()`, `rtw89_core_unregister()`, allocation/free helpers.

Station/vif/MLO APIs:

- `rtw89_init_vif()` and `rtw89_init_sta()` pre-populate per-link instances and MAC IDs.
- `rtw89_vif_set_link()`, `rtw89_vif_unset_link()`, `rtw89_sta_set_link()`, and `rtw89_sta_unset_link()` bind mac80211 link ids to available driver link instances.
- `rtw89_core_sta_link_add()`, `_assoc()`, `_disassoc()`, `_disconnect()`, and `_remove()` coordinate CAM entries, firmware role/join/CAM H2Cs, RFK, RA/BF setup, beacon filters, BTC role notifications, P2P retry limits, and regulatory 6 GHz recalculation.
- `rtw89_core_mlsr_switch()` changes active MLO links for MLSR mode after stopping queues and leaving LPS.

## Control Flow

Device setup flows from allocation to registration:

1. `rtw89_alloc_ieee80211_hw()` recognizes early firmware features, possibly replaces chanctx ops with mac80211 emulation, decides MLO support, allocates `ieee80211_hw`, and stores chip/variant/firmware state.
2. Bus probe code calls `rtw89_core_init()`, which initializes lists, work items, waits, queues, PPDU status queues, traffic stats, BTC packet work, firmware loading, SER/entity/SAR/antenna-gain state.
3. `rtw89_chip_info_setup()` powers MAC on, waits for firmware, recognizes firmware/features, parses efuse and PHY capability maps, sets RFE/TX power tables, derives power-save mode, then powers MAC off.
4. `rtw89_core_register()` configures wiphy/mac80211 capabilities, supported bands, regulatory state, rfkill polling, PHY DM data, and debugfs.
5. `rtw89_core_start()` performs MAC/PHY/HCI power-up, BTC power/init notifications, BB/RF init, dynamic-management init, PPDU/PHY report enables, HCI start, periodic tracking scheduling, late RFK, radio-state notification, firmware logging, BA CAM init, and TAS timer enable.

TX flow:

1. mac80211 dequeue or direct send reaches `rtw89_core_tx_write()`.
2. The designated station/vif link is selected; `rtw89_core_tx_write_link()` accumulates traffic stats, parses WoW AKM hints, fills descriptor info, possibly wakes firmware from low-power state, and writes the SKB to HCI.
3. Descriptor fill chooses management/data/firmware handling. Management frames get fixed rates, MAC IDs, high queue handling, optional hardware management encryption, and sequence behavior. Data frames get TID/qsel/DMA mapping, security CAM info, retry fallback rate, HE QoS HTC/BSR adjustment, special packet BTC notifications, AMPDU info, and LLC header length.
4. HCI-specific code later uses `rtw89_core_fill_txdesc*()` to serialize descriptor dwords for the chip generation.
5. TX queues are scheduled by `rtw89_core_txq_work()` over all ACs, bounded by reclaimable HCI resources and aggregation wait heuristics, then kicked.

RX flow:

1. HCI parses RX descriptors via the appropriate `rtw89_core_query_rxdesc*()` variant and calls `rtw89_core_rx()`.
2. C2H and PPDU-status packets are handled as reports. PPDU status is parsed into `rtw89_rx_phy_ppdu`, used to update station EWMA RSSI/SNR/EVM and to enrich queued SKBs.
3. Wi-Fi data/control/management packets get `ieee80211_rx_status` populated from descriptor fields. PPDU-filtered frames may wait in per-PHY queues until matching PPDU status arrives; other frames go directly to `ieee80211_rx_napi()`.
4. RX stats update device/vif counters, trigger-frame counters, beacon RSSI/statistics, 6 GHz probe offload cancellation, MLO link id status, RSSI offload, and traffic rate histograms.

Power, tracking, and coexistence flow:

1. Periodic traffic work computes EWMA throughput and traffic levels for the device and vifs.
2. If traffic level changes, HCI interrupt mitigation and BTC WLAN station notification are updated.
3. Beacon tracking uses received beacon TSF distributions to tune TBTT offset and timeout for LPS reliability.
4. LPS entry is gated by traffic, TDLS/off-channel state, beacon tracking readiness, and BTC LPS state.
5. RFK/PHY/RA/CFO/SAR/chanctx/rfkill/MLO periodic functions run only while not scanning and while tracking work is allowed.

## State and Persistence Behavior

Most state is in `struct rtw89_dev` and per-vif/per-station private data allocated behind mac80211 objects:

- Device flags track running, NAPI, low-power, WOWLAN, rfkill, and tracking restrictions.
- `rtwdev->stats`, `rtwvif->stats`, and `rtwvif->stats_ps` store rolling traffic counters and EWMAs that are reset every tracking interval.
- `rtwdev->phystat`, `ppdu_sts`, and per-station link EWMAs store transient RX signal, beacon, and PPDU correlation state.
- `rtwdev->mac_id_map`, BA CAM bitmaps/lists, vif/station link maps, and channel entity state persist for the lifetime of active interfaces/stations.
- Firmware/chip-derived state (`fw`, `hal`, `efuse`, `rfe_parms`, `ps_mode`) is established at probe/chip-info time and reused by registration/start paths.
- Workqueues and delayed work provide asynchronous persistence for tracking, TXQ reinvocation, BA retries, BTC packet notifications, ROC timeouts, scan cleanup, and firmware loading.

There is no durable on-disk persistence. Device state is rebuilt on probe, firmware recognition, interface creation, association, and channel context updates.

## Dependencies and Integration Points

Kernel/mac80211 dependencies include `ieee80211_hw`, `wiphy`, `cfg80211_chan_def`, `ieee80211_vif`, `ieee80211_sta`, `ieee80211_txq`, SKBs, NAPI, workqueues, RCU, atomics, completions, bitmaps, rfkill, DMI, and regulatory/SAR capabilities.

Internal rtw89 dependencies are broad:

- `cam.h` for address/BSSID/security/BA CAM allocation and H2C programming.
- `chan.h` for channel contexts, entity modes, MCC/DBCC/MLSR operations, and ROC channel setup.
- `coex.h` for BTC notifications and BT slot changes.
- `fw.h` for firmware recognition, H2C/C2H, scan/beacon/filter/offload commands, logging, and waits.
- `mac.h` for MAC power, channel prep/done, RX filters, retry limits, PPDU/PHY reports, BF, rfkill registers, XTAL SI, and queue flushing.
- `phy.h` for BB/RF init, RFK, DIG, RA, CFO, antenna diversity, EDCCA, UL TB, statistics, and power conversions.
- `ps.h` and `wow.h` for IPS/LPS and wake-on-wireless behavior.
- `sar.h`, `ser.h`, `txrx.h`, `util.h`, `reg.h`, and chip-specific `chip->ops`/`mac_def`.

External integration is through exported symbols used by bus/HCI-specific modules and chip modules, including descriptor fill/query functions, NAPI functions, core init/register/start/stop, chip info setup, allocation/free, TX DMA mapping, and RX/TX entry points.

## Risks and Edge Cases

- RX descriptor variants are tightly coupled to chip generation and layout. A wrong query function can corrupt packet size, offsets, MAC ID, security flags, or PPDU correlation.
- `rtw89_core_rx()` buffers PPDU-filtered SKBs until PPDU status arrives or PPDU count changes. Mismatched counts or missing PPDU reports can delay status enrichment and require flush fallback.
- PN/SN validation in `rtw89_core_skb_pn_valid()` applies only to AX QoS data with hardware decryption and active TID stats. Incorrect assumptions here can drop valid frames or permit reorder anomalies.
- TX descriptor fields depend on vif/station link selection, MLO mode, address CAM validity, security CAM presence, and firmware/chip capabilities. Missing links return `-ENOLINK`; missing security CAM entries only warn and continue with unencrypted descriptor state.
- `rtw89_core_tx_update_he_qos_htc()` mutates SKB headers with `skb_push()` and `memmove()` when there is enough headroom. Callers rely on `extra_tx_headroom` registration to make this safe.
- BTC packet notification inspects `skb->protocol`, `ip_hdr()`, and `udp_hdr()`. It assumes the SKB protocol/header metadata is valid for the transmitted 802.11 frame.
- Work cancellation ordering in `rtw89_core_stop()` is critical. Late C2H, BTC packet work, TX waits, or delayed tracking work can race with HCI/MAC teardown if new work is queued after flags clear.
- BA CAM fallback replaces an existing non-0/non-5 TID entry when resources are full for TID 0 or 5. This policy is intentional but can surprise aggregation behavior under heavy TID usage.
- MLO support is conditionally enabled from early firmware features, channel context support, AP info notification, and `RTW89_MLD_NON_STA_LINK_NUM == 1`. Changes to softAP MLO support require revisiting allocation sizes, AP link PS, and link scheduling assumptions.
- Beacon tracking divides by DTIM/beacon parameters; association code defaults missing beacon interval to 100 TU but trusts DTIM from mac80211.
- `rtw89_core_rfkill_get()` interprets a masked read as inverted blocked state. Board-specific rfkill register definitions must be accurate.

## Test Signals

High-value test signals:

- Compile and sparse/endian checks across AX and BE chip builds, especially descriptor fill/query and little-endian bitfield use.
- Probe/register/remove tests verifying `rtw89_alloc_ieee80211_hw()`, `rtw89_core_init()`, `rtw89_chip_info_setup()`, `rtw89_core_register()`, `rtw89_core_start()`, stop, unregister, deinit, and free ordering.
- Association/disassociation tests for station, AP, P2P, TDLS, monitor, MLO/MLSR, MCC, and DBCC paths, with CAM/H2C failures injected.
- TX tests for management, data, EAPOL, ARP, DHCP, ICMP, injected frames, encrypted frames, AMPDU start/stop, TID config, nullfunc wait timeouts, and H2C resource exhaustion.
- RX tests for AX/BE descriptor variants, PPDU status matching, monitor radiotap HE/EHT TLVs, scan frequency correction, MCC channel correction, CCK correction, hardware decrypt flags, CRC/ICV errors, and PN/SN drop behavior.
- Power-save tests covering module parameter `disable_ps_mode`, firmware `NO_DEEP_PS`/`NO_LPS_PG`, LPS entry under low traffic, beacon tracking readiness, ROC/scan transitions, and firmware TX wake behavior.
- Coexistence tests verifying BTC power/radio/scan/band/role/special-packet notifications are generated in expected order.
- Stress tests with concurrent scan, ROC, TXQ scheduling, NAPI RX, station removal, and core stop to expose workqueue and RCU lifetime issues.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtw89/core.c -->
