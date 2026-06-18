<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/tunnel_conf.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/tunnel_conf.c

## Purpose
`tunnel_conf.c` manages Flower tunnel offload control-plane state: active tunnel keep-alives, route and neighbor resolution requested by firmware, tunnel endpoint IP lists, offloaded MAC address indexes, pre-tunnel rule programming, and netevent-driven neighbor updates.

## Important APIs, Types, And Functions
Public APIs include `nfp_tunnel_config_start()`, `nfp_tunnel_config_stop()`, `nfp_tunnel_keep_alive()`, `nfp_tunnel_keep_alive_v6()`, `nfp_tunnel_request_route_v4()`, `nfp_tunnel_request_route_v6()`, `nfp_tunnel_add_ipv4_off()`, `nfp_tunnel_del_ipv4_off()`, `nfp_tunnel_add_ipv6_off()`, `nfp_tunnel_put_ipv6_off()`, `nfp_tunnel_mac_event_handler()`, `nfp_flower_xmit_pre_tun_flow()`, `nfp_flower_xmit_pre_tun_del_flow()`, and pre-tunnel neighbor link helpers.

## Control Flow
Keep-alive handlers validate message length/count, resolve egress ports to netdevs, look up IPv4/IPv6 neighbors, and refresh neighbor timestamps. Route request handlers perform namespace-local route lookups based on ingress port, find the neighbor, and force-write the neighbor to firmware. Netevent notifications allocate work items, hold the neighbor, and on a high-priority workqueue populate flowi source/destination data and call `nfp_tun_write_neigh()`.

`nfp_tun_write_neigh()` is the central neighbor state machine. It creates a neighbor table entry and sends it when a valid neighbor is first seen, sends a zero/delete-style payload and removes the table entry when invalid, or refreshes MAC data on override/MAC change. It also links neighbor entries to decap pre-tunnel rules by matching local/remote MACs and sets host context/VLAN extension fields. MAC offload tracks shared MAC addresses in an rhashtable, chooses physical-port or global IDA-backed indexes, adjusts bridge/pre-tunnel bits, and sends add/delete/mod firmware messages on netdev up/down/address/upper changes.

## State And Persistence
State includes `tun.offloaded_macs`, IPv4 and IPv6 endpoint lists with refcounts, `mac_off_ids`, `neigh_table`, `predt_list` links, per-representor/non-representor MAC offload flags, and `pre_tun_rule_cnt`. Firmware state is sent through tunnel control messages for neighbor, endpoint IP, MAC, and pre-tunnel rule types. All state is in memory and should be drained by flow deletion and tunnel config stop.

## Dependencies And Integration Points
The file depends on ARP/ND neighbor tables, IPv4/IPv6 route lookup, netevent notifier, OVS bridge recognition, NFP representor and non-representor helpers, LAG metadata, Flower feature flags for decap v2 and tunnel-neighbor LAG, and match/offload code that stores tunnel endpoint refs and pre-tunnel metadata.

## Risks
Several paths run from notifier/workqueue context and use `GFP_ATOMIC` under `predt_lock`; allocation or firmware-send failures can leave host and firmware state divergent. MAC index transitions for bridge/shared/repr cases are subtle, especially when reverting global IDs back to physical-port IDs. `nfp_tunnel_request_route_v4/v6()` call `dev_put(netdev)` on failure labels even when `netdev` lookup failed, which is a fragile pattern to audit. Stop frees IPv4 list entries and destroys the IPv6 lock but does not explicitly walk/free IPv6 endpoint entries here, relying on flow reference cleanup before stop.

## Test Signals
Test IPv4/IPv6 route requests, keep-alive length/count validation, neighbor valid/invalid/MAC-change events, bridge upper link/unlink transitions, duplicate/shared MAC refcounts, LAG egress neighbor metadata, tunnel endpoint list limit handling, pre-tunnel rule count limit, decap v2 neighbor/pre-tunnel linking, and module/device teardown under outstanding neighbor work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/flower/tunnel_conf.c -->
