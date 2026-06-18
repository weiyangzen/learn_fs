# subset-b-004843 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/libertas_tf.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/libertas_tf.h

## Purpose
This header is the shared contract for the Libertas thin firmware driver library. It defines the firmware command IDs, command result convention, packet descriptor layouts, command payload structures, bus callback interface, and the central `struct lbtf_private` state used by `main.c`, `cmd.c`, and USB glue code.

## Important APIs, Types, And Functions
Key constants include command numbers such as `CMD_GET_HW_SPEC`, `CMD_MAC_CONTROL`, `CMD_802_11_RADIO_CONTROL`, beacon commands, and `CMD_RET(cmd)` for firmware responses. `enum mv_ms_type` classifies host-to-card payloads as data, command, txdone, or event. `enum lbtf_mode` maps firmware operating modes to passive, station, and AP behavior.

`struct lbtf_ops` is the bus abstraction: `hw_host_to_card`, `hw_prog_firmware`, and `hw_reset_device` are supplied by interface drivers such as USB. `struct lbtf_private` is the driver object backing `ieee80211_hw`; it stores bus state, command queues, locks, timers, tx skbs, mac80211 vif pointer, radio/channel state, multicast list, supported channels/rates, and current noise.

Firmware ABI structures are packed and endian annotated: `txpd`, `rxpd`, `cmd_header`, `cmd_ctrl_node`, and `cmd_ds_*` payloads for hardware spec, MAC control, multicast, mode, BSSID, radio, channel, reset, boot2 version, and beacon control/set. The command helper macro `lbtf_cmd()` temporarily normalizes `hdr.size` to the command struct size while passing the original copyback size into `__lbtf_cmd()`.

## Control Flow
The header does not execute logic, but it shapes command flow: callers allocate `cmd_ctrl_node` instances, fill a packed command payload, enqueue via `__lbtf_cmd()` or `lbtf_cmd_async()`, then receive completion through callbacks or wait queues. Data flow is similarly defined: mac80211 packets are prefixed with `txpd`; firmware RX buffers start with `rxpd`.

## State And Persistence
All state is in memory. Persistent hardware state is firmware-owned and is driven by commands. `struct lbtf_private` is volatile per-card state and contains concurrency-sensitive fields protected by `mutex lock`, `spinlock_t driver_lock`, command timers, and list heads. No on-disk persistence exists.

## Dependencies And Integration Points
The header depends on Linux kernel locking, device, kthread, and mac80211 headers plus local debug definitions. It integrates bus-specific modules through `struct lbtf_ops`, command implementation through exported prototypes, and mac80211 through `struct ieee80211_hw`, `struct ieee80211_vif`, channels, rates, and skbs.

## Risks
The packed firmware ABI is sensitive to structure size, alignment, and endian mistakes. `struct lbtf_private` centralizes many ownership domains, so changes to command, tx, or vif fields can create locking regressions. The `lbtf_cmd()` macro mutates `hdr.size` before dispatch, which is subtle and easy to misuse with incorrectly initialized command buffers.

## Test Signals
Useful validation includes building with sparse/endian checks, loading the USB thinfirm module, verifying firmware download and `CMD_GET_HW_SPEC`, exercising station/AP interface add/remove, changing channel/radio state, transmitting data and beacons, and checking command timeout/retry behavior under injected bus failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/libertas_tf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/main.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/main.c

## Purpose
`main.c` is the core Libertas thin firmware mac80211 driver library. It owns module lifetime, shared workqueue creation, adapter initialization, mac80211 operation callbacks, firmware programming handoff, tx/rx conversion between firmware descriptors and mac80211 skbs, command timeout retry work, and exported card add/remove APIs used by interface drivers.

## Important APIs, Types, And Functions
The exported surface is `lbtf_add_card()`, `lbtf_remove_card()`, `lbtf_rx()`, `lbtf_send_tx_feedback()`, and `lbtf_bcn_sent()`. Internal mac80211 callbacks include `lbtf_op_tx`, `lbtf_op_start`, `lbtf_op_stop`, `lbtf_op_add_interface`, `lbtf_op_remove_interface`, `lbtf_op_config`, multicast/filter handlers, `lbtf_op_bss_info_changed`, and `lbtf_op_get_survey`.

`lbtf_cmd_work()` processes command responses and timeout-driven retries, while `command_timer_fn()` marks the active command timed out and queues command work. `lbtf_tx_work()` selects either buffered broadcast/multicast AP power-save frames or a normal queued skb, prepends `txpd`, programs per-packet rate, and calls `ops->hw_host_to_card()`.

## Control Flow
Module init allocates `lbtf_wq`; module exit destroys it. A bus driver calls `lbtf_add_card()`, which allocates `ieee80211_hw`, initializes command queues/timer/locks, sets 2.4 GHz channel and rate tables, registers supported bands, initializes work items, calls `hw_prog_firmware()`, reads hardware spec, validates firmware version, turns the radio off, and registers with mac80211.

Mac80211 tx stores one skb in `priv->skb_to_tx`, queues tx work, and stops queues until firmware tx feedback arrives. Firmware tx feedback clears status, reports ACK when appropriate, strips `txpd`, calls `ieee80211_tx_status_irqsafe()`, and wakes or continues queues. RX starts with `rxpd`, builds `ieee80211_rx_status`, adjusts for Marvell rate numbering, conditionally adds padding for QoS/A4/A-MSDU headers, and calls `ieee80211_rx_irqsafe()`.

Interface add switches firmware mode to AP/mesh or STA and sets the MAC address. BSS info changes push beacons, BSSID, and preamble changes to firmware. Stop drains pending commands, cancels work, flushes buffered broadcast frames, and turns radio off.

## State And Persistence
The module stores global debug state and workqueue pointer. Per-card state is in `lbtf_private`: current vif, `skb_to_tx`, in-flight `tx_skb`, command queues, firmware version, channel/frequency, radio state, multicast list, beacon PS buffer, and noise. State is volatile and re-derived on probe; firmware settings persist only while device firmware remains running.

## Dependencies And Integration Points
The file integrates with mac80211 (`ieee80211_ops`, queues, beacon helpers, survey reporting), Linux workqueues/timers/skbs, and bus-specific callbacks. It calls command-layer helpers declared in `libertas_tf.h`, including radio, MAC, multicast, mode, BSSID, beacon, channel, and hardware-spec commands.

## Risks
`lbtf_tx_work()` assumes `priv->vif` is valid when work runs; lifecycle ordering around interface removal and queued tx work is important. Single pending `skb_to_tx`/`tx_skb` state constrains concurrency and can fail badly if queue stop/wake sequencing regresses. Command timeout retry logic resubmits at the head of the pending queue and must preserve list ownership under `driver_lock`. RX padding manipulation uses `memmove`/`skb_reserve` and is sensitive to skb headroom.

## Test Signals
Signals include successful module load/unload, firmware version acceptance, mac80211 hardware registration, station association, AP/mesh beacon update, multicast filter programming, channel changes, tx feedback queue wakeups, RX signal/noise reporting, survey noise reads, and command timeout retries under mocked or unplugged hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/libertas_tf/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11ac.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11ac.c

## Purpose
`11ac.c` implements mwifiex 802.11ac/VHT support. It negotiates VHT capability and MCS maps, appends VHT association TLVs, prepares firmware 11ac configuration commands, chooses BlockAck defaults for 11ac operation, detects whether the current BSS is in VHT mode, and computes center-frequency indices for supported 5 GHz VHT channel groups.

## Important APIs, Types, And Functions
`mwifiex_fill_vht_cap_tlv()` merges user/device VHT MCS support with the peer/AP MCS maps and updates highest RX/TX rates. `mwifiex_cmd_append_11ac_tlv()` appends VHT capability, VHT operation, and operating mode notification IEs into a command buffer. `mwifiex_cmd_11ac_cfg()` serializes `mwifiex_11ac_vht_cfg` into `HostCmd_CMD_11AC_CFG`. `mwifiex_set_11ac_ba_params()` applies 11ac-specific AMPDU window sizes. `mwifiex_is_bss_in_11ac_mode()` and `mwifiex_get_center_freq_index()` provide current-BSS and channel helper logic.

## Control Flow
Association command construction calls `mwifiex_cmd_append_11ac_tlv()` after scan/join code has populated VHT pointers in `mwifiex_bssdescriptor`. If AP VHT capability is present, the code copies the AP IE into an mwifiex TLV, then clamps each NSS MCS field to the minimum of user/device support and AP support. Highest rates are computed from static 80 MHz and 160 MHz long-GI tables. If a VHT operation IE is present for STA mode, the requested channel width is capped to the user/device supported width while keeping the peer's center-channel suggestion. Operating mode notification is copied when advertised.

## State And Persistence
The code reads persistent adapter configuration fields such as `usr_dot_11ac_dev_cap_a`, `usr_dot_11ac_dev_cap_bg`, and `usr_dot_11ac_mcs_support`, but does not persist data itself. `mwifiex_set_11ac_ba_params()` mutates `priv->add_ba_param` for the active interface role. VHT state is otherwise represented in transient command buffers and current BSS descriptors.

## Dependencies And Integration Points
It depends on cfg80211/mac80211 VHT structures and constants, mwifiex firmware command structures from `fw.h`, adapter/private state from `main.h`, and local bitfield macros such as `GET_VHTNSSMCS`, `SET_VHTNSSMCS`, and `GET_VHTCAP_CHWDSET`. It integrates with join path TLV assembly, firmware 11ac configuration, BA setup defaults, and channel selection.

## Risks
The static max-rate tables assume valid MCS indices; fallback only handles zero entries for unsupported MCS9 combinations. Buffer advancement in `mwifiex_cmd_append_11ac_tlv()` assumes caller-provided space is sufficient. Channel center-index logic handles a fixed subset of 5 GHz VHT groups and defaults unknown AAC primary channels to 42, which could mask unsupported channel inputs.

## Test Signals
Tests should cover joining VHT APs with different NSS/MCS maps, 80/160/80+80 channel width advertisements, 2.4 GHz VHT configuration paths, operating mode notification copying, firmware 11ac config command bytes, BA window changes for STA versus uAP, and center-index results for every switch case.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11ac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11ac.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11ac.h

## Purpose
`11ac.h` is the public local header for mwifiex VHT support. It exposes configuration bits, default VHT MCS values, and function prototypes used by join, command, and capability code.

## Important APIs, Types, And Functions
The header defines `VHT_CFG_2GHZ`, `VHT_CFG_5GHZ`, `DEFAULT_VHT_MCS_SET`, `DISABLE_VHT_MCS_SET`, and `VHT_BW_80_160_80P80`. `enum vht_cfg_misc_config` describes firmware VHT operation modes: TX operation, association, and uAP-only configuration. Prototypes expose `mwifiex_cmd_append_11ac_tlv()`, `mwifiex_cmd_11ac_cfg()`, and `mwifiex_fill_vht_cap_tlv()`.

## Control Flow
The header enables other mwifiex modules to request VHT TLV construction and firmware configuration. It does not contain executable control flow beyond declaration-level coupling.

## State And Persistence
No state is stored here. The macros encode firmware/user configuration choices that are applied to adapter state or command buffers by `11ac.c` and callers.

## Dependencies And Integration Points
It depends on `struct mwifiex_private`, `struct mwifiex_bssdescriptor`, `struct host_cmd_ds_command`, `struct mwifiex_11ac_vht_cfg`, and `struct ieee80211_vht_cap` being declared through including translation units. It is included by `11ac.c` and used by mwifiex join/command paths.

## Risks
The header intentionally keeps only a small surface, so risks are mostly semantic: changes to constants must remain aligned with firmware interpretation and `11ac.c` bitfield handling. Prototype changes can affect several mwifiex modules.

## Test Signals
Build coverage across full mwifiex with `__CHECK_ENDIAN` is the primary signal. Functional signals come from 11ac association and firmware config paths that call these declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11ac.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11h.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11h.c

## Purpose
`11h.c` implements mwifiex 802.11h spectrum management and DFS/CAC handling. It activates firmware 11h mode, appends power/channel capability TLVs during joins, issues radar channel report commands, handles CAC completion/abort/radar events, and completes AP channel-switch work.

## Important APIs, Types, And Functions
`mwifiex_init_11h_params()` initializes per-interface 11h flags. `mwifiex_is_11h_active()` reports active state. `mwifiex_11h_process_join()` enables/disables firmware 11h and appends join TLVs through `mwifiex_11h_process_infra_join()`. `mwifiex_11h_activate()` sends `HostCmd_CMD_802_11_SNMP_MIB` for `DOT11H_I` and adds `MWIFIEX_MASTER_RADAR_DET_MASK` for uAP radar detection.

DFS helpers include `mwifiex_cmd_issue_chan_report_request()`, `mwifiex_stop_radar_detection()`, `mwifiex_abort_cac()`, `mwifiex_dfs_cac_work_queue()`, `mwifiex_11h_handle_chanrpt_ready()`, `mwifiex_11h_handle_radar_detected()`, and `mwifiex_dfs_chan_sw_work_queue()`.

## Control Flow
On infrastructure join, if the scanned BSS advertises 11h, the driver enables firmware 11h, marks it active, sets the spectrum management capability bit, and appends power capability, local power constraint, and supported-channel passthrough IE data based on wiphy band channels. If not sensed, it disables firmware 11h and clears the capability bit.

For DFS, cfg80211-triggered CAC issues a channel report request with channel number, width, and dwell time. A delayed work item emits `NL80211_RADAR_CAC_FINISHED` when CAC completes without radar. Abort sends a zero-dwell stop request, cancels delayed work, and emits `NL80211_RADAR_CAC_ABORTED`. Firmware channel report events parse TLVs for radar map bits and emit `NL80211_RADAR_DETECTED`; direct radar events call `cfg80211_radar_event()`. Channel-switch delayed work updates uAP config, restarts AP, and notifies cfg80211.

## State And Persistence
State lives in `priv->state_11h`, `priv->dfs_chandef`, `priv->wdev.links[0].cac_started`, delayed work items, and `priv->bss_cfg`. It is runtime-only and synchronized through cfg80211 work/event ordering rather than on-disk persistence.

## Dependencies And Integration Points
The file depends on cfg80211 radar/CAC APIs, wiphy channel tables, mwifiex command dispatch, uAP configuration/start helpers, firmware channel report event structures, and adapter debug logging. It bridges firmware radar detection to Linux regulatory/cfg80211 behavior.

## Risks
`mwifiex_11h_handle_chanrpt_ready()` repeatedly points `rpt` at `rpt_event->tlvbuf` inside the loop without advancing a separate pointer, so multiple TLVs would not be walked correctly. Join TLV construction assumes a valid `sband` and enough command-buffer space. DFS state depends on `cac_started` and delayed work cancellation order; double notifications or stale chandefs are the main behavioral risks.

## Test Signals
Signals include joining 11h and non-11h APs, checking capability bit changes, validating join TLV bytes, starting CAC and observing finished/aborted events, injecting radar channel-report and radar-detected firmware events, and verifying uAP channel switch restart plus `cfg80211_ch_switch_notify()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11h.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n.c

## Purpose
`11n.c` implements mwifiex HT/802.11n capability negotiation, HT join TLV construction, firmware 11n and A-MSDU command preparation, Tx BlockAck stream lifecycle, BA table introspection, default BA parameter selection, secondary-channel helpers, and AMPDU window-size updates.

## Important APIs, Types, And Functions
Capability/TLV APIs include `mwifiex_fill_cap_info()`, `mwifiex_cmd_11n_cfg()`, `mwifiex_cmd_append_11n_tlv()`, `mwifiex_cmd_recfg_tx_buf()`, and `mwifiex_cmd_amsdu_aggr_ctrl()`. BA response and lifecycle APIs include `mwifiex_ret_11n_delba()`, `mwifiex_ret_11n_addba_req()`, `mwifiex_get_ba_tbl()`, `mwifiex_create_ba_tbl()`, `mwifiex_send_addba()`, `mwifiex_send_delba()`, `mwifiex_11n_delete_ba_stream()`, and table cleanup/query helpers. `mwifiex_set_ba_params()`, `mwifiex_get_sec_chan_offset()`, and `mwifiex_update_ampdu_txwinsize()` set defaults and react to coexistence/window changes.

## Control Flow
HT capability fill reads cfg80211 band HT capabilities and copies AMPDU, MCS, cap, extended cap, and optional beamforming fields into the outgoing IE. Join TLV construction copies peer HT capability and operation IEs, adjusts HT40/SGI based on channel flags, adds a channel-list TLV with secondary-channel encoding, copies 20/40 coexistence and extended capabilities, and tracks Hotspot 2.0 interworking state.

Tx BA setup creates a per-RA/TID table entry, sends an ADDBA request, and completes the stream when firmware reports success. Failures reset RA-list status, remove BA entries, and may mark a TID as disallowed. DELBA responses delete Tx/Rx BA state according to initiator/type semantics and may trigger pending ADDBA setup. Window-size changes send DELBA for affected complete streams so streams can be renegotiated.

## State And Persistence
Runtime state lives in `priv->tx_ba_stream_tbl_ptr`, `priv->tx_ba_stream_tbl_lock`, per-RA WMM nodes, `priv->aggr_prio_tbl`, `priv->add_ba_param`, `priv->hs2_enabled`, adapter coexistence settings, and per-interface media state. Nothing is persisted beyond active firmware state and in-memory tables.

## Dependencies And Integration Points
The file integrates with cfg80211 band capabilities, mwifiex WMM RA lists, station/TDLS lookup, firmware command dispatch, endian-safe command structures, RX reorder deletion in `11n_rxreorder.c`, A-MSDU policy in `11n_aggr.c`, and 11ac-aware BA sizing for TDLS peers.

## Risks
`mwifiex_11n_delete_tx_ba_stream_tbl_entry()` has a suspicious guard: `if (!tx_ba_tsr_tbl && mwifiex_is_tx_ba_stream_ptr_valid(...)) return;` allows NULL to continue to `list_del()` instead of returning, and does not reject invalid non-NULL pointers. Join TLV builders assume caller buffer capacity and valid channel lookup. BA state spans Tx table, RA-list state, and firmware commands, so partial failures can leave mismatched aggregation state.

## Test Signals
Validation should cover HT association with/without HT40, no-HT40 channel flags, extended capability/HS2 parsing, 11n config command serialization, ADDBA success/failure/timeouts, DELBA from local and peer initiators, coexistence-driven TX window changes, TDLS 11ac peer BA sizing, and debug/ioctl reads of Tx BA tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n.h

## Purpose
`11n.h` is the local public header for mwifiex HT aggregation. It ties together A-MSDU aggregation, RX reorder, WMM, command response handlers, BA stream management APIs, and inline policy helpers for whether AMPDU/A-MSDU or 11n station behavior is allowed.

## Important APIs, Types, And Functions
The header exports prototypes for 11n command builders, TLV construction, BA send/delete/create/query routines, reorder-table query, Tx buffer and A-MSDU controls, and secondary-channel offset. Inline helpers include `mwifiex_is_station_ampdu_allowed()`, `mwifiex_is_ampdu_allowed()`, `mwifiex_is_amsdu_allowed()`, `mwifiex_space_avail_for_new_ba_stream()`, `mwifiex_find_stream_to_delete()`, `mwifiex_is_sta_11n_enabled()`, and `mwifiex_tdls_peer_11n_enabled()`.

## Control Flow
The inline helpers are used by WMM/Tx paths to decide whether aggregation may be started or whether an existing lower-priority stream should be removed. The policy checks reject broadcast RA, distinguish uAP/STA/TDLS behavior, inspect per-TID aggregation priority tables, and account for firmware-advertised maximum BA stream counts.

## State And Persistence
No state is defined in the header, but helpers read station table entries, RA-list entries, adapter private slots, `aggr_prio_tbl`, firmware API version/capabilities, fixed rate bitmap, and Tx BA list counts. All referenced state is runtime-only.

## Dependencies And Integration Points
It includes `11n_aggr.h`, `11n_rxreorder.h`, and `wmm.h`, making it the aggregation umbrella header. It depends on station lookup, BA status enums, adapter/private structures, and list-count helpers from the wider mwifiex driver.

## Risks
Because the header contains policy in inline functions, semantic changes here can alter Tx scheduling and BA stream admission across multiple call sites. `mwifiex_space_avail_for_new_ba_stream()` sums streams across all priv instances, so invalid or partially initialized adapter `priv[]` entries would affect admission decisions.

## Test Signals
Build coverage plus runtime aggregation tests are needed: broadcast rejection, uAP station ampdu policy, TDLS peer policy, fixed-rate A-MSDU disallowance, firmware v15 BA stream limits, and stream deletion victim selection by priority.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.c

## Purpose
`11n_aggr.c` implements mwifiex Tx A-MSDU aggregation. It dequeues multiple MSDUs from a WMM receiver-address list, encapsulates them as A-MSDU subframes with LLC/SNAP headers and padding, prepends a firmware TxPD, and submits the aggregate through the active bus interface.

## Important APIs, Types, And Functions
`mwifiex_11n_aggregate_pkt()` is the exported aggregation entry point and releases `priv->wmm.ra_list_spinlock` as part of its contract. `mwifiex_11n_form_amsdu_pkt()` creates one A-MSDU subframe from an Ethernet skb and computes four-byte padding. `mwifiex_11n_form_amsdu_txpd()` constructs the firmware `txpd` for a completed aggregate, including priority, packet delay, BSS identifiers, packet type `PKT_TYPE_AMSDU`, TDLS flag, tx control, and power-save last-packet marker.

## Control Flow
The aggregation path peeks the RA queue, allocates a DMA-aligned aggregate buffer sized by `adapter->tx_buf_size`, reserves interface header and TxPD space, inherits metadata from the first skb, and repeatedly dequeues source skbs while the aggregate can fit. It unlocks while copying each subframe and completing the original skb, then relocks and verifies the RA-list is still valid. After trimming final padding, it forms the TxPD, pushes interface headroom, and either queues behind existing data/tx lock state or calls `host_to_card()` for USB or generic data.

If the bus returns `-EBUSY`, the aggregate is requeued on the RA list and marked requeued. On hard failure it updates debug counters and completes the skb with error. On success or in-progress, normal completion/rotation occurs.

## State And Persistence
The function mutates WMM RA-list queues, per-list packet counts, `priv->wmm.tx_pkts_queued`, adapter `tx_queued`, `tx_data_q`, `data_sent`, and `tx_lock_flag`. It also uses skb control block metadata. All state is in-memory queue state.

## Dependencies And Integration Points
It depends on WMM RA-list validity and rotation, DMA-aligned skb allocation, bus `host_to_card` operations, mwifiex write completion, firmware `txpd`, TDLS flags, STA power-save/UAPSD helpers, and the packet type constant from `11n_aggr.h`.

## Risks
Aggregation is concurrency-sensitive because it drops and reacquires the RA-list spinlock inside the loop. Revalidating `pra_list` prevents use-after-free, but missed validation would be dangerous. The aggregate buffer limit check includes payload plus LLC/SNAP length but padding and header reservations must remain consistent with `tx_buf_size`. Requeueing an aggregate on `-EBUSY` changes queue contents from normal MSDUs to an aggregate skb, so downstream code must honor the requeued/aggr flags.

## Test Signals
Signals include aggregate creation from multiple queued skbs, exact subframe length/padding checks, TDLS flag propagation, STA UAPSD last-packet behavior, USB and non-USB send paths, `-EBUSY` requeue handling, RA-list invalidation during aggregation, and WMM queue/count invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.h

## Purpose
`11n_aggr.h` declares the mwifiex A-MSDU aggregation/deaggregation interface and constants used to identify firmware A-MSDU packets.

## Important APIs, Types, And Functions
It defines `PKT_TYPE_AMSDU` as the firmware packet type and `MIN_NUM_AMSDU` as the minimum aggregation count. It declares `mwifiex_11n_deaggregate_pkt()` for RX-side deaggregation and `mwifiex_11n_aggregate_pkt()` for Tx aggregation from a WMM RA-list. The aggregation prototype documents lock semantics with `__releases(&priv->wmm.ra_list_spinlock)`.

## Control Flow
The header has no executable flow. It allows Tx scheduling code to call aggregation while transferring ownership of the RA-list spinlock to the implementation.

## State And Persistence
No state is held. The declared functions operate on runtime skbs, RA lists, and mwifiex private state.

## Dependencies And Integration Points
It is included by `11n.h` and `11n_aggr.c`; RX reorder code also interprets `PKT_TYPE_AMSDU`. It depends on `struct mwifiex_private`, `struct mwifiex_ra_list_tbl`, and `struct sk_buff` being declared by including files.

## Risks
The lock annotation is part of the API contract; callers must enter with the RA-list spinlock held and must not unlock again after calling. Mismatched use can cause deadlocks or unlock imbalance.

## Test Signals
Build-time sparse/lock checking is valuable because of the `__releases` annotation. Runtime signals are the same aggregation/deaggregation paths that consume the declared functions and packet type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_aggr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_rxreorder.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_rxreorder.c

## Purpose
`11n_rxreorder.c` implements mwifiex RX BlockAck reorder handling. It creates and deletes per-peer/TID reorder windows, buffers out-of-order packets, dispatches contiguous packets, flushes holes by timer, handles ADDBA/DELBA firmware commands and responses, adjusts RX AMPDU windows for coexistence, and processes RXBA sync events.

## Important APIs, Types, And Functions
Core reorder dispatch helpers are `mwifiex_11n_dispatch_amsdu_pkt()`, `mwifiex_11n_dispatch_pkt()`, `mwifiex_11n_dispatch_pkt_until_start_win()`, and `mwifiex_11n_scan_and_dispatch()`. Table lifecycle is handled by `mwifiex_11n_create_rx_reorder_tbl()`, `mwifiex_del_rx_reorder_entry()`, `mwifiex_11n_get_rx_reorder_tbl()`, `mwifiex_11n_del_rx_reorder_tbl_by_ta()`, and `mwifiex_11n_cleanup_reorder_tbl()`.

Command/event APIs include `mwifiex_cmd_11n_addba_req()`, `mwifiex_cmd_11n_addba_rsp_gen()`, `mwifiex_cmd_11n_delba()`, `mwifiex_11n_rx_reorder_pkt()`, `mwifiex_del_ba_tbl()`, `mwifiex_ret_11n_addba_resp()`, `mwifiex_11n_ba_stream_timeout()`, `mwifiex_update_rxreor_flags()`, `mwifiex_coex_ampdu_rxwinsize()`, and `mwifiex_11n_rxba_sync_event()`.

## Control Flow
When an ADDBA request is accepted, the response generator computes negotiated window size and A-MSDU permission, returns an ADDBA response command, and creates a reorder table at the requested starting sequence number. Incoming packets call `mwifiex_11n_rx_reorder_pkt()`: without a matching table they are dispatched immediately; with a table, old/duplicate packets are dropped, BAR frames advance the window, out-of-window packets shift and flush the window, and normal packets are stored at a computed index before contiguous packets are dispatched.

The reorder buffer is linear; helpers rotate pointer arrays to simulate a circular window. A timer flushes through the last occupied slot when holes persist. Deleting a BA table drains pending packets, synchronizes against RX processing, deletes the timer, removes the list node, and frees storage. RXBA sync TLVs instruct the driver to drop indicated packets by feeding NULL payloads through the reorder path.

## State And Persistence
State lives in `priv->rx_reorder_tbl_ptr`, per-table `start_win`, `init_win`, `win_size`, `amsdu`, flags, `rx_reorder_ptr[]`, and timer context. It also reads per-station/per-interface last RX sequence arrays and mutates `priv->add_ba_param.rx_win_size` for coexistence. All state is volatile.

## Dependencies And Integration Points
This file integrates with firmware ADDBA/DELBA/BATIMEOUT/RXBA events, WMM TID handling, station tables, cfg80211 interface type for A-MSDU conversion, uAP and STA RX delivery paths, TDLS action handling, adapter RX workqueue locking, and the Tx BA table deletion functions in `11n.c`.

## Risks
RX reorder logic is sequence-number and wraparound sensitive; mistakes can drop valid packets or release stale duplicates. `mwifiex_11n_rxba_sync_event()` returns if any referenced reorder table is missing, which can skip later TLVs in the same event. Timer callbacks hold table pointers, so deletion must keep `timer_delete_sync()` ordering intact. A-MSDU dispatch passes `skb->len` rather than `rx_skb->len` into TDLS action processing, which may be semantically surprising.

## Test Signals
Tests should cover in-order packets, gaps plus timer flush, duplicates, old sequence drops, sequence wraparound, BAR handling, ADDBA accept/reject, DELBA initiated by peer/local, A-MSDU allowed/disallowed in AMPDU, RXBA sync bitmap drops, coexistence-driven RX window changes, and teardown under active RX work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_rxreorder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_rxreorder.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_rxreorder.h

## Purpose
`11n_rxreorder.h` declares constants, flags, and APIs for mwifiex RX BlockAck reorder support.

## Important APIs, Types, And Functions
Constants define reorder timer minimums, BA window size thresholds, firmware packet type `PKT_TYPE_BAR`, TID sequence modulus helpers, ADDBA/DELBA bit positions, immediate BlockAck, default RX sequence number, and BA setup thresholds. `enum mwifiex_rxreor_flags` declares `RXREOR_FORCE_NO_DROP` and `RXREOR_INIT_WINDOW_SHIFT`. `mwifiex_reset_11n_rx_seq_num()` resets per-TID sequence numbers to `0xffff`.

Prototypes expose RX reorder packet handling, BA table deletion, timeout handling, ADD/DELBA command builders and response handlers, cleanup, table lookup, TA-based deletion, flag update, and RXBA sync event handling.

## Control Flow
The header itself has no runtime flow, but its constants drive sequence-window math and command field packing in `11n_rxreorder.c` and `11n.c`.

## State And Persistence
No state is owned here. The inline reset helper mutates `priv->rx_seq` in caller-owned runtime state.

## Dependencies And Integration Points
It is included by `11n.h` and implemented by `11n_rxreorder.c`. It depends on firmware command structures, `mwifiex_private`, and `mwifiex_adapter` declarations from broader mwifiex headers.

## Risks
Bit-position constants must remain aligned with IEEE 802.11 and firmware command layouts. The sequence modulus definitions (`MAX_TID_VALUE`, `TWOPOW11`) are central to wraparound handling; changes risk broad RX reorder regressions.

## Test Signals
Compile-time coverage plus reorder runtime tests should exercise command field packing, sequence reset, BAR packet handling, wraparound, timer thresholds, and flag update behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/11n_rxreorder.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/Kconfig

## Purpose
This Kconfig file exposes build-time configuration for the mwifiex core and its SDIO, PCIe, and USB transport modules.

## Important APIs, Types, And Functions
`CONFIG_MWIFIEX` is a tristate core option depending on `CFG80211`. `CONFIG_MWIFIEX_SDIO` depends on `MWIFIEX && MMC` and selects firmware loader plus device coredump support. `CONFIG_MWIFIEX_PCIE` depends on `MWIFIEX && PCI` and also selects firmware loader and coredump support. `CONFIG_MWIFIEX_USB` depends on `MWIFIEX && USB` and selects firmware loader.

## Control Flow
Kconfig controls whether the core `mwifiex` object and transport modules are built in, built as modules, or omitted. Transport choices require the core and their bus subsystem.

## State And Persistence
No runtime state exists. User/kernel configuration persists in the kernel build configuration and determines compiled artifacts.

## Dependencies And Integration Points
The file integrates with Linux wireless configuration (`CFG80211`), bus subsystems (`MMC`, `PCI`, `USB`), firmware loading, device coredump support, and the adjacent Makefile's `obj-$(CONFIG_*)` rules.

## Risks
Incorrect dependencies could allow a transport to build without required core or bus APIs. Missing `FW_LOADER` selection would break firmware-based devices at runtime. USB lacks `WANT_DEV_COREDUMP` selection unlike SDIO/PCIe, which may be intentional but affects diagnostics.

## Test Signals
Build matrix checks should cover core disabled, core built-in/module, each transport built-in/module, missing bus dependencies, firmware loader availability, and module names `mwifiex`, `mwifiex_sdio`, `mwifiex_pcie`, and `mwifiex_usb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/Makefile

## Purpose
This Makefile defines the object composition for the mwifiex core module and its SDIO, PCIe, and USB transport modules.

## Important APIs, Types, And Functions
`mwifiex-y` aggregates core objects: initialization, command/event handling, utilities, tx/rx, WMM, 11n, 11ac, A-MSDU aggregation, RX reorder, scan/join, station/uAP command/event handling, cfg80211, ethtool, 11h, and TDLS. `mwifiex-$(CONFIG_DEBUG_FS)` adds debugfs support. `obj-$(CONFIG_MWIFIEX)` emits the core module.

Transport object lists build `mwifiex_sdio.o` from `sdio.o`, `mwifiex_pcie.o` from `pcie.o` and `pcie_quirks.o`, and `mwifiex_usb.o` from `usb.o`. `ccflags-y += -D__CHECK_ENDIAN` enables endian checking annotations.

## Control Flow
Kbuild evaluates `CONFIG_*` variables to decide which objects compile and link. Core protocol files such as `11n.o`, `11ac.o`, `11n_aggr.o`, `11n_rxreorder.o`, and `11h.o` are always part of the core when `CONFIG_MWIFIEX` is enabled.

## State And Persistence
No runtime state exists. The file affects build artifacts and module composition.

## Dependencies And Integration Points
It pairs with the adjacent Kconfig. It integrates all major mwifiex source modules into one core object and separates hardware bus transports into independent modules depending on selected config symbols.

## Risks
Missing an object from `mwifiex-y` would create unresolved symbols or disabled functionality even when source exists. Since protocol support is compiled into the core, regressions in 11n/11ac/11h files affect all transports. Endian-check flag is important for firmware ABI correctness; dropping it would weaken static validation.

## Test Signals
Build tests should verify `CONFIG_MWIFIEX`, SDIO, PCIe, USB, and `CONFIG_DEBUG_FS` combinations, confirm module object contents, and run sparse/endian checks for command structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/Makefile -->
