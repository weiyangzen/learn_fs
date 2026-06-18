<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.c -->
# sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.c research

Purpose: manages gateway client behavior: tracking announced gateways, selecting the best current gateway through routing-algorithm hooks, emitting gateway uevents, parsing DHCP packets for gateway-related forwarding, and detecting DHCP requests sent to an outdated gateway.

Important APIs and functions: public functions include `batadv_gw_get_selected_gw_node()`, `batadv_gw_get_selected_orig()`, `batadv_gw_reselect()`, `batadv_gw_check_client_stop()`, `batadv_gw_election()`, `batadv_gw_check_election()`, `batadv_gw_node_update()`, `batadv_gw_node_delete()`, `batadv_gw_node_free()`, `batadv_gw_dump()`, `batadv_gw_dhcp_recipient_get()`, and `batadv_gw_out_of_range()`. `batadv_gw_node_release()` owns kref teardown.

Control flow: TVLV processing in gateway common calls `batadv_gw_node_update()` to add, update, or remove gateway nodes. `batadv_gw_check_election()` sets a reselect flag when a candidate can beat the current gateway. `batadv_gw_election()` runs in client mode, asks `algo_ops->gw.get_best_gw_node()` for the best gateway, validates router and interface info, emits ADD/DEL/CHANGE uevents, and swaps `bat_priv->gw.curr_gw` under `gw.list_lock`. DHCP parser walks Ethernet, optional VLAN, IPv4/IPv6, UDP, and BOOTP/DHCP fields and returns whether a packet targets a server or client. `batadv_gw_out_of_range()` uses TT and gateway list lookup to decide if a unicast DHCP request targets a gateway with TQ worse than the current gateway by more than `BATADV_GW_THRESHOLD`.

State and persistence: `bat_priv->gw.gateway_list` is an RCU hlist protected for writes by `gw.list_lock`, with `generation` tracking netlink dump consistency. `curr_gw` is an RCU pointer with kref ownership. Each `batadv_gw_node` references an originator and stores announced down/up bandwidth in tenths of Mbit. All state is rebuilt from TVLV announcements and is not persisted.

Dependencies and integration: depends on routing algorithm gateway hooks, originator and neighbor lookups, TT search for DHCP destination, netlink, hard-interface primary selection for dumps, logging, and `batadv_throw_uevent()`. It is coupled to gateway_common TVLV registration and to routing paths that need DHCP-aware gateway handling.

Risks: current gateway replacement must balance references on both old and new nodes. Updates remove nodes when down bandwidth reaches zero and must reselect if the removed node was current. DHCP parsing modifies `header_len` as it advances, so callers must pass initialized offsets and expect skb data may be pulled. `batadv_gw_out_of_range()` subtracts TQ values and compares threshold; type widths and ordering matter.

Test signals: gateway add/update/remove TVLVs, gateway client mode transitions, uevent ADD/DEL/CHANGE generation, routing algorithm hooks missing or returning NULL, netlink dump with inactive primary interface, IPv4/IPv6 DHCP to server/client parsing, VLAN DHCP parsing, and out-of-range detection under controlled TQ differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/batman-adv/gateway_client.c -->
