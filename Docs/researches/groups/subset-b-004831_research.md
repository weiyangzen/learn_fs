# Research: subset-b-004831

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tx.c

## Purpose

This file implements the MLD transmit path for Intel iwlwifi: dynamic firmware TXQ allocation/removal, skb-to-`TX_CMD` construction, TSO/A-MSDU segmentation, queue draining from mac80211 TXQs, firmware TX response handling, compressed BA reclaim, station queue flushing, and TX antenna fallback. It bridges mac80211 queuing and status APIs with the lower iwl transport and firmware datapath APIs.

## Important APIs, Types, and Functions

- `iwl_mld_add_txq_list()`, `iwl_mld_add_txqs_wk()`, `iwl_mld_ensure_queue()`, `iwl_mld_remove_txq()`, and `iwl_mld_free_txq()` manage `struct ieee80211_txq` backing queues and map them to firmware SCD queues.
- `iwl_mld_tx_from_txq()` is the mac80211 TXQ drain loop. It uses `mld_txq->tx_request` to serialize concurrent drainers without repeatedly contending on the transport queue lock.
- `iwl_mld_tx_skb()` routes GSO packets through `iwl_mld_tx_tso()` and normal packets through `iwl_mld_tx_mpdu()`.
- `iwl_mld_fill_tx_cmd()` and helpers populate `struct iwl_tx_cmd`, including MAC header copy, encryption flag, rate flags, length, priority, and offload assist bits.
- `iwl_mld_get_tx_queue_id()` chooses a firmware queue for station TXQs, AP/IBSS broadcast and multicast, P2P/NAN auxiliary queues, monitor queues, and off-channel station management frames.
- `iwl_mld_handle_tx_resp_notif()` and `iwl_mld_handle_compressed_ba_notif()` reclaim transmitted SKBs from transport queues and report status to mac80211.
- `iwl_mld_flush_link_sta_txqs()` sends `TXPATH_FLUSH` for all TIDs of a firmware station and reclaims flushed queues.
- Rate helpers include `iwl_mld_get_lowest_rate()`, `iwl_mld_mac80211_rate_idx_to_fw()`, `iwl_mld_get_inject_tx_rate()`, `iwl_mld_get_tx_rate_n_flags()`, and `iwl_mld_hwrate_to_tx_rate()`.

## Control Flow

Queue setup starts when an `ieee80211_txq` is added to `mld->txqs_to_add`. The work item `iwl_mld_add_txqs_wk()` skips allocation during hardware restart, otherwise `iwl_mld_add_txq_list()` repeatedly calls `iwl_mld_add_txq()`. Queue allocation computes the firmware station mask, maps mac80211 management TID to `IWL_MGMT_TID`, chooses queue size from HE/EHT capabilities, disables watchdog for AP queues, calls `iwl_trans_txq_alloc()`, stores `fw_id`, marks the queue allocated, and publishes `mld->fw_id_to_txq[id]` under RCU. If allocation succeeds, pending frames are immediately drained.

Transmit drain enters `iwl_mld_tx_from_txq()`. The atomic `tx_request` state collapses concurrent requests: `0` means this caller becomes the drainer, `1` means another drainer should make one extra pass, and `2` means that extra pass is already requested. Under RCU, the loop dequeues SKBs while the queue is not marked `stop_full`, then calls `iwl_mld_tx_skb()` for each frame. Normal SKBs use `iwl_mld_tx_mpdu()`, while GSO SKBs use `iwl_mld_tx_tso()`.

`iwl_mld_tx_mpdu()` resolves a firmware queue, drops nullfunc frames, allocates an `iwl_device_tx_cmd`, optionally appends P2P NoA data to probe responses, fills the TX command, derives TID for debug/logging, clears mac80211 status and driver data, stores the command pointer in `info->driver_data[1]`, and calls `iwl_trans_tx()`. On transport failure it frees the command and reports drop; callers free or consume the SKB as appropriate.

TSO flow checks that a station TXQ exists, computes TCP payload length, and either sends one MPDU directly or calls `iwl_mld_tx_tso_segment()`. Segmentation builds MPDUs using `iwl_tx_tso_segment()`, with A-MSDU support when QoS data, station A-MSDU limits, IPv4 or simple IPv6/TCP constraints, TID-specific max A-MSDU length, max subframe count, and transport fragment limits allow it. Each resulting SKB is transmitted as an MPDU; failures purge remaining generated SKBs and free the failed segment while returning success to indicate ownership was consumed.

Response flow receives firmware `iwl_tx_resp`, validates frame count and payload size, derives SSN, reclaims descriptors with `iwl_trans_reclaim()`, frees stored TX command pointers, maps firmware status to `IEEE80211_TX_STAT_ACK`, triggers debug time points on failures, converts initial firmware rate into mac80211 status, handles time-sync frames specially, and otherwise calls `ieee80211_tx_status_skb()`. It also toggles management or pre-authorization data antenna on management/preauth failures and updates per-station MPDU counters.

Compressed BA flow validates `tfd_cnt`, reclaims each referenced TXQ/index through `iwl_mld_tx_reclaim_txq()`, then finds the link station and counts transmitted MPDUs. Flush flow sends `TXPATH_FLUSH`, validates response length/station/count, and reclaims each returned queue in flush mode so ACK is cleared.

## State and Persistence Behavior

Persistent driver state is held in `struct iwl_mld` and per-TXQ private data. `mld_txq->zeroed_on_hw_restart` contains firmware queue identity and allocation/full state that must be reset on restart. `mld->fw_id_to_txq[]` and `mld->fw_id_to_link_sta[]` are RCU-published firmware ID maps. `mld->mgmt_tx_ant` and per-station `data_tx_ant` are adjusted after selected failures. Command pointers live transiently in `IEEE80211_SKB_CB(skb)->driver_data[1]` until reclaim. The code updates low-latency counters when frames are queued, not only when they complete, to catch latency-sensitive traffic earlier.

## Dependencies and Integration Points

This file depends on mac80211 TXQ, VIF, STA, link-station, rate-control, and status APIs; Linux networking/GSO/checksum helpers; iwl transport allocation/transmit/reclaim/free primitives; firmware datapath commands such as `SCD_QUEUE_CONFIG_CMD`, `TXPATH_FLUSH`, `TX_CMD`, and compressed BA notifications; and local MLD station, VIF, link, time-sync, and low-latency helpers. It is built around wiphy locking for queue allocation/removal and RCU for link/station lookup.

## Risks

- Queue ID selection has many interface-specific branches. Incorrect `control.vif`, link ID, ROC state, or station presence can drop frames or send management frames on an unintended auxiliary/broadcast queue.
- `info->control` is explicitly invalid after status/driver data is cleared in `iwl_mld_tx_mpdu()`. Future edits must not access control fields after that point.
- TSO/A-MSDU segmentation relies on exact header length, subframe padding, GSO size, IPv6 extension-header limitations, and max fragment accounting. Off-by-one errors can produce firmware-invalid descriptors.
- Reclaim logic assumes one frame in regular TX responses and different semantics for BA/flush reclaim. Misclassifying flush vs success can misreport ACKs.
- Antenna toggle is intentionally limited to management or unauthenticated station failure paths; broadening it can harm normal rate control.
- `iwl_mld_probe_resp_set_noa()` may expand SKB head/tail in atomic context and relies on RCU-protected probe response data.

## Test Signals

Useful validation includes AP/STA/P2P/NAN/monitor TX smoke tests, off-channel action frame transmission, TSO and non-TSO TCP throughput, A-MSDU generation with HE/EHT peers, injected fixed-rate frames, firmware queue allocation failure handling, restart recovery with pending TXQs, TX status ACK/failure reporting, compressed BA reclaim under aggregation, flush behavior during station removal, and checksum offload with IPv4, IPv6 without extension headers, and IPv6 extension-header fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tx.h

## Purpose

This header defines the MLD TXQ private data contract and declares the MLD transmit, reclaim, queue-management, rate, antenna, and notification entry points implemented by `mld/tx.c`.

## Important APIs, Types, and Functions

- `IWL_MLD_INVALID_QUEUE` and `IWL_MLD_INVALID_DROP_TX` are sentinel return values used by queue selection to distinguish internal invalid state from intentional drop.
- `struct iwl_mld_txq` is stored in `ieee80211_txq::drv_priv`. Its `fw_id`, `status.allocated`, and `status.stop_full` are grouped as `zeroed_on_hw_restart`; its `list` participates in `mld->txqs_to_add`; and `tx_request` serializes queue drain requests.
- `iwl_mld_init_txq()` initializes the list head and atomic drain state.
- `iwl_mld_txq_from_mac80211()` casts mac80211 TXQ private storage into the driver TXQ object.
- Function declarations expose queue add/remove/free, TX drain, direct SKB TX, TX response and BA notification handling, station flush, station-mask queue update, antenna toggle, lowest-rate selection, and queue ensure operations.

## Control Flow

mac80211 allocates TXQs with enough driver-private space for `struct iwl_mld_txq`; initialization calls `iwl_mld_init_txq()`. Runtime code uses `iwl_mld_txq_from_mac80211()` to reach firmware queue state, allocates queues through `iwl_mld_add_txq_list()` or `iwl_mld_ensure_queue()`, drains through `iwl_mld_tx_from_txq()`, and tears down through `iwl_mld_remove_txq()`/`iwl_mld_free_txq()`. Firmware notifications enter through the declared response and compressed BA handlers.

## State and Persistence Behavior

The explicit `struct_group(zeroed_on_hw_restart, ...)` documents which TXQ fields are invalidated by a firmware restart. The list membership and atomic `tx_request` survive that zeroing and must be initialized separately. `status.stop_full` is a runtime backpressure bit consumed by the drain loop.

## Dependencies and Integration Points

The header depends on `mld.h`, mac80211 `struct ieee80211_txq`, `struct ieee80211_tx_info`, `struct ieee80211_vif`, Linux `sk_buff`, and iwl firmware RX packet types. It is included by the MLD TX implementation and by other MLD modules that need to enqueue, flush, or update station TXQs.

## Risks

- The cast in `iwl_mld_txq_from_mac80211()` assumes mac80211 TXQ private allocation size and alignment match `struct iwl_mld_txq`.
- Fields in `zeroed_on_hw_restart` must stay limited to firmware-derived state; moving list or atomic fields into it would corrupt restart behavior.
- Callers must interpret the two invalid queue sentinels correctly: one is a warning-worthy bug path, the other is an intentional drop path.

## Test Signals

Build coverage should catch signature drift between the header and implementation. Runtime restart tests should verify TXQ private data is reinitialized correctly, pending TXQs are re-added, and `tx_request` does not wedge after firmware restart or queue full/stop transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/tx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/Makefile

## Purpose

This Makefile defines the kernel build composition for the Intel iwlwifi MVM object. It aggregates the core `iwlmvm.o` object from feature-specific C files and conditionally includes debugfs, LED, suspend/D3, MEI vendor command, and KUnit test pieces.

## Important APIs, Types, and Functions

- `obj-$(CONFIG_IWLMVM) += iwlmvm.o` builds the MVM module/object when the driver option is enabled.
- `obj-$(CONFIG_IWLWIFI_KUNIT_TESTS) += tests/` includes the local KUnit test directory conditionally.
- `iwlmvm-y += ...` lines enumerate always-built MVM units: firmware/mac80211 operations, NVM, PHY/MAC context, RX/TX, binding, quota, station, scan, power, BT coexistence, TDLS, FTM, RFI, MLD key/MAC/link/STA/mac80211 support, PTP, and time sync.
- `iwlmvm-$(CONFIG_IWLWIFI_DEBUGFS)`, `iwlmvm-$(CONFIG_IWLWIFI_LEDS)`, `iwlmvm-$(CONFIG_PM_SLEEP)`, and `iwlmvm-$(CONFIG_IWLMEI)` gate optional source files.
- `subdir-ccflags-y += -I $(src)/../` exposes parent iwlwifi headers.

## Control Flow

There is no runtime control flow. During kbuild evaluation, config symbols expand the object lists. The final linked `iwlmvm.o` includes all unconditional MVM components plus optional objects selected by kernel configuration.

## State and Persistence Behavior

No runtime state is stored here. Build-time state is limited to object membership. Conditional entries affect which debugfs, D3/WoWLAN, LED, vendor, and test code exists in the resulting build.

## Dependencies and Integration Points

This file integrates with Linux kbuild, Kconfig symbols, and the source layout under `drivers/net/wireless/intel/iwlwifi`. It directly controls whether files researched in this subset are compiled: `binding.c` and `coex.c` are unconditional; `debugfs.c` and `debugfs-vif.c` require `CONFIG_IWLWIFI_DEBUGFS`; `d3.c` requires `CONFIG_PM_SLEEP`.

## Risks

- Removing or mis-gating an object can silently drop feature support for a configuration.
- Optional files must keep their external declarations guarded consistently with config symbols.
- Parent include path changes can break local `#include "fw-api.h"` and sibling header usage.

## Test Signals

Run kernel builds across representative configs: base `CONFIG_IWLMVM`, with `CONFIG_IWLWIFI_DEBUGFS`, with `CONFIG_PM_SLEEP`, with `CONFIG_IWLWIFI_LEDS`, with `CONFIG_IWLMEI`, and with KUnit tests enabled. Link failures are the main signal for stale object membership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/binding.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/binding.c

## Purpose

This file manages MVM firmware binding contexts: the association between one PHY context and the MAC contexts currently using it. It sends add/modify/remove binding commands and selects LMAC IDs for CDB-capable firmware.

## Important APIs, Types, and Functions

- `struct iwl_mvm_iface_iterator_data` accumulates MAC IDs/colors for interfaces sharing a PHY context, optionally ignoring the interface being added or removed.
- `iwl_mvm_binding_cmd()` builds `struct iwl_binding_cmd`, chooses command size/version and LMAC ID based on firmware capabilities, fills PHY and MAC ID/color fields, sends `BINDING_CONTEXT_CMD`, and checks firmware status.
- `iwl_mvm_iface_iterator()` is the mac80211 active-interface iterator that collects matching interfaces.
- `iwl_mvm_binding_update()` determines whether the binding operation is add, modify, or remove and appends the target VIF when needed.
- `iwl_mvm_binding_add_vif()` disables Smart FIFO if needed before adding a VIF to a binding.
- `iwl_mvm_binding_remove_vif()` removes a VIF from the binding and re-enables Smart FIFO if possible.
- `iwl_mvm_get_lmac_id()` maps 2.4 GHz or non-CDB to `IWL_LMAC_24G_INDEX`, otherwise to `IWL_LMAC_5G_INDEX`.

## Control Flow

Adding a VIF requires an existing `deflink.phy_ctxt`. The add path first updates Smart FIFO state because many bound MACs are incompatible with SF. It then iterates active interfaces on the same PHY context, excluding the target VIF, and chooses `FW_CTXT_ACTION_ADD` if no other MAC is bound or `FW_CTXT_ACTION_MODIFY` if an existing binding must be updated. The target MAC ID/color is appended and `iwl_mvm_binding_cmd()` sends the resulting command.

Removal mirrors this flow. It iterates active interfaces on the same PHY context while ignoring the VIF being removed, chooses `FW_CTXT_ACTION_REMOVE` if no MACs remain or `FW_CTXT_ACTION_MODIFY` otherwise, sends the binding command, and then attempts Smart FIFO update. Firmware command failures propagate as errors; Smart FIFO re-enable failure after removal is logged but does not override a successful binding removal.

## State and Persistence Behavior

The binding command is derived from current runtime state: VIF IDs/colors, PHY context ID/color, active-interface membership, and firmware capabilities. The file does not own persistent data structures beyond stack iterator data. Firmware stores the binding state after successful commands.

## Dependencies and Integration Points

This code depends on mac80211 active-interface iteration, `mvm->mutex` serialization, MVM VIF and PHY context private data, Smart FIFO update (`iwl_mvm_sf_update()`), firmware capabilities (`IWL_UCODE_TLV_CAPA_BINDING_CDB_SUPPORT`, `IWL_UCODE_TLV_CAPA_CDB_SUPPORT`), and `iwl_mvm_send_cmd_pdu_status()`.

## Risks

- The iterator assumes no more than `MAX_MACS_IN_BINDING`; overflow returns a warning and may leave firmware binding incomplete.
- Binding updates must be serialized under `mvm->mutex`; callers that skip this can race active-interface membership.
- SF update failure before add is treated as fatal to avoid illegal firmware state; changing that policy risks enabling unsupported multiple-MAC configurations.
- CDB command sizing must match firmware capability advertisement.

## Test Signals

Exercise single VIF add/remove, multiple VIFs sharing a PHY, AP plus STA concurrency, CDB and non-CDB firmware, Smart FIFO disable/enable transitions, and firmware status failure injection for `BINDING_CONTEXT_CMD`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/binding.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/coex.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/coex.c

## Purpose

This file implements Bluetooth/Wi-Fi coexistence policy for MVM. It initializes firmware coexistence mode, processes BT profile notifications, selects primary/secondary 2.4 GHz channel-interference masks, updates SMPS and reduced TX power, reacts to RSSI events, and exposes coexistence decisions used by aggregation, MIMO, antenna, TPC, and TX-priority code.

## Important APIs, Types, and Functions

- `iwl_ci_mask` maps 2.4 GHz channel and bandwidth placement to channel-interference bitmasks sent in `BT_COEX_CI`.
- `iwl_get_coex_type()` resolves the active LUT type for a VIF by matching its PHY context to the last primary or secondary CI command.
- `iwl_mvm_send_bt_init_conf()` sends `BT_CONFIG`, honoring forced antenna mode or enabling normal coexistence modules such as Sync2SCO, MPLUT, and high-band retention.
- `iwl_mvm_bt_coex_reduced_txp()` toggles station reduced TX power on pre-AX210 devices using `BT_COEX_UPDATE_REDUCED_TXP`.
- `iwl_mvm_bt_notif_per_link()` handles per-link effects of BT activity: SMPS constraints, low-latency primary selection, AP/STA primary/secondary assignment, load tracking, reduced TX power, and RSSI event thresholds.
- `iwl_mvm_bt_coex_notif_handle()` iterates active interfaces, applies TCM-based primary/secondary swapping, builds CI masks, and sends changed `BT_COEX_CI` commands.
- `iwl_mvm_rx_bt_coex_old_notif()` stores firmware BT notification state and triggers policy recalculation.
- Helper policies include `iwl_mvm_bt_rssi_event()`, `iwl_mvm_coex_agg_time_limit()`, `iwl_mvm_bt_coex_is_mimo_allowed()`, `iwl_mvm_bt_coex_is_ant_avail()`, `iwl_mvm_bt_coex_is_shared_ant_avail()`, `iwl_mvm_bt_coex_is_tpc_allowed()`, `iwl_mvm_bt_coex_get_single_ant_msk()`, `iwl_mvm_bt_coex_tx_prio()`, and `iwl_mvm_bt_coex_vif_change()`.

## Control Flow

Initialization clears cached BT notification and CI command state, selects forced BT/Wi-Fi antenna mode if configured, otherwise enables normal coexistence modules and sends `BT_CONFIG`.

On each BT coexistence notification, the driver copies the notification into `mvm->last_bt_notif` and calls `iwl_mvm_bt_coex_notif_handle()`. That handler ignores updates in forced antenna mode, iterates station/AP interfaces and all MLD links under RCU while holding `mvm->mutex`, and lets `iwl_mvm_bt_notif_per_link()` apply per-link behavior. Links not on 2.4 GHz clear BT constraints. Station links on 2.4 GHz derive SMPS mode from BT activity grading and schema version; RRC status can relax SMPS. Low-latency links are preferred as primary. AP links can become primary if active and no low-latency interface takes precedence. STA/P2P client links fill primary then secondary slots.

After iteration, pre-AX210 devices may swap primary/secondary based on TCM load every 10 seconds unless the primary is low-latency. CI masks are computed from channel number and width/sideband and sent only when different from `mvm->last_bt_ci_cmd`. Reduced TX power is enabled for associated station links when coexistence is not loose, BT is active, and RSSI is high enough; RSSI thresholds are armed so later mac80211 RSSI events can flip reduced TX power.

## State and Persistence Behavior

The file updates `mvm->last_bt_notif`, `mvm->last_bt_ci_cmd`, `mvm->bt_coex_last_tcm_ts`, per-station `bt_reduced_txpower`, and per-link beacon-filter RSSI event thresholds in `link_info->bf_data`. It reads module constants from `constants.h` and configuration fields such as `bt_force_ant_mode`, `bt_tx_prio`, `cfg->non_shared_ant`, and TCM load.

## Dependencies and Integration Points

It integrates with firmware commands and notifications in `fw/api/coex.h`, mac80211 channel contexts and SMPS, MVM station/VIF/link/PHY context state, beacon filtering RSSI event machinery, TCM load accounting, rate-control aggregation decisions, TX priority assignment, and antenna-selection helpers. It assumes caller serialization by `mvm->mutex` for notification handling and some RCU-safe channel/VIF access in rate-control paths.

## Risks

- `iwl_get_coex_type()` is intentionally racy in rate-control paths; stale LUT data can temporarily produce wrong aggregation/MIMO decisions.
- CI mask indexing depends on 2.4 GHz channel `hw_value` matching the static table.
- Reduced TX power state is skipped on AX210 and newer; behavior changes by device family.
- Primary/secondary selection assumes at most two relevant 2.4 GHz contexts.
- Per-link MLD handling still has FIXME notes around TCM load granularity.
- Forced antenna mode suppresses dynamic updates, so stale notification-derived state should not be interpreted as active policy.

## Test Signals

Validate with BT off/low/high/very-high activity, 2.4 GHz and 5/6 GHz operation, AP plus STA concurrency, low-latency VIFs, TCM load changes, RSSI threshold events, pre-AX210 and AX210+ devices, forced BT/Wi-Fi antenna modes, loose/tight/TX-disallowed LUTs, and rate-control decisions for aggregation time limit, MIMO, shared antenna availability, and TX priority.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/coex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/constants.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/constants.h

## Purpose

This header centralizes MVM compile-time default constants for power save, U-APSD, Bluetooth coexistence, quota, rate scaling, time-of-flight/FTM, adaptive dwell, traffic classification, aggregation, scanning, TWT, AP FILS, passive scan timing, beacon interval limits, and EML defaults.

## Important APIs, Types, and Functions

There are no functions or types. Important constant groups include:

- Power-save defaults: `IWL_MVM_DEFAULT_PS_*`, `IWL_MVM_WOWLAN_PS_*`, `IWL_MVM_SHORT_PS_*`, snooze windows, U-APSD timeouts, and heavy traffic thresholds.
- Coexistence defaults: `IWL_MVM_BT_COEX_*`, MPLUT register defaults, antenna coupling threshold, and reduced TX power RSSI thresholds.
- Quota and low-latency defaults: `IWL_MVM_LOWLAT_QUOTA_MIN_PERCENT`, `IWL_MVM_QUOTA_THRESHOLD`, and TCM load thresholds.
- Rate scaling knobs: retry counts, table limits, success/failure thresholds, aggregation limits, spatial reuse thresholds, and TPC tuning.
- FTM/ToF defaults: initiator/responder algorithm, repetition, STS, LTF, secure LTF, smoothing, and timing bounds.
- Feature gates and timing defaults: EBS, TWT, non-transmitting AP behavior, AP FILS disable, 6 GHz passive scan timeouts, minimum beacon interval, and automatic EML enable.

## Control Flow

The header has no control flow. Values are included at compile time by MVM implementation files and shape runtime command defaults and policy thresholds.

## State and Persistence Behavior

The constants are immutable at runtime unless implementation code layers debugfs/module-parameter overrides on top. They influence persistent driver behavior across associations, suspend/resume, scans, coexistence events, and rate-control decisions.

## Dependencies and Integration Points

The header includes `linux/ieee80211.h` and `fw-api.h` for constants used in expressions, such as WMM queue bits and firmware ToF algorithm values. It is consumed broadly by MVM power, coexistence, rate-scaling, scan, FTM, and debugfs code.

## Risks

- Small threshold changes can have broad behavioral impact across power use, latency, coexistence, throughput, and roaming.
- Some values encode units explicitly in comments; confusing microseconds, milliseconds, TU, seconds, or percentages can produce severe runtime changes.
- Firmware expectations may bound values more tightly than the compiler can validate.

## Test Signals

Changes should be validated by power-save behavior, WoWLAN latency, BT coexistence, throughput/rate-scaling, FTM accuracy, scan dwell behavior, 6 GHz passive scan timing, AP beacon interval acceptance, and EML behavior. Static build coverage catches only syntax and missing symbol problems, not policy regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/constants.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/d3.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/d3.c

## Purpose

This file implements MVM suspend/resume support for D3, WoWLAN, fast suspend/resume, and net-detect. It programs rekey material, key replay counters, TKIP material, wake patterns, protocol offloads, D3 configuration, net-detect scans, and on resume parses wake status/notifications, restores key sequence state, reports wake reasons to mac80211/cfg80211, decides whether the connection can be kept, and requests hardware restart when firmware state cannot be preserved.

## Important APIs, Types, and Functions

- mac80211 callbacks: `iwl_mvm_set_rekey_data()`, `iwl_mvm_ipv6_addr_change()`, `iwl_mvm_set_default_unicast_key()`, `iwl_mvm_suspend()`, `iwl_mvm_resume()`, and `iwl_mvm_set_wakeup()`.
- Fast path entry points: `iwl_mvm_fast_suspend()` and `iwl_mvm_fast_resume()`.
- Key programming: `iwl_mvm_wowlan_program_keys()`, `iwl_mvm_wowlan_config_rsc_tsc()`, `iwl_mvm_wowlan_config_key_params()`, `iwl_mvm_wowlan_get_tkip_data()`, and `iwl_mvm_wowlan_gtk_type_iter()`.
- Wake configuration: `iwl_mvm_get_wowlan_config()`, `iwl_mvm_wowlan_config()`, `iwl_mvm_send_patterns_v1()`, `iwl_mvm_send_patterns()`, and `iwl_mvm_send_proto_offload()`.
- D3 firmware transition: `iwl_mvm_switch_to_d3()`, `iwl_mvm_d3_reprogram()`, `iwl_mvm_resume_firmware()`, `iwl_mvm_d3_notif_wait()`, and `iwl_mvm_d3_resume_notif_based()`.
- Status representation: `struct iwl_wowlan_status_data`, `struct iwl_multicast_key_data`, `enum iwl_d3_notif`, and `struct iwl_d3_data`.
- Resume parsing/restoration: `iwl_mvm_send_wowlan_get_status()`, `iwl_mvm_parse_wowlan_info_notif*()`, `iwl_mvm_wowlan_store_wake_pkt()`, `iwl_mvm_report_wakeup_reasons()`, `iwl_mvm_setup_connection_keep()`, and `iwl_mvm_query_wakeup_reasons()`.
- Net-detect: `iwl_mvm_netdetect_config()`, `iwl_mvm_netdetect_query_results()`, `iwl_mvm_nd_match_info_handler()`, and `iwl_mvm_query_netdetect_reasons()`.

## Control Flow

Suspend starts in `iwl_mvm_suspend()`, which pauses TCM, suspends firmware runtime debug, and calls `__iwl_mvm_suspend()`. The inner function selects the BSS VIF, sets `IWL_MVM_STATUS_IN_D3`, synchronizes networking, and branches on association state. If no AP station is present, only net-detect is valid; it switches firmware if needed, starts a net-detect scheduled scan, and stores match sets/channels for later reporting. If associated, it ensures the offload TID queue exists, builds `WOWLAN_CONFIGURATION` flags from cfg80211 wake triggers, optionally switches to D3 firmware and manually reprograms PHY/MAC/binding/STA/quota for non-unified images, programs key/RSC/TSC/TKIP/rekey material, sends wake patterns and protocol offload, updates power device/MAC state, and finally sends `D3_CONFIG_CMD` before transport D3 suspend.

Resume starts in `iwl_mvm_resume()` and calls `__iwl_mvm_resume()`. It locks `mvm->mutex`, verifies the device is still in D3, reloads the BSS VIF, reads D3 debug data, checks runtime error tables for rfkill or firmware errors, then either waits for notification-based status (`WOWLAN_INFO_NOTIFICATION`, optional wake packet, optional net-detect match info, and `D3_END_NOTIFICATION`) or resumes firmware and later queries `WOWLAN_GET_STATUSES`. If D3 end flags do not require reset, it updates regulatory data, PPAG, SAR, and stops unified-image net-detect scan when needed. It then calls `iwl_mvm_choose_query_wakeup_reasons()`, which routes to net-detect wake reporting or normal WoWLAN wake reporting and connection preservation.

Normal wake reporting updates offloaded TID sequence numbers, transport queue pointers on newer devices, reports cfg80211 wake reasons and optional wake packet, and calls `iwl_mvm_setup_connection_keep()`. Connection keep restores PTK/GTK/IGTK/BIGTK sequence counters, installs rekeyed GTK/IGTK/BIGTK material, notifies GTK rekey, stores non-QoS sequence for later firmware reprogramming on older APIs, and returns false if wake reasons indicate disconnection. After resume, other station VIFs are disconnected unless the connection was kept. Unified images can avoid full restart if D3 exit succeeded and reset is not required; otherwise the function sets `IWL_MVM_STATUS_HW_RESTART_REQUESTED` and returns restart-needed.

Fast suspend/resume is a reduced flow used while the mutex is already held. Fast suspend pauses TCM, marks D3/fast-resume, updates power, sends `D3_CONFIG_CMD`, and calls transport D3 suspend without switching images. Fast resume checks runtime firmware status, waits only for `D3_END_NOTIFICATION`, resumes TCM, clears D3/fast flags, and returns an error if the notification is missing or firmware failed.

## State and Persistence Behavior

The file stores GTK rekey material in `mvmvif->rekey_data`, IPv6 target/tentative addresses in `mvmvif`, default TX key index in `mvmvif->tx_key_idx`, key IV/ICV lengths in `mvm`, net-detect match/channel copies in `mvm->nd_match_sets` and `mvm->nd_channels`, D3 state in `mvm->status`, offloaded TID in `mvm->offload_tid`, `mvm->net_detect`, `mvm->fast_resume`, non-QoS sequence replay state in `mvmvif->seqno`, and wake debug counters under debugfs. Resume restores mac80211 key RX sequence numbers and driver per-queue PN mirrors for new RX API.

## Dependencies and Integration Points

This code integrates with cfg80211 WoWLAN and net-detect configuration, mac80211 key iteration and rekey APIs, station queues, firmware command version/capability negotiation, D3/D0 transport hooks, protocol offload, scheduled scan, regulatory/PPAG/SAR, firmware debug/runtime error reporting, notification wait infrastructure, and Linux PM wakeup reporting. Many paths require `mvm->mutex`; key iterators sometimes take and release it internally because mac80211 iteration requires non-atomic context.

## Risks

- The file supports many firmware command/notification versions. Wrong size/version selection for `WOWLAN_TSC_RSC_PARAM`, `WOWLAN_KEK_KCK_MATERIAL`, `WOWLAN_CONFIGURATION`, or status notifications can corrupt suspend/resume.
- Key counter conversion must preserve endian and per-TID semantics for TKIP/AES/GCMP and both old/new RX APIs; mistakes can trigger replay drops after resume.
- Wake packet reconstruction strips 802.11 IV/ICV/FCS differently for protected data and management frames; truncation handling is subtle.
- Non-unified-image D3 reprogramming manually recreates PHY/MAC/binding/STA/quota state and is sensitive to missing association or PHY context.
- Notification-based resume depends on expected/received bitmaps; missing wake-packet or D3-end notifications change reset behavior.
- Net-detect stores copies of match sets/channels and must free them on every error/resume path.

## Test Signals

Key validation includes suspend/resume with magic packet, pattern, disconnect, GTK rekey, EAP identity, 4-way handshake, TCP offload, rfkill release, net-detect, and non-wireless wake. Test with unified and non-unified firmware images, older and newer WoWLAN command versions, TKIP/CCMP/GCMP/BIP keys, MFP/beacon protection, wake packets with protected and unprotected frames, D3 firmware errors, reset-required D3 end flags, fast suspend/resume, and failed allocations/commands in suspend error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/d3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs-vif.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs-vif.c

## Purpose

This file creates and implements per-VIF and per-link debugfs entries for MVM. It exposes VIF power-management overrides, TX power limit, MAC/VIF state, beacon-filter parameters, OS/device time offset, low-latency flags, U-APSD misbehavior tracking, RX PHY info flags, quota minimum override, max TXOP override, FTM unprotected mode, and debugfs symlinks from device-level directories back to mac80211 netdev entries.

## Important APIs, Types, and Functions

- `iwl_mvm_vif_add_debugfs()` creates the VIF-level `iwlmvm` debugfs directory and files.
- `iwl_mvm_vif_dbgfs_add_link()` and `iwl_mvm_vif_dbgfs_rm_link()` maintain device-level symlinks to per-netdev debugfs directories.
- `iwl_mvm_link_add_debugfs()` creates link-level `iwlmvm` directories; `iwl_mvm_debugfs_add_link_files()` is currently a placeholder.
- `iwl_dbgfs_update_pm()` and `iwl_dbgfs_pm_params_write/read()` maintain per-VIF power-save debug overrides and re-send MAC power configuration.
- `iwl_dbgfs_update_bf()` and `iwl_dbgfs_bf_params_write/read()` maintain beacon-filter/beacon-abort debug overrides and enable/disable firmware beacon filtering.
- `iwl_dbgfs_mac_params_read()` reports VIF type, MAC ID/color, BSSID, TCM load, QoS parameters, AP station reduced TX power, and RX chain settings.
- Low-latency handlers use wiphy-locked debugfs writes and `iwl_mvm_update_low_latency()`.
- `iwl_dbgfs_rx_phyinfo_write()` updates `mvm->dbgfs_rx_phyinfo` and reprograms active PHY contexts.
- `iwl_dbgfs_quota_min_write()` enforces at most one VIF with a quota minimum override and updates quotas.

## Control Flow

Per-VIF debugfs registration creates an `iwlmvm` directory under `vif->debugfs_dir`. Power-management controls are created for station interfaces when the module power scheme is not CAM. Other generic VIF files are always added, with `bf_params` only for the station VIF currently allowed to use beacon filtering.

Writes parse user input from fixed-size buffers through macros in `debugfs.h`. PM writes identify a named parameter, validate where needed, lock `mvm->mutex`, update `mvmvif->dbgfs_pm`, and call `iwl_mvm_power_update_mac()`. Beacon-filter writes similarly validate named parameters, update `mvmvif->dbgfs_bf`, and call either `iwl_mvm_disable_beacon_filter()` or `iwl_mvm_enable_beacon_filter()`. Low-latency writes are routed through `wiphy_locked_debugfs_write()` and then serialized with `mvm->mutex`. RX PHY info writes update the global debug flag and walk active links, copying channel context data under RCU before sending PHY context changes outside the RCU section. Quota writes clear the current VIF override, scan all interfaces for another override, and only set/update quotas if no conflict exists.

## State and Persistence Behavior

Debugfs writes update driver runtime state: `mvmvif->dbgfs_pm`, `mvmvif->dbgfs_bf`, `mvmvif->low_latency`, `mvmvif->uapsd_misbehaving_ap_addr`, `mvm->dbgfs_rx_phyinfo`, `mvmvif->dbgfs_quota_min`, `mvmvif->max_tx_op`, and `mvmvif->ftm_unprotected`. These are debug overrides, not persistent configuration across driver reload. Symlink dentries are stored in `mvmvif->dbgfs_slink`.

## Dependencies and Integration Points

The file depends on debugfs, mac80211 VIF/link debugfs directories, MVM power, beacon filter, low-latency, PHY context, quota, TCM, station, and time-sync helpers. It uses `mvm->mutex`, RCU channel context access, wiphy-locked debugfs helpers, and the shared debugfs macro wrappers in `debugfs.h`.

## Risks

- Debugfs writes can actively reprogram firmware power, PHY, beacon filtering, quota, and latency behavior; invalid validation could destabilize live connections.
- Fixed-size input buffers truncate long writes by design; parsers must not assume full user input beyond the buffer.
- `mac_params` and quota iteration use shared runtime state and must remain properly serialized.
- RX PHY info reconfiguration copies channel context under RCU; future changes must not send firmware commands while holding RCU read lock.
- Link-level debugfs scaffolding exists but no per-link files are currently added; future link files should not duplicate VIF-private state accidentally.

## Test Signals

Enable `CONFIG_IWLWIFI_DEBUGFS` and verify file creation for station, P2P, AP, and monitor cases. Exercise PM and beacon-filter writes with valid/invalid bounds, low-latency force/unset transitions, RX PHY info reprogramming on active links, quota conflict detection across multiple VIFs, symlink creation/removal, and read output under association/disassociation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs-vif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs.c

## Purpose

This file implements device-level and link-station debugfs for MVM. It exposes firmware/device telemetry, thermal controls, CTDP controls, TX flush, SRAM and firmware memory access, station/rate/AMSDU state, power-off overrides, TAS/SAR/6E status, firmware and driver RX statistics, firmware restart/NMI triggers, scan antenna controls, RSS indirection, packet/beacon injection, firmware debug controls, HE sniffer configuration, LTR, RFI table access, NVM blobs, and PM-sleep debug flags.

## Important APIs, Types, and Functions

- `iwl_mvm_dbgfs_register()` creates all device-level entries under `mvm->debugfs_dir`.
- `iwl_mvm_link_sta_add_debugfs()` adds per-link-station `rs_data` and `amsdu_len` entries.
- CTDP/thermal controls include `iwl_dbgfs_ctdp_budget_read()`, `iwl_dbgfs_start_ctdp_write()`, `iwl_dbgfs_stop_ctdp_write()`, `iwl_dbgfs_force_ctkill_write()`, `iwl_dbgfs_set_nic_temperature_*()`, and `iwl_dbgfs_nic_temp_read()`.
- Memory/firmware access includes `iwl_dbgfs_sram_read/write()`, `iwl_dbgfs_prph_reg_read/write()`, and binary `iwl_dbgfs_mem_read/write()`.
- Statistics readers include `iwl_dbgfs_stations_read()`, `iwl_dbgfs_rs_data_read()`, `iwl_dbgfs_fw_rx_stats_read()`, `iwl_dbgfs_fw_system_stats_read()`, and `iwl_dbgfs_drv_rx_stats_read()`.
- Active controls include `iwl_dbgfs_tx_flush_write()`, `iwl_dbgfs_disable_power_off_write()`, `iwl_dbgfs_fw_restart_write()`, `iwl_dbgfs_fw_nmi_write()`, `iwl_dbgfs_scan_ant_rxchain_write()`, `iwl_dbgfs_indirection_tbl_write()`, `iwl_dbgfs_inject_packet_write()`, `_iwl_dbgfs_inject_beacon_ie()`, `iwl_dbgfs_fw_dbg_conf_write()`, `iwl_dbgfs_fw_dbg_clear_write()`, `iwl_dbgfs_dbg_time_point_write()`, `iwl_dbgfs_he_sniffer_params_write()`, `iwl_dbgfs_ltr_config_write()`, and `iwl_dbgfs_rfi_freq_table_write()`.
- Link-station wrappers `_iwl_dbgfs_link_sta_wrap_read/write()` resolve `struct ieee80211_link_sta` to MVM station/link private data under `mvm->mutex`.

## Control Flow

Registration initializes `drv_stats_lock`, adds device files via the shared debugfs macros, conditionally adds ACPI/SAR/6E, PM sleep, LTR, and PHY integration entries, creates NVM blobs, creates a binary `mem` file with custom file ops, and creates a symlink from mac80211 wiphy debugfs back to the device directory.

Most write handlers validate that firmware is running and often that the regular firmware image is active, parse a small text command, lock `mvm->mutex`, issue a firmware command or mutate driver state, unlock, and return either the original byte count or an error. Read handlers allocate or stack-build output buffers, optionally request fresh firmware statistics, copy state while holding the mutex or stats spinlock, then serve output via `simple_read_from_buffer()`.

Special flows include packet injection, which hex-decodes a synthetic RX packet into an allocated page and feeds it through `iwl_mvm_rx_mq()` in BH-disabled context; beacon IE injection, which locates an AP VIF, obtains a beacon template with extra tailroom, appends a hex-decoded IE, and sends per-link beacon template commands; and HE sniffer configuration, which installs a notification wait so `cur_aid`/`cur_bssid` are updated in RX ordering relative to firmware command processing.

The binary `mem` file maps file offsets to LMAC/UMAC debug memory commands. Reads align address and size to dwords, send `LMAC_RD_WR` or `UMAC_RD_WR`, and copy back only the requested unaligned slice. Writes choose byte or dword write op based on alignment and advance `ppos` by the accepted data size.

## State and Persistence Behavior

Debugfs state includes SRAM offset/length (`dbgfs_sram_offset`, `dbgfs_sram_len`), test temperature (`temperature_test`, `temperature`), station AMSDU original length overrides (`orig_amsdu_len`), power-off disable flags, scan RX antenna mask, firmware debug configuration, PRPH register address, HE sniffer AID/BSSID, beacon injection flags/tailroom, RFI behavior, driver RX frame stats protected by `drv_stats_lock`, and several booleans/blobs exposed directly by debugfs. These settings are runtime/debug state and generally disappear on driver unload or hardware restart, though some mutate live firmware state immediately.

## Dependencies and Integration Points

This file integrates with Linux debugfs, user-copy helpers, firmware command APIs, transport memory/prph access, mac80211 station/VIF/link state, RX path injection, beacon template generation, rate-control formatting, thermal/CTDP, regulatory SAR/TAS, ACPI DSM, RFI, LTR, RSS, firmware debug runtime, notification wait infrastructure, and NVM blob storage. It is compiled only when `CONFIG_IWLWIFI_DEBUGFS` is enabled.

## Risks

- Many entries are destructive or invasive: firmware restart/NMI, packet injection, raw memory writes, PRPH writes, TX flush, beacon injection, thermal override, and power-off overrides can destabilize a live device.
- Buffer sizing relies on fixed estimates for text output; new fields must preserve bounds.
- `iwl_dbgfs_indirection_tbl_write()` divides by `nbytes`; empty or odd-length input must remain guarded by caller/write semantics to avoid invalid repeat calculations.
- Memory read/write alignment and UMAC/LMAC selection are offset-sensitive and can target wrong address spaces.
- Beacon injection manipulates global `extra_beacon_tailroom` and must restore it on all paths.
- Link-station wrappers depend on link private data still existing under `mvm->mutex`; station teardown races should return `-ENODEV`.

## Test Signals

With debugfs enabled, verify file creation and permissions, read-only telemetry while firmware is running/not running, invalid input rejection for every write knob, TX flush on old/new TX APIs, SRAM window reads, binary memory read/write alignment, station and rate data after association, AMSDU override/revert, firmware restart/NMI debug triggers, scan antenna validation against valid RX antennas, RSS indirection hex patterns, packet injection validation, beacon IE inject/restore on AP mode, HE sniffer ordering, RFI table read/default resend, and PM sleep-only files when `CONFIG_PM_SLEEP` is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs.h

## Purpose

This header provides local macro helpers for defining MVM debugfs file operations. It removes repetitive boilerplate for read-only, write-only, and read/write debugfs entries that use typed private data and small text write buffers.

## Important APIs, Types, and Functions

- `MVM_DEBUGFS_READ_FILE_OPS(name)` creates a static `file_operations` with `.read = iwl_dbgfs_<name>_read`, `simple_open`, and `generic_file_llseek`.
- `MVM_DEBUGFS_WRITE_WRAPPER(name, buflen, argtype)` creates `_iwl_dbgfs_<name>_write()`, copies at most `buflen - 1` bytes from userspace into a zeroed stack buffer, casts `file->private_data` to `argtype *`, and calls the typed `iwl_dbgfs_<name>_write()` implementation.
- `_MVM_DEBUGFS_READ_WRITE_FILE_OPS(name, buflen, argtype)` combines the write wrapper with a read method in `file_operations`.
- `_MVM_DEBUGFS_WRITE_FILE_OPS(name, buflen, argtype)` creates write-only `file_operations`.

## Control Flow

Implementation files first define context-specific aliases for `MVM_DEBUGFS_WRITE_FILE_OPS` and `MVM_DEBUGFS_READ_WRITE_FILE_OPS` by binding `argtype` to `struct iwl_mvm`, `struct ieee80211_vif`, or another private type. When a user writes a debugfs file, the generated wrapper copies a bounded string from userspace, leaves it NUL-terminated because the stack buffer is zero-initialized, and dispatches to the typed handler.

## State and Persistence Behavior

The header stores no state. Its generated wrappers determine how much user input reaches debugfs handlers and how `file->private_data` is interpreted.

## Dependencies and Integration Points

It depends on Linux `struct file_operations`, `copy_from_user()`, `simple_open`, and `generic_file_llseek`. It is included by `debugfs.c` and `debugfs-vif.c`, which supply the actual read/write handlers and context-specific macro aliases.

## Risks

- The macros assume handler names and signatures exactly match the generated names.
- Fixed stack buffers intentionally truncate input to `buflen - 1`; handlers must treat `count`/`buf_size` as bounded input size.
- The `argtype *` cast relies on debugfs files being created with the matching private-data pointer.
- Because macros create static symbols, duplicate names in the same translation unit would collide.

## Test Signals

Compile coverage is the main validation for macro signature drift. Runtime debugfs tests should verify writes are NUL-terminated, oversized writes are bounded, invalid user pointers return `-EFAULT`, and each file is created with private data matching its wrapper type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mvm/debugfs.h -->
