# sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_cmd.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/staging/rtl8723bs/core/rtw_cmd.c` implements the RTL8723BS host command/event worker layer. It owns initialization and teardown of `cmd_priv` and `evt_priv`, the serialized command queue consumed by `rtw_cmd_thread()`, wrappers that build MLME/security/power-management command objects, command completion callbacks, and deferred C2H/driver-extra work dispatch. The file was read completely as a 1931-line source file.

## Important APIs, Types, and Functions

Primary exported entry points include `rtw_init_cmd_priv()`, `rtw_init_evt_priv()`, `rtw_free_cmd_priv()`, `rtw_free_evt_priv()`, `rtw_enqueue_cmd()`, `rtw_dequeue_cmd()`, `rtw_stop_cmd_thread()`, and `rtw_cmd_thread()`. Command constructors include `rtw_sitesurvey_cmd()`, `rtw_createbss_cmd()`, `rtw_startbss_cmd()`, `rtw_joinbss_cmd()`, `rtw_disassoc_cmd()`, `rtw_setopmode_cmd()`, `rtw_setstakey_cmd()`, `rtw_clearstakey_cmd()`, `rtw_addbareq_cmd()`, `rtw_reset_securitypriv_cmd()`, `rtw_free_assoc_resources_cmd()`, and the deferred-work helpers such as `rtw_dynamic_chk_wk_cmd()`, `rtw_lps_ctrl_wk_cmd()`, `rtw_dm_in_lps_wk_cmd()`, `rtw_dm_ra_mask_wk_cmd()`, `rtw_ps_cmd()`, `rtw_chk_hi_queue_cmd()`, `rtw_c2h_packet_wk_cmd()`, and `rtw_c2h_wk_cmd()`.

The central static tables are `rtw_cmd_callback[]`, mapping command codes to post-handler callbacks, and `wlancmds[]`, mapping command codes to MLME extension handlers such as `join_cmd_hdl`, `disconnect_hdl`, `createbss_hdl`, `setopmode_hdl`, `sitesurvey_cmd_hdl`, `setauth_hdl`, `setkey_hdl`, `set_stakey_hdl`, `add_ba_hdl`, `set_ch_hdl`, `tx_beacon_hdl`, `mlme_evt_hdl`, `rtw_drvextra_cmd_hdl`, `h2c_msg_hdl`, `set_chplan_hdl`, `set_csa_hdl`, `tdls_hdl`, `chk_bmc_sleepq_hdl`, and `run_in_thread_hdl`. `struct cmd_obj`, `struct cmd_priv`, `struct evt_priv`, `struct drvextra_cmd_parm`, `struct submit_ctx`, and command parameter structs declared in driver headers are the main data types touched here.

## Control Flow

Initialization sets up completions, spinlocks, queue heads, command/rsp buffers, sequence counters, and the submit-context mutex. `rtw_enqueue_cmd()` stamps the adapter pointer, applies `rtw_cmd_filter()`, appends the command under the queue spinlock, and completes `cmd_queue_comp`. `rtw_cmd_filter()` drops most commands if hardware initialization has not completed or if the command thread is not running; `_SetChannelPlan` is the explicit early-allowed exception.

`rtw_cmd_thread()` waits on `cmd_queue_comp`, exits on stop/surprise-removal conditions, registers command activity with the power-control layer, drains every pending command, copies command parameters into the shared aligned command buffer, calls the matching `wlancmds[]` handler, resolves any synchronous `submit_ctx`, then invokes the matching callback or frees the command. Shutdown drains remaining queue entries and frees command parameters, including nested `drvextra_cmd_parm->pbuf` for `_Set_Drv_Extra`.

Command-constructor flow is consistent: allocate a `cmd_obj`, allocate or borrow a parameter buffer, fill command-specific fields, call `init_h2fwcmd_w_parm_no_rsp()` or manual setup, and enqueue. Some helpers support direct execution when `enqueue` is false, such as disassociation, opmode setup, key setup, and start-BSS paths. Join flow is richer: `rtw_joinbss_cmd()` copies the target BSS into `securitypriv.sec_bss`, rewrites security/WMM/HT/extended-capability IEs, records AP vendor information, then enqueues `_JoinBss_CMD_` with the security-owned BSS buffer.

Driver-extra control is multiplexed through `rtw_drvextra_cmd_hdl()`, which handles periodic dynamic checks, power-save processing, LPS control, DM-in-LPS updates, DTIM changes, high-queue checks, security reset, assoc-resource free, C2H handling, RA mask updates, and BT info notifications. `c2h_wk_callback()` drains the C2H circular buffer, reads/clears unread events when needed, validates them, handles CCX events inline, and forwards other C2H events to the command thread.

## State and Persistence Behavior

State is volatile driver state stored in `cmd_priv`, `evt_priv`, `mlme_priv`, `security_priv`, `pwrctrl_priv`, `sta_priv`, and `dvobj_priv`. Command queue membership is protected by spinlocks; command-thread lifecycle uses completions and `cmdthd_running`; synchronous callers use `submit_ctx` under `sctx_mutex`. Scans and joins persist progress through `_FW_UNDER_SURVEY`, `_FW_UNDER_LINKING`, timers, and `to_join`; power-save state is persisted in `pwrctrl_priv` fields such as `LpsIdleCount`, `DelayLPSLastTimeStamp`, `dtim`, and firmware PS mode.

No on-disk persistence exists. EFUSE, hardware registers, firmware H2C messages, CAM entries, and firmware media reports are external persistent-ish integration points from the driver's perspective. Command objects and parameter buffers are short-lived and must be freed by callbacks or the command thread.

## Dependencies and Integration Points

Direct includes are `drv_types.h`, `hal_btcoex.h`, `linux/jiffies.h`, `linux/align.h`, and `linux/delay.h`. The file integrates with MLME extension handlers, HAL register/H2C/C2H APIs, Bluetooth coexistence notifications, LPS/IPS power-control helpers, security/CAM helpers, station table management, beacon/TIM update logic, cfg80211-visible MLME events through callbacks in `rtw_mlme.c`, and low-level I/O indirectly through HAL handlers.

Important cross-file dependencies in this work item include `rtw_mlme.c` for `rtw_free_network_queue()`, `rtw_restruct_sec_ie()`, `rtw_restruct_wmm_ie()`, `rtw_ht_use_default_setting()`, `rtw_restructure_ht_ie()`, `rtw_append_exented_cap()`, `rtw_reset_securitypriv()`, and `rtw_free_assoc_resources()`, and `rtw_ioctl_set.c` for user-driven scan/join/disconnect callers that eventually enqueue commands here.

## Risks and Edge Cases

Command lifetime is the main risk. `_JoinBss_CMD_` and `_CreateBss_CMD_` intentionally borrow buffers and are exempted from normal `parmbuf` freeing, while most other command parameters are owned by the command object. `_Set_Drv_Extra` may own a nested `pbuf` that must be freed only when `size > 0`. Incorrect command-code setup or callback registration can produce leaks, double frees, or use-after-free.

The command queue is serialized but fed from many contexts. The code uses spinlocks and GFP_ATOMIC allocations in several paths; allocation failures must unwind precisely. Commands can be dropped if hardware init is incomplete or the command thread has stopped, which means callers must tolerate `_FAIL` after partially updating MLME/security state. Timer-based failure recovery for scan/join (`scan_to_timer`, `assoc_timer`) means ordering bugs can present as late cfg80211 notifications.

C2H handling is sensitive to SDIO context: comments explicitly warn not to perform reads/writes inside `rtw_c2h_wk_cmd()` because SDIO interrupt context may already hold the host. BT-info parsing clamps the reported length but still depends on valid firmware-provided buffers. Power-save and traffic watchdog logic has threshold hysteresis and touches firmware state; regressions can cause missed LPS entry/exit or throughput problems.

## Test Signals

Useful tests include command-thread startup/shutdown with queued commands, allocation-failure injection for each command constructor, scan success/failure/timeout coverage, join success/failure/timeout coverage, direct-vs-enqueued disassoc/opmode/key paths, and verification that callbacks free their command objects exactly once. Integration tests should exercise cfg80211 scan/connect/disconnect flows, WEP/WPA/WPA2 key setup, AP/IBSS BSS creation, LPS transitions during idle and busy traffic, BT coexistence C2H events, high-queue TIM clearing, and driver unload while commands/C2H work are pending. Static analysis should focus on command ownership, lock ordering between `mlmepriv->lock`, scanned queue locks, and `sctx_mutex`, and bounds/lifetime handling for firmware-provided C2H buffers.
