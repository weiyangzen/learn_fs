# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_main.c

## Purpose
This file provides the bus-independent RSI 91x core object lifecycle, debug logging, RX packet demultiplexing, TX scheduler thread, and optional Bluetooth coexistence callbacks. SDIO and USB probes call `rsi_91x_init`, then transport code supplies host-interface operations and starts firmware initialization.

## Important APIs, Types, and Functions
Exports include `rsi_zone_enabled`, `rsi_dbg`, `rsi_read_pkt`, `rsi_91x_init`, and `rsi_91x_deinit`. Internal helpers include `opmode_str`, `rsi_print_version`, `rsi_prepare_skb`, and `rsi_tx_scheduler_thread`. With `CONFIG_RSI_COEX`, `g_proto_ops`, `rsi_get_host_intf`, `rsi_set_bt_context`, and `rsi_attach_bt` bridge the WLAN driver to the Bluetooth side.

## Control Flow
Initialization allocates `struct rsi_hw` and `struct rsi_common`, initializes all software TX queues, events, mutexes, the TX scheduler thread, default power-save and background-scan parameters, ROC timer, completions, operating mode, and coexistence mode. The TX scheduler waits on `common->tx_thread.event` with a bus-supplied timeout, then runs `rsi_core_qos_processor` once `init_done` is true. RX bytes from SDIO or USB enter `rsi_read_pkt`, which walks one or more frame descriptors, extracts queue number/length/extended descriptor, and dispatches packets to coexistence, WLAN management, WLAN data, or Bluetooth callbacks. Deinit stops the TX thread, purges queues, detaches BT/coex, clears `init_done`, and frees core objects and bus-private storage.

## State and Persistence Behavior
The file owns process-lifetime heap state for `adapter` and `common`, queue contents in `common->tx_queue[]`, `common->coex_mode`, `common->oper_mode`, `common->init_done`, `common->bt_defer_attach`, `common->bt_adapter`, and thread/event state. Debug zones are module-global and exported. No persistent state survives module unload; firmware and EEPROM state are handled elsewhere.

## Dependencies and Integration Points
It depends on `rsi_mgmt_pkt_recv`, `rsi_indicate_pkt_to_os`, `rsi_core_qos_processor`, `rsi_default_ps_params`, `init_bgscan_params`, optional `rsi_coex_*`, optional `rsi_bt_ops`, and bus callbacks `determine_event_timeout`. Transport drivers use this file as their common allocation and teardown layer.

## Risks
RX descriptor parsing trusts packet layout and casts unaligned descriptor bytes directly to `u16`, which is risky on strict-alignment architectures. `rsi_prepare_skb` truncates oversized USB packets but still relies on descriptor-provided offsets. TX thread shutdown assumes the thread was created and will complete. Coexistence attach may be deferred until MAC init; wrong FSM transitions can miss BT attach. Deinit frees `adapter->rsi_dev`, so transport disconnect paths must not use that pointer afterward.

## Test Signals
Probe/remove loops for USB and SDIO, RX demux for data/mgmt/coex/BT queues, invalid queue handling, multi-frame USB aggregates, TX scheduler wakeups under buffer-full timeouts, coexistence mode selection for all module `dev_oper_mode` values, deferred BT attach, and queue purge on unload are key signals.
