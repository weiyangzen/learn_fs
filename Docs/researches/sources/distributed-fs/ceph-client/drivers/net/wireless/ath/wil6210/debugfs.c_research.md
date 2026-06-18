# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wil6210/debugfs.c

## Purpose
`debugfs.c` builds the wil6210 debugfs control and inspection surface. It exposes ring/status-ring state, mailbox contents, raw firmware memory blobs, interrupt registers, station/reorder state, firmware version/capabilities, suspend counters, PMC capture controls, LED controls, link statistics, and several privileged write-only command paths. It is diagnostic glue around `wil6210_priv`, WMI helpers, TX/RX rings, PMC, power management, and firmware memory mappings.

## Important APIs, Types, And Functions
The local `enum dbg_off_type` and `struct dbg_off` describe debugfs entries backed by driver fields, static globals, or MMIO offsets. `wil6210_debugfs_init()` creates the top-level directory, allocates per-register `wil_debugfs_iomem_data`, initializes PMC state, and registers all files, blobs, ISR register directories, pseudo-ISR registers, and interrupt moderation counters. `wil6210_debugfs_remove()` recursively removes debugfs, frees helper state and latency histograms, and frees PMC memory without sending firmware commands during teardown.

Read-side show functions include `ring_show()`, `srings_show()`, `mbox_show()`, `txdesc_show()`, `status_msg_show()`, `rx_buff_mgmt_show()`, `bf_show()`, `temp_show()`, `link_show()`, `info_show()`, `sta_show()`, `mids_show()`, `wil_tx_latency_debugfs_show()`, `wil_link_stats_debugfs_show()`, `fw_capabilities_show()`, and `fw_version_show()`. Write-side controls include `wil_write_file_rxon()`, `wil_write_file_rbufcap()`, `wil_write_back()`, `wil_write_pmccfg()`, `wil_write_file_txmgmt()`, `wil_write_file_wmi()`, `wil_write_file_recovery()`, `wil_tx_latency_write()`, `wil_link_stats_write()`, `wil_link_stats_global_write()`, `wil_write_file_led_cfg()`, `wil_write_led_blink_time()`, `wil_write_suspend_stats()`, and `wil_compressed_rx_status_write()`.

## Control Flow
Initialization is table driven. `dbg_files[]` maps names to `file_operations`, while `dbg_wil_off[]`, `dbg_wil_regs[]`, `dbg_statics[]`, `isr_off[]`, `pseudo_isr_off[]`, and ITR tables map fields/registers to debugfs scalar files. Ring and mailbox readers acquire runtime PM and, where needed, `wil_mem_access_lock()` plus HALP votes before touching device memory. Writable entries parse user input, validate ranges, and issue WMI commands or update driver fields. Several show paths call firmware synchronously through WMI, for example beamforming, temperature, and link statistics.

## State And Persistence
Most state is live kernel/device state, not persistent storage. The file has static debug selector variables (`mem_addr`, descriptor/ring/status indices) shared across devices by design, noted in the source as a hack. Persistent-in-driver state includes `wil->dbg_data`, PMC context, latency histogram allocation per station, `wil->fw_version`, `wil->fw_capabilities`, suspend counters, and EDMA configuration flags. Debugfs removal must free allocations that can outlive open debug sessions.

## Dependencies And Integration Points
The file depends on Linux debugfs/seq_file, runtime PM, cfg80211, WMI command helpers, TX/RX descriptor formats, firmware mappings, power supply status, LED globals, and PMC APIs from `pmc.c`. It integrates with reset/suspend protection through runtime PM and `wil_mem_access_lock()`, with P2P/cfg80211 through management frame injection, and with WMI for control commands.

## Risks
The surface is powerful and should remain debugfs-only: raw WMI send, raw management transmit, register writes, RX-on control, aggregation control, and firmware recovery control can destabilize hardware. `wil_compressed_rx_status_write()` only blocks changes once interfaces are active; future EDMA config toggles need the same guard. Static debug selector variables are not per-device. Several show paths dereference live ring/state under limited locking, so teardown/NAPI synchronization assumptions matter.

## Test Signals
Useful signals include debugfs creation/removal under probe/remove, reading every show file while up/down/suspended, WMI failures from temperature/link stats/beamforming, PMC alloc/free/read error paths, invalid parser inputs for writable files, EDMA versus legacy ring displays, and lockdep/KASAN testing around teardown while debugfs files are open.
