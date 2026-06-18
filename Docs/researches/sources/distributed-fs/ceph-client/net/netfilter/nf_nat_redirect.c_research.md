
# sources/distributed-fs/ceph-client/net/netfilter/nf_nat_redirect.c

Purpose: Implements REDIRECT destination NAT for IPv4 and IPv6 by mapping packets to a local address on the receiving interface or loopback for locally generated packets.

Important APIs and functions: Internal `nf_nat_redirect()` builds a destination NAT range around a selected address and calls `nf_nat_setup_info()`. Exported `nf_nat_redirect_ipv4()` selects loopback for local-out or the first IPv4 address on the ingress device for prerouting. Exported `nf_nat_redirect_ipv6()` selects loopback for local-out or a usable scoped IPv6 address on the ingress device. `nf_nat_redirect_ipv6_usable()` filters tentative, mapped, and wrong-scope addresses.

Control flow: The public helpers assert valid hook numbers, choose `newdst`, return `NF_DROP` if no usable ingress address exists, then delegate to generic NAT setup with `NF_NAT_MANIP_DST` while preserving original protocol range constraints.

State and persistence: No local mutable state except the static IPv6 loopback constant. NAT state is stored in conntrack by NAT core.

Dependencies and integration: Used by redirect targets/expressions. Depends on RCU inet device access, IPv6 address device locking, address scope helpers, and NAT core.

Risks: Address selection is intentionally simple and can drop when an interface has no usable address. Risks include IPv6 tentative/optimistic handling, scope filtering, RCU/locking around interface address lists, and preserving port range flags. Test signals include local-out and prerouting redirect for IPv4/IPv6, no-address drop, tentative IPv6 address filtering, link-local/global scope matching, and port-preserving redirects.
