<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/in6.h -->
# sources/distributed-fs/ceph-client/include/linux/in6.h

Purpose: Provides kernel IPv6 socket/address helpers and well-known address declarations.

Important APIs/types/functions: `struct sockaddr_inet` overlays IPv4 and IPv6 socket addresses. Externs and initializer macros define any, loopback, link-local all-nodes/all-routers, interface-local all-nodes/all-routers, and site-local all-routers addresses.

Control flow: Networking code uses the union-style sockaddr when handling AF_INET/AF_INET6 generically and references global address constants.

State/persistence: The extern address constants are immutable global data; the header owns no mutable state.

Dependencies/integration: Includes UAPI IPv6 definitions and integrates socket, routing, multicast, and neighbor code.

Risks: Initializer constants must match IPv6 multicast scope semantics; sockaddr overlay users must respect active address family.

Test signals: Compile users, equality checks against well-known IPv6 addresses, and generic sockaddr handling for IPv4/IPv6.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/in6.h -->
