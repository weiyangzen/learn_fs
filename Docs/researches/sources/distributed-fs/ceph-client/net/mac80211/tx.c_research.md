# sources/distributed-fs/ceph-client/net/mac80211/tx.c

## Purpose

`tx.c` is the central mac80211 transmit implementation. It converts Ethernet frames into IEEE 802.11 frames, runs transmit handlers, handles software power-save buffering, key selection and software crypto, rate-control preparation, sequence and fragment generation, TXQ/FQ-CoDel scheduling, fast-xmit shortcuts, 802.3 hardware encapsulation offload, pending queue retry, beacon/template generation, and exported driver helper APIs for management/control frames.

The file is not Ceph-specific; in this source tree it is part of the Linux wireless client/server substrate that a Ceph client build carries. It is performance- and correctness-critical because it sits between netdev `ndo_start_xmit` entry points, cfg80211/mac80211 management operations, station state, keys, channel context, and low-level driver `drv_tx()`/TXQ pull APIs.

## Important APIs, Types, and Functions

The main transient state object is `struct ieee80211_tx_data`, populated by `ieee80211_tx_prepare()` and then consumed by handler chains. Per-packet state is stored in `struct ieee80211_tx_info` inside `skb->cb`, including flags, band, selected rates, hardware queue, vif pointer, hardware key pointer, MLO link selection, status-cookie metadata, and TXQ control flags. Persistent state lives in `struct ieee80211_local`, `struct ieee80211_sub_if_data`, `struct sta_info`, `struct ieee80211_link_data`, `struct ps_data`, `struct txq_info`, `struct ieee80211_key`, and beacon/probe/template data structures.

Transmit handlers are split into early and late phases. Early handlers include `ieee80211_tx_h_dynamic_ps()`, `ieee80211_tx_h_check_assoc()`, `ieee80211_tx_h_ps_buf()`, `ieee80211_tx_h_check_control_port_protocol()`, and `ieee80211_tx_h_select_key()`. Late handlers include rate control, Michael MIC insertion, sequence assignment, fragmentation, statistics, encryption, and duration calculation. `invoke_tx_handlers()` runs the full chain; `ieee80211_tx()` may stop after early handlers if the frame is queued into a software TXQ.

Important frame conversion and entry points are `ieee80211_subif_start_xmit()`, `__ieee80211_subif_start_xmit()`, `ieee80211_build_hdr()`, `ieee80211_xmit()`, and `ieee80211_monitor_start_xmit()`. Hardware 802.3 encapsulation uses `ieee80211_subif_start_xmit_8023()`, `ieee80211_8023_xmit()`, `ieee80211_tx_8023()`, and `__ieee80211_tx_8023()`.

TXQ support is implemented by `ieee80211_get_txq()`, `ieee80211_txq_enqueue()`, `ieee80211_tx_dequeue()`, `ieee80211_next_txq()`, `__ieee80211_schedule_txq()`, `ieee80211_txq_may_transmit()`, `ieee80211_txq_airtime_check()`, and `ieee80211_txq_schedule_start()`. Queue storage is backed by `struct fq`, per-TID `struct fq_tin`, per-flow CoDel variables, and `txqi->frags` for already-fragmented or management frames.

Fast transmit support is built by `ieee80211_check_fast_xmit()`, invalidated by `ieee80211_clear_fast_xmit()`, and consumed by `ieee80211_xmit_fast()` and `__ieee80211_xmit_fast()`. A-MSDU aggregation in this fast path is handled by `ieee80211_amsdu_prepare_head()` and `ieee80211_amsdu_aggregate()`.

Beacon and template APIs exported to drivers include `ieee80211_beacon_get_template()`, `ieee80211_beacon_get_template_ema_index()`, `ieee80211_beacon_get_template_ema_list()`, `ieee80211_beacon_free_ema_list()`, `ieee80211_beacon_get_tim()`, `ieee80211_proberesp_get()`, `ieee80211_get_fils_discovery_tmpl()`, `ieee80211_get_unsol_bcast_probe_resp_tmpl()`, `ieee80211_pspoll_get()`, `ieee80211_nullfunc_get()`, `ieee80211_probereq_get()`, `ieee80211_rts_get()`, `ieee80211_ctstoself_get()`, and `ieee80211_get_buffered_bc()`. Control and management helpers include `ieee80211_tx_control_port()`, `ieee80211_probe_mesh_link()`, `ieee80211_tx_skb_tid()`, `__ieee80211_tx_skb_tid_band()`, `ieee80211_reserve_tid()`, and `ieee80211_unreserve_tid()`.

## Control Flow

For ordinary 802.3 netdev transmit, `ieee80211_subif_start_xmit()` first handles multicast special cases. AP multicast-to-unicast conversion clones a multicast Ethernet frame per associated station when enabled and when the payload is ARP, IPv4, or IPv6. MLO AP multicast may be copied to active links with `IEEE80211_TX_CTRL_MLO_LINK` encoded in control flags when the driver cannot do multi-link multicast itself. Frames then enter `__ieee80211_subif_start_xmit()`.

`__ieee80211_subif_start_xmit()` validates the interface, updates socket pacing, optionally uses mesh fast-xmit, looks up the receiver station with `ieee80211_lookup_ra_sta()`, selects the queue, triggers aggregation setup checks, and tries station fast-xmit if a cached `sta->fast_tx` exists. If no fast path handles the frame, it fixes GSO/checksum/linearization limitations, loops over any software-generated segments, builds an IEEE 802.11 header with `ieee80211_build_hdr()`, updates netdev stats, and calls `ieee80211_xmit()`.

`ieee80211_build_hdr()` is the core 802.3-to-802.11 conversion routine. It constructs AP, AP_VLAN, station, TDLS, 4-address station, OCB, adhoc, mesh, and NAN DATA headers. It resolves MLO link source addresses, optional mesh addressing extensions, RFC1042 or bridge-tunnel encapsulation, QoS header insertion, authorization checks, TX-status cookie cloning, SKB sharing, headroom expansion, and initial `ieee80211_tx_info` fields. It rejects unicast data to unauthorized non-mesh/non-OCB stations unless it is allowed control-port traffic from the local station.

`ieee80211_xmit()` ensures encryption and hardware headroom, performs mesh next-hop resolution for unicast mesh data, sets QoS header fields, and enters `ieee80211_tx()`. `ieee80211_tx()` prepares `struct ieee80211_tx_data`, sets hardware queue information, invokes early handlers, optionally queues into TXQ, then invokes late handlers and sends fragments through `__ieee80211_tx()`. `__ieee80211_tx()` maps monitor/AP_VLAN special cases to the actual driver vif and calls `ieee80211_tx_frags()`, which either calls `drv_tx()` per fragment or splices frames onto `local->pending[]` if queues are stopped.

TXQ control flow splits early and late processing. When intermediate queues are enabled, `ieee80211_queue_skb()` selects a per-vif or per-station TXQ and enqueues the SKB into FQ/CoDel storage. Later, drivers call `ieee80211_tx_dequeue()` from softirq context. Dequeue checks AQL, hardware queue stop reasons, management-fragment queues, FQ-CoDel dequeue, authorization, fresh key selection, AMPDU flags, hardware encapsulation, fast-xmit finish, late handlers, fragment splicing, frag-list linearization, monitor/AP_VLAN vif mapping, and expected-airtime accounting before returning one SKB to the driver.

Monitor injection enters through `ieee80211_monitor_start_xmit()`. It validates and strips radiotap, may map a locally addressed injected frame onto a real interface, validates channel context and regulatory TX permission, selects queue priority, parses injection options with `ieee80211_parse_tx_radiotap()`, and sends via `ieee80211_xmit()`. The radiotap parser accepts FCS stripping, WEP/encryption override, fragmentation override, no-ack/no-sequence/order flags, antenna bitmap, data retries, legacy rate, MCS, and VHT rate fields.

The 802.3 offload path starts at `ieee80211_subif_start_xmit_8023()`. It requires a valid uploaded authorized station, skips control-port frames, chooses a hardware-uploaded non-TKIP key if present, and then `ieee80211_8023_xmit()` prepares `IEEE80211_TX_CTL_HW_80211_ENCAP` frames for driver transmission or TXQ enqueue. If aggregation is not operational or offload assumptions fail, it falls back to the normal 802.11 conversion path.

## State and Persistence Behavior

Power-save buffering persists in AP/mesh `ps_data.bc_buf`, per-station `sta->ps_tx_buf[ac]`, `ps->tim`, `ps->num_sta_ps`, `ps->dtim_count`, and `local->total_ps_buffered`. Unicast buffering is protected by `sta->ps_lock`; multicast buffering is released only after DTIM through `ieee80211_get_buffered_bc()`. `purge_old_ps_buffers()` bounds total buffered frames by dropping the oldest broadcast/multicast frame per AP/mesh interface and one low-priority frame per station.

Sequence state persists in `sdata->sequence_number`, `sta->tid_seq[tid]`, and `sdata->mld_mcast_seq`. QoS unicast frames get per-station/per-TID sequence numbers, multicast or non-QoS frames use interface sequence assignment, and AP MLD multicast follows the special MLO multicast sequence handling.

Key state is RCU-managed in station PTKs, default unicast keys, per-link multicast/management/beacon keys, and `info->control.hw_key`. `ieee80211_tx_h_select_key()` reselects keys after dequeue because queued packets may outlive key changes. Software encryption mutates SKBs in late handlers or in exported beacon/encrypt helper paths; fast-xmit only caches keys that are hardware-uploaded and not tainted.

TXQ state persists in `local->fq`, `local->cvars`, per-`txq_info` tins, CoDel stats, `txqi->frags`, active TXQ lists, per-AC schedule rounds, airtime deficits, AQL pending airtime, queue stop reasons, and `local->pending[]`. `ieee80211_txq_setup_flows()` initializes FQ-CoDel limits and codel parameters; `ieee80211_txq_teardown_flows()` and `ieee80211_txq_purge()` free queued SKBs and scheduling state.

Fast-xmit state persists as an RCU pointer `sta->fast_tx`. It caches a prebuilt 802.11 header, DA/SA offsets, header length including crypto IV space and RFC1042 header, selected band, PN offset, and hardware key. The cache is valid only while its out-of-band assumptions remain true: authorized uploaded station, no relevant power-save state, no no-ack map, compatible fragmentation settings, supported interface type, usable channel context, and hardware crypto conditions.

Beacon/template state is read through RCU from AP, IBSS, mesh, and link data. Runtime mutable fields include TIM bitmaps, DTIM counters, CSA/color-change countdown offsets and counters, S1G short-beacon counters, MBSSID/EMA element lists, and default beacon keys. Template generation sets `ieee80211_tx_info` fields for no-ack, assigned sequence, clear PS filter, band, selected link, and rate-control output.

## Dependencies and Integration Points

This file integrates with cfg80211/mac80211 public APIs, `net_device_ops` in `iface.c`, cfg80211 control-port callbacks in `cfg.c`, TDLS transmit helpers, mesh path resolution, rate-control operations, key management and cipher implementations in `wep.c`/`wpa.c`, station lifecycle in `sta_info`, channel context/bss configuration, LED throughput triggers, FQ-CoDel and Linux SKB/GSO/checksum APIs, regulatory checks, and low-level driver operations through `drv_tx()`, driver TXQ pull, and aggregation capability callbacks.

Driver-facing exports form a major contract: drivers can pull from TXQs with `ieee80211_tx_dequeue()`, schedule/fairness-manage TXQs with `ieee80211_next_txq()`, `__ieee80211_schedule_txq()`, `ieee80211_txq_may_transmit()`, and `ieee80211_txq_schedule_start()`, request beacon/probe/null/PS-Poll/RTS/CTS templates, encrypt a prepared SKB in software, and retrieve buffered broadcast/multicast frames after DTIM. These functions assume correct context: for example `ieee80211_tx_dequeue()` warns if not called from softirq context.

MLO integration appears throughout the path. The code carries link ID in `IEEE80211_TX_CTRL_MLO_LINK`, chooses link addresses for AP MLDs and TDLS links, handles MLD multicast sequence numbering and multi-link multicast cloning, treats MLD data as not relying on a single band in several paths, and fills beacon/template control flags with the link ID.

## Risks

The highest risks are concurrency, stale cached assumptions, and protocol corner cases. TX state crosses RCU, spin locks, bottom-half disabled sections, tasklets, driver callbacks, and queued SKBs that may be transmitted after station/key/channel state changes. Key selection must be repeated after TXQ dequeue to avoid using removed keys, and fast-xmit invalidation must be maintained whenever any cached assumption changes.

Power-save buffering can leak correctness if TIM bits, `total_ps_buffered`, `dtim_count`, or MoreData flags diverge from actual queued frames. Races around station wakeup are mitigated with `sta->ps_lock`, but changes in PS state while frames are being queued or delivered remain sensitive.

Fragmentation, rate control, and duration calculation are protocol-sensitive. Fragmented frames disable multi-rate retries after the first rate to avoid NAV inconsistencies. Duration calculation intentionally skips MCS/VHT and S1G because hardware is expected to handle them. Any future rate mode or PHY support must either keep that assumption or update duration handling.

Queueing risks include deadlocks from late handlers that must not generate frames while station locks may be held, incorrect ordering between pending queues and hardware queues, AQL starvation or over-admission, FQ-CoDel memory/backlog accounting errors during A-MSDU aggregation, and driver misuse of exported TXQ APIs from the wrong context.

Input validation risks include monitor injection radiotap parsing, regulatory/channel gating, insufficient SKB headroom/tailroom, unauthorized port handling, TDLS setup exceptions, MLO link ID mismatch, and control-port encryption flags. Beacon generation risks include countdown offset bounds, S1G TIM encoding, MBSSID/EMA element lengths, and beacon protection key taint or software/hardware crypto mismatch.

## Test Signals

Useful signals include successful and failed transmit through normal, fast-xmit, TXQ, and 802.3 offload paths; AP, AP_VLAN, station, TDLS, mesh, adhoc, OCB, NAN DATA, monitor injection, and MLO AP modes; control-port traffic with encrypted and unencrypted flags; multicast-to-unicast conversion; MLO multicast cloning; PS buffering and DTIM release; TIM bit recalculation; sequence numbering per TID and MLD multicast; fragmentation and no-fragment paths; software crypto for WEP/TKIP/CCMP/GCMP/BIP; key removal while frames are queued; A-MSDU aggregation limits; GSO/checksum fixups; queue stop/pending retry behavior; AQL/airtime fairness scheduling; codel drops; beacon/probe/FILS/unsolicited probe templates; S1G short/long beacon alternation; CSA/color countdown update; and lockdep/KCSAN/KASAN coverage under station/key/channel teardown during TX.

Concrete regression probes should include driver TXQ dequeue under stopped queues, `ieee80211_tx_dequeue()` softirq-context warnings, `ieee80211_get_buffered_bc()` only after DTIM, `ieee80211_reserve_tid()` queue stop/flush/BA teardown behavior, `ieee80211_tx_control_port()` link-address selection for MLO, radiotap injection with invalid lengths/rates, and fast-xmit invalidation when authorization, keys, power-save flags, fragmentation thresholds, or channel context change.
