# sources/distributed-fs/ceph-client/drivers/net/wireless/marvell/mwifiex/main.c

## Purpose
`main.c` is the common mwifiex driver core. It registers adapters, drives firmware request/download completion, owns the main/RX/host-MLME workqueues, coordinates command/event/RX/TX processing, implements netdev operations, handles software shutdown/reinit/removal, sets up wake IRQs, and exposes module parameters/debug helpers.

## Important APIs, Types, and Functions
Exported/common functions include `mwifiex_queue_main_work()`, `mwifiex_main_process()`, `mwifiex_queue_tx_pkt()`, `mwifiex_clone_skb_for_tx_status()`, `mwifiex_set_mac_address()`, `mwifiex_multi_chan_resync()`, `mwifiex_upload_device_dump()`, `mwifiex_drv_info_dump()`, `mwifiex_prepare_fw_dump_info()`, `mwifiex_init_priv_params()`, `is_command_pending()`, `mwifiex_shutdown_sw()`, `mwifiex_reinit_sw()`, `mwifiex_add_card()`, `mwifiex_remove_card()`, and `_mwifiex_dbg()`. Important static paths are `mwifiex_register()`, `mwifiex_unregister()`, `mwifiex_process_rx()`, `_mwifiex_fw_dpc()`, `mwifiex_init_hw_fw()`, netdev callbacks, workqueue callbacks, `mwifiex_uninit_sw()`, and OF wake IRQ handling.

## Control Flow
`mwifiex_add_card()` allocates/registers adapter software, probes wake IRQ from device tree, creates workqueues, calls bus `register_dev()`, then requests firmware asynchronously. `_mwifiex_fw_dpc()` downloads firmware, optionally loads calibration data, enables interrupts, initializes firmware state, registers cfg80211, creates default STA and optional AP/P2P interfaces, and marks the adapter up. The main work function calls `mwifiex_main_process()`, which serializes with `main_proc_lock`, throttles RX backlog, handles interrupts, wakes sleeping firmware when commands/TX are pending, processes events and command responses, confirms sleep, executes pending commands, and drains normal, bypass, and WMM TX queues. RX work drains `rx_data_q` and deaggregates or dispatches packets. Netdev TX validates skb length/headroom, fills mwifiex TX control block, optionally clones for TX status, timestamps, checks TDLS, and queues into bypass or WMM paths.

## State and Persistence
Module parameters include `debug_mask`, `cal_data_cfg`, `driver_mode`, `mfg_mode`, and `aggr_ctrl`. Runtime state is in `mwifiex_adapter`: work flags, workqueues, firmware pointers, command/event/RX/TX flags, power-save state, wake IRQ, coredump buffers, cfg80211/wiphy, and bus ops. Per-interface state is in `mwifiex_private`: netdev, MAC, WMM pending counts, custom IE indexes, scan flags, ACK-status IDR, histogram, and connection fields. Firmware/calibration blobs are released after use; coredumps are handed to `dev_coredumpv()`.

## Dependencies and Integration Points
`main.c` integrates Linux module parameters, firmware loader, cfg80211/wiphy, rtnetlink and netdev ops, skbuff queues, workqueues, timers, device tree IRQ parsing, PM wakeup APIs, devcoredump, USB/SDIO/PCIe bus `if_ops`, WMM/11n/TDLS helpers, and debugfs init/cleanup.

## Risks and Edge Cases
The central risk is asynchronous lifecycle ordering: firmware callbacks, removal, suspend, reset, workqueues, and interrupts share adapter state. `fw_done` completion gates shutdown/reinit but callers must avoid suspend races. `mwifiex_main_process()` has many break/continue paths around sleep, command, scan, and TX locks; regressions can stall commands or data. TX status cloning uses a small IDR range and must preserve skb ownership on allocation failure. Device dump building uses sprintf into dump buffers and reallocates only for firmware sections. Teardown must disable interrupts before destroying workqueues and netdevs.

## Test Signals
Validate add/remove while firmware request is pending, firmware download failure cleanup, reset via `mwifiex_reinit_sw()`, suspend wake IRQ behavior, RX backlog throttling, command/event ordering, PS wakeup timer, netdev open/close/scan abort, TX queue backpressure and timeout reset, MAC address changes, multicast mode changes, device coredump generation, and debug mask logging.
