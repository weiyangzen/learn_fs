<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/in.h -->
# sources/distributed-fs/ceph-client/include/linux/in.h

Purpose: Adds kernel IPv4 helpers around the UAPI IPv4 definitions.

Important APIs/types/functions: `proto_ports_offset()` maps IPPROTO TCP/UDP/DCCP/SCTP/UDPLITE to source/destination port offsets or `-EINVAL`. Address classifiers cover loopback, multicast, local multicast, limited broadcast, all-snoopers, zeronet, RFC1918 private ranges, link-local, 6to4 anycast, and test networks.

Control flow: Networking code calls static inline classifiers on hot paths without function-call overhead.

State/persistence: Stateless bitmask checks over network-order IPv4 addresses.

Dependencies/integration: Includes `uapi/linux/in.h` and errno definitions; used by routing, filtering, socket, and packet parsing code.

Risks: Classifiers assume `__be32` network byte order and exact masks; misuse with host-order values misclassifies addresses.

Test signals: Table-driven address classification, unsupported protocol offset errors, and endian-sensitive compile/runtime tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/in.h -->
