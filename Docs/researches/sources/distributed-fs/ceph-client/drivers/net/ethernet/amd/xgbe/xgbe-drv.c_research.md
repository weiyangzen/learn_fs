# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-drv.c

## Purpose

`xgbe-drv.c` is the main Linux netdev runtime for the AMD XGBE driver. It owns channel allocation, open/close, IRQ and NAPI orchestration, service timers, ECC handling, powerdown/powerup, TX skb preparation, RX skb assembly, stats exposure, feature toggles, traffic-class setup, VLAN notifications, VXLAN UDP tunnel registration, restart/stop work, and debug packet/descriptor dumps.

This file coordinates high-level kernel networking lifecycles with the hardware callbacks implemented in `xgbe-dev.c` and descriptor resource callbacks implemented in `xgbe-desc.c`.

## Important APIs and Functions

- Channel/memory lifecycle: `xgbe_alloc_channels()`, `xgbe_free_channels()`, `xgbe_alloc_memory()`, `xgbe_free_memory()`, TX/RX data cleanup, and coalescing initialization.
- Device lifecycle: `xgbe_open()`, `xgbe_close()`, `xgbe_start()`, `xgbe_stop()`, `xgbe_restart_dev()`, `xgbe_full_restart_dev()`, `xgbe_powerdown()`, and `xgbe_powerup()`.
- IRQ/NAPI: `xgbe_request_irqs()`, `xgbe_free_irqs()`, `xgbe_isr()`, `xgbe_isr_bh_work()`, `xgbe_dma_isr()`, `xgbe_ecc_isr()`, `xgbe_one_poll()`, and `xgbe_all_poll()`.
- Timers/work: service timer/work for PHY status, per-channel TX timers for coalescing, restart work, stop-device work, ECC bottom-half work, and TX timestamp work.
- TX path: `xgbe_xmit()`, `xgbe_packet_info()`, `xgbe_prep_tso()`, `xgbe_prep_vlan()`, `xgbe_is_tso()`, `xgbe_is_vxlan()`, descriptor availability checks, and queue stop/wake logic.
- RX path: `xgbe_rx_poll()`, `xgbe_rx_refresh()`, `xgbe_create_skb()`, buffer length helpers, checksum/VLAN/RSS/timestamp/tunnel skb annotation, and GRO delivery.
- Netdev operations: `xgbe_netdev_ops` includes open/stop/start_xmit/set_rx_mode/set_mac/change_mtu/tx_timeout/get_stats64/VLAN add-kill/setup_tc/fix_features/set_features/features_check/hwtstamp hooks.
- Hardware discovery and tunnels: `xgbe_get_all_hw_features()` decodes feature registers; `xgbe_get_udp_tunnel_info()` exposes one VXLAN port table.
- Diagnostics: `xgbe_dump_tx_desc()`, `xgbe_dump_rx_desc()`, and `xgbe_print_pkt()`.

## Control Flow

Open creates device and auto-negotiation workqueues, enables clocks, initializes work items and PTP, allocates rings/descriptors, starts hardware, and clears the DOWN state. Start sets real TX/RX queue counts, prepares the RSS table, calls `hw_if->init`, enables NAPI, requests IRQs, resets and starts PHY, enables TX/RX, resets UDP tunnel state, starts queues and timers, queues initial service work, and clears STOPPED.

Stop is the reverse operational path: stop TX queues, drop carrier, stop timers, flush work, disable VXLAN, disable TX/RX, stop PHY, free IRQs, disable/delete NAPI, reset hardware, reset netdev TX queues, and set STOPPED. Close then frees memory, disables clocks, destroys workqueues, and sets DOWN. Restart variants either preserve allocated rings while freeing packet data or fully free/reallocate memory for ring-count changes.

The shared interrupt handler reads DMA status, schedules either global or per-channel NAPI for TX/RX/RBU work, handles fatal bus error by scheduling restart, services MAC MMC/timestamp/MDIO interrupts, and invokes AN/ECC/I2C handlers when those IRQs share the device line. Per-channel DMA interrupts schedule the channel NAPI directly. ECC bottom-half handling rate-limits corrected errors, disables noisy SEC sources, and stops the device on repeated detected errors.

Transmit prepares packet metadata, checks descriptor availability, performs TSO header preparation, maps the skb through `desc_if->map_tx_skb`, prepares TX timestamping, accounts bytes to BQL, and delegates descriptor programming to `hw_if->dev_xmit`. RX polling repeatedly asks `hw_if->dev_read` to parse descriptors, builds skbs from header and page-frag buffers, preserves partial packet state across budget exits, validates MTU, annotates checksum/tunnel/VLAN/timestamp/RSS metadata, and submits packets through GRO.

## State and Persistence Behavior

Driver state lives in `struct xgbe_prv_data`, channels, rings, timers, workqueues, NAPI structures, and statistics structures. Runtime state includes channel affinity/IRQ mappings, ring indices, queue-stopped flags, coalescing settings, ECC error periods/counts, power-down status, workqueue handles, active VLAN bitmap, netdev feature cache, VXLAN port, PTP timestamp work state, and `dev_state` flags such as DOWN/STOPPED.

No state is persisted outside the running kernel. Hardware and ring state is rebuilt on open and restart. Module parameters for ECC thresholds are persistent only for the loaded module instance and are exposed when ECC support is compiled in.

## Dependencies and Integration Points

The file integrates with core Linux networking APIs: netdev operations, NAPI, BQL, GRO, VLAN, GSO/TSO, UDP tunnel offload, traffic control mqprio, ethtool hwtstamp hooks, netpoll, PHY status, workqueues, timers, IRQ management, CPU/NUMA affinity, clocks, and module parameters. It depends heavily on `pdata->hw_if`, `pdata->desc_if`, `pdata->phy_if`, and `pdata->i2c_if` being initialized by sibling driver modules before open.

## Risks and Failure Modes

- NAPI/IRQ ordering is delicate. Interrupts are disabled before scheduling and re-enabled after `napi_complete_done`; mistakes cause interrupt storms or lost RX/TX completions.
- Global-NAPI mode divides budget by RX ring count. A zero or inconsistent `rx_ring_count` would be fatal; queue count setup must precede polling.
- TX descriptor count calculation must stay synchronized with `xgbe-desc.c` mapping and `xgbe-dev.c` descriptor emission.
- Link-down TX cleanup intentionally force-frees stuck descriptors without counting them as wire transmissions. This improves recovery but must not double-free skbs or over-report BQL completions.
- `xgbe_service_timer()` uses faster 100 ms polling while carrier is up and 1 s while down. That improves link-down detection but increases timer/service workload while the link is healthy.
- Stop/restart paths combine workqueue flushing, timer deletion, NAPI disable, IRQ free, PHY stop, and hardware reset; races here can surface as use-after-free, dead workqueue callbacks, or stuck queues.
- Feature changes can schedule restarts while toggling hardware bits. Callers must be under normal netdev serialization, and hardware callbacks must tolerate live state.

## Test Signals

Broad validation should include open/close loops, suspend-like powerdown/powerup, ring-count changes, MTU changes, traffic under TX/RX checksum offloads, TSO/GSO, VLAN add/remove/filtering, VXLAN tunnel registration, RSS, DCB traffic classes, PTP TX/RX timestamping, netpoll, link flap, fatal-bus/ECC recovery if injectable, and IRQ modes with and without per-channel interrupts. Monitor BQL, queue stop/wake logs, NAPI completion, DMA API checks, workqueue lifetime warnings, `tx_timeout`, MMC stats consistency, and packet drops during link transitions.
