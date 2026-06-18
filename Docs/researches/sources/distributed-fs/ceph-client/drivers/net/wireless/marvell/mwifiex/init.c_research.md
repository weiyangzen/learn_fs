# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/init.c

## Purpose
`init.c` initializes and shuts down mwifiex adapter/private runtime state, command buffers, work-related locks/lists, firmware defaults, BSS priority tables, wakeup/device-dump support, and the common firmware download sequence.

## Important APIs, Types, and Functions
Exported/common functions are `mwifiex_init_priv()`, `mwifiex_set_trans_start()`, `mwifiex_wake_up_net_dev_queue()`, `mwifiex_stop_net_dev_queue()`, `mwifiex_init_lock_list()`, `mwifiex_init_fw()`, `mwifiex_free_priv()`, `mwifiex_shutdown_drv()`, `mwifiex_dnld_fw()`, and `mwifiex_free_cmd_buffers()`. Internal helpers include `mwifiex_add_bss_prio_tbl()`, `wakeup_timer_fn()`, `fw_dump_work()`, `mwifiex_allocate_adapter()`, `mwifiex_init_adapter()`, `mwifiex_invalidate_lists()`, `mwifiex_adapter_cleanup()`, and `mwifiex_delete_bss_prio_tbl()`.

## Control Flow
Firmware bring-up through `mwifiex_init_fw()` sets hardware status to initializing, allocates command and sleep-confirm buffers, seeds adapter defaults, initializes every `mwifiex_private`, and sends per-interface STA init commands unless manufacturing mode is active. `mwifiex_init_adapter()` prepares sleep-confirm command contents, power-save defaults, scan timing, host-sleep defaults, firmware capability placeholders, interface limits, wakeup timer, and firmware dump work. `mwifiex_init_lock_list()` initializes all adapter/private spinlocks, command/scan queues, RX/TX queues, BSS priority lists, WMM RA lists, BA/reorder lists, station/TDLS lists, and ACK-status IDRs. Shutdown cancels current commands, frees per-priv TX/RX state, drains TX/RX queues, wakes waiters, cancels timers/work, and marks hardware not ready.

## State and Persistence
State is entirely in memory and hardware/firmware. `mwifiex_adapter` holds command queues, power state, scan defaults, firmware capability state, wait queues, sleep confirmation skb, wakeup timer, device dump work, and interface limits. Each `mwifiex_private` holds connection/security/WMM/rate/scan/IE defaults. BSS priority nodes are dynamically allocated and later removed from adapter priority lists.

## Dependencies and Integration Points
The file relies on command allocation helpers, WMM and 11h initialization, bus `if_ops` callbacks, skbuff queues, Linux timers/workqueues, netdev queue APIs, firmware request/download paths, and command/event wait queues. `mwifiex_dnld_fw()` delegates bus-specific firmware status, winner arbitration, and programming to SDIO/PCIe/USB operations.

## Risks and Edge Cases
Initialization has many partially allocated states; missing cleanup on an intermediate failure can leak command buffers or sleep-confirm skbs. `mwifiex_invalidate_lists()` uses `list_del()` during free, so it assumes list heads were initialized and not already invalidated. Wakeup timeout forces hardware reset if firmware does not respond. Firmware download winner arbitration can skip programming on non-winning functions and must still poll long enough for firmware readiness. Shutdown drains RX by indexing `adapter->priv[rx_info->bss_num]`, so corrupted RX metadata would be risky.

## Test Signals
Validate cold probe, firmware-already-running probe, multi-function winner/non-winner firmware download, manufacturing mode, reset/reinit cycles, wakeup timer card reset, clean module removal with zero pending RX/TX/CMD counters, sleep-confirm command contents, and netdev queue stop/wake behavior under TX timeout and teardown.
