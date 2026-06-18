# sources/distributed-fs/ceph-client/net/ipv4/ip_output.c

## Purpose
Implements the IPv4 transmit path for locally generated packets: final header checksum and LOCAL_OUT/POST_ROUTING hooks, route-backed packet output, multicast/broadcast loopback, GSO and fragmentation handling, corked datagram assembly, skb construction from user/kernel buffers, and helper replies such as TCP reset/ack style unicast replies.

## APIs, Types, and Functions
Exported entry points include `ip_send_check()`, `__ip_local_out()`, `ip_local_out()`, `ip_build_and_send_pkt()`, `ip_output()`, `__ip_queue_xmit()`, `ip_queue_xmit()`, `ip_do_fragment()`, `ip_fraglist_init()`, `ip_fraglist_prepare()`, `ip_frag_init()`, `ip_frag_next()`, `ip_generic_getfrag()`, `ip_append_data()`, `__ip_make_skb()`, `ip_send_skb()`, `ip_push_pending_frames()`, `ip_flush_pending_frames()`, `ip_make_skb()`, `ip_send_unicast_reply()`, and `ip_init()`. Important local helpers are `ip_finish_output2()`, `ip_finish_output_gso()`, `__ip_finish_output()`, `ip_finish_output()`, `ip_mc_output()`, `ip_fragment()`, `__ip_append_data()`, `ip_setup_cork()`, `ip_cork_release()`, and `ip_reply_glue_bits()`.

## Control Flow
Transmit starts either from a prebuilt skb (`ip_local_out()`, `ip_output()`), a transport skb needing an IPv4 header (`__ip_queue_xmit()`), or corked data (`ip_append_data()` then `ip_push_pending_frames()`). The local path sets total length and checksum, applies L3 master handling, runs `NF_INET_LOCAL_OUT`, and then calls destination output. Post-routing output runs cgroup egress BPF and `NF_INET_POST_ROUTING`, handles multicast/broadcast loopback clones, resolves lightweight tunnels and neighbours, and emits through `neigh_output()`.

Large packets are processed by `__ip_finish_output()`: GSO skbs are either emitted directly if segment sizes fit the MTU or segmented and fragmented; non-GSO skbs exceeding MTU or carrying `frag_max_size` go through `ip_fragment()`. Fragmentation uses a fast `frag_list` path when geometry/headroom/share checks pass, otherwise allocates and copies fragments with `ip_frag_next()`. Corked sends accumulate skbs on a write queue, choose checksum/zerocopy/splice/page-frag modes, then `__ip_make_skb()` chains fragments, builds the final IPv4 header, assigns DF/TTL/TOS/ID/options, attaches the route, and releases cork state.

## State and Persistence
The file mostly mutates transient skb, cork, and socket state. Persistent or longer-lived state includes socket route capabilities (`sk_setup_caps()`), `inet->cork.base` fields and `sk_write_queue` until pushed or flushed, socket write-memory accounting, timestamp keys, dst references stolen into corks/skbs, IP statistics counters, neighbour confirmation, and peer/route/multicast initialization in `ip_init()`. Error paths update socket error queues through `ip_local_error()` and increment MIB discard/fragment failure counters.

## Dependencies and Integration
This code is a central integration point for routing (`rtable`, `dst_output`, `ip_route_output_flow()`), netfilter, cgroup BPF egress, L3 master devices, lightweight tunnels, XFRM reroute, neighbour/ARP output, socket corking, checksum and GSO helpers, zerocopy/splice page handling, ICMP PMTU feedback, IGMP multicast, and protocol callers such as TCP, UDP, raw sockets, ICMP, and tunnel modules.

## Risks
High-risk areas are MTU/DF interactions, fragment list validation and ownership transfer, checksum mode transitions, cork error unwinding, zerocopy reference accounting, route reference lifetime, timestamp key rollback, local multicast clone semantics, and subtle skb metadata copying across fragments. Recursion through XFRM/netfilter/lwtunnel and mixed GSO/fragmentation paths are especially sensitive to regressions.

## Test Signals
Useful signals include packetdrill or kselftest coverage for UDP corking, MSG_MORE, MSG_ZEROCOPY, MSG_SPLICE_PAGES, PMTU EMSGSIZE and ICMP generation, netfilter LOCAL_OUT/POST_ROUTING ordering, cgroup egress drops, multicast and broadcast loopback delivery, GSO over low-MTU paths, raw/IP options handling, and fragment counters (`FRAGOKS`, `FRAGFAILS`, `FRAGCREATES`). Runtime validation should inspect skb lengths, DF/MF/offset fields, checksums, route/device selection, and socket error queue contents.
