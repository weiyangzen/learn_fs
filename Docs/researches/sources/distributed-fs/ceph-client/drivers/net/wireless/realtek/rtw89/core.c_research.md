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
