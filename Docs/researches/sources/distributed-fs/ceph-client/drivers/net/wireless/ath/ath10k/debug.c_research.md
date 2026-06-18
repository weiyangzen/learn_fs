# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/debug.c

## Purpose

`debug.c` implements ath10k logging helpers, firmware/board/boot information printing, debugfs control and inspection files, firmware statistics aggregation, TPC statistics retrieval, ethtool statistics, crash simulation controls, register/memory access hooks, and runtime debug feature toggles.

## Important APIs and Functions

Always-built logging helpers are `ath10k_info()`, `ath10k_err()`, and `ath10k_warn()`, all of which log through the device and tracepoints. `ath10k_debug_print_hwfw_info()`, `ath10k_debug_print_board_info()`, `ath10k_debug_print_boot_info()`, and exported `ath10k_print_driver_info()` summarize firmware, board, Kconfig, checksums, HTT/WMI versions, calibration mode, raw mode, and hardware crypto state.

Under `CONFIG_ATH10K_DEBUGFS`, key exported functions are `ath10k_debug_create()`, `ath10k_debug_register()`, `ath10k_debug_start()`, `ath10k_debug_stop()`, `ath10k_debug_unregister()`, `ath10k_debug_destroy()`, `ath10k_debug_fw_stats_process()`, `ath10k_debug_fw_stats_request()`, `ath10k_debug_tpc_stats_process()`, and `ath10k_debug_tpc_stats_final_process()`.

Debugfs files include `fw_stats`, `fw_reset_stats`, `wmi_services`, `simulate_fw_crash`, `reg_addr`, `reg_value`, `mem_value`, `chip_id`, `htt_stats_mask`, `htt_max_amsdu_ampdu`, `fw_dbglog`, `cal_data`, `nf_cal_period`, `ani_enable`, DFS controls/statistics, `pktlog_filter`, `quiet_period`, `tpc_stats`, `btcoex`, `peer_stats`, `enable_extd_tx_stats`, `fw_checksums`, `sta_tid_stats_mask`, `tpc_stats_final`, `warm_hw_reset`, `ps_state_enable`, and `reset_htt_stats`, with several gated by firmware service bits or Kconfig.

Under `CONFIG_ATH10K_DEBUG`, `__ath10k_dbg()` and `ath10k_dbg_dump()` implement debug-mask and tracepoint-backed verbose logging and hex dumps.

## Control Flow

Debug storage is allocated in `ath10k_debug_create()` before registration: calibration data buffer and firmware stats list heads. `ath10k_debug_register()` creates the per-phy `ath10k` debugfs directory after firmware capability discovery so service-gated files can be conditionally exposed. `ath10k_debug_start()` runs during firmware start and applies configured HTT stats polling, firmware dbglog mask, pktlog filter, and noise-floor calibration period. `ath10k_debug_stop()` snapshots calibration data when possible, cancels periodic HTT stats work without synchronous cancellation to avoid deadlock, and disables pktlog.

Firmware stats flow is request/response oriented. `ath10k_debug_fw_stats_request()` resets aggregate state, repeatedly sends WMI stats requests, waits on `fw_stats_complete`, and stops when `fw_stats_done` is observed. `ath10k_debug_fw_stats_process()` parses WMI stats skb payloads, handles multi-event ping-pong semantics, updates station RX duration for peer stats, splices pdev/vdev/peer lists, bounds peer/vdev growth, and completes waiters.

Several debugfs writes directly affect firmware. Crash simulation sends WMI force-hang, invalid vdev commands, assert-trigger install-key commands, or queues hardware restart. Register and memory files use HIF read/write or diagnostic windows. HTT controls send HTT stats/aggr commands. ANI, NF calibration period, pktlog, quiet period, BT coexistence, peer stats, warm reset, and PS state toggles send WMI pdev commands or trigger recovery.

## State and Persistence

Debugfs writes persist in `struct ath10k_debug` or adjacent `struct ath10k` fields for the life of the driver object: firmware dbglog mask/level, HTT stats mask/reset mask, register address, NF calibration period, calibration data snapshot, extended TX stats enable, TPC stats, DFS stats, pktlog filter, peer stats flag, BT coexistence flag, station TID stats mask, and PS-state enable. No on-disk persistence is performed.

Most debug operations are guarded by `conf_mutex` and state checks for `ATH10K_STATE_ON`, `ATH10K_STATE_UTF`, or `ATH10K_STATE_RESTARTED`. Shared stats lists and counters use `data_lock`.

## Dependencies and Integration Points

The file integrates with debugfs, tracepoints, firmware loader CRCs, WMI operations, HTT operations, HIF diagnostic reads/writes, mac80211 ethtool stats hooks, DFS detector, thermal throttling, core recovery, and core firmware metadata. It is tightly coupled to `core.h` state layout and to WMI service bits because debugfs file availability reflects firmware capability.

## Risks

Debugfs exposes powerful write paths: arbitrary register/memory writes, forced firmware crashes, warm resets, runtime firmware parameter changes, and recovery triggers. These must stay root-only or appropriately permissioned. Several paths allocate buffers based on user read/write sizes (`mem_value`) or fixed 1 MiB stats buffers; large reads can stress memory. Stats aggregation relies on firmware event ordering and could drop or misinterpret malformed stats. `ath10k_tpc_stats_final_open()` requests final TPC stats but fills from `ar->debug.tpc_stats`, which is a notable behavior to verify because a separate `tpc_stats_final` pointer exists.

## Test Signals

Test through debugfs file creation under different Kconfig and WMI service combinations, fw stats read success and timeout behavior, ethtool stats fallback to zero when no stats exist, crash simulation triggering recovery/coredump, register/memory access returning `-ENETDOWN` when firmware is down, pktlog/HTT polling start-stop cancellation without workqueue deadlocks, and lockdep coverage around stats processing and debugfs reads/writes.
