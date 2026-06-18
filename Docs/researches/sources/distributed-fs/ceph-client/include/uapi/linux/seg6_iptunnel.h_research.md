<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_iptunnel.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/seg6_iptunnel.h

Purpose: defines netlink attributes and mode constants for SRv6 lightweight tunnel encapsulation.

Important APIs, types, and functions: attributes include `SEG6_IPTUNNEL_SRH` and max constants. Mode constants include inline, encap, L2 encap, encap with reduced SRH, and L2 encap with reduced SRH. `SEG6_IPTUNNEL_SRH_SIZE(srh)` computes SRH byte size from `hdrlen`.

Control flow: route configuration passes an SRH and mode through netlink. Kernel lwtunnel code validates the SRH, stores it in route encap state, and applies inline or encapsulation behavior when packets match the route.

State and persistence behavior: route/lwtunnel entries retain the serialized SRH and mode until route deletion or replacement. The header itself stores nothing.

Dependencies and integration points: integrates with `seg6.h`, rtnetlink route encap attributes, IPv6 lwtunnel output, and iproute2.

Risks and edge cases: reduced modes have specific segment-list requirements. The size macro assumes a valid SRH pointer and must only run after attribute length checks. Inline mode mutates existing IPv6 packets while encap modes add outer headers.

Test signals: route add/dump/delete for each mode, packet forwarding checks, invalid SRH length rejection, reduced-mode segment validation, and l2/l3 encapsulation tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/seg6_iptunnel.h -->
