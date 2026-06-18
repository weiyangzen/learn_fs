# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_common.c

## Purpose
Implements common PF/VF vNIC behavior independent of NFD3 versus NFDK datapath: firmware reconfiguration, mailbox access, IRQ/vector setup, open/close, ring reconfiguration, MTU/features/RSS/coalesce, multicast/VLAN/flow steering, XDP/XSK hooks, netdev ops, UDP tunnel sync, allocation/init/clean, TLS/IPsec initialization, and stats.

## Important APIs, Types, and Functions
- Reconfig machinery: `__nfp_net_reconfig()`, `nfp_net_reconfig()`, `nfp_net_reconfig_post()`, timer-based async reconfig, and mailbox wrappers serialize firmware updates through BAR update fields and QCP config queue.
- IRQ/lifecycle: `nfp_net_irqs_alloc/assign/disable()`, auxiliary IRQ request/free, `nfp_net_open_alloc_all()`, `nfp_net_set_config_and_enable()`, `nfp_net_clear_config_and_disable()`, `nfp_net_netdev_open()`, `nfp_net_netdev_close()`, `nfp_ctrl_open()`, and `nfp_ctrl_close()`.
- Offload/config: RSS key/table writing, coalesce/DIM work, `nfp_net_set_features()`, feature fix/check, bridge mode, UDP tunnel sync, XDP driver/HW setup, XSK setup delegation, TLS TX fallback/undo, VLAN filter mailbox, multicast mailbox, and flow steering add/delete.
- Object lifecycle: `nfp_net_alloc()`, `nfp_net_free()`, `nfp_net_init()`, `nfp_net_clean()`, `nfp_net_read_caps()`, and `nfp_net_netdev_init()`.
- Exports two netdev ops tables: `nfp_nfd3_netdev_ops` and `nfp_nfdk_netdev_ops`, differing mainly in start_xmit and XSK wakeup support.

## Control Flow
Allocation reads firmware version, selects datapath ops, validates DMA mask, initializes queue counts, locks, TLV caps, and common control mailbox. Init reads firmware capabilities, computes MTU/freelist size, initializes RSS/coalesce/control bits, disables firmware rings, initializes netdev features/offloads, TLS/IPsec, vectors, async mailbox work, flow steering list, and registers netdev.

Open requests auxiliary and queue IRQs, prepares RX/TX rings through datapath ops, assigns rings to vectors, configures queue counts, enables physical port, writes RSS/coalesce/ring/MAC/MTU/freelist config, fills RX freelists, enables firmware, enables NAPI/IRQs and TX queues, then reads link status. Close disables IRQs/NAPI/TX, unsyncs multicast if needed, disables firmware and rings, disables port, frees rings and IRQs.

Ring/MTU/XDP reconfiguration clones `nfp_net_dp`, adjusts counts and DMA offsets, validates XDP/XSK constraints, prepares new resources if running, closes stack, disables firmware, swaps datapath, tries to enable new config, attempts rollback on failure, frees old resources, and reopens stack.

## State and Persistence Behavior
Maintains volatile vNIC state mirrored into firmware via BARs. Reconfig state (`reconfig_posted`, timer, sync-present flag) merges async updates while allowing synchronous callers to take ownership. Async mailbox messages are queued in memory and flushed during clean. Flow steering rules are stored in `nn->fs.list` and removed from firmware during clean. Feature bits are mirrored between `netdev->features`, `nn->dp.ctrl`, and firmware.

## Dependencies and Integration Points
Depends on Linux netdev/ethtool/VLAN/bridge/BPF/XDP/XSK/TLS/XFRM/DIM/PCI APIs, NFP control ABI, datapath ops, app callbacks, port operations, crypto/TLS/IPsec helpers, SR-IOV helpers, common control mailbox, and ring helpers. It is the central integration file for `nfp_net.h`.

## Risks
Firmware reconfig serialization is subtle; posted updates can be merged, cancelled, or taken over by sync callers. Open/close and ring reconfig have many partial-resource unwind paths. Feature negotiation must keep firmware ctrl bits and netdev advertised features consistent, especially mutually exclusive VLAN stripping and TSO/TXVLAN limitations. `nfp_net_ring_reconfig()` rollback can fail, leaving firmware communication broken. Async multicast mailbox work may outlive netdev changes unless flushed correctly.

## Test Signals
Probe/init with NFD3 and NFDK firmware, netdev open/close loops, `ip link set mtu`, ethtool ring/RSS/coalesce changes, feature toggles, VLAN add/del, multicast list churn, XDP attach/detach and XSK pool setup, TLS/IPsec configs, flow steering rules, bridge VEPA/VEB, VXLAN port sync, forced firmware reconfig timeout/error, and cleanup with pending async mailbox work.
