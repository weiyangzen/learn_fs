# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_netdev.c

## Purpose
`fm10k_netdev.c` implements Linux `net_device` integration for the fm10k driver. It allocates and frees descriptor resources, opens and closes the interface, prepares outbound skbs for the ring transmit path, handles netdev VLAN/MAC/multicast/promiscuous changes, restores and resets Rx filter state, exposes statistics and traffic-class setup, manages macvlan L2 forwarding offload, checks offload features, and allocates/configures the netdev instance.

## Important APIs, types, and functions
Resource management is provided by `fm10k_setup_tx_resources()`, `fm10k_setup_rx_resources()`, `fm10k_free_tx_resources()`, `fm10k_free_rx_resources()`, `fm10k_clean_all_tx_rings()`, `fm10k_clean_all_rx_rings()`, and `fm10k_unmap_and_free_tx_resource()`.

Netdev lifecycle and transmit entry points are `fm10k_open()`, `fm10k_close()`, `fm10k_xmit_frame()`, and `fm10k_tx_timeout()`. Filter and address management use `fm10k_queue_vlan_request()`, `fm10k_queue_mac_request()`, `fm10k_clear_macvlan_queue()`, `fm10k_update_vid()`, `fm10k_set_mac()`, `fm10k_set_rx_mode()`, `fm10k_restore_rx_state()`, and `fm10k_reset_rx_state()`.

Other important APIs include `fm10k_get_stats64()`, `fm10k_setup_tc()`, `__fm10k_setup_tc()`, `fm10k_dfwd_add_station()`, `fm10k_dfwd_del_station()`, `fm10k_features_check()`, `fm10k_alloc_netdev()`, and the `fm10k_netdev_ops` table. The file also defines `fm10k_udp_tunnels` and `fm10k_udp_tunnel_sync()` for VXLAN/Geneve port tracking.

## Control flow
Opening the interface allocates all Tx/Rx descriptor rings, requests queue-vector IRQs, computes GLORT range assignment, publishes actual Tx/Rx queue counts to the stack, and calls `fm10k_up()` in the PCI layer to program hardware and start traffic. Closing calls `fm10k_down()`, frees queue-vector IRQs, and releases Tx/Rx resources.

Transmit begins in `fm10k_xmit_frame()`. It handles inline 802.1Q headers by converting them to hardware-accelerated VLAN tags, pads very small packets to the hardware minimum, normalizes an out-of-range queue mapping, and delegates descriptor construction to `fm10k_xmit_frame_ring()` in `fm10k_main.c`.

VLAN/MAC state changes are queued rather than synchronously blasted to hardware. `fm10k_queue_vlan_request()` and `fm10k_queue_mac_request()` allocate `struct fm10k_macvlan_request` entries under `macvlan_lock` and schedule `macvlan_task` in `fm10k_pci.c`. `fm10k_update_vid()` updates the active VLAN bitmap, adjusts per-Rx-ring default VLAN suppression, and, when running, queues VLAN and MAC updates for the base interface plus L2-accelerated macvlan stations. `fm10k_set_rx_mode()` converts netdev flags into FM10K xcast mode, queues all-VLAN changes for promiscuous transitions, updates hardware xcast mode when the host mailbox is ready, and syncs unicast/multicast lists.

Rx state restoration after reset reenables the logical port, requeues VLAN/MAC filters for active VLANs and L2 accel stations, restores xcast mode and tunnel configuration, and synchronizes address lists. Resetting Rx state waits for pending MAC/VLAN work to finish, clears queued requests, disables the logical port, and clears netdev address-sync flags.

## State and persistence behavior
This file maintains runtime state in `struct fm10k_intfc`: active VLAN bitmap, GLORT base/count, default/current VID state, xcast mode, L2 acceleration table, queued MAC/VLAN requests, VXLAN/Geneve port values, ring counts, and feature flags. Descriptor memory is allocated with `dma_alloc_coherent()` and software ring metadata with `vzalloc()`, then freed on close, reset, or error unwind.

MAC/VLAN requests persist in memory until the delayed `macvlan_task` submits them through mailbox operations or `fm10k_clear_macvlan_queue()` cancels them. L2 forwarding offload state is RCU-protected because Rx rings dereference it during packet delivery. Statistics returned to the stack are accumulated from per-ring counters with `u64_stats_fetch_begin/retry` so 32-bit readers see consistent values.

## Dependencies and integration points
The file depends on Linux netdev, VLAN, UDP tunnel, DMA coherent allocation, vmalloc, macvlan, multicast/unicast address sync, mqprio traffic-class, and stats APIs. It integrates with `fm10k_main.c` for descriptor datapath functions, with `fm10k_pci.c` for hardware up/down, IRQs, mailbox IRQs, and macvlan task execution, with hardware ops through `hw->mac.ops`, with IOV ndo handlers for VF configuration, and with ethtool setup.

Tunnel integration supports one VXLAN and one Geneve UDP port in `udp_tunnel_nic_info`; PF-only tunnel registers are restored after reset. L2 forwarding acceleration integrates with macvlan destination-filter capability and DGLORT mapping.

## Risks and edge cases
Resource unwind paths must free partially allocated rings in reverse order and avoid double-freeing descriptor memory. `fm10k_xmit_frame()` mutates skbs to convert inline VLAN headers; failure paths must drop safely after `skb_share_check()`, `pskb_may_pull()`, or `skb_cow_head()`. VLAN override mode restricts VLAN additions and suppresses some removal requests.

MAC/VLAN queue processing is asynchronous, so reset/down paths must stop or drain the delayed work before clearing state. `fm10k_clear_macvlan_queue()` has subtle filtering behavior: MAC requests are GLORT-specific, while VLAN requests are removed only when the `vlans` parameter allows it. L2 acceleration grows the table under RCU; incorrect assignment could leave Rx rings pointing to freed state. Traffic-class setup closes and reopens the device and can detach the netdev on failure.

## Test signals
Validation should cover open/close error unwinds, ring allocation failures, transmit with inline VLAN tags, tiny packet padding, Tx timeout false-positive backoff vs real reset, VLAN add/remove with default VLAN and override cases, promiscuous/allmulti transitions, MAC address changes while up and down, address-list sync/unsync, reset-time Rx state replay, tunnel port add/delete restore, mqprio setup for PF vs VF, and macvlan L2 offload add/remove under traffic. Useful runtime signals include active VLAN bitmap changes, queued MAC/VLAN list length, xcast mode, GLORT mappings, stats64 totals, and mailbox readiness gating.
