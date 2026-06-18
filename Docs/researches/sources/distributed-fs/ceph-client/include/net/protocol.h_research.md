# sources/distributed-fs/ceph-client/include/net/protocol.h

Purpose: declares IPv4/IPv6 protocol dispatch registration structures, offload registration, and inet socket protocol switch descriptors.

Important APIs and types: `MAX_INET_PROTOS` is 256. `struct net_protocol` supplies IPv4 handler/error handler and policy flags. `struct inet6_protocol` does the same for IPv6 with extension flags. `struct net_offload` stores GSO/offload callbacks and flags. `struct inet_protosw` registers socket type/protocol to proto/proto_ops with reuse/permanent/ICSK flags. Global RCU arrays hold protocol and offload entries. Functions add/delete IPv4/IPv6 protocols and offloads and register/unregister protosw entries.

Control flow: IP receive dispatch indexes protocol arrays by 8-bit protocol, invokes handlers/error handlers, and socket creation scans registered protosw entries for type/protocol matches.

State and persistence: runtime global RCU registration tables/lists only; modules add/remove entries.

Dependencies and integration points: depends on skbuff, netdevice, IPv6 optional headers, offload callbacks, proto/proto_ops, and module registration.

Risks and test signals: risks include duplicate registrations, deleting permanent protocols, RCU lifetime errors, policy flag misuse, and IPv6 module config drift. Test add/delete protocol modules, ICMP/ICMPv6 error dispatch, GSO extension header offload, socket creation by protocol/type, and concurrent receive during unregister.
