# sources/distributed-fs/ceph-client/drivers/net/ethernet/google/gve/gve_main.c

## Purpose

`gve_main.c` is the core PCI/netdev driver entry point for Google Virtual Ethernet. It owns probe/remove/shutdown/PM, adminq and device-resource lifecycle, queue allocation/start/stop/reconfiguration, NAPI and interrupt setup, reset recovery, XDP/AF_XDP control, link/status handling, stats reporting, timestamp configuration, and netdev operation dispatch between GQI and DQO datapaths.

## Important APIs, types, and functions

- Netdev dispatch: `gve_start_xmit`, `gve_features_check`, `gve_get_stats`, `gve_netdev_ops`.
- Device setup: `gve_probe`, `gve_init_priv`, `gve_setup_device_resources`, `gve_teardown_device_resources`, `gve_verify_driver_compatibility`.
- Interrupt/NAPI: `gve_alloc_notify_blocks`, `gve_free_notify_blocks`, `gve_intr`, `gve_intr_dqo`, `gve_mgmnt_intr`, `gve_napi_poll`, `gve_napi_poll_dqo`.
- Queue lifecycle: `gve_queues_mem_alloc`, `gve_queues_start`, `gve_open`, `gve_queues_stop`, `gve_close`, `gve_queues_mem_remove`, `gve_create_rings`, `gve_destroy_rings`.
- QPL/page helpers: `gve_alloc_page`, `gve_free_page`, `gve_alloc_queue_page_list`, `gve_free_queue_page_list`, `gve_register_qpls`, `gve_unregister_qpls`.
- Reconfiguration: `gve_adjust_config`, `gve_adjust_queues`, `gve_set_rx_buf_len_config`, `gve_set_hsplit_config`, `gve_set_features`.
- XDP/AF_XDP: `gve_set_xdp`, `gve_xdp`, `gve_xdp_xmit`, `gve_xsk_pool_enable`, `gve_xsk_pool_disable`, `gve_xsk_wakeup`, XDP metadata ops.
- Reset/status/stats: `gve_schedule_reset`, `gve_reset`, `gve_reset_recovery`, `gve_service_task`, `gve_handle_report_stats`, `gve_stats_report_timer`.
- Per-queue management/stat ops: `gve_queue_mgmt_ops`, `gve_stat_ops`.

## Control flow and state

Probe enables PCI, maps register and doorbell BARs, writes the driver version byte stream, allocates a multiqueue netdev, initializes feature flags, creates the ordered workqueue, and calls `gve_init_priv()`. `gve_init_priv()` allocates adminq, verifies compatibility, describes the device unless reset recovery skips it, derives queue counts from MSI-X vectors, initializes default queue/coalescing/timestamp state, allocates XSK bitmap, sets XDP features, and configures device resources.

Opening allocates TX/RX ring memory using GQI or DQO implementations, starts rings, registers XDP RXQ info and QPLs, creates hardware queues through adminq, turns NAPI/interrupts on, and schedules service work. Closing turns carrier off, disables NAPI, destroys hardware queues, unregisters QPLs, unregisters XDP state, stops rings, and then frees queue memory. Live ethtool/XDP changes allocate a new config first, close existing queues, and start replacement queues.

Driver state is in `struct gve_priv`: PCI/netdev handles, BAR pointers, queue configs, descriptor counts, ring arrays, adminq resources, DMA counter/stat report buffers, notify blocks/MSI-X vectors, state flags, ethtool flags, RSS/flow caches, XSK bitmap, PTP timestamp state, XDP program, and counters. Runtime state is volatile and rebuilt on reset; no persistent on-disk state exists.

## Dependencies and integration points

The file integrates Linux PCI, netdev, NAPI, MSI-X, DMA, BPF/XDP, AF_XDP, ethtool-facing helpers, workqueues, timers, and PM hooks. It calls adminq for compatibility, device description, resources, queues, QPLs, RSS, stats, flow rules, and reset-related operations. It dispatches to `gve_tx.c`/`gve_rx.c` for GQI and DQO files for DQO. Register flags come from `gve_register.h`; descriptor and doorbell details come from `gve_desc.h` and `gve_dqo.h`.

## Risks and test signals

Risks concentrate around lifecycle ordering: failing to unregister QPLs after queue destroy, double-freeing ring memory during reset, leaving NAPI enabled while queue structs are replaced, stale XSK pool pointers, feature changes racing XDP, and reset paths that skip normal teardown. Test signals include PCI probe/remove fault injection, open/close loops, suspend/resume, reset under traffic, ethtool queue/ring changes while up, XDP attach/detach with AF_XDP pools, single RX queue start/stop through queue-mgmt ops, stats-report timer behavior, and link/status interrupt handling.
