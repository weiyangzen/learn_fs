# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/debug.c

## Purpose
`debug.c` implements ath6kl logging helpers, target-stat reads, firmware log collection, debugfs files, diagnostic register access, credit/endpoint statistic reporting, roam-table commands, and debugfs knobs for roaming, keepalive, disconnect timeout, QoS streams, scan interval, listen interval, and power-save parameters. Most of the file is compiled only with `CONFIG_ATH6KL_DEBUG`, but `ath6kl_printk()`, `ath6kl_info()`, `ath6kl_err()`, `ath6kl_warn()`, and `ath6kl_read_tgt_stats()` are always present and exported.

## Important APIs, types, and functions
`ath6kl_dbg()` and `ath6kl_dbg_dump()` gate debug output on `debug_mask` and always feed tracepoints. `ath6kl_read_tgt_stats()` serializes a WMI stats request with `ar->sem`, sets `STATS_UPDATE_PEND`, sends `ath6kl_wmi_get_stats_cmd()`, and waits on `ar->event_wq`. `ath6kl_debug_fwlog_event()` records fixed-size firmware log slots in `ar->debug.fwlog_queue`, limiting the queue to 20 entries. `ath6kl_debug_roam_tbl_event()` validates and stores firmware roam-table events and wakes waiters.

The debugfs file operations expose `tgt_stats`, SDIO-only `credit_dist_stats`, `endpoint_stats`, `fwlog`, `fwlog_block`, `fwlog_mask`, `reg_addr`, `reg_dump`, `lrssi_roam_threshold`, `reg_write`, `war_stats`, `roam_table`, `force_roam`, `roam_mode`, `keepalive`, `disconnect_timeout`, `create_qos`, `delete_qos`, `bgscan_interval`, `listen_interval`, and `power_params`. Initialization is split between `ath6kl_debug_init()` for early firmware logs and `ath6kl_debug_init_fs()` after cfg80211/wiphy debugfs exists.

## Control flow and integration
Read paths either format cached driver fields or actively query firmware. Stats and roam table reads issue WMI commands and wait for event handlers to clear pending bits. Firmware log reads pull pending firmware logs with `ath6kl_read_fwlogs()` then drain the SKB queue; `fwlog_block` waits on a completion if the queue is empty. Register dump uses `ath6kl_diag_read32()` over valid register ranges, with `reg_addr` selecting either a single register or all predefined ranges. Write paths parse user input, update local debug fields, and send WMI commands such as `set_roam_lrssi`, `force_roam`, `set_roam_mode`, `set_keepalive`, `disctimeout`, QoS create/delete, scan params, listen interval, and PM params.

## State and persistence behavior
Debug state persists in `ar->debug`: firmware log queue/completion/open flag, `fwlog_mask`, diagnostic read/write addresses, workaround counters, roam-table buffer and length, keepalive, and disconnect timeout. The firmware log queue is bounded and drops oldest entries. Roam table storage is dynamically resized. Many debugfs writes update driver fields only after or before sending WMI; those fields are in-memory and reset on driver teardown.

## Dependencies and integration points
The file depends on debugfs, SKBs, vmalloc, tracepoints, target register macros, WMI command/event paths, HTC endpoint and credit distribution structures, diagnostic HIF helpers, and cfg80211 wiphy debugfs. It observes `ar->hif_type` to expose SDIO credit distribution only for mailbox/SDIO-style operation.

## Risks and test signals
Risks include debugfs read buffers sized by estimates, blocking waits under `ar->sem`, firmware log single-open semantics without a lock around `fwlog_open`, user-triggered diagnostic register writes, and many debugfs controls that can alter firmware runtime behavior. Test signals include reading every debugfs file before and after association, blocked fwlog wakeup behavior, roam table timeout/error handling, invalid register address rejection, endpoint stat reset, WMI command error propagation, and cleanup waking blocked fwlog readers.
