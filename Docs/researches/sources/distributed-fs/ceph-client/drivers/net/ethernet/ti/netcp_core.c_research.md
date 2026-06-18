# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp_core.c

## Purpose
This file implements the TI Keystone NetCP core platform driver and netdev framework. It manages NetCP module registration/probing/attachment, ordered RX/TX hook lists, Navigator DMA/QMSS descriptor queues, NAPI RX/TX completion, netdev operations, address/VLAN fanout to modules, timestamp delegation, interface creation from DT, and platform probe/remove.

## Important APIs, types, and functions
- Internal device/module structs: `struct netcp_device`, `struct netcp_inst_modpriv`, `struct netcp_intf_modpriv`, and `struct netcp_tx_cb`.
- Descriptor helpers get/set packet, descriptor, original-buffer, software-word, EPIB, and PS data fields with little-endian conversion where needed.
- Module APIs: `netcp_register_module()`, `netcp_unregister_module()`, `netcp_module_probe()`, `netcp_release_module()`, and `netcp_module_get_intf_data()`.
- Hook APIs: `netcp_register_txhook()`, `_unregister_txhook()`, `netcp_register_rxhook()`, and `_unregister_rxhook()`, preserving ascending order.
- RX datapath: `netcp_allocate_rx_buf()`, `netcp_rxpool_refill()`, `netcp_process_one_rx_packet()`, `netcp_rx_poll()`, `netcp_rx_notify()`, and cleanup helpers.
- TX datapath: `netcp_tx_map_skb()`, `netcp_tx_submit_skb()`, `netcp_ndo_start_xmit()`, `netcp_process_tx_compl_packets()`, `netcp_tx_poll()`, and `netcp_tx_notify()`.
- TX pipe exports: `netcp_txpipe_init()`, `_open()`, and `_close()`.
- Netdev ops: open/stop, start_xmit, set_rx_mode, ioctl, stats, VLAN add/delete, TX timeout, mqprio setup, and hardware timestamp get/set.
- Platform: `netcp_create_interface()`, `netcp_delete_interface()`, `netcp_probe()`, `netcp_remove()`, and OF match `ti,netcp-1.0`.

## Control flow
Platform probe defers until knav DMA and QMSS are ready, enables runtime PM, creates interfaces from `netcp-interfaces`, links the device into the global device list, then probes any already registered modules under `netcp_modules_lock`. Module registration adds the module to the global list and probes it against existing devices; module probe looks for a matching DT child under `netcp-devices`, calls module probe, attaches it to each interface that references the module by phandle, and registers netdevs once a primary module is available.

Netdev open creates Navigator resources: RX/TX descriptor pools, TX completion queue, RX completion queue, RX free descriptor queues, notifiers, and RX DMA channel. It then calls each attached module open, enables NAPI and queue notifications, refills RX FDQs, and wakes TX queues. Stop halts queues/carrier, clears address marks and fanout deletions, disables notifications/NAPI, calls module close, recycles RX and TX descriptors, validates TX pool count, and frees Navigator resources.

TX maps skb linear and fragment buffers into one or more DMA descriptors, runs ordered TX hooks, requires a hook to select a `netcp_tx_pipe`, writes PS data/EPIB/return queue/target port info, stores skb/timestamp callback in descriptor/SKB control state, maps the descriptor, pushes it to the DMA queue, and pauses subqueues when descriptors fall below threshold. TX completion pops completion descriptors, unmaps/free descriptor chains, invokes timestamp callback, wakes subqueues if descriptor count recovers, updates stats, and frees skb.

RX refills FDQs with primary buffers and secondary page buffers. RX notify schedules NAPI. RX NAPI pops descriptors, builds an skb from the primary buffer, attaches page frags for chained descriptors, trims FCS for older hardware, runs RX hooks, updates stats, delivers with `netif_receive_skb()`, and refills FDQs.

## State and persistence behavior
Global runtime state includes `netcp_devices`, `netcp_modules`, and `netcp_modules_lock`. Per-device state tracks interface and module-private lists. Per-interface state holds DMA queues/pools/channels, NAPI instances, hook lists, address records, module-private attachments, stats, and DT-derived queue/pool configuration. Resources are created on probe/interface creation or netdev open and are destroyed on stop/remove. No disk persistence is present.

## Dependencies and integration points
The file depends on Linux platform, OF, PM runtime, netdevice, VLAN, tc mqprio, DMA mapping, NAPI, TI knav QMSS and DMA APIs, and local `netcp.h`. It exports GPL symbols for NetCP submodules and declares a platform driver for `ti,netcp-1.0`.

## Risks and edge cases
- The code stores virtual pointers in 32-bit descriptor `sw_data` fields, with explicit warnings that this will not work on 64-bit machines.
- In RX, `pkt_sz` is initialized to zero and masked without reading descriptor packet length first, so the packet-size mismatch debug comparison appears ineffective or suspicious.
- DMA mapping direction in RX allocation uses `DMA_TO_DEVICE` for buffers that are later unmapped with `DMA_FROM_DEVICE`; this deserves careful verification against the target DMA API expectations.
- Module lifecycle is order-sensitive; primary-module registration controls netdev registration.
- TX frag-list is unsupported and rejected after some mapping work, so unwind paths must remain correct.
- Address list updates call module callbacks while holding `netcp->lock`; callback behavior must avoid deadlocks.
- `netcp_delete_interface()` calls `unregister_netdev()` even if registration may not have happened unless interface creation/probe sequencing guarantees it.

## Test signals
Test probe with missing DT properties and deferred DMA/QMSS readiness; module registration before/after platform probe; primary-module delayed registration; netdev open/stop resource allocation and unwind; RX buffer refill and chained RX packets; TX linear, fragmented, and frag-list skb paths; TX completion and timeout recovery; hook ordering/rejection; address/promiscuous/multicast fanout; VLAN add/delete; hwtstamp get/set delegation; runtime PM remove; and 64-bit build/static analysis for descriptor pointer truncation.
