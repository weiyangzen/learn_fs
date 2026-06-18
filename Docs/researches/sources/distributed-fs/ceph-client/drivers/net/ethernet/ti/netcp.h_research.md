# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/netcp.h

## Purpose
This is the local interface for the TI Keystone NetCP core. It defines the netcp interface state, module plugin contract, TX pipe abstraction, packet metadata passed through ordered hooks, address tracking, statistics, hardware link-mode constants, and exported core APIs used by NetCP submodules.

## Important APIs, types, and functions
- `struct netcp_tx_pipe` describes a DMA TX path, including queue/channel names, queue ID, target switch port, and tag-info behavior.
- `struct netcp_addr` and `enum netcp_addr_type` track broadcast, device, unicast, multicast, and promiscuous wildcard addresses with mark bits.
- `struct netcp_stats` uses `u64_stats_sync` and `u64_stats_t` for RX/TX packets and bytes plus 32-bit errors/drops.
- `struct netcp_intf` is the per-netdev core state: DMA queues, pools, NAPI, hook lists, module-private list, address list, runtime flags, lock, device pointers, and queue depth configuration.
- `struct netcp_packet` is the object passed through RX/TX hooks, containing skb, descriptor EPIB/PS data, flags, selected TX pipe, timestamp callback, and context.
- `netcp_push_psdata()` reserves protocol-specific words at the tail of the PS data array.
- `netcp_align_psdata()` reports padding needed for a desired byte alignment.
- `struct netcp_module` is the submodule plugin interface: probe/remove once per device, attach/release per netdev, open/close, address/VLAN updates, ioctl, RX mode, and hardware timestamp get/set.

## Control flow
NetCP platform probe creates `struct netcp_intf` objects. Submodules register via `netcp_register_module()`, are probed per device, attached per interface via phandles, and can register RX/TX hooks. During TX, hooks inspect and mutate `struct netcp_packet`, select a `netcp_tx_pipe`, and populate PS/EPIB/timestamp behavior. During RX, hooks process packet metadata before the core delivers the skb to the network stack. Address/VLAN/RX-mode changes are fanned out to attached modules.

## State and persistence behavior
All state is kernel runtime state. The interface object owns lists of modules, hooks, and address records. DMA queues/pools/channels are opened on netdev open and closed on stop. Stats persist for the netdev lifetime.

## Dependencies and integration points
The header depends on Linux netdevice, TI knav DMA, and u64 stats APIs. It is implemented by `netcp_core.c` and used by Keystone Ethernet switch/SGMII/XGBE modules.

## Risks and edge cases
- The packet hook contract is powerful but implicit: TX must be claimed by exactly one hook through `p_info.tx_pipe`.
- PS data helpers reserve from the end of a fixed word array; hook order must be coordinated.
- Several implementation paths store kernel pointers in 32-bit descriptor software words, noted as not working on 64-bit machines.
- Module registration order and primary-module behavior affect when interfaces become registered.

## Test signals
Compile submodules against the module API, register/unregister modules before and after platform probe, TX hook ordering and TX pipe selection, RX hook rejection, PS data alignment/push bounds, address list fanout, VLAN fanout, and hardware timestamp delegation.
