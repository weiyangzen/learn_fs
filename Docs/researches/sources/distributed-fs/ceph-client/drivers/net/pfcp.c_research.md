# sources/distributed-fs/ceph-client/drivers/net/pfcp.c

Purpose: Implements an rtnetlink-created PFCP virtual interface that receives PFCP UDP packets on the standard PFCP port, strips the PFCP header, attaches tunnel metadata, and injects payloads through GRO cells.

Important APIs, types, and functions: `struct pfcp_dev` stores list linkage, UDP socket, netdev, net namespace, and GRO cells. `struct pfcp_net` stores per-netns device list. RX functions are `pfcp_encap_recv()`, `pfcp_session_recv()`, and `pfcp_node_recv()`. Netdev lifecycle is `pfcp_link_setup()`, `pfcp_dev_init()`, `pfcp_dev_uninit()`, `pfcp_newlink()`, and `pfcp_dellink()`. Socket setup is `pfcp_create_sock()`, `pfcp_add_sock()`, and `pfcp_del_sock()`. Namespace/module lifecycle is `pfcp_net_init()`, `pfcp_net_exit_rtnl()`, `pfcp_init()`, and `pfcp_exit()`.

Control flow: Module init registers pernet ops and rtnl link kind `"pfcp"`. Newlink creates a UDP IPv4 socket bound to `PFCP_PORT`, installs a UDP tunnel receive callback with `sk_user_data = pfcp`, registers the netdev, and links it into the namespace list. RX validates minimum PFCP header, allocates tunnel metadata, records node/session type and SEID when present, marks PFCP tunnel options, pulls the PFCP header, sets skb dst/dev/headers, and delivers via GRO cells.

State and persistence behavior: One `pfcp_dev` exists per PFCP netdev, owning its UDP socket and GRO cells. `pfcp_net` tracks devices per namespace for exit cleanup. There is no persistent storage beyond netdev/socket lifetime.

Dependencies and integration points: It depends on rtnl link ops, pernet operations, UDP tunnel socket helpers, `net/pfcp.h` header parsing and metadata definitions, ip tunnel metadata, GRO cells, and netdev stats helpers.

Risks and edge cases: Only an IPv4 wildcard UDP socket is created, so IPv6 PFCP is not handled here. `pfcp_encap_recv()` drops all malformed packets and always consumes the skb. Metadata allocation and `iptunnel_pull_header()` failures must free skb and avoid leaking `metadata_dst`; ownership transfers through `skb_dst_set()` on success. Namespace exit must unregister queued netdevs under rtnl. Binding to PFCP_PORT can fail if unavailable in the namespace.

Test signals: Create/delete PFCP links in multiple netns, port bind failure, receive node and session PFCP packets with SEID metadata, too-short packet drops, metadata allocation failure injection, GRO delivery, namespace teardown with live devices, stats reads, module unload, and verification that PFCP tunnel option bits are visible to consumers.
