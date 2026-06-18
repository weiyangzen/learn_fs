# sources/distributed-fs/ceph-client/include/uapi/linux/lwtunnel.h

Purpose: defines lightweight tunnel netlink attribute IDs used by routes with encapsulation actions.

Important APIs and types: `enum lwtunnel_encap_types` covers MPLS, IPv4, ILA, IPv6, Segment Routing, BPF, SEG6 local, RPL, IOAM6, and XFRM encapsulations. Attribute enums define IPv4/IPv6 tunnel IDs, source/destination addresses, TTL/hoplimit, TOS/traffic class, flags, options, Geneve/VXLAN/ERSPAN option layouts, BPF program fd/name attributes for in/out/xmit hooks, XMIT headroom, and XFRM if_id/link attributes. `LWT_BPF_MAX_HEADROOM` caps BPF tunnel headroom.

Control flow: route management tools encode lwtunnel attributes in rtnetlink route messages. Kernel routing decodes the selected encapsulation type and nested attributes, attaches tunnel state or BPF programs to the route, and applies them on forwarding/output.

State and persistence: route entries hold lwtunnel configuration in kernel FIB state. Persistence depends on userspace route configuration replay, not this header.

Dependencies and integration points: depends on `linux/types.h`; integrates rtnetlink, iproute2, MPLS, IP/IP6 tunnels, SEG6, BPF LWT hooks, XFRM interfaces, Geneve/VXLAN/ERSPAN options, and IOAM/RPL support.

Risks and test signals: risks include nested attribute policy drift, unsupported encap type handling, BPF headroom bounds, address-family confusion, and route dump/restore incompatibility. Test iproute2 add/dump/delete for every encap type, invalid nested attrs, BPF fd lifetime, XFRM link attributes, and packet-path forwarding.
