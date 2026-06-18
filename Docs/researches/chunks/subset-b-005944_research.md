# sources/distributed-fs/ceph-client/include/net/mac80211.h lines 6413-8135

## Scope

This chunk covers the final driver-facing helper/API section of `include/net/mac80211.h`, from the tail of the interface iteration helpers through the end of the header guard. The range is mostly declarations and small inline wrappers used by wireless drivers that integrate with the Linux `mac80211` subsystem. It does not contain the core implementations; instead it defines the public contracts, locking requirements, ownership rules, and callback sequencing that drivers must follow.

The chunk begins in the documentation for `ieee80211_iterate_active_interfaces()` and includes APIs for interface/station/key/channel-context iteration, mac80211 workqueue scheduling, TX/RX aggregation, station lookup and power-save signaling, airtime fairness and TXQ scheduling, connection-loss and channel-switch events, rate-control registration, capability helpers, P2P NoA parsing, TDLS/TID reservation, NAN notifications, MLO active-link handling, OMI bandwidth changes, and final compatibility/emulation helpers.

## Purpose

This section is the "driver services" surface of `mac80211.h`. It lets low-level WLAN drivers:

- Inspect mac80211-owned objects such as active interfaces, uploaded stations, keys, and channel contexts without directly walking private subsystem lists.
- Queue work safely onto the mac80211 workqueue.
- Start, stop, refresh, or notify completion of Block Ack aggregation sessions.
- Locate station objects under RCU and interact with station power-save/EOSP state.
- Report airtime usage, beacon/connection loss, CQM events, radar detection, channel-switch completion, WoWLAN wakeup, NAN events, and color collisions.
- Use mac80211 software TXQs, airtime scheduling, and rate-control infrastructure.
- Obtain management-frame templates for probe requests, FILS discovery, and unsolicited broadcast probe responses.
- Convert and query PHY/capability state for HT/HE/EHT/UHR, P2P interface types, and RX bandwidth.
- Coordinate newer MLO client-link transitions and RX OMI bandwidth sequencing.

The header records integration contracts rather than policy. Policy decisions such as association state, BA-session state machines, TXQ scheduling order, key storage, connection recovery, and active-link reconfiguration are implemented in mac80211 and cfg80211 code outside this header.

## Important APIs, Types, and Data

Interface iteration APIs include `ieee80211_iterate_active_interfaces()`, `ieee80211_iterate_active_interfaces_atomic()`, `__ieee80211_iterate_interfaces()`, `for_each_interface`, `for_each_active_interface`, and `ieee80211_iterate_active_interfaces_mtx()`. The inline active-interface wrapper adds `IEEE80211_IFACE_ITER_ACTIVE` before calling `ieee80211_iterate_interfaces()`. The mutex form uses `__ieee80211_iterate_interfaces()` and is only valid while holding the wiphy mutex; the atomic form requires a non-sleeping callback.

Station iteration mirrors the interface helpers with `ieee80211_iterate_stations_atomic()`, `__ieee80211_iterate_stations()`, `for_each_station`, and `ieee80211_iterate_stations_mtx()`. These only visit stations currently uploaded to the driver, making them suitable for driver state synchronization rather than arbitrary cfg80211 station enumeration.

Workqueue helpers `ieee80211_queue_work()` and `ieee80211_queue_delayed_work()` enqueue immediate or delayed work on the mac80211 workqueue and centralize checks that drivers are not queueing work in inappropriate states.

TX Block Ack helpers include `ieee80211_refresh_tx_agg_session_timer()`, `ieee80211_start_tx_ba_session()`, `ieee80211_start_tx_ba_cb_irqsafe()`, `ieee80211_stop_tx_ba_session()`, and `ieee80211_stop_tx_ba_cb_irqsafe()`. The public flow separates the driver request to start/stop aggregation from the irqsafe callback used when hardware preparation/teardown completes.

Station lookup and power-save APIs include `ieee80211_find_sta()`, `ieee80211_find_sta_by_ifaddr()`, `ieee80211_find_sta_by_link_addrs()`, `ieee80211_sta_block_awake()`, `ieee80211_sta_eosp()`, `ieee80211_send_eosp_nullfunc()`, and `ieee80211_sta_recalc_aggregates()`. The lookup functions are RCU-protected. `find_sta_by_ifaddr()` explicitly warns that passing `localaddr == NULL` can return an unreliable first match when multiple logical stations share a remote address. `find_sta_by_link_addrs()` extends lookup to MLO link addresses and can return the link ID.

Airtime and TXQ APIs include `ieee80211_sta_register_airtime()`, `ieee80211_txq_airtime_check()`, `ieee80211_tx_dequeue()`, `ieee80211_tx_dequeue_ni()`, `ieee80211_handle_wake_tx_queue()`, `ieee80211_next_txq()`, `ieee80211_txq_schedule_start()`, deprecated no-op `ieee80211_txq_schedule_end()`, `__ieee80211_schedule_txq()`, `ieee80211_schedule_txq()`, `ieee80211_return_txq()`, `ieee80211_txq_may_transmit()`, `ieee80211_txq_get_depth()`, `ieee80211_calc_rx_airtime()`, and `ieee80211_calc_tx_airtime()`. `ieee80211_tx_dequeue_ni()` is the inline process-context wrapper that disables/enables bottom halves around `ieee80211_tx_dequeue()`. `ieee80211_schedule_txq()` and `ieee80211_return_txq()` are force-aware wrappers around `__ieee80211_schedule_txq()`.

Key and channel-context iteration are exposed through `ieee80211_iter_keys()`, `ieee80211_iter_keys_rcu()`, `ieee80211_iter_chan_contexts_atomic()`, and `ieee80211_iter_chan_contexts_mtx()`. The key iterator can include keys known to mac80211 even if not currently programmed in the device, which matters during WoWLAN suspend/resume reprogramming. The channel-context iterators describe add/remove/restart visibility semantics.

Connection, channel, and regulatory/event notification APIs include `ieee80211_ap_probereq_get()`, `ieee80211_beacon_loss()`, `ieee80211_connection_loss()`, `ieee80211_disconnect()`, `ieee80211_resume_disconnect()`, `ieee80211_hw_restart_disconnect()`, `ieee80211_cqm_rssi_notify()`, `ieee80211_cqm_beacon_loss_notify()`, `ieee80211_radar_detected()`, `ieee80211_chswitch_done()`, `ieee80211_channel_switch_disconnect()`, `ieee80211_request_smps()`, `ieee80211_ready_on_channel()`, and `ieee80211_remain_on_channel_expired()`.

RX aggregation helpers include `ieee80211_stop_rx_ba_session()`, `ieee80211_mark_rx_ba_filtered_frames()`, `ieee80211_send_bar()`, `ieee80211_manage_rx_ba_offl()`, inline `ieee80211_start_rx_ba_session_offl()`, inline `ieee80211_stop_rx_ba_session_offl()`, and `ieee80211_rx_ba_timer_expired()`. The offload wrappers validate `tid < IEEE80211_NUM_TIDS`; the stop wrapper passes `tid + IEEE80211_NUM_TIDS` to the shared manager to encode stop versus start.

Rate-control types include `struct ieee80211_tx_rate_control`, `enum rate_control_capabilities`, and `struct rate_control_ops`. The rate-control struct packages hardware, band, BSS config, skb, reported rate, RTS/short-preamble flags, rate masks, and AP/IBSS indication for a rate algorithm. Capabilities include `RATE_CTRL_CAPA_VHT_EXT_NSS_BW` and `RATE_CTRL_CAPA_AMPDU_TRIGGER`. `struct rate_control_ops` defines allocation/free hooks, station-private lifecycle hooks, rate init/update/free, TX status reporting hooks, `get_rate`, debugfs hooks, and expected-throughput reporting.

Rate helper functions include `rate_supported()`, `rate_lowest_index()`, `rate_usable_index_exists()`, `rate_control_set_rates()`, `ieee80211_rate_control_register()`, and `ieee80211_rate_control_unregister()`. The inline helpers rely on `sta->deflink.supp_rates[band]` and supported-band bitrate tables, warning and returning index 0 if no usable rate exists.

Channel-width and interface-type helpers include `conf_is_ht20()`, `conf_is_ht40_minus()`, `conf_is_ht40_plus()`, `conf_is_ht40()`, `conf_is_ht()`, `ieee80211_iftype_p2p()`, `ieee80211_vif_type_p2p()`, `ieee80211_get_he_iftype_cap_vif()`, `ieee80211_get_he_6ghz_capa_vif()`, `ieee80211_get_eht_iftype_cap_vif()`, `ieee80211_get_uhr_iftype_cap_vif()`, and `ieee80211_chan_width_to_rx_bw()`. The P2P helpers map station/AP iftypes to P2P client/GO only when `p2p` is true. The HE/EHT/UHR helpers translate the VIF type before delegating to cfg80211 capability lookup functions.

Management/offload support APIs include `ieee80211_update_mu_groups()`, `ieee80211_enable_rssi_reports()`, `ieee80211_disable_rssi_reports()`, `ieee80211_ave_rssi()`, `ieee80211_calculate_rx_timestamp()`, `ieee80211_report_wowlan_wakeup()`, `ieee80211_tx_prepare_skb()`, `ieee80211_parse_tx_radiotap()`, `struct ieee80211_noa_data`, `ieee80211_parse_p2p_noa()`, `ieee80211_update_p2p_noa()`, `ieee80211_tdls_oper_request()`, `ieee80211_reserve_tid()`, and `ieee80211_unreserve_tid()`.

NAN and MLO-specific APIs include `ieee80211_nan_func_terminated()`, `ieee80211_nan_func_match()`, `ieee80211_nan_sched_update_done()`, `ieee80211_get_fils_discovery_tmpl()`, `ieee80211_get_unsol_bcast_probe_resp_tmpl()`, `ieee80211_obss_color_collision_notify()`, `ieee80211_set_active_links()`, `ieee80211_set_active_links_async()`, `ieee80211_send_teardown_neg_ttlm()`, `ieee80211_prepare_rx_omi_bw()`, and `ieee80211_finalize_rx_omi_bw()`.

Small terminal helpers include `ieee80211_is_tx_data()`, which treats hardware-encapsulated frames as data and otherwise checks the 802.11 frame-control field; older-driver channel-context emulation declarations `ieee80211_emulate_add_chanctx()`, `ieee80211_emulate_remove_chanctx()`, `ieee80211_emulate_change_chanctx()`, and `ieee80211_emulate_switch_vif_chanctx()`; `ieee80211_vif_nan_started()`; and `ieee80211_encrypt_tx_skb()`.

## Control Flow

Iteration flows are callback-driven. The sleeping interface iterator can include interfaces being added; the active variants do not iterate a new interface during `add_interface()`. Mutex-only macros perform repeated calls to the internal iterator with the previous object pointer. Atomic variants require callbacks that cannot sleep and are intended for contexts where normal locking would be unsafe.

TX aggregation flows start with a driver or mac80211 request through `ieee80211_start_tx_ba_session()`. mac80211 manages session state and AddBA negotiation, while drivers notify readiness from any context through `ieee80211_start_tx_ba_cb_irqsafe()`. Stop flows use `ieee80211_stop_tx_ba_session()` and `ieee80211_stop_tx_ba_cb_irqsafe()` similarly. Drivers can refresh session timers under RCU with `ieee80211_refresh_tx_agg_session_timer()`, but the session lifecycle remains mac80211-owned.

RX aggregation flows let drivers request teardown of open RX BA sessions, advance BA reorder state for firmware-filtered frames, send BAR frames to flush peer reorder buffers, and bridge partial offload devices into mac80211 reorder structures. The offload start/stop inline wrappers are deliberately thin validation and encoding layers over `ieee80211_manage_rx_ba_offl()`.

Power-save control depends on driver accounting of outstanding frames. If a device needs queued frames for a sleeping station to drain before mac80211 sends poll responses or post-wakeup frames, the driver calls `ieee80211_sta_block_awake()` while outstanding frames remain and unblocks when they reach zero. EOSP handling is split between TX status flags and explicit `ieee80211_sta_eosp()` calls; `ieee80211_send_eosp_nullfunc()` is an auxiliary path when the device needs mac80211 to transmit an EOSP Nullfunc/NDP.

TXQ scheduling follows a start/dequeue/return pattern. A driver starts a scheduling round with `ieee80211_txq_schedule_start()`, obtains eligible queues with `ieee80211_next_txq()`, dequeues frames through `ieee80211_tx_dequeue()` under RCU with softirqs disabled, and returns queues with `ieee80211_return_txq()`. Drivers that have their own buffered packets can force scheduling through `ieee80211_schedule_txq()` or the `force` argument to `ieee80211_return_txq()`. `ieee80211_txq_may_transmit()` provides an alternate airtime-fairness gate for drivers with their own round-robin list while also rotating mac80211's list to stay aligned.

Connection and channel event flows are driver notifications into mac80211/cfg80211. Beacon loss can trigger monitoring/recovery behavior when beacon filtering and power save are active. Connection loss forces immediate disassociation without recovery attempts. Resume and hardware-restart disconnect APIs defer disconnection to recovery paths. Channel switch completion tells mac80211 whether to adopt the new operational channel and wake queues; channel switch disconnect handles the case where blocked TX means a normal deauth frame should not be sent.

Rate-control flow is pluggable. A rate-control implementation registers `struct rate_control_ops`, allocates global and per-station private data, initializes or updates station rate state when capabilities/channel definitions change, receives TX status, chooses rates through `get_rate()`, and can push a station rate table back to mac80211/driver with `rate_control_set_rates()`.

MLO active-link switching has an explicitly documented callback sequence. For a client-mode link switch, mac80211 may first call `change_vif_links()` with the union of old and new links, unassign old channel contexts, assign new ones, temporarily update AP/STA link sets, remove and add group keys on the affected links, then finish with final `change_sta_links()` and `change_vif_links()` calls. `ieee80211_set_active_links_async()` schedules the same logical transition from any context but completion occurs later.

RX OMI bandwidth changes are two-phase. Drivers call `ieee80211_prepare_rx_omi_bw()` before sending OMI, then must call `ieee80211_finalize_rx_omi_bw()` if preparation returned true, including after hardware restart. Widening can happen during prepare, while narrowing is delayed until finalize to preserve peer signaling order.

## State and Persistence Behavior

This chunk primarily exposes transient kernel and firmware state mediated by mac80211. Interfaces, stations, keys, channel contexts, BA sessions, TXQs, and active links remain owned by mac80211; drivers receive pointers or callbacks with strict locking and lifetime rules rather than storing independent persistent copies.

RCU state is central for station lookup and TX dequeue. `ieee80211_find_sta*()` results are only valid inside the RCU read-side critical section. `ieee80211_tx_dequeue()` also requires RCU coverage that lasts until the dequeued SKB has been handled because fields in `skb->cb`, including key pointers, are RCU-protected.

Workqueue state is asynchronous. `ieee80211_queue_work()` and `ieee80211_queue_delayed_work()` persist pending work items on mac80211's workqueue until execution or cancellation by the usual kernel workqueue lifecycle. The header does not define cancellation semantics.

Aggregation state is mac80211-managed. Drivers may initiate or acknowledge BA session transitions, refresh timers, and signal RX reorder adjustments, but the session-level state machine and reorder buffers are not persisted by the driver-facing declarations here.

Power-save state combines mac80211's view of station sleep/wake state with driver-maintained outstanding-frame counts. Calling `ieee80211_sta_block_awake()` can force mac80211 to treat a station as asleep despite the actual peer state until the driver unblocks it. EOSP and buffered-frame signaling affect service-period closure and `more_data` correctness.

TXQ and airtime state is scheduler-owned and intentionally dynamic. Airtime registration updates fairness accounting. TXQ depth reads can be incoherent across frame and byte counts because queue state can change during the call. `ieee80211_txq_may_transmit()` can mutate scheduler rotation as a side effect.

Key iteration state is mac80211 key-store state, not necessarily hardware-programmed key state. This distinction matters for suspend/resume and WoWLAN where a driver may need to reprogram keys that are known to mac80211 but not currently in device tables.

MLO active-link state persists as vif `valid_links` and `active_links` state in mac80211 and is reflected into driver callbacks, channel-context assignments, station link membership, and group-key programming. The active link bitmap must be a subset of valid links and is client-mode only; AP mode treats all links as active.

Persistent device state is touched indirectly through WoWLAN wakeup reporting, resume disconnect decisions, hardware restart disconnects, radar/channel switch notifications, and firmware/NAN/offload events. The header does not define on-disk or NVM persistence, but several calls drive user-visible cfg80211 state that can survive beyond the immediate driver callback sequence.

## Dependencies and Integration Points

The declarations depend on core Linux kernel types and facilities: `struct sk_buff`, `struct work_struct`, `struct delayed_work`, `gfp_t`, RCU read-side locking, bottom-half control, `WARN_ON()`/`WARN_ON_ONCE()`, `BIT()`, endian/fixed-width integer types, debugfs dentries, and kernel networking device types.

The main subsystem dependencies are mac80211 and cfg80211/nl80211. Types such as `struct ieee80211_hw`, `struct ieee80211_vif`, `struct ieee80211_sta`, `struct ieee80211_link_sta`, `struct ieee80211_bss_conf`, `struct ieee80211_chanctx_conf`, `struct ieee80211_txq`, `struct ieee80211_key_conf`, `struct ieee80211_rx_status`, `struct ieee80211_tx_info`, `struct ieee80211_supported_band`, `struct ieee80211_p2p_noa_attr`, `struct cfg80211_wowlan_wakeup`, `struct cfg80211_nan_match_params`, and nl80211 enums tie drivers to the rest of the wireless stack.

Driver integration is mostly through callbacks in `struct ieee80211_ops`, even though the callback table is outside this chunk. Several comments reference contexts where calls are valid: `add_interface`, `bss_info_changed`, `sta_state`, `resume`, `wake_tx_queue`, channel-context callbacks, NAN schedule update, and MLO link-change callbacks. Drivers must observe these callback-specific constraints because many helpers call back into the driver or assume locks already held.

User-space integration is mediated through cfg80211/nl80211 events. RSSI CQM, beacon loss, TDLS operation requests, WoWLAN wakeups, NAN matches/termination, OBSS color collision, disconnects, channel switches, and radar detection can all become nl80211-visible state or events.

Hardware/firmware offload integration is explicit in APIs for beacon filtering, connection monitoring, HW crypto key reprogramming during WoWLAN, RX/TX BA offload, software TXQ offload, hardware encapsulation, NAN, FILS/unsolicited probe templates, MLO active-link offload, and OMI bandwidth management.

Rate control can be internal to mac80211 or supplied by modules through `ieee80211_rate_control_register()`. Integration with debugfs is optional through `add_debugfs` and `add_sta_debugfs`, while `get_expected_throughput()` feeds higher-layer reporting/scheduling decisions.

## Risks

Locking-context mismatches are the largest risk. Many APIs are only valid under RCU, with softirqs disabled, while holding the wiphy mutex, from a specific driver callback, or outside driver locks because the helper can call back into the driver. Calling the right helper from the wrong context can deadlock, sleep in atomic context, race object teardown, or corrupt scheduler state.

Pointer lifetime is subtle. Station lookup results and dequeued SKBs rely on RCU-protected embedded pointers. Iteration callbacks receive mac80211-owned objects whose validity depends on the iterator variant and locks held. Drivers should not cache these pointers beyond the documented lifetime unless a separate reference/lifetime contract exists elsewhere.

Address ambiguity can cause wrong-station behavior. `ieee80211_find_sta_by_ifaddr()` warns that `localaddr == NULL` may return the first matching remote address and is unreliable when multiple logical stations share a remote address. MLO adds additional link-address ambiguity unless `ieee80211_find_sta_by_link_addrs()` and link IDs are used correctly.

Aggregation sequencing mistakes can break throughput or reorder correctness. Drivers must distinguish request APIs from irqsafe completion callbacks, use valid TIDs, keep RX BA windows synchronized when firmware filters frames, and avoid starting/stopping offloaded reorder state without matching peer negotiation.

Power-save and EOSP handling can create dropped or stuck traffic. If a driver blocks a station awake and forgets to unblock, mac80211 can withhold frames indefinitely. If EOSP is reported both through TX status and `ieee80211_sta_eosp()`, or through mixed irqsafe/non-irqsafe paths, service-period accounting can become inconsistent. `ieee80211_send_eosp_nullfunc()` also depends on prior buffered-frame state so the `more_data` bit is correct.

TXQ scheduler misuse can harm fairness or crash. `ieee80211_tx_dequeue()` requires RCU and disabled softirqs; `ieee80211_tx_dequeue_ni()` is the safer process-context wrapper. Drivers must not run multiple TXQ scheduling rounds concurrently, must return TXQs after use, and must account for `ieee80211_txq_may_transmit()` mutating list order.

State-read APIs can be approximate. TXQ depth values are explicitly not coherent with each other. RSSI averages may return 0 when not applicable. Channel-context iteration sees removing and restarted contexts differently from newly adding contexts.

MLO active-link changes have high callback blast radius. Link switches can temporarily expose a union of old and new links, move channel contexts, update station links, and remove/add group keys. Drivers that assume a single atomic bitmap flip can mishandle queues, keys, or TDLS state.

OMI bandwidth changes are easy to leave half-applied. If `ieee80211_prepare_rx_omi_bw()` returns true, the driver must finalize even across restart paths. Narrowing and widening happen at different phases, and the driver must ensure no TDLS or other chanctx users conflict when reducing listen bandwidth.

Template ownership mistakes leak SKBs. Probe request, FILS discovery, and unsolicited broadcast probe response template APIs return SKBs that the driver is responsible for freeing.

## Test and Validation Signals

Compile validation should build all mac80211 drivers against this header with `W=1` and sparse/lockdep-friendly configurations to catch prototype drift, missing includes, endian/type issues, and misuse of inline helpers.

Locking validation should exercise RCU-protected station lookup, TX dequeue, wiphy-mutex-only iterators, atomic iterators, NAN schedule update, active-link changes, and OMI bandwidth changes under lockdep and KCSAN. Negative tests should confirm code paths avoid sleeping callbacks in atomic iterator contexts.

Interface/station/key/channel-context tests should create multiple VIFs and stations, include active and inactive interfaces, add/remove interfaces during iteration, remove stations during key iteration, and run hardware restart flows to verify documented iterator visibility.

Aggregation tests should cover TX BA start/stop success and failure, invalid TIDs, irqsafe callbacks from interrupt-like context, timer refresh under RCU, RX BA offload start/stop, RX BA timeout, filtered-frame bitmap advancement, BAR transmission, and `max_rx_aggregation_subframes <= 64` assumptions for filtered-frame windows.

Power-save tests should simulate sleeping stations with outstanding hardware queues, verify `ieee80211_sta_block_awake()` prevents premature poll responses, unblock after queues drain, confirm wake notifications occur, and validate EOSP accounting through both TX status and explicit `ieee80211_sta_eosp()` paths without mixing incompatible reporting modes.

TXQ and airtime tests should dequeue under both softirq and process-context wrappers, check that force scheduling works for driver-buffered packets, validate `ieee80211_txq_may_transmit()` fairness decisions and list rotation, verify `ieee80211_txq_airtime_check()` against AQL limits, and compare `ieee80211_sta_register_airtime()`/calculated airtime values against known frame/rate inputs.

Connection/channel event tests should cover beacon loss with beacon filtering and power save, connection loss with and without hardware connection monitor support, resume/hardware-restart disconnect paths, successful and failed channel switches, channel switch disconnect when TX is blocked, radar detection with MLO/non-MLO channel contexts, remain-on-channel ready/expired sequencing, and SMPS requests.

Rate-control tests should register/unregister a dummy `rate_control_ops`, allocate/free station private data, exercise init/update/status/get-rate callbacks, verify lowest-rate fallback warnings only happen for truly unsupported stations, and ensure `rate_control_set_rates()` propagates selected station tables to drivers that support them.

Capability helper tests should verify HT20/HT40 plus/minus/no-HT width classification, P2P station/AP mapping to client/GO, HE/EHT/UHR capability lookup by VIF type, 6 GHz capability selection, and channel-width-to-RX-bandwidth conversion including WARN coverage for invalid/default widths.

Management/offload tests should validate probe/FILS/unsolicited probe response template allocation/freeing, RX timestamp normalization at multiple MPDU offsets, radiotap parse failure/success with initialized `chandef`, P2P NoA parsing and update of next absent-state TSF, TDLS operation requests, and TID reserve/unreserve flushing plus alternate-TID redirection during `sta_state`.

NAN/MLO tests should cover NAN termination/match events outside hard IRQ, NAN schedule update under wiphy mutex, `ieee80211_vif_nan_started()` for NAN and non-NAN vifs, active-link bitmap subset validation, asynchronous active-link completion ordering, group-key movement across links, OBSS color collision notification by link, negotiated TTLM teardown, and RX OMI prepare/finalize after normal completion and hardware restart.

## Cross-Chunk Notes

This chunk starts mid-comment for `ieee80211_iterate_active_interfaces()`; the preceding lines define `enum ieee80211_interface_iteration_flags` and `ieee80211_iterate_interfaces()`, which are necessary context for the first inline wrapper. Earlier chunks of `mac80211.h` define the major structs, enums, flags, and `struct ieee80211_ops` callback table referenced throughout this range. The merge lane should combine this document with those earlier chunks for a complete per-file report.
