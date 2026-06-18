# sources/distributed-fs/openafs/src/external/heimdal/roken/inet_ntop.c

Purpose: fallback implementation of `inet_ntop()` for IPv4 and optional IPv6.

Important APIs/types/functions: `inet_ntop_v4()`, `inet_ntop_v6()` under `HAVE_IPV6`, and public `inet_ntop(int af, const void *src, char *dst, size_t size)`.

Control flow: IPv4 converts the network-order address to host order and writes dotted decimal. IPv6 prints eight 16-bit hex groups and compresses a run of zero groups using `::` with a simple first-run strategy. Public dispatch sets `EAFNOSUPPORT` for unsupported families.

State and persistence behavior: writes into caller-provided buffer only.

Dependencies and integration points: used by fallback `getnameinfo()` and address formatting callers on platforms without native support.

Risks: IPv6 zero-compression implementation is simpler than modern canonical formatting and may not choose the longest run in all cases. Buffer size checks require `INET_ADDRSTRLEN` or `INET6_ADDRSTRLEN`. No null pointer guards.

Test signals: IPv4 formatting, insufficient buffer ENOSPC, IPv6 normal and compressed addresses, all-zero IPv6, and unsupported family.
