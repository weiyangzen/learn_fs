# sources/distributed-fs/ceph-client/drivers/net/ethernet/sun/sunvnet.c

## Purpose
`sunvnet.c` is the Sun LDOM virtual network driver front end. It creates and manages Linux netdevs for virtual networks described by the SPARC machine description, probes `vnet-port` VIO devices, assigns ports to parent vnets by local MAC address, chooses transmit ports/queues, exposes ethtool information and statistics, and delegates packet protocol mechanics to `sunvnet_common.c`.

## Important APIs, Types, And Functions
- Module interface: `vnet_init()`, `vnet_exit()`, `vnet_port_driver`, VIO match table for `"vnet-port"`, and supported VIO versions 1.8, 1.7, 1.6, and 1.0.
- Netdev setup: `vnet_new()`, `vnet_find_or_create()`, `vnet_cleanup()`, `vnet_ops`, and `vnet_ethtool_ops`.
- TX routing: `__tx_port_find()`, `vnet_tx_port_find()`, `vnet_select_queue()`, and wrapper `vnet_start_xmit()`.
- RX/multicast/common wrappers: `vnet_set_rx_mode()` and optional `vnet_poll_controller()`.
- Machine-description lookup: `vnet_find_parent()` finds the containing `"network"` node and its `local-mac-address`.
- Port lifecycle: `vnet_port_probe()` and `vnet_port_remove()` allocate/free `struct vnet_port`, initialize VIO/LDC, add NAPI, link the port into parent lists/hash table, allocate a TX queue index, start VIO handshake, and tear everything down.
- Ettool statistics: `vnet_get_sset_count()`, `vnet_get_strings()`, and `vnet_get_ethtool_stats()` combine netdev stats with per-port stats.

## Control Flow
At module load the VIO driver is registered. Each `vnet-port` probe grabs the machine description, finds or creates a parent `struct vnet` based on the network node's local MAC, reads the port's remote MAC, allocates a `struct vnet_port`, initializes generic VIO state and an LDC channel, attaches NAPI to the parent netdev, marks switch-port capability from MD properties, inserts the port into the parent list and hash under `vp->lock`, assigns a least-used TX queue, stores driver data, creates the cleanup timer, enables NAPI, and calls `vio_port_up()` to begin handshake.

The parent vnet netdev is created once per local MAC with multiple TX queues, feature bits for TSO/GSO/checksum/scatter-gather, MTU range up to 65535, fixed MAC from MD, and source `vnet_ops`. TX queue selection hashes the destination MAC to a live direct port, falling back to the first live switch port. Remove disables VIO timers/NAPI, removes RCU list/hash entries, synchronizes readers, shuts down cleanup, returns the TX queue allocation, deletes NAPI, frees TX buffers and LDC resources, and frees the port. Module exit unregisters the VIO driver then frees parent netdevs after asserting their port lists are empty.

## State And Persistence
Global `vnet_list` tracks parent vnets by `local_mac` under `vnet_list_mutex`. Each `struct vnet` stores port list/hash state, queue usage, multicast list, netdev pointer, and local MAC. Each `struct vnet_port` stores remote MAC, switch/direct role, VIO state, per-port counters, NAPI, cleanup timer, negotiated offload values, and queue index. All state is volatile kernel memory; the authoritative topology comes from the machine description.

## Dependencies And Integration Points
The file depends on Linux netdev/ethtool/etherdevice/SKB APIs, mutex/RCU/list primitives, SPARC `asm/vio.h` and `asm/ldc.h`, machine-description APIs, and the common functions declared in `sunvnet_common.h`. It integrates with VIO control operations through `vnet_vio_ops`, with LDC events through `vnet_ldc_cfg`, and with ethtool through dynamic per-port string/stat generation.

## Risks And Edge Cases
- Ettool string count depends on `vp->nports`; concurrent port removal is protected by RCU during iteration, but userspace stats reads can still observe topology changes between count and fetch.
- `vnet_cleanup()` uses `BUG_ON(!list_empty(&vp->port_list))`, so module exit assumes VIO unregister has already removed every port.
- `__tx_port_find()` returns `NULL` when no live direct or switch port exists; common TX then drops.
- Queue selection and TX routing must stay aligned with `sunvnet_port_add_txq_common()` and per-port queue indexes.
- Machine-description properties are mandatory; missing local or remote MAC fails probe.

## Test Signals
Signals include module load/unload, vnet creation for shared local MACs, multiple port probes/removes, switch-port fallback routing, per-port queue distribution, ethtool stat names and counts with changing port counts, MTU boundary behavior, VIO handshake completion, and RCU-safe removal under traffic.
