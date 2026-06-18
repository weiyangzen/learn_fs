# sources/distributed-fs/ceph-client/include/net/mac80211.h lines 1-6412

## Scope

This chunk covers the first 6,412 lines of the mac80211 low-level driver interface header. It is a public kernel header, not executable implementation code. The covered range defines the main contracts between mac80211 and wireless hardware drivers: frame metadata, BSS/VIF/STA state, channel contexts, crypto keys, hardware capability flags, driver callback operations, hardware allocation/registration APIs, RX/TX status APIs, beacon/template helpers, TKIP/key sequence helpers, queue control, scan completion notifications, and the beginning of interface iteration support.

The mapped range ends in the interface-iteration API documentation after declaring `ieee80211_iterate_interfaces()`. Later declarations in the same header are intentionally outside this chunk and should be reconciled by later chunk research.

## Purpose

`include/net/mac80211.h` is the core mac80211 driver ABI. It lets low-level WLAN drivers describe their device capabilities to mac80211, receive configuration and state-change callbacks from the stack, hand RX frames upward, accept TX frames downward, report TX completion, and request mac80211-generated management/control frame templates.

The header also defines important behavioral contracts:

- Drivers must not call most mac80211 APIs from hard IRQ context. Only the IRQ-safe RX/TX status helpers are explicitly allowed there.
- Frames passed between mac80211 and drivers generally start with an IEEE 802.11 header and exclude the FCS, except where hardware crypto, hardware fragmentation, or encapsulation/decapsulation offload changes that shape.
- mac80211 owns intermediate software TX queues and can either push frames through the `tx` callback or let drivers pull/schedule TXQs through `wake_tx_queue`/dequeue APIs declared in this and later header ranges.
- Driver-visible objects such as `ieee80211_hw`, `ieee80211_vif`, `ieee80211_bss_conf`, `ieee80211_sta`, `ieee80211_link_sta`, `ieee80211_txq`, and `ieee80211_key_conf` are long-lived state carriers with explicit lifetime, RCU, mutex, and callback sequencing rules.

## Important APIs, Types, and Data

The channel and BSS configuration model starts with `ieee80211_chan_req`, `ieee80211_chanctx_conf`, `ieee80211_vif_chanctx_switch`, and `ieee80211_bss_conf`. `ieee80211_chanctx_conf` is the driver-visible channel context, with operating/minimum/AP channel definitions, RX chain requirements, radar state, radio index, and driver-private storage. `ieee80211_bss_conf` is the dense per-link BSS state block: association/beacon timing, BSSID/link address, channel request, QoS/ERP/HT/VHT/HE/EHT/UHR flags, TWT, FTM responder, MBSSID, BSS color, FILS discovery, power envelopes, MLD link status, negotiated TTLM notification flags, and RCU-protected channel context pointers.

`enum ieee80211_bss_change` is the update bitmap used by `bss_info_changed()`, `link_info_changed()`, and `vif_cfg_changed()` paths. It includes association, beacon, beacon enable, QoS, PS, txpower, bandwidth, CQM, FTM, TWT, HE color/OBSS PD, FILS, unsolicited probe response, MLD valid links, TTLM, transmit power envelope, and NAN local schedule changes.

NAN support in this range is represented by `ieee80211_nan_channel`, `ieee80211_nan_peer_map`, `ieee80211_nan_peer_sched`, and `ieee80211_nan_sched_cfg`. These carry negotiated NAN channel requests, time-slot schedules, peer maps, availability blobs, and deferred schedule state.

TX metadata is centered on `ieee80211_tx_info`, stored in `skb->cb` and accessed through `IEEE80211_SKB_CB()`. Its flags distinguish control and status roles: ACK/status request, sequence assignment, no-ACK frames, PS filter clearing, A-MPDU membership, injected/internal frames, hardware encapsulation, off-channel TX, LDPC/STBC, EOSP, min-rate, no-fragment, and no-ack-transmitted status. The control union carries rate-control data, the VIF, hardware key, flags, and enqueue time; the status union carries attempted rates, ACK signal, A-MPDU lengths, airtime, antenna, and driver status data. `ieee80211_tx_rate` plus helper functions encode legacy/HT/VHT retry stages and VHT MCS/NSS packing.

RX metadata is centered on `ieee80211_rx_status`, stored in `skb->cb` and accessed through `IEEE80211_SKB_RXCB()`. It carries TSF/boottime/hardware timestamp data, frequency plus 500 kHz offset, band, signal and per-chain signal, rate index, NSS, encoding and bandwidth, HE/EHT/UHR RU/GI/DCM fields, A-MPDU reference, zero-length PSDU type, flags, and MLO link validity/link ID. `ieee80211_rx_status_to_khz()` converts the MHz plus half-MHz offset encoding.

The hardware/device configuration model is `ieee80211_conf`, `ieee80211_conf_flags`, `ieee80211_conf_changed`, `ieee80211_smps_mode`, `ieee80211_hw_flags`, and `ieee80211_hw`. `ieee80211_hw` stores the `wiphy`, private driver pointer, advertised feature flags, queue counts, rate-control limits, aggregate limits, radiotap capabilities, netdev feature defaults, U-APSD limits, NAN limits, pacing/airtime settings, MTU, and supported TX power levels. The inline helpers `ieee80211_hw_set()` and `ieee80211_hw_check()` manipulate/check feature flags.

`ieee80211_vif_cfg` and `ieee80211_vif` describe virtual interfaces. They hold interface type, association/IBSS/PS/AID state, SSID and ARP filter data, AP/MLD address, NAN local schedule, per-link BSS configs, valid/active/dormant/suspended MLO link bitmaps, negotiated TTLM maps, interface MAC address, P2P marker, queue IDs, TXQs, netdev/offload flags, debugfs pointers, probe/action registration flags, and driver-private storage. Inline helpers identify MLD VIFs, usable/active links, and mesh interfaces; RCU helper macros dereference per-link configs under the wiphy mutex or lockdep checks.

Key and crypto contracts are expressed by `ieee80211_key_flags`, `ieee80211_key_conf`, `ieee80211_key_seq`, and `set_key_cmd`. Drivers receive key setup/removal via `set_key()`, set `hw_key_idx` for hardware crypto, and may request software IV/MMIC/MMIE generation or tailroom/mic space reservation through flags. `ieee80211_key_seq` stores TKIP IV32/IV16, CCMP/CMAC/GMAC/GCMP PNs, or generic hardware sequence bytes. The range also declares TKIP phase-key helpers, PN add helpers, RX sequence get/set helpers, GTK rekey addition/notification, MIC failure accounting, and replay accounting.

Station state uses `ieee80211_sta_state`, `ieee80211_sta_rx_bandwidth`, `ieee80211_sta_rates`, `ieee80211_sta_txpwr`, `ieee80211_sta_aggregates`, `ieee80211_link_sta`, and `ieee80211_sta`. `ieee80211_sta` is RCU-managed and can represent an MLD station with multiple `ieee80211_link_sta` entries. It tracks AID, QoS/WME/U-APSD, rate table, TDLS/MFP/MLO/SPP/EPP properties, aggregate limits, active aggregate view, per-TID TXQs, NAN peer schedule, and driver-private storage. Lockdep/RCU macros guide safe per-link station access.

`ieee80211_txq` is the driver-visible intermediate TXQ identity: VIF, optional STA, TID, AC, and driver-private storage. This supports mac80211 software queueing and airtime scheduling while letting drivers retain per-queue private state.

`enum ieee80211_hw_flags` is one of the highest-impact declarations in the chunk. It advertises rate-control ownership, RX FCS inclusion, host broadcast PS buffering, signal units, spectrum management, A-MPDU, PS/dynamic PS, MFP, monitor behavior, software crypto control, fast-xmit, TX ACK status, connection monitoring, queue control, per-STA GTK, AP link PS, hardware TX A-MPDU setup, rate-control table support, P2P address behavior, beacon-only timing, HT/CCK aggregation handling, channel-context CSA, cloned skb support, single all-band scan, TDLS wider bandwidth, A-MSDU/A-MPDU support, beacon TX status, unique station address requirements, hardware reorder buffer, RSS, TX A-MSDU/frag-list/fragmentation, low-ACK reporting, TDLS buffer station, buffered MMPDU TXQ, VHT extended NSS BW, STA MMPDU TXQ, missing AMPDU length reporting, multi-BSSID support, encapsulation/decapsulation offload, monitor plus decap concurrency, BSS color collision detection, MLO multicast multi-link TX, puncturing restrictions, quiet CSA handling, strict spec behavior, and S1G NDP block-ack support.

`struct ieee80211_ops` is the main callback table from mac80211 to drivers. The covered callbacks include lifecycle (`start`, `stop`, suspend/resume, add/change/remove interface), configuration (`config`, BSS/VIF/link change, filter, multicast, queue params, TSF, antenna, bitrate mask, SAR, radar background, hardware timestamp), TX/RX/scan (`tx`, hw/scheduled/software scans, flush, TX pending, remain-on-channel, channel switch), key and power-save (`set_key`, TKIP update, rekey data, default WEP key, TIM, station PS notification, buffered-frame release), station lifecycle/statistics (`sta_add`, `sta_remove`, `sta_state`, `sta_pre_rcu_remove`, rate updates, station/link stats, per-station TX power, 4-address and decap offload), aggregation (`ampdu_action`, `can_aggregate_in_amsdu`), debug/test/ethtool hooks, IBSS/TDLS/NAN/PMSR/TWT support, netdev forwarding/TC offload, MLO link activation/change, TTLM negotiation, interface preallocation, and EML operation mode.

Allocation and registration APIs include `ieee80211_alloc_hw_nm()`, inline `ieee80211_alloc_hw()`, `ieee80211_register_hw()`, `ieee80211_unregister_hw()`, `ieee80211_free_hw()`, `ieee80211_restart_hw()`, `wiphy_to_ieee80211_hw()`, `wdev_to_ieee80211_vif()`, `ieee80211_vif_to_wdev()`, `SET_IEEE80211_DEV()`, and `SET_IEEE80211_PERM_ADDR()`.

Driver-to-mac80211 data path APIs in this range include `ieee80211_rx_list()`, `ieee80211_rx_napi()`, inline `ieee80211_rx()`, `ieee80211_rx_irqsafe()`, inline `ieee80211_rx_ni()`, `ieee80211_tx_status_skb()`, `ieee80211_tx_status_ext()`, inline `ieee80211_tx_status_noskb()`, inline `ieee80211_tx_status_ni()`, `ieee80211_tx_status_irqsafe()`, `ieee80211_free_txskb()`, and `ieee80211_purge_tx_queue()`. Queue control APIs include `ieee80211_wake_queue()`, `ieee80211_stop_queue()`, `ieee80211_queue_stopped()`, `ieee80211_stop_queues()`, and `ieee80211_wake_queues()`.

Template and timing helpers include beacon template APIs (`ieee80211_beacon_get_template()`, EMA variants, TIM variant, countdown update/set/check, CSA/color-change finish), probe response/request, PS-Poll, nullfunc, RTS/CTS-to-self frame generation, RTS/CTS duration helpers, generic frame duration calculation, and `ieee80211_get_buffered_bc()` for host-buffered broadcast/multicast after DTIM beacons.

LED and scan notification APIs include the conditional LED trigger name helpers, throughput LED trigger creation, `ieee80211_scan_completed()`, `ieee80211_sched_scan_results()`, and `ieee80211_sched_scan_stopped()`. The chunk ends with `ieee80211_interface_iteration_flags` and `ieee80211_iterate_interfaces()`.

## Control Flow

Driver initialization begins with `ieee80211_alloc_hw()` or `ieee80211_alloc_hw_nm()`. The driver fills `hw->wiphy` bands/capabilities, sets device and permanent address, sets hardware flags, private-data sizes, queue and aggregation limits, optional LED trigger data, and the `ieee80211_ops` table. It then calls `ieee80211_register_hw()`. Normal teardown is the reverse: unregister first, then free the hardware object.

Runtime interface lifecycle flows through callbacks. mac80211 calls `start()` before the first enabled netdev, `add_interface()` for each non-monitor interface, then configuration callbacks as association/channel/BSS/link state changes. On teardown it calls `remove_interface()` and eventually `stop()`. Drivers that support runtime type changes implement `change_interface()`. MLO-capable drivers additionally handle per-link BSS changes and `change_vif_links()`/`change_sta_links()` transitions.

TX flow is mac80211-to-driver. The stack fills `IEEE80211_SKB_CB(skb)` with `ieee80211_tx_info`, selects queues/rates/keys/flags, and invokes `ops->tx()` or wakes an intermediate TXQ through `wake_tx_queue()`. The driver must honor frame flags such as sequence assignment, no-ACK, off-channel, PS response, MLO link selection, encryption offload, aggregation, and EOSP. When transmission completes, the driver reports status with one of the TX status APIs, filling attempted rates, ACK status/signal, A-MPDU accounting, no-ack result, and timestamp data when relevant.

RX flow is driver-to-mac80211. The driver places `ieee80211_rx_status` in `skb->cb`, ensures the skb starts at an 802.11 header unless decap offload semantics apply, sets frequency/band/signal/rate/encoding/flags/link data, and calls the matching RX API for its context. The header explicitly forbids mixing IRQ-safe and non-IRQ-safe RX/status APIs for one hardware and requires serialization between RX and TX status paths.

Scan flow depends on driver offload. If `hw_scan()` is implemented, mac80211 passes an `ieee80211_scan_request` with cfg80211 request data and scan IEs. The driver either starts hardware scan and later calls `ieee80211_scan_completed()`, returns an error immediately, or returns 1 to request software scan fallback. Scheduled scan uses `sched_scan_start()`/`sched_scan_stop()` with driver notifications through `ieee80211_sched_scan_results()` and `ieee80211_sched_scan_stopped()`.

Crypto flow starts when mac80211 invokes `set_key()` with `SET_KEY` or `DISABLE_KEY`. For hardware crypto the driver accepts the key, assigns `hw_key_idx`, possibly sets required key flags, and later reports/deals with PN/IV behavior. TKIP hardware that needs RX phase-1 key updates implements `update_tkip_key()`. WoWLAN GTK rekey flows use `set_rekey_data()`, `ieee80211_gtk_rekey_add()`, `ieee80211_set_key_rx_seq()`, and `ieee80211_gtk_rekey_notify()` on resume.

AP power-save flow is split between mac80211-managed and driver-managed modes. Without `IEEE80211_HW_AP_LINK_PS`, mac80211 observes PM bits, stops transmissions to sleeping stations, calls `sta_notify()`, handles PS-Poll/U-APSD service periods, and asks drivers to release buffered frames. With `IEEE80211_HW_AP_LINK_PS`, the driver reports transitions and trigger frames through `ieee80211_sta_ps_transition()`, `ieee80211_sta_pspoll()`, and `ieee80211_sta_uapsd_trigger()`. Driver-buffered frames must be reflected via `ieee80211_sta_set_buffered()` so TIM bits remain correct.

Aggregation flow is driven by `ampdu_action()`. mac80211 requests RX/TX BA session start/stop/operational transitions with `ieee80211_ampdu_params`. Drivers must tolerate TX aggregation stop requests before the start has fully completed, and once TX aggregation is operational they must respect the peer reorder-buffer size when retransmitting lost subframes.

Channel and BSS changes flow through `config()`, channel-context callbacks, `assign_vif_chanctx()`, `switch_vif_chanctx()`, CSA callbacks, beacon template refreshes, and completion notifications such as CSA/color-change finish. The design lets one PHY host multiple virtual interfaces and links while hiding mac80211-internal channel context objects behind driver-visible config structures.

## State and Persistence Behavior

Most persistent state is owned by mac80211 or the driver/hardware, with this header defining the shared views and callback sequencing. `ieee80211_hw` persists for the registered PHY lifetime. Its private driver area and feature flags must be initialized before registration and remain stable enough for mac80211 to make capability decisions.

`ieee80211_vif` persists for an added virtual interface. Its `drv_priv` area is sized by `hw->vif_data_size`; its `link_conf[]` entries are RCU-protected and must be accessed through the provided helpers or under the appropriate mutex. `ieee80211_bss_conf` fields are mutable over the BSS/link lifetime and are synchronized to drivers by change bitmaps.

`ieee80211_sta` is RCU-managed and persists until station removal completes. The header warns that after `sta_remove()`/downward `sta_state()` removal callbacks return, drivers cannot safely use the pointer, even under RCU, unless they used `sta_pre_rcu_remove()` to clear their own references. Per-link station pointers are also RCU-protected.

Keys persist until mac80211 calls `set_key(DISABLE_KEY)` or reconfiguration removes them. The `ieee80211_key_conf` pointer is a stable cookie during that lifetime, but hardware crypto state and `hw_key_idx` are driver-owned. TX PN is atomic in `ieee80211_key_conf`; RX sequence state must not be read or written while RX processing can run concurrently.

TX skbs and RX skbs transfer ownership at API boundaries. After the driver calls RX or TX status/free APIs, mac80211 owns the skb. Queue stop/wake state is maintained through mac80211 queue APIs, not direct netdev queue calls.

Beacon, probe, PS-Poll, nullfunc, and RTS/CTS helper APIs allocate or fill transient templates. Returned skbs are usually driver-owned until freed or uploaded; mutable offsets mark fields drivers or firmware may update, such as TIM and countdown counters.

Hardware-restart state is explicit. If the driver calls `ieee80211_restart_hw()`, mac80211 assumes hardware is fully stopped/uninitialized and starts a reconfiguration sequence from `start()` onward. Drivers must clear or rebuild their own hardware state before calling it.

## Dependencies and Integration Points

This header depends heavily on cfg80211 and core kernel networking types. It includes or references `net/cfg80211.h`, `linux/ieee80211.h`, `linux/skbuff.h`, `net/codel.h`, `net/ieee80211_radiotap.h`, `struct wiphy`, `struct wireless_dev`, `struct cfg80211_*`, `struct sk_buff`, `struct net_device`, `struct net_device_path`, `struct napi_struct`, `struct station_info`, `struct survey_info`, `struct ethtool_stats`, RCU primitives, lockdep, debugfs, and optional PM/IPv6/testmode/LED configs.

The primary consumers are wireless drivers under the kernel tree that register with mac80211, plus mac80211 implementation files that fill or consume these public structures. Typical driver integration points include PCI/USB/SDIO WLAN drivers that allocate `ieee80211_hw`, define `ieee80211_ops`, set hardware capability flags, and use RX/TX/scan/status/template helpers in interrupt, NAPI, workqueue, and firmware-event paths.

cfg80211/nl80211 integration is pervasive. Interface types, bands, regulatory channel definitions, scan requests, scheduled scan requests, bitrate masks, SAR specs, PMSR/FTM/TWT/NAN data, WoWLAN data, TX power settings, and user-visible station/survey/ethtool statistics all cross the mac80211/cfg80211 boundary through these types.

The Linux networking stack integration appears through skb ownership, netdev feature flags, queue control, traffic-control offload (`net_setup_tc`), forwarding path fill, software queueing, CoDel time fields, pacing shift, checksumming/GSO feature masking, and multicast address filtering.

Security integration spans software crypto, hardware crypto offload, MFP, TKIP helpers, WoWLAN GTK rekeying, replay/MIC-failure accounting, and management-frame encryption policy. Drivers must coordinate their firmware key tables with mac80211 key lifetimes and cfg80211 cipher-suite advertisement.

Power-management integration includes WoWLAN suspend/resume callbacks, device wakeup toggling, powersave config flags, dynamic PS, U-APSD, AP client PS, beacon filtering, GTK rekey while suspended, and restart/reconfiguration flows.

Modern Wi-Fi feature integration includes HT/VHT/HE/EHT/UHR capabilities, MLO valid/active/dormant links, TTLM, EML operation mode, MBSSID/EMA beacons, BSS color changes, puncturing constraints, channel contexts, background radar, hardware timestamping for TM/FTM, NAN, TDLS channel switching, TWT, and encapsulation/decapsulation offload.

## Risks

Context misuse is a major risk. The header distinguishes callbacks and APIs that are atomic, sleepable, process-context, NAPI-context, BH-disabled, or IRQ-safe. Calling a sleepable path from atomic context, mixing IRQ-safe and non-IRQ-safe RX/TX status APIs for one hardware, or running RX concurrently with non-IRQ-safe TX status can trigger races, deadlocks, or corrupted mac80211 state.

Lifetime and RCU misuse are high risk. `ieee80211_sta`, per-link station data, per-link BSS config, and `tx_bss_conf`/`chanctx_conf` are protected by explicit RCU or mutex rules. Caching these pointers beyond the documented callback lifetime can become use-after-free during station removal, MLO link changes, interface removal, or hardware restart.

Capability flags must match actual hardware behavior. Setting flags such as hardware rate control, queue control, AP link PS, reorder buffer support, cloned skb support, encryption/decryption offload, decap monitor concurrency, MLO multicast multi-link TX, or quiet CSA without fully implementing the corresponding behavior can break correctness in paths mac80211 will no longer manage in software.

TX status accuracy affects rate control, powersave, aggregation, MLME, statistics, and station kickout. Missing ACK status, wrong rates/counts, incorrect A-MPDU lengths, bad EOSP/no-ack flags, or skipped status for frames that requested it can leave service periods stuck, mis-train rate control, or delay MLME state machines.

RX status accuracy affects radiotap, monitor mode, regulatory behavior, MLO routing, crypto/replay decisions, reordering, and user-visible signal/rate data. Wrong frequency/band/link ID, missing failed-FCS/PLCP flags, inconsistent encoding fields, or bad timestamp units can mislead mac80211 and userspace.

Crypto offload has strict ordering requirements. PTK replacement, IV generation, management-frame protection, RX PN sequence restoration, TKIP phase key updates, and WoWLAN GTK rekeying must avoid decrypting with stale keys, transmitting unencrypted frames, reusing PNs, or accepting replayed frames.

Power-save races are subtle. Sleeping stations can have frames in hardware, driver buffers, and mac80211 TXQs simultaneously. Drivers must report filtered frames correctly, set buffered TID state, release service-period frames with correct EOSP/MORE_DATA handling, and serialize station PS transition APIs.

MLO adds cross-link complexity. Link IDs are embedded in TX control, RX status, VIF state, BSS config, station links, keys, beacon helpers, channel switches, and TTLM/EML operations. Treating link 0 as universally equivalent to non-MLO behavior can misroute frames or apply state to the wrong link.

Template helpers require caller discipline. Drivers that offload beaconing must refresh templates when change flags indicate beacon, MBSSID/EMA, CSA, color, TIM, or link state changes. Mutable offsets are only offsets, not automatic updates by mac80211 after upload.

Queue-control mistakes can deadlock traffic. Drivers must use `ieee80211_stop_queue()`/`wake_queue()` APIs rather than netdev queue helpers, and queue IDs must match `hw->queues`, per-VIF AC queues, CAB queues, and off-channel queues when `IEEE80211_HW_QUEUE_CONTROL` is set.

## Test and Validation Signals

Compile validation should build mac80211 and representative drivers with `CONFIG_MAC80211`, `CONFIG_CFG80211`, `CONFIG_PM`, `CONFIG_MAC80211_DEBUGFS`, `CONFIG_MAC80211_LEDS`, `CONFIG_NL80211_TESTMODE`, IPv6, and MLO-capable code paths enabled. This catches callback signature drift, structure member mismatches, and conditional-compilation mistakes.

Registration tests should allocate/register/unregister hardware with different feature flag combinations, queue counts, private-data sizes, radiotap settings, band/rate tables, and netdev feature masks. Invalid combinations should be rejected or warned by mac80211 registration checks.

TX/RX data-path tests should exercise normal, NAPI, process-context, and IRQ-safe variants without mixing incompatible APIs. They should validate skb ownership, `skb->cb` layout, rate status reporting, ACK/no-ACK handling, A-MPDU accounting, RX frequency/link/status fields, monitor/radiotap output, and concurrent queue stop/wake behavior.

Power-save tests should cover STA powersave, AP client legacy PS, PS-Poll, U-APSD, driver-buffered TIDs, filtered TX retries, EOSP handling, TIM updates, broadcast/multicast DTIM buffering, beacon filtering, dynamic PS, and WoWLAN GTK rekey/resume.

Crypto tests should cover hardware and software fallback, `IEEE80211_HW_SW_CRYPTO_CONTROL`, PTK replacement, per-link keys, MFP management TX/RX, TKIP phase-key update, PN get/set around suspend, replay/MIC failure accounting, and GTK rekey addition/notification.

Aggregation tests should cover RX/TX BA start/stop, immediate and delayed TX aggregation start, stop-before-start-complete races, buffer-size limits, retransmission ordering, A-MSDU-in-A-MPDU limits, and station removal while sessions are active.

MLO tests should cover VIF link activation, dormant/suspended links, station link add/remove, per-link BSS changes, per-link keys, TX control MLO link selection, RX link reporting, channel switch per link, negotiated TTLM accept/reject/suggest flows, and EML operation mode updates.

Scan/off-channel tests should validate hardware scan completion on success, cancellation, and firmware error; scheduled scan result/stopped notifications; software scan start/complete notifications; remain-on-channel ready/expired/cancel flows; and off-channel TX flag handling.

Beacon/template tests should verify template contents and mutable offsets for normal AP, MLO AP, MBSSID/EMA, DTIM, CSA countdown, color change, probe response, PS-Poll, nullfunc/QoS NDP, RTS/CTS-to-self, duration helpers, and host-buffered broadcast/multicast retrieval after DTIM beacon generation.

Recovery tests should trigger `ieee80211_restart_hw()` while interfaces, stations, keys, channel contexts, scans, and queues exist. Expected signals are orderly callback replay, no stale driver-private pointers, skipped unsafe interface iteration only when requested, and no use-after-free across station/interface/link removal.

## Cross-Chunk Notes

This chunk intentionally covers only lines 1-6412 of `sources/distributed-fs/ceph-client/include/net/mac80211.h`. The header continues past this point with more helper APIs, notifications, TXQ helpers, mesh/ROC/CSA completion utilities, rate-control registration, and additional declarations. The merge/reconciliation lane should combine this document with later chunk documents into the final per-file report for `include/net/mac80211.h`.
