# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/debug.c

Purpose: Implements WFx trace name helpers and debugfs interfaces for counters, RX stats, TX power loop information, PDS upload, and raw HIF command injection.

Important APIs and functions: `wfx_get_hif_name()`, `wfx_get_mib_name()`, and `wfx_get_reg_name()` map numeric IDs to trace strings. Debugfs show/write handlers include `wfx_counters_show()`, `wfx_rx_stats_show()`, `wfx_tx_power_loop_show()`, `wfx_send_pds_write()`, and `wfx_send_hif_msg_*()`. `wfx_debug_init()` creates debugfs files under the wiphy debugfs directory.

Control flow and integration: Counter reads iterate each vif and call `wfx_hif_get_counters_table()`. RX stats and TX power loop show functions read data last populated by generic HIF indications under locks. PDS write copies user data and calls `wfx_send_pds()`. Raw HIF write parses hex user input into a request, sends it with `wfx_cmd_send()`, and exposes the reply through read.

State and persistence: Debugfs raw HIF sessions allocate `struct dbgfs_hif_msg` per open file. RX stats and TX power loop state persist in `wdev` and are updated asynchronously by firmware generic indications.

Dependencies: Depends on debugfs/seq_file/usercopy, WFx HIF/MIB/debug name tables, mac80211 wiphy debugfs, and generated trace headers.

Risks and test signals: Risks include unsafe debugfs raw command injection, user buffer parsing/size errors, stale stats, and missing vif handling. Tests should cover debugfs file creation, counter reads on zero/two vifs, PDS write validation, raw HIF write/read with malformed and valid hex, and locking around async stats updates.

Test signals: Source read size: 331 lines, 8801 bytes.
