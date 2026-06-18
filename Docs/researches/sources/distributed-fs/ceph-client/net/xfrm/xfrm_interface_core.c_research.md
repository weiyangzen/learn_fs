# sources/distributed-fs/ceph-client/net/xfrm/xfrm_interface_core.c

Purpose: `xfrm_interface_core.c` implements the `xfrm` virtual netdevice. It routes packets through XFRM SAs by `if_id`, receives decapsulated packets onto matching virtual devices, supports collect-metadata mode, registers lwtunnel XFRM encap, and wires protocol handlers for ESP/AH/IPComp/IPIP/IPIP6.

Important APIs and types: `struct xfrmi_net` stores per-net hash buckets of `struct xfrm_if` and one collect-md interface. Rtnetlink ops create/change/delete devices with `IFLA_XFRM_LINK`, `IFLA_XFRM_IF_ID`, and `IFLA_XFRM_COLLECT_METADATA`. LWT ops build/fill/compare `LWTUNNEL_ENCAP_XFRM` metadata. Protocol handlers call `xfrmi_input()` and `xfrmi_rcv_cb()`. Module init registers pernet state, IPv4/IPv6 protocol and tunnel handlers, rtnl link ops, BPF kfuncs, lwtunnel ops, and `xfrm_if_cb`.

Control flow: Receive callbacks locate an up xfrm interface by state `if_id` or collect-md, switch `skb->dev`, enforce inbound policy for cross-net delivery, scrub packet metadata, optionally attach metadata dst with if_id/link, and update rx stats. Transmit decodes IPv4/IPv6 flow, obtains or builds a route, performs `xfrm_lookup_with_ifid()`, rejects routing loops and wrong `if_id`, handles PMTU/ICMP errors, scrubs packet, switches to the underlying device, and calls `dst_output()`. Error handlers map ICMP/ICMPv6 PMTU and redirects back to matching SAs.

State and persistence: Per-net interface hash tables persist while net namespace lives. Each netdevice stores `xfrm_if_parms`, owning net, gro cells, and stats. Collect-md mode stores packet-specific metadata in dst metadata.

Dependencies and integration: Integrates with XFRM policy lookup, XFRM input callbacks, route/lwtunnel infrastructure, rtnetlink, IPv4/IPv6 tunnel/protocol registration, BPF kfuncs, gro cells, and namespace generic storage.

Risks: Cross-netns scrubbing and secpath reset are critical isolation points. Routing-loop detection prevents recursive xfrm output. Collect-md and fixed-if_id modes have different validation rules; allowing changes incorrectly could misroute traffic. Error handler SPI parsing must match AH/ESP/IPComp headers.

Test signals: Create fixed and collect-md xfrm devices, verify duplicate if_id rejection, change if_id, delete namespace cleanup, transmit IPv4/IPv6 through matching/missing policies, receive decapsulated traffic, PMTU errors, redirects, cross-netns paths, lwtunnel encap routes, TC-BPF metadata steering, and module unload cleanup.
