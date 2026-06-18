# subset-b-005425 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_mlme_ext.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_mlme_ext.c

## Purpose

`rtw_mlme_ext.c` is the Realtek RTL8723BS staging driver's extended MAC-layer management engine. It owns 802.11 management-frame dispatch, AP and station authentication and association state machines, scan progression, IBSS/AP beacon construction, channel-plan handling, Block Ack negotiation, SA Query handling, MLME event reporting, and the command handlers that bridge the driver's command thread into hardware and firmware operations.

This file is not persistent storage code. Its durable state is in adapter-owned runtime structures such as `struct mlme_ext_priv`, `struct mlme_ext_info`, `struct mlme_priv`, `struct sta_priv`, `struct security_priv`, CAM key tables, firmware/hardware registers, timers, and command queues. The file is central to connection lifetime because it decides when the interface is scanning, linking, authenticated, associated, AP-mode serving stations, disconnecting, or restoring the operating channel after off-channel scan work.

## Important APIs, types, and functions

Key static dispatch tables are `mlme_sta_tbl[]`, mapping management subtypes to handlers, and `OnAction_tbl[]`, mapping action categories to action handlers. Important exported or cross-file entry points include `init_mlme_ext_priv()`, `free_mlme_ext_priv()`, `mgt_dispatcher()`, `issue_*()` management transmit helpers, `site_survey()`, `collect_bss_info()`, `start_clnt_join()`, `receive_disconnect()`, `report_*_event()`, timer handlers, and H2C command handlers such as `join_cmd_hdl()`, `sitesurvey_cmd_hdl()`, `setkey_hdl()`, and `add_ba_hdl()`.

The main data carriers are adapter substructures: `mlmeextpriv` holds current channel, bandwidth, scan result state, action duplicate cache, timers, and event sequence; `mlmext_info` holds connection state bits, current BSS, auth/assoc counters, HT/WMM state, key index, SA Query sequence, and firmware station slots; `mlmepriv` holds host MLME state, cfg80211-facing buffers, scanned queues, QoS/HT details, and WPS IEs; `stapriv` and `sta_info` hold station lists, per-station auth/assoc state, rates, AID, HT capability, reorder state, and sleep queues.

The file also defines channel plan tables, Realtek/WPA/WMM/WPS/P2P OUIs, and helper functions such as `rtw_ch_set_search_ch()`, `init_channel_set()`, `init_channel_list()`, `update_hidden_ssid()`, and `rtw_scan_ch_decision()`.

## Control flow

Initialization flows through `init_mlme_ext_priv()`: it stores the adapter pointer, resets MLME extension values, installs timers, initializes AP info, builds the regulatory channel set and P2P channel list, and enables active keepalive checks. `init_hw_mlme_ext()` then applies the current channel and bandwidth to hardware. Cleanup only deletes timers when the driver is stopped.

Receive management flow starts at `mgt_dispatcher()`, usually from the receive path after `validate_recv_mgnt_frame()`. It rejects non-management frames and frames not addressed to the interface or broadcast, checks duplicate management sequence numbers per station, picks the subtype handler, and switches auth handling between AP-side `OnAuth()` and client-side `OnAuthClient()`. Probe/beacon frames feed scanning and BSS update paths; auth/assoc frames advance AP or station state; deauth/disassoc reports disconnect; action frames delegate to spectrum, BACK, public, HT, and SA Query handlers.

AP association control is split between `OnAuth()` and `OnAssocReq()`. `OnAuth()` allocates or refreshes a station, maintains auth and assoc lists, supports open/shared-key auth including WEP challenge text, and transmits auth replies. `OnAssocReq()` validates authenticated state, SSID, supported rates, WPA/WPA2/WPS/WMM/HT capabilities, assigns an AID, moves the station to the associated list, updates AP capability state, stores the assoc request, sends the assoc response, and reports an add-station event.

Station association control starts in `join_cmd_hdl()`. It tears down an existing station link if necessary, resets join state, copies the selected `wlan_bssid_ex`, parses WMM and HT IEs, decides channel/bandwidth with `rtw_chk_start_clnt_join()`, writes BSSID and join state to hardware, switches channel, and enters `start_clnt_join()`. The station then waits for a beacon in `WIFI_FW_AUTH_NULL`, starts auth from `OnBeacon()` via `start_clnt_auth()`, handles auth response in `OnAuthClient()`, transmits assoc in `start_clnt_assoc()`, and finalizes from `OnAssocRsp()` by parsing WMM/HT/ERP IEs, storing the assoc response, and reporting join result.

Scanning starts in `sitesurvey_cmd_hdl()`. It copies requested SSIDs and channels, filters channels through the local channel plan, optionally sends null data to enter AP power-save mode before leaving the serving channel, disables dynamic PHY functions, sets initial gain and no-link MSR, marks hardware under site survey, and calls `site_survey()`. `site_survey()` switches to each channel, sends active probe requests when allowed, arms `survey_timer`, reports BSS records from beacons/probe responses with `report_survey_event()`, then restores channel/bandwidth, MSR, dynamic functions, and null-data wake state before reporting survey done.

Transmit management helpers all allocate an extended xmit frame and xmit buffer, populate 802.11 headers and IEs, update `mgnt_seq`, set packet attributes, and submit through `rtw_hal_mgnt_xmit()` or an ack/wait variant. This includes beacon, probe response/request, auth, assoc response/request, null data, QoS null data, deauth, SA Query, BA actions, and 20/40 coexistence public actions.

Command and timer flows keep the state machine moving. `link_timer_hdl()` handles auth-null timeout, re-auth retries, and re-assoc retries. `survey_timer_hdl()` requeues `_SiteSurvey` commands and handles scan abort. `sa_query_timer_hdl()` disconnects when protected-management SA Query times out. H2C handlers set op mode, create BSS, join, disconnect, set auth/key/station-key, request ADDBA, send queued multicast frames, transmit beacon, change channel/channel plan, and run a callback in the command thread.

## State and persistence behavior

All state is volatile and adapter-scoped. Important counters include `event_seq`, `mgnt_seq`, `sa_query_seq`, auth/reassoc/link retry counts, scan channel index and BSS count, and AP alive retry counters. Timers persist state transitions across asynchronous gaps. CAM programming through `write_cam()`, hardware registers such as `HW_VAR_BSSID`, `HW_VAR_MLME_JOIN`, `HW_VAR_SEC_CFG`, and `HW_VAR_H2C_FW_PWRMODE`, and beacon/TIM updates are side effects outside normal memory but are still runtime device state.

The file updates stored association buffers in `mlmepriv->assoc_req` and `assoc_rsp`, stores AP-side per-station assoc request copies, and updates channel plans after Country IE processing. It never writes files or stable on-disk configuration.

## Dependencies and integration points

The module depends on `drv_types.h`, `rtw_wifi_regd.h`, `hal_btcoex.h`, Linux timer/work/memory primitives, cfg80211 notification helpers, and many local driver helpers from receive, transmit, station, security, command, AP, HT, WMM, HAL, and regulatory layers. Integration points include `rtw_enqueue_cmd()` for MLME events and H2C commands, `rtw_hal_set_hwreg()` and `rtw_hal_get_hwreg()` for device state, `rtw_cfg80211_rx_action()` for public action frames, Bluetooth coexistence notifications, `rtw_lps_ctrl_wk_cmd()` for power-save state, CAM key management, and AP-mode beacon/TIM update functions.

`rtw_recv.c` invokes `mgt_dispatcher()` after management-frame validation. `rtw_pwrctrl.c` and transmit code depend on `issue_nulldata()`, `issue_qos_nulldata()`, and LPS connect/disconnect notifications. AP data-path power-save behavior depends on station state established by this file.

## Risks and edge cases

Several frame-building paths return after allocating transmit resources without freeing them on some error branches, for example oversized beacon/probe response IE paths. This is important in AP mode because malformed or oversized IEs could leak xmit resources over repeated attempts.

`rtw_ch_set_search_ch()` uses `if (i >= ch_set[i].ChannelNum)` after the loop, which compares an index to a channel number rather than to a channel-set size. The zero sentinel often makes this work for not-found cases, but the condition is suspicious and should be regression-tested before reuse.

Much parsing uses raw offsets into received IEs and frame bodies. Many paths check top-level lengths, but several loops trust IE lengths while incrementing through `pnetwork->ies` or received bodies. Fuzzing malformed management frames, especially vendor IEs, HT IEs, Country IEs, and action frames, is high-value.

State changes are split across timers, command thread, receive context, and AP station lists. Locking is present for station auth/assoc lists and beacon updates, but many `mlmeext_info` fields are updated without a dedicated lock. Tests should watch for races during scan while disconnecting, reconnect while link timer fires, AP station re-auth during timeout, and protected-management SA Query timeout during deauth.

802.11w handling is split with receive validation in `rtw_recv.c` and SA Query actions here. Robust-management failures should be tested because incorrect failures can disconnect valid protected sessions or accept unauthenticated teardown frames.

## Test signals

Useful signals are successful init/free with timers, complete active and passive scans, survey event counts, channel restoration after scan, station open and shared-key auth, WPA/WPA2/WPS assoc acceptance and rejection paths, AP station AID allocation exhaustion, WMM/HT capability negotiation, ADDBA request/response/DELBA behavior, null-data and QoS-null LPS transitions, SA Query timeout disconnect, 802.11d Country IE channel-plan changes, and correct event callbacks for join, add STA, del STA, WMM, survey, and survey done. Kernel tests should include malformed IE fuzzing, repeated beacon/probe response generation with oversized IEs to detect leaks, and concurrent scan/disconnect/join stress with lockdep and KASAN enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_mlme_ext.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_pwrctrl.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_pwrctrl.c

## Purpose

`rtw_pwrctrl.c` implements runtime power management for the RTL8723BS driver. It controls inactive power save (IPS), leisure power save (LPS), firmware RPWM/CPWM state transitions, task-alive accounting for command and transmit paths, power-save deny masks, and public configuration setters for LPS/IPS modes.

The file keeps the adapter and firmware in a state where the NIC can sleep when idle but wake reliably before IO, transmit, command processing, scan, join, AP mode, or system suspend constraints require full power. Its state is volatile and stored in `struct pwrctrl_priv`, with side effects in firmware registers, timers, work items, and Bluetooth coexistence notifications.

## Important APIs, types, and functions

Important entry points include `ips_enter()`, `ips_leave()`, `rtw_ps_processor()`, `traffic_check_for_leave_lps()`, `rtw_set_rpwm()`, `rtw_set_ps_mode()`, `LPS_Enter()`, `LPS_Leave()`, `LeaveAllPowerSaveModeDirect()`, `LeaveAllPowerSaveMode()`, `LPS_Leave_check()`, `cpwm_int_hdl()`, task-alive functions (`rtw_register_task_alive()`, `rtw_unregister_task_alive()`, `rtw_register_tx_alive()`, `rtw_register_cmd_alive()`, `rtw_unregister_tx_alive()`, `rtw_unregister_cmd_alive()`), `rtw_init_pwrctrl_priv()`, `_rtw_pwr_wakeup()`, `rtw_pm_set_lps()`, `rtw_pm_set_ips()`, and the power-save deny helpers.

The core state object is `struct pwrctrl_priv`, reached through `adapter_to_pwrctl()` or `dvobj_to_pwrctl()`. Critical fields are `rf_pwrstate`, `change_rfpwrstate`, `ips_mode`, `ips_mode_req`, `bips_processing`, `bpower_saving`, `bkeepfwalive`, `ps_processing`, `pwr_mode`, `power_mgnt`, `bLeisurePs`, `fw_current_in_ps_mode`, `rpwm`, `cpwm`, `tog`, `cpwm_tog`, `brpwmtimeout`, `alives`, `ps_deny`, `ips_deny_time`, suspend flags, timers, and work items.

## Control flow

IPS entry is driven by `rtw_ps_processor()`, normally reached through the power-state check timer and command path. It first checks the `ps_deny` mask, suspend status, requested IPS mode, and `rtw_pwr_unassociated_idle()`. The idle check rejects power-down if the interface or buddy is associated, linking, scanning, AP/IBSS, under WPS, already saving power, within the IPS deny window, or holding non-free transmit buffers. Every fourth check while RF is on, the processor sets `change_rfpwrstate = rf_off` and calls `ips_enter()`, which notifies Bluetooth coexistence, takes the power lock, and calls `_ips_enter()` to power down hardware through `rtw_ips_pwr_down()`.

IPS leave uses `ips_leave()` and `_ips_leave()`. If RF is off and no IPS transition is active, it marks processing, requests `rf_on`, calls `rtw_ips_pwr_up()`, updates `rf_pwrstate`, clears firmware-alive and power-saving flags, unlocks, and notifies coexistence with `IPS_NONE`.

LPS entry uses `LPS_Enter()`. It rejects Bluetooth-controlled LPS, requires exactly one associated interface, reuses `PS_RDY_CHECK()`, waits through an idle counter, and calls `rtw_set_ps_mode()` with the configured `power_mgnt` mode. LPS leave uses `LPS_Leave()` or `LeaveAllPowerSaveMode*()`, sets active mode, raises RPWM to awake state, optionally waits for firmware RF-on with `LPS_RF_ON_check()`, and clears `bpower_saving`.

`rtw_set_ps_mode()` is the main firmware power-mode setter. For active mode, it raises RPWM to `PS_STATE_S4`, sends `HW_VAR_H2C_FW_PWRMODE`, clears `fw_current_in_ps_mode`, and notifies coexistence unless BT owns LPS. For sleep modes, it requires `PS_RDY_CHECK()` or BT-owned LPS, stores smart-PS and antenna mode, sends firmware power mode, picks a target RPWM level (`S0` if no tasks alive, `S2` otherwise or per BT constraint), and calls `rtw_set_rpwm()`.

`rtw_set_rpwm()` writes requested power state to firmware through `HW_VAR_SET_RPWM`. It avoids redundant transitions, handles surprise removal and driver-stopped constraints, toggles the RPWM toggle bit, adds `PS_ACK` when waking from low states to S2 or higher, arms a timeout timer, and polls CPWM for a matching toggle until `LPS_RPWM_WAIT_MS` expires. Timeout work either synthesizes CPWM S2 for a non-0xEA register condition or retries RPWM with `brpwmtimeout` set.

Task-alive registration is used by command and transmit paths before touching firmware in LPS. Register functions set `CMD_ALIVE`, `XMIT_ALIVE`, or a caller tag, request RPWM S2 when firmware is asleep, and can return `_FAIL` until CPWM rises. Unregister functions clear the bit and lower RPWM toward S0 only when no alive tasks remain or BT requires S2.

Wakeup flow in `_rtw_pwr_wakeup()` leaves all power-save modes, updates the IPS deny window, waits up to about 3 seconds for power processing or autosuspend to clear, rejects system suspend or net-closed autosuspend, leaves IPS if RF is off, and finally validates driver-up and hardware-init state.

## State and persistence behavior

All persisted information is in memory for the adapter lifetime. Initialization sets RF on, IPS/LPS modes from registry settings, CPWM S4, RPWM 0, active power mode, smart-PS parameters, timers, work items, suspend flags, counters, and wake-on-WLAN flags. No file or NVRAM state is written.

The firmware-visible state is updated with HAL register calls: `HW_VAR_SET_RPWM`, `HW_VAR_CPWM`, `HW_VAR_H2C_FW_PWRMODE`, and `HW_VAR_FWLPS_RF_ON`. The power lock protects most `pwrctrl_priv` transitions. The timer and work item split is important: timer handlers avoid IO and schedule work when a register retry is needed.

## Dependencies and integration points

This module depends on `drv_types.h`, `hal_data.h`, jiffies/timers, HAL power-up/down hooks (`rtw_ips_pwr_down()`, `rtw_ips_pwr_up()`), Bluetooth coexistence (`hal_btcoex_*`), MLME state checks, cfg80211 power-management policy, transmit and command completions, and `rtw_lps_ctrl_wk_cmd()` for queued LPS control. `rtw_recv.c` calls `traffic_check_for_leave_lps()` after RX traffic, and transmit paths call the same helper for TX bursts. MLME connection callbacks call LPS controls when connecting or disconnecting.

## Risks and edge cases

`traffic_check_for_leave_lps()` uses static `start_time` and `xmit_cnt`, so TX traffic accounting is shared across adapters instead of per adapter. In multi-interface scenarios this can leave LPS too early or too late.

Several paths busy wait with `mdelay()` or one-millisecond polling. `_rtw_pwr_wakeup()` can spin for up to roughly 3 seconds while waiting for suspend or power processing, and `rtw_set_rpwm()` polls CPWM. These paths must remain out of atomic context and can affect resume or command latency.

Task-alive registration can initially return `_FAIL` then recheck CPWM after unlocking. Callers must be prepared for transient failure during wake. Missed unregister calls would pin firmware at a higher power state, while premature unregister could lower RPWM while command or transmit work still needs IO.

Power mode transitions are coordinated with Bluetooth coexistence policy. Tests need to cover both BT-controlled and Wi-Fi-controlled LPS because branches can suppress or override normal state changes.

IPS decisions assume transmit buffer counts are fully free before powering down. Any accounting leak in xmit buffers can block IPS indefinitely; any false free count can power down while work remains.

## Test signals

Important test signals include IPS entering only while unassociated and idle, IPS leave restoring RF and clearing `bpower_saving`, LPS entering after the idle threshold, LPS leave on RX/TX bursts, `LeaveAllPowerSaveMode()` behavior when linked and unlinked, RPWM/CPWM timeout recovery, command/transmit alive registration under LPS, suspend/autosuspend wake rejection, `rtw_pm_set_lps()` and `rtw_pm_set_ips()` return values for invalid modes, PS deny mask behavior, and Bluetooth coexistence ownership of LPS. Instrumenting `rf_pwrstate`, `pwr_mode`, `fw_current_in_ps_mode`, `rpwm`, `cpwm`, `alives`, and HAL power-mode writes gives the clearest regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_pwrctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_recv.c -->
# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_recv.c

## Purpose

`rtw_recv.c` is the core receive pipeline for RTL8723BS. It initializes receive-frame pools, validates 802.11 control/management/data frames, handles duplicate and fragment reassembly, decrypts WEP/TKIP/AES payloads when needed, enforces 802.1X port control, converts 802.11 payloads to Ethernet skbs, handles A-MSDU and A-MPDU reorder delivery, forwards AP-mode traffic, updates RX statistics and signal averages, and dispatches management frames into `rtw_mlme_ext.c`.

The file is stateful but not persistent on disk. It mutates `recv_priv`, per-station receive state, security state, MLME link-detect counters, reorder queues, timers, and network stack skbs.

## Important APIs, types, and functions

Initialization and queue APIs include `_rtw_init_sta_recv_priv()`, `_rtw_init_recv_priv()`, `_rtw_free_recv_priv()`, `_rtw_alloc_recvframe()`, `rtw_alloc_recvframe()`, `rtw_free_recvframe()`, `_rtw_enqueue_recvframe()`, `rtw_enqueue_recvframe()`, `rtw_free_recvframe_queue()`, `rtw_free_uc_swdec_pending_queue()`, and recv-buffer enqueue/dequeue helpers.

Security and validation helpers include `rtw_handle_tkip_mic_err()`, `recvframe_chkmic()`, `decryptor()`, `portctrl()`, `recv_decache()`, `validate_recv_ctrl_frame()`, `recvframe_defrag()`, `recvframe_chk_defrag()`, `validate_recv_mgnt_frame()`, `validate_recv_data_frame()`, `validate_80211w_mgmt()`, and `validate_recv_frame()`.

Indication and aggregation helpers include `wlanhdr_to_ethhdr()`, `rtw_alloc_msdu_pkt()`, `rtw_recv_indicate_pkt()`, `amsdu_to_msdu()`, `check_indicate_seq()`, `enqueue_reorder_recvframe()`, `rtw_recv_indicatepkt()`, `recv_indicatepkts_in_order()`, `recv_indicatepkt_reorder()`, `rtw_reordering_ctrl_timeout_handler()`, `process_recv_indicatepkts()`, and the top-level `rtw_recv_entry()`.

The main data types are `union recv_frame`, `struct recv_frame_hdr`, `struct rx_pkt_attrib`, `struct recv_priv`, `struct sta_recv_priv`, `struct stainfo_rxcache`, `struct recv_reorder_ctrl`, `struct sta_info`, `struct security_priv`, and Linux `struct sk_buff`.

## Control flow

Receive setup allocates `NR_RECVFRAME` aligned `union recv_frame` objects with `vzalloc()`, links them onto `free_recv_queue`, initializes pending and software-decrypt queues, delegates HAL receive init, and starts the signal-stat timer. Freeing drains the unicast software-decrypt pending queue, frees attached skbs, releases the frame pool, and calls HAL cleanup.

The top-level data path is `rtw_recv_entry() -> recv_func()`. `recv_func()` first drains queued unicast frames that were waiting for TKIP key availability, then calls `recv_func_prehandle()` to validate frame control, address roles, station lookup, duplicate sequence, QoS fields, privacy flags, and encryption metadata. Some station-mode encrypted unicast frames are queued on `uc_swdec_pending_queue` until `busetkipkey` is ready, with a starvation escape when free frames drop below one quarter of the pool. Valid frames continue to `recv_func_posthandle()`.

`recv_func_posthandle()` decrypts when hardware did not or software decrypt is forced, performs fragment reassembly, applies 802.1X port control so blocked stations only pass EAPOL, updates RX statistics and LPS traffic checks, and delivers through `process_recv_indicatepkts()`. For HT mode, `recv_indicatepkt_reorder()` handles A-MPDU reorder windows; for non-HT mode, frames are converted directly to Ethernet and indicated.

Management frames are handled inside validation rather than the data indication pipeline. `validate_recv_frame()` calls `validate_80211w_mgmt()` for protected-management checks, then `validate_recv_mgnt_frame()`, which defragments, updates station management statistics, and calls `mgt_dispatcher()` in `rtw_mlme_ext.c`. The function then forces a non-success return so management frames are freed by the prehandle path and not indicated as data.

Control frames are mostly filtered. `validate_recv_ctrl_frame()` accepts only frames addressed to this device with known station info, counts control packets, and handles PS-Poll in AP mode by dequeuing a sleeping station's buffered frame, updating TIM, or sending a null data frame when no buffered packet remains. Control frames are also forced out of the data path after handling.

Data validation splits by ToDS/FromDS bits. `sta2sta_data_frame()` handles IBSS, station, AP, and MP address semantics for no-DS frames. `ap2sta_data_frame()` validates AP-to-station traffic for linked or linking station mode, rejects wrong BSSID and can issue deauth for class-3 errors, counts no-data frames, and has MP/AP special cases. `sta2ap_data_frame()` handles AP-mode station-to-AP traffic, validates BSSID, deauths non-associated stations, processes power-management and WMM-PS triggers, and counts no-data frames.

Decryption uses the IV key index, current security algorithm, and software cipher helpers. TKIP MIC verification is performed after defrag for privacy frames, using group or pairwise MIC keys, reporting Michael MIC failures through cfg80211 and legacy wireless event data, and enforcing group-key check state.

Ethernet indication first removes WLAN headers, IV/ICV, and RFC1042 or bridge-tunnel SNAP headers when appropriate. A-MSDU frames are split into sub-skbs up to `MAX_SUBFRAME_COUNT` with padding handling. AP-mode indication may bridge/forward frames back into the transmit path for associated local stations or multicast clones before delivering remaining traffic to the host stack with `eth_type_trans()` and `rtw_netif_rx()`.

Reorder control uses per-TID `recv_reorder_ctrl`. `check_indicate_seq()` maintains a 12-bit sequence window, `enqueue_reorder_recvframe()` inserts frames in sequence order and rejects duplicates, `recv_indicatepkts_in_order()` drains ready frames or forced timeout frames, and `rtw_reordering_ctrl_timeout_handler()` forces delivery when a gap remains past `REORDER_WAIT_TIME`.

Signal statistics are periodically smoothed by `rtw_signal_stat_timer_hdl()`. It consumes sampled average signal strength and quality, skips updates while surveying or not linked, supports a debug override, converts percentage to dBm, and rearms the timer.

## State and persistence behavior

Receive frame ownership moves among free, pending, software-decrypt, defrag, reorder, and indication paths. Each `union recv_frame` can own an skb until `rtw_recv_indicatepkt()` nulls the frame's `pkt` pointer after handoff. Per-station state includes duplicate sequence cache, defrag queue, reorder queues and timers, sleep queues, RX counters, QoS/UAPSD flags, and HT reorder state.

Security state includes TKIP countermeasure timestamps, group key installed/check flags, software decrypt configuration, hardware decrypt observations, and BIP/802.11w key availability. MLME state is updated indirectly via link-detect RX counters and management dispatch. No on-disk persistence exists.

## Dependencies and integration points

The module depends on `drv_types.h`, `rtw_recv.h`, cfg80211, Linux skb/list/timer primitives, local security helpers (`rtw_wep_decrypt()`, `rtw_tkip_decrypt()`, `rtw_aes_decrypt()`, `rtw_seccalctkipmic()`, `rtw_BIP_verify()`), station lookup, AP sleep-queue transmit helpers, MLME state helpers, `mgt_dispatcher()` from `rtw_mlme_ext.c`, `issue_deauth()`, `issue_qos_nulldata()`, `issue_nulldata_in_interrupt()`, LPS traffic checks from `rtw_pwrctrl.c`, HAL receive init/free and debug access, and netdevice receive/forwarding APIs.

It is tightly coupled to `rtw_mlme_ext.c`: management frames validated here drive auth, assoc, scan, beacon, action, and disconnect behavior there. It is also coupled to AP transmit buffering and power save through PS-Poll and WMM-PS handling.

## Risks and edge cases

`recv_func_posthandle()` increments `precvpriv->rx_drop` at the `_recv_data_drop` label even on the normal success fallthrough path. That makes the drop counter suspect for all successfully posthandled data frames and should be verified before using it as a reliability metric.

Length handling is security-sensitive. A-MSDU parsing checks subframe bounds, but malformed SNAP, short encrypted payloads, bogus QoS headers, fragment sequences, and protected-management frames should be fuzzed because many calculations subtract header, IV, ICV, MIC, or SNAP lengths from frame length.

Defrag and reorder queues manipulate receive-frame lists in paths where some spin locks are commented out because callers already hold locks or the code assumes single-threaded receive context. Any future parallel receive changes need careful lock auditing.

TKIP MIC handling relies on key-index timing exceptions for multicast frames and reports countermeasures only when `bdecrypted` is set. Rekey timing should be tested because false MIC errors can trigger countermeasures and dropped traffic.

AP-mode forwarding clones multicast skbs and may pass the original skb into transmit before optionally continuing with a clone. Ownership is subtle; regressions here can cause skb leaks, double frees, or local-delivery loss.

802.11w management validation allocates a temporary buffer for decrypted management body and rewrites the receive frame in place. Allocation failure, decrypt failure, and MME verification paths all drop the frame; protected deauth/disassoc/action coverage is important.

## Test signals

Useful tests include receive pool allocation/free under pressure, queue count consistency, malformed management/data/control frame rejection, ToDS/FromDS address validation in station/AP/IBSS/MP modes, duplicate sequence drops per TID, fragment reassembly success and failure, WEP/TKIP/AES software and hardware decrypt paths, TKIP MIC success/failure and countermeasure timing, 802.1X blocked station EAPOL-only behavior, PS-Poll and WMM-PS AP delivery, A-MSDU split with padding and max subframes, A-MPDU reorder in-order/out-of-order/timeout delivery, AP local forwarding and multicast clone behavior, management dispatch into scan/auth/assoc handlers, and signal-stat smoothing while linked, unlinked, surveying, and debug-forced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_recv.c -->
