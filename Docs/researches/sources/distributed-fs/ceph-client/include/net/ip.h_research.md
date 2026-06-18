# sources/distributed-fs/ceph-client/include/net/ip.h

Purpose: central IPv4 networking header for packet metadata, output/input prototypes, fragmentation, corked sends, stats, PMTU/MTU helpers, IPID selection, multicast address mapping, defrag users, options, cmsg handling, and socket option wrappers.

Important APIs/types: `struct inet_skb_parm` overlays `skb->cb` for IPv4 flags, ingress ifindex, options, and frag max size. `struct ipcm_cookie` carries sendmsg control state. `ip_ra_chain` stores router-alert sockets. Fragment helpers use `ip_fraglist_iter` and `ip_frag_state`. Core APIs include `ip_rcv()`, `ip_local_deliver()`, `ip_output()`, `ip_do_fragment()`, `ip_queue_xmit()`, `ip_append_data()`, `ip_make_skb()`, `ip_send_skb()`, datagram connect, unicast reply, defrag, forward, options, cmsg, sockopt, and error helpers.

Control flow and state: receive enters `ip_rcv()`, may defrag, route, deliver locally/forward, and update MIB counters. Send paths build `flowi4`, append/cork payload into write queues, make skbs, select IPID, set checksums/options, fragment if needed, and output. PMTU helpers choose MTU from route, sysctls, device MTU, and lwtunnel headroom.

Dependencies and integration: depends on inet sock, route, SNMP, flow, flow dissector, netns hash, lwtunnel, DSCP, dst metrics, ICMP, and proc/sysctl optional code.

Risks: skb control-block aliasing, PMTU policy, IP options, fragmentation, and checksum/IPID updates are high risk. Tests should cover sendmsg cmsg, cork/flush, fragmentation with DF/PMTU, defrag users, route scope, multicast MAC mapping, options echo/compile, error queues, stats counters, and sysctl-influenced behavior.
