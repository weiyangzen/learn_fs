# sources/distributed-fs/ceph-client/include/linux/seg6_iptunnel.h

Purpose: `seg6_iptunnel.h` wraps UAPI definitions for SRv6 IP tunnel encap/decap behavior.

Important APIs/types/functions: It includes `<uapi/linux/seg6_iptunnel.h>` and adds no kernel-only API.

Control flow: No control flow is implemented here. Tunnel code uses UAPI structures for route attributes and lightweight tunnel setup.

State and persistence behavior: Tunnel state is stored in route/lwtunnel objects outside this header.

Dependencies and integration points: It integrates with IPv6 route attributes, lwtunnel infrastructure, netlink, and SRv6 encapsulation modes.

Risks: Attribute layout must match userspace. Callers must validate segment list lengths and tunnel mode constraints in implementation code.

Test signals: Route add/delete with SRv6 tunnel encap, packet forwarding through tunnels, netlink dump round trips, and invalid attribute rejection.
