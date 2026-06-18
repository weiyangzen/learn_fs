# subset-b-004829 research

Grouped research for Intel `iwlwifi` MLD files under `sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mlo.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mlo.c

Purpose: implements MLD multi-link operation policy, especially EMLSR entry, exit, blocking, retry, and active-link selection. It translates driver, firmware, scan, Bluetooth, channel-load, NAN, ROC, TDLS, and throughput signals into mac80211 `ieee80211_set_active_links*()` decisions.

Important APIs/functions: `iwl_mld_exit_emlsr()`, `iwl_mld_block_emlsr()`, `iwl_mld_block_emlsr_sync()`, `iwl_mld_unblock_emlsr()`, `iwl_mld_update_emlsr_block()`, `iwl_mld_emlsr_check_non_bss_block()`, `iwl_mld_emlsr_check_tpt()`, `iwl_mld_get_emlsr_rssi_thresh()`, KUnit-visible `iwl_mld_emlsr_pair_state()`, `iwl_mld_select_links()`, `iwl_mld_emlsr_check_bt()`, `iwl_mld_emlsr_check_chan_load()`, `iwl_mld_retry_emlsr()`, and NAN/TPT ignore helpers. Static helpers format reason masks, manage prevention timers, score link pairs, and collect link-selection inputs.

Control flow: block requests set `mld_vif->emlsr.blocked_reasons`, optionally cancel TPT work, and force exit to a kept link. Unblock clears one reason and triggers an internal MLO scan once all reasons are clear. Firmware EMLSR notifications either request leave or report transition failure; transition failure can disconnect all relevant interfaces or fall back to a firmware-validated link. Link selection starts from recent MLO scan results, filters stale BSS data, grades each usable link, then tries a two-link EMLSR pair if capability and blocker state allow it.

State and persistence: state is in `struct iwl_mld_vif::emlsr` fields, including blocker mask, selected links/primary, last entry/exit timestamps, repeated exit counters, delayed works, and MPDU counters attached to AP station data. Channel-load history persists in `struct iwl_mld_phy`. No disk persistence exists.

Dependencies and integration: depends on mac80211 MLO link APIs, `iwl_mld_vif/link/sta` private state, scan timestamps, channel context data, firmware ESR notifications, low-latency policy, Bluetooth coexistence, NAN and ROC modules, and KUnit export macros. It assumes callers hold the wiphy lock where asserted.

Risks: delayed work races can produce stale unblocks if blocker lifetime is mishandled; active-link changes are asynchronous in several paths; scan freshness warnings prevent link selection after stale scans; EMLSR channel-load decisions are invalid while EMLSR is active and explicitly clear averages on exit; pair scoring currently warns if more than two active links are supported. Test signals include KUnit coverage of `iwl_mld_emlsr_pair_state()`, forced blocker/unblock paths, firmware transition failure handling, stale scan handling, and TPT counter windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mlo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mlo.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mlo.h

Purpose: declares the MLO/EMLSR interface used by the rest of the MLD driver and provides inline helpers for common MLO state queries. It is the contract between link management, scan, NAN/ROC blocking, notification handling, and mac80211 callbacks.

Important APIs/types: inline `iwl_mld_emlsr_active()`, `iwl_mld_vif_has_emlsr_cap()`, `iwl_mld_max_active_links()`, `iwl_mld_count_active_links()`, `iwl_mld_get_primary_link()`, and `iwl_mld_get_other_link()` are the main call-site helpers. The exported declarations cover EMLSR delayed work callbacks, block/unblock/exit, firmware notification handlers, link selection, Bluetooth/channel-load/TPT retries, NAN blocking, and TPT ignore mode. `struct iwl_mld_link_sel_data` carries link id, chandef, signal, and grade into link-pair scoring.

Control flow: callers first use capability and active-link helpers to decide whether EMLSR logic is applicable. Blocking and retry APIs then route into `mlo.c` to change active links or schedule an internal MLO scan. Firmware notification handlers are declared here for table-driven dispatch in `notif.c`.

State and persistence: no storage is defined here, but helper semantics rely on `struct iwl_mld_vif` private state, `vif->active_links`, `IEEE80211_VIF_EML_ACTIVE`, firmware capability counts, and `mld->trans->info.hw_rf_id`. State survives only in kernel objects, not on disk.

Dependencies and integration: includes Linux/mac80211 headers plus local `iwl-config.h`, `iwl-trans.h`, `iface.h`, and `phy.h`. The capability helper rejects unauthorized VIFs, non-station/P2P station types, non-MLD VIFs, missing EMLSR capability, and CDB dual-radio hardware.

Risks and test signals: primary-link helper warns on empty active-link masks and AP-mode semantics differ from station mode. `iwl_mld_get_other_link()` is only well-defined for zero, one, or two active links and warns on larger counts. KUnit can access `iwl_mld_emlsr_pair_state()` when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/mlo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/nan.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/nan.c

Purpose: implements NAN support for MLD devices: capability detection, start/modify/stop configuration, aux-station lifecycle, EMLSR blocking while NAN is active, and NAN firmware notification delivery to cfg80211.

Important APIs/functions: `iwl_mld_nan_supported()` checks firmware capability. `iwl_mld_start_nan()`, `iwl_mld_nan_change_config()`, and `iwl_mld_stop_nan()` are mac80211/cfg80211 operation callbacks. `iwl_mld_handle_nan_cluster_notif()` and `iwl_mld_handle_nan_dw_end_notif()` translate firmware events to cfg80211. Cancellation callbacks always return true because NAN notifications are keyed by object type rather than a unique id.

Control flow: start blocks EMLSR globally for NAN, adds the VIF aux station, builds a full `NAN_CFG_CMD`, and rolls back aux station plus EMLSR blocker on failure. Change ignores the `changes` mask because firmware expects a complete configuration. Stop sends remove, flushes aux-station TX queues, removes the aux station, cancels queued NAN async notifications, and unblocks EMLSR. Cluster notifications validate that a NAN wdev exists and is started before reporting cluster join. DW-end notifications validate state, flush aux queues, choose a placeholder next channel from band, and notify cfg80211.

State and persistence: uses `mld->nan_device_vif`, `mld_vif->aux_sta.sta_id`, firmware NAN config, and queued async notification state. It persists only in live driver/mac80211 structures.

Dependencies and integration: depends on `fw/api/mac-cfg.h` NAN command structures, `iwl_mld_add_aux_sta()`, `iwl_mld_remove_aux_sta()`, `iwl_mld_flush_link_sta_txqs()`, `iwl_mld_update_emlsr_block()`, notification cancellation from `notif.c`, and cfg80211 NAN reporting APIs.

Risks and test signals: extra NAN/vendor attributes are concatenated into one duplicated host-command buffer, so length handling and allocation failures matter. The DW-end channel selection is marked TODO and currently maps band to fixed example channels. Tests should cover start rollback, stop cancellation, missing `nan_device_vif`, invalid DW band, optional 5 GHz config, saturated scan/dwell values, and EMLSR blocker symmetry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/nan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/nan.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/nan.h

Purpose: exposes the MLD NAN interface to mac80211 operation tables and notification dispatch.

Important APIs/types: declares `iwl_mld_nan_supported()`, start/change/stop callbacks taking `struct ieee80211_hw`, `struct ieee80211_vif`, and `struct cfg80211_nan_conf`, plus cluster and discovery-window-end notification handlers and cancellation callbacks.

Control flow: callers use the support helper before registering or accepting NAN operation, then route lifecycle callbacks through `nan.c`. `notif.c` uses the handler and cancellation declarations for `NAN_JOINED_CLUSTER_NOTIF` and `NAN_DW_END_NOTIF`.

State and persistence: no state is stored in the header. Implementations operate on live `struct iwl_mld`, `mld->nan_device_vif`, and aux-station state.

Dependencies and integration: includes cfg80211 and etherdevice headers. It intentionally relies on surrounding includes for `struct iwl_mld`, `struct iwl_rx_packet`, and mac80211 types, matching local driver header style.

Risks and test signals: cancellation callbacks take an `obj_id` even though NAN has no unique id, which is a useful signal for tests around object-type cancellation. Header consumers should verify NAN support before invoking lifecycle paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/nan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/notif.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/notif.c

Purpose: central receive-notification dispatcher for MLD firmware events. It separates data/RSS fast paths from table-driven notifications, validates firmware payload versions and sizes, handles selected sync notifications immediately, and queues async notifications onto wiphy work with object-aware cancellation.

Important APIs/functions: `iwl_mld_rx()`, `iwl_mld_rx_rss()`, `iwl_mld_async_handlers_wk()`, `iwl_mld_cancel_async_notifications()`, `iwl_mld_cancel_notifications_of_object()`, and `iwl_mld_delete_handlers()`. The visible `iwl_mld_rx_handlers[]` table maps command ids to handlers, contexts, payload size/version tables, object types, and cancellation functions. Static handlers cover MFUART, MU-MIMO group updates, CSA start/error, and beacon manager state.

Control flow: the primary RX entry checks MPDU, frame-release, RX queue sync, and sniffer notifications before falling back to `iwl_mld_rx_notif()`. The dispatcher scans the handler table, validates version and payload length, calls sync handlers inline, or steals the RX buffer page into an async list and queues `async_handlers_wk`. After dispatch it wakes notification waiters and records debug time points. Async work splices the pending list under a spinlock, then runs handlers under wiphy work context. Cancellation scans pending async entries by object type and object id.

State and persistence: owns `mld->async_handlers_list`, `mld->async_handlers_lock`, `mld->async_handlers_wk`, notification wait state, and `mld->ibss_manager`. State is in memory and is purged on cancellation/removal.

Dependencies and integration: integrates nearly every MLD submodule: scan, MCC, session protection, link, TX/RX, TLC, aggregation, thermal, ROC, stats, coexistence, time sync, FTM, NAN, and MLO. It depends on firmware command metadata for notification version lookup.

Risks and test signals: handler ordering matters for hot notifications; async handlers can be observed after later sync notifications; page stealing requires exactly one owner and proper freeing; version validation fallback appears inverted-risk-prone and should be covered by KUnit/fuzzed payload size cases. Tests should cover object cancellation for scan/ROC/NAN/STA/link, duplicate ROC cancellation races, RSS queue bounds, and handler table version coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/notif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/notif.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/notif.h

Purpose: declares the MLD notification/RX dispatch interface and the object-type vocabulary used to cancel queued async notifications safely.

Important APIs/types: exports normal and RSS RX entry points, async handler work, bulk async cancellation, command-specific handler deletion, and object cancellation. `enum iwl_mld_object_type` includes none, link, station, VIF, ROC, scan, FTM request, and NAN.

Control flow: transport callbacks call `iwl_mld_rx()` or `iwl_mld_rx_rss()`. Teardown paths call `iwl_mld_cancel_async_notifications()`, while object removal paths call `iwl_mld_cancel_notifications_of_object()` with an object type/id pair to prune queued work before object memory disappears.

State and persistence: the header stores no state. It defines the public contract for manipulating `mld->async_handlers_*` state owned by `notif.c`.

Dependencies and integration: forward-declares `struct iwl_mld` and references `struct iwl_op_mode`, `struct napi_struct`, `struct iwl_rx_cmd_buffer`, `struct wiphy`, and firmware packet types supplied by surrounding driver includes.

Risks and test signals: callers must pass a meaningful object type and firmware object id; `IWL_MLD_OBJECT_TYPE_NONE` is explicitly invalid for object cancellation. Tests should ensure all async object handlers use a matching enum and cancellation predicate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/notif.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/phy.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/phy.c

Purpose: manages firmware PHY context identifiers, channel-definition selection, control-channel encoding, PHY context commands, global PHY configuration, and cached channel definitions.

Important APIs/functions: `iwl_mld_allocate_fw_phy_id()`, `iwl_mld_get_chandef_from_chanctx()`, `iwl_mld_get_fw_ctrl_pos()`, `iwl_mld_phy_fw_action()`, `iwl_mld_send_phy_cfg_cmd()`, and `iwl_mld_update_phy_chandef()`. Static helpers detect FILS/FTM cases requiring full `ctx->def`, convert nl80211 bandwidths to firmware values, and derive valid antenna chain masks.

Control flow: allocation scans `mld->used_phy_ids` for a clear bit. Channel-definition selection iterates active interfaces and chooses full `ctx->def` for AP FTM responder or 6 GHz PSC/FILS-style cases, otherwise `ctx->min_def`. Firmware action builds `PHY_CONTEXT_CMD` from cached `phy->chandef`, optional puncturing and SBB/AP chandef, sends it, and logs failures. Global PHY config masks firmware config with valid TX/RX antennas and default calibration triggers.

State and persistence: updates in-memory `mld->used_phy_ids` and `struct iwl_mld_phy::chandef`. No disk persistence. `struct_group(zeroed_on_hw_restart)` in the header indicates `fw_id` and chandef are reset on hardware restart.

Dependencies and integration: depends on mac80211 channel contexts, cfg80211 channel definitions, firmware PHY context APIs, local host-command wrappers, antenna helpers from MLD core, and AP link settings.

Risks and test signals: control-position encoding is bit-sensitive for 80/160/320 MHz layouts; invalid bandwidth falls back to 20 MHz after warning; allocation has no locking internally and assumes caller serialization. Tests should cover fw id exhaustion, FILS/FTM chandef choice, puncturing propagation, SBB fields, and each control-channel offset class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/phy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/phy.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/phy.h

Purpose: defines the private PHY context state attached to mac80211 channel contexts and declares PHY command helpers.

Important APIs/types: `struct iwl_mld_phy` stores firmware id, cached chandef, channel load by device, averaged channel load by others, and back pointer to `struct iwl_mld`. `iwl_mld_phy_from_mac80211()` casts channel context private storage. `iwl_mld_cleanup_phy()` wraps `CLEANUP_STRUCT()`. Declarations expose fw id allocation, PHY action, chandef choice, control position conversion, global PHY config command, and chandef update.

Control flow: channel context setup code allocates/initializes this private structure, uses command helpers from `phy.c`, and later cleanup/restart paths zero the restart-sensitive group.

State and persistence: `zeroed_on_hw_restart` includes `fw_id` and `chandef`; channel-load statistics survive hardware restart. This is live kernel state only.

Dependencies and integration: includes `mld.h` and uses mac80211 `struct ieee80211_chanctx_conf` private storage. It integrates with MLO channel-load decisions in `mlo.c` and PHY context firmware programming in `phy.c`.

Risks and test signals: callers must not use stale `fw_id` after restart cleanup. Channel-load fields are used by EMLSR policy and need tests around clearing/updating across active-link transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/phy.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/power.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/power.c

Purpose: builds and sends device-level power, beacon filtering, per-MAC power-management, AP/TPE power constraints, and link transmit-power commands for MLD operation.

Important APIs/functions: `iwl_mld_update_device_power()`, `iwl_mld_enable_beacon_filter()`, `iwl_mld_disable_beacon_filter()`, `iwl_mld_update_mac_power()`, `iwl_mld_send_ap_tx_power_constraint_cmd()`, and `iwl_mld_set_tx_power()`. Static helpers handle station PS iteration, radar/DTIM skip checks, U-APSD command flags, TPE table min selection, AP power type mapping, and command-version-specific TX power layouts.

Control flow: device power enables power save unless CAM mode or any station VIF disables PS, and adds D3 no-sleep flags when requested. Beacon filtering is station-only and considers debugfs disable and CQM RSSI thresholds. MAC power chooses a representative active link for MLD VIFs, sets keepalive, returns early when PS is disabled or TDLS exists, then configures SMPS, LPRX, D3/low-latency/default timeouts, DTIM skipping, and U-APSD. AP constraints are sent only for active 6 GHz links.

State and persistence: reads `mld_vif->ps_disabled`, `vif->cfg.ps`, `link->queue_params`, debugfs flags, TDLS station count, and link TPE/power-type state. It sends firmware commands; no persistent local storage is created.

Dependencies and integration: depends on mac80211 BSS/link config, local MLD VIF/link helpers, constants, firmware power APIs, regulatory 6 GHz power types, and command-version lookup.

Risks and test signals: MLD MAC power uses the lowest active link because firmware accepts one config per VIF; this can misrepresent heterogeneous links. DTIM math must avoid zero beacon/DTIM periods. U-APSD QNDP TID selection depends on AC ordering and ACM flags. Tests should cover CAM vs PS, D3, radar channels, debugfs overrides, 6 GHz AP type mapping, default max TX power, command v10/v11 lengths, and inactive link skips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/power.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/power.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/power.h

Purpose: declares MLD power-management and transmit-power command helpers used by interface/link lifecycle code.

Important APIs/types: exported declarations cover device power update, beacon filter enable/disable, MAC power update, AP TX power constraint command, and per-link TX power setting.

Control flow: callers invoke these helpers when association, suspend/D3, link configuration, beacon filtering, 6 GHz TPE, or user/regulatory TX power state changes. The implementation translates mac80211 state into firmware commands.

State and persistence: no state is defined here. Functions operate on `struct iwl_mld`, `struct ieee80211_vif`, and `struct ieee80211_bss_conf` live state.

Dependencies and integration: includes mac80211 and local `mld.h`. Integrates with interface/link modules and regulatory information that populates link power type/TPE fields.

Risks and test signals: callers need correct serialization around link state and should avoid sending AP power constraints for inactive or non-6 GHz links. TX power units are driver-specific and are converted in implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/power.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ptp.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ptp.c

Purpose: provides a PTP hardware clock for the MLD device using the firmware/hardware GP2 timer, including adjusted time calculation, frequency/delta adjustments, wraparound tracking, cross-timestamp support, registration, and teardown.

Important APIs/functions: `iwl_mld_ptp_get_adj_time()`, `iwl_mld_ptp_init()`, and `iwl_mld_ptp_remove()` are exported. Static PTP callbacks implement gettime, unsupported settime, adjtime, adjfine, delayed wrap-check work, firmware cross timestamp read, and PHC cross timestamp conversion.

Control flow: gettime reads GP2, locks `ptp_data.lock`, converts GP2 microseconds to adjusted nanoseconds, and returns `timespec64`. adjtime accumulates `delta`. adjfine first snapshots adjusted time under the old scale, stores the new GP2 anchor, clears delta/wrap counter, and updates scaled frequency. A delayed work runs hourly to observe GP2 and detect wraps. Cross timestamp sends a firmware PTM read-both command under wiphy lock, validates response size, converts GP2 10 ns units to microseconds, then adjusts it through the same time-scale logic.

State and persistence: `struct ptp_data` holds `ptp_clock`, callback info, spinlock, delta, scale anchor GP2/adjusted ns, scaled frequency, last GP2, wrap counter, and delayed work. State is in memory and reset on removal.

Dependencies and integration: depends on Linux PTP clock APIs, timekeeping, direct PRPH GP2 register reads, firmware `WNM_PLATFORM_PTM_REQUEST_CMD`, host-command wrappers, and debug logging. `rx.c` can use `iwl_mld_ptp_get_adj_time()` for monitor-mode radiotap timestamps.

Risks and test signals: wrap detection distinguishes old reads from real wraps using a 5000 usec threshold; wrong thresholding affects long-running PHC accuracy. `settime` is intentionally unsupported. Tests should cover invalid GP2 sentinel, adjfine anchoring, wrap counter behavior, delayed work cancellation after unregister, response-size validation, and concurrent RX timestamp adjustment under the spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ptp.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ptp.h

Purpose: defines the MLD PTP clock state and declares the small public PTP API used by MLD init/teardown and RX timestamp paths.

Important APIs/types: `struct ptp_data` contains the registered PHC pointer, `ptp_clock_info`, spinlock, delta and scaling anchors, scaled frequency, GP2 wrap tracking, and delayed work. Declarations expose init, remove, and adjusted-time conversion.

Control flow: MLD initialization calls `iwl_mld_ptp_init()` to register the PHC and set callbacks; teardown calls remove; timestamp consumers call `iwl_mld_ptp_get_adj_time()` while holding `ptp_data.lock`.

State and persistence: all PTP state is live kernel memory; `last_gp2` and `wrap_counter` are reset on removal. No persistent clock calibration is stored here.

Dependencies and integration: includes Linux `ptp_clock_kernel.h` and relies on `struct iwl_mld` from surrounding headers. The state is embedded in `struct iwl_mld`.

Risks and test signals: the contract requires callers of adjusted-time conversion to hold the spinlock, enforced by lockdep in implementation. Tests should check lock discipline and initialization failure behavior where `ptp_clock_register()` returns error or NULL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/ptp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/regulatory.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/regulatory.c

Purpose: loads platform regulatory BIOS/UEFI data into firmware runtime state and sends SAR, geo SAR, SGOM, PPAG, LARI, AP type, and TAS commands to firmware.

Important APIs/functions: `iwl_mld_get_bios_tables()`, `iwl_mld_config_sar_profile()`, `iwl_mld_init_sar()`, `iwl_mld_init_sgom()`, `iwl_mld_init_ppag()`, `iwl_mld_configure_lari()`, `iwl_mld_init_ap_type_tables()`, and `iwl_mld_init_tas()`. Static helpers select geo SAR command version, send PPAG v7/v8 payloads, and derive LARI config bitmaps from DSM values.

Control flow: BIOS loading obtains GUID lock status, PPAG, WRDS/EWRD/WGDS, UEFI UATS/UNEB, and PHY filters, with WRDS absence suppressing geo SAR use. SAR init chooses default or user profiles, sends chain limits, and then geo tables if SAR is enabled. SGOM/PPAG are sent only when enabled/approved. LARI collects many DSM/WBEM feature bitmaps, masks them unless firmware accepts raw DSM, skips command if all fields are zero, and uses a shortened command for version 12. TAS requires firmware capability and BIOS table, then adjusts US/Canada block list unless DMI vendor is approved.

State and persistence: reads and populates `mld->fwrt` runtime regulatory fields such as table revisions/sources, SAR profiles, PPAG chains/flags, SGOM table, DSM metadata, AP type map, TAS data, and PHY filters. Persistent source is platform BIOS/UEFI; driver state is in memory.

Dependencies and integration: depends on `fw/regulatory.h`, ACPI, UEFI, DMI, host-command wrappers, firmware command-version lookup, and shared regulatory fill/approval helpers.

Risks and test signals: command versions 5/6, 7/8, 10/11, and LARI v12/newer have distinct layouts; table revision compatibility can silently skip PPAG send; positive SAR fill return means disabled profile and must not be treated as fatal. Tests should cover missing WRDS with WGDS present, unsupported command versions, raw DSM capability masking, TAS vendor block list growth, and command length selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/regulatory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/regulatory.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/regulatory.h

Purpose: declares regulatory initialization/configuration entry points for MLD firmware startup and runtime SAR profile changes.

Important APIs/types: declarations cover BIOS table loading, LARI configuration, AP type tables, TAS, PPAG, SGOM, SAR, and SAR profile configuration.

Control flow: startup paths call BIOS table loading before firmware configuration, then initialize SAR/SGOM/PPAG/LARI/AP type/TAS as supported. Runtime profile selection can call `iwl_mld_config_sar_profile()`.

State and persistence: no state is declared here. Implementations read platform ACPI/UEFI data into `mld->fwrt` and send firmware commands.

Dependencies and integration: includes local `mld.h`, tying regulatory operations to the MLD context and firmware runtime state.

Risks and test signals: callers must order table loading before command sends and respect return values where unsupported or disabled tables are nonfatal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/regulatory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/roc.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/roc.c

Purpose: implements remain-on-channel operations for P2P device, station hotspot, and management TX contexts, coordinating aux station setup, EMLSR blocking, firmware ROC commands, cancellation, and mac80211 ROC notifications.

Important APIs/functions: `iwl_mld_start_roc()`, `iwl_mld_cancel_roc()`, and `iwl_mld_handle_roc_notif()`. Static helpers find the VIF for a firmware ROC activity, block/unblock EMLSR across active interfaces, and destroy ROC state by resetting activity, synchronizing TX, flushing aux-station queues, and removing the aux station.

Control flow: start validates VIF type, maps mac80211 ROC type to firmware activity, rejects duplicate activity, blocks EMLSR, adds aux station, builds `ROC_CMD` add with 20 MHz channel, max delay, duration, station id, and node address, and records `mld_vif->roc_activity`. Cancel sends remove if active, cancels queued async ROC notification for the activity to handle races, then destroys local state. Firmware notification finds the VIF by activity, ignores stale canceled notifications, reports ready on successful start, otherwise cancels/removes and reports expiration.

State and persistence: state is `mld_vif->roc_activity` plus aux station state and queued async notifications. `synchronize_net()` ensures TX observes reset before queue flush/removal. No disk persistence.

Dependencies and integration: depends on mac80211 ROC APIs, firmware `ROC_CMD`/`ROC_NOTIF`, local aux-station helpers, notification cancellation, station TX flushing, MLO EMLSR blocking, and channel band conversion.

Risks and test signals: start error after aux-station add but failed command returns without local aux cleanup, which is a notable leak/race risk to audit. Duplicate activity detection assumes firmware supports one ROC per type. Tests should cover unsupported VIF types, P2P type mapping, duplicate activity, firmware start failure notification, cancel/notification race, and EMLSR blocker cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/roc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/roc.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/roc.h

Purpose: declares the MLD remain-on-channel interface used by mac80211 operations and notification dispatch.

Important APIs/types: `iwl_mld_start_roc()` starts a ROC on a requested channel/duration/type, `iwl_mld_cancel_roc()` cancels it for a VIF, and `iwl_mld_handle_roc_notif()` handles firmware completion/start notifications.

Control flow: mac80211 operation tables call start/cancel; `notif.c` dispatches `ROC_NOTIF` to the handler and can cancel queued async ROC notifications by object id/activity.

State and persistence: no state is defined here. Implementation uses `mld_vif->roc_activity`, aux station state, and async notification queue state.

Dependencies and integration: includes mac80211 and relies on local MLD structures from surrounding includes. ROC is tightly coupled to MLO EMLSR blocking and aux station management.

Risks and test signals: callers should hold the expected wiphy serialization. Tests should verify the activity value passed to notification cancellation matches firmware activity encoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/roc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/rx.c -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/rx.c

Purpose: implements the MLD RX MPDU data path and monitor/sniffer receive path: firmware descriptor parsing, PHY/radiotap metadata construction for legacy/VHT/HE/EHT/UHR-related status, station lookup, duplicate and PN validation, crypto status handling, SKB construction, reorder integration, RX queue synchronization, and no-data sniffer reporting.

Important APIs/functions: `iwl_mld_rx_mpdu()`, `iwl_mld_pass_packet_to_mac80211()`, `iwl_mld_sync_rx_queues()`, `iwl_mld_handle_rx_queues_sync_notif()`, and `iwl_mld_handle_phy_air_sniffer_notif()` are exported to notification dispatch and aggregation code. KUnit-visible helpers include `iwl_mld_is_dup()`. Major static helpers fill PHY data, signal, VHT/HE/EHT radiotap fields, LSIG, RX rate/status, SKB fragments, station-related counters, management protection status, crypto flags, and AMPDU state.

Control flow: `iwl_mld_rx_mpdu()` rejects hardware restart and malformed packet lengths, extracts descriptor PHY data, allocates a small SKB plus optional monitor space, fills band/frequency early, looks up station/link under RCU, drops duplicates, updates monitor AMPDU state, marks CRC/overrun failures, records TSF/boottime for management frames, fills rate/signal/radiotap status, processes crypto, builds the SKB from copied head plus optional stolen page fragment, diverts time-sync frames, runs reorder handling, and finally calls mac80211. Sniffer PHY notifications either produce zero-length PSDU radiotap packets immediately or cache PHY data for the next MPDU.

State and persistence: uses `mld->monitor` PHY/radiotap/AMPDU state, `mld->rxq_sync` wait queue/cookie/state, station duplicate data, PTK PN arrays, BAID last RX timestamps, low-latency counters, scan pass-all state, and per-link average beacon energy. It persists only in kernel memory.

Dependencies and integration: depends on mac80211 RX status/SKB APIs, iwl firmware RX descriptors, aggregation/reorder (`agg.c`), station/link maps, time sync, PTP for monitor timestamps, debugfs monitor configuration, firmware rate bit definitions, and notification routing from `notif.c`.

Risks: this is security- and correctness-sensitive. PN validation is skipped on default queue/multicast/non-data and relies on per-queue PTK PN state for RSS queues. Duplicate detection must handle A-MSDU subframes and same-PN allowance correctly. SKB construction steals RX pages and adjusts padding/MIC/FCS lengths, so length arithmetic and checksum validation are high risk. Radiotap EHT/HE bit mapping is macro-heavy and sensitive to spec/firmware layout drift. RX queue sync uses a one-second timeout and cookie matching; stale notifications are expected and checked.

Test signals: KUnit should exercise duplicate detection, same-PN A-MSDU behavior, rate/status decoding for CCK/OFDM/HT/VHT/HE/EHT/UHR, invalid descriptor lengths, crypto status branches including BIGTK management protection, monitor no-PSDU cases, cached sniffer PHY release, RXQ sync cookie/second-response handling, and SKB fragment offset calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/rx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/rx.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/rx.h

Purpose: declares RX data-path entry points and defines the internal RX-queue synchronization payloads shared between queue-sync command senders and notification handlers.

Important APIs/types: `enum iwl_mld_internal_rxq_notif_type` currently has empty sync and DELBA notification types. `struct iwl_mld_internal_rxq_notif` is a packed firmware-echoed internal payload with type, cookie, reserved alignment, and variable payload. `struct iwl_mld_rx_queues_sync` stores wait queue, cookie, and bitmask state. Function declarations expose MPDU handling, RX queue sync command, sync notification handling, packet pass-through to mac80211, and PHY air sniffer notification handling.

Control flow: aggregation or teardown code can call `iwl_mld_sync_rx_queues()` to broadcast an internal message to all RX queues and wait until `iwl_mld_handle_rx_queues_sync_notif()` clears each queue bit. Normal notification dispatch calls `iwl_mld_rx_mpdu()` for MPDUs and sniffer handler for PHY air notifications.

State and persistence: the state structure is embedded in `struct iwl_mld`; it is a live synchronization primitive with a monotonic cookie and bitmask, not persistent storage.

Dependencies and integration: includes local `mld.h`, uses NAPI, firmware RX command buffers/packets, and mac80211 station/SKB types. DELBA payload integration is implemented in aggregation code.

Risks and test signals: the internal payload must remain DWORD-aligned because firmware echoes it opaquely. Cookie handling is the primary stale-notification guard. Tests should verify variable payload sizing and that all RX queue bits clear before wait completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mld/rx.h -->
