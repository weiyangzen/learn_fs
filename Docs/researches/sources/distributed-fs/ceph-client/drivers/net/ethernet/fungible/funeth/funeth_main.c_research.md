# sources/distributed-fs/ceph-client/drivers/net/ethernet/fungible/funeth/funeth_main.c

## Purpose
Provides the core PCI/netdev driver for Fungible Ethernet devices. It manages PCI probe/remove, admin device enablement, port creation/destruction, netdev operations, link events, queue/IRQ lifecycle, RSS, XDP mode transitions, SR-IOV VF configuration, devlink ports, statistics DMA setup, and service-task reactions to resource changes.

## Important APIs and Functions
Netdev operations include `funeth_open()`, `funeth_close()`, `fun_start_xmit()`, stats, MTU/MAC changes, XDP setup/xmit, VF configuration, and hardware timestamp get/set. Admin helpers include `fun_port_write_cmds()`, `fun_port_read_cmds()`, `fun_config_rss()`, `fun_destroy_rss()`, `fun_port_create()`, `fun_vi_create()`, and `fun_create_and_bind_tx()`. Queue lifecycle helpers include `fun_alloc_queue_irqs()`, `fun_alloc_rings()`, `fun_advance_ring_state()`, `fun_up()`, `fun_down()`, `fun_replace_queues()`, and `fun_change_num_queues()`. PCI entry points are `funeth_probe()`, `funeth_remove()`, and `funeth_sriov_configure()`.

## Control Flow
Probe allocates devlink, enables the `fun_dev` admin core with admin SQ/CQ/RQ depths, queries port count, creates each netdev, restarts service work, and registers devlink. Netdev creation computes maximum/default queue counts, creates a port resource, binds port events to admin CQ, reads MAC/capabilities/advertising/MTU, initializes RSS/stats DMA, registers a devlink port, optionally enables kTLS, then registers the netdev. Open allocates IRQ-backed rings, creates hardware queues if needed, creates a VI, publishes queue arrays with RCU, enables IRQ/NAPI, binds RSS or single CQ, writes stats DMA and enable keys, then starts Tx queues. Close disables the port, carrier, Tx queues, RSS, VI, IRQs, and frees rings.

## State and Persistence
Key persistent state lives in `struct funeth_priv`: admin/device pointers, `netdev`, port id, queue arrays, IRQ XArray, queue depths, RSS DMA/config/hardware id, link snapshot fields protected by `seqcount_t`, stats DMA area, XDP program/count, kTLS id/counters, and SR-IOV vport state under `fun_ethdev.state_mutex`. Live Rx/XDP queue pointers use RCU publication and `synchronize_net()` during teardown or replacement.

## Dependencies and Integration Points
Depends on funeth admin protocol definitions, `fun_queue` SQ/CQ helpers, devlink, PCI/MSI-X, netdevice, XDP/BPF, TLS, SR-IOV, and ethtool. `fun_event_cb()` consumes async admin CQ notifications for link state and resource count changes; `fun_service_cb()` creates/destroys ports when the device reports resource changes.

## Risks and Test Signals
High-risk areas are live queue resizing with mixed old/new queues, IRQ state transitions, RCU queue pointer replacement, RSS table rollback on admin failure, XDP enter/exit ordering, probe unwind labels, and stats DMA allocation/free size symmetry. Test signals include probe/remove/hotplug, open/close loops, `ethtool -L/-G` while traffic runs, XDP attach/detach/redirect, SR-IOV enable/disable and VF MAC/VLAN/rate, link notifications, kdump one-queue mode, and fault injection in admin commands and allocations.
