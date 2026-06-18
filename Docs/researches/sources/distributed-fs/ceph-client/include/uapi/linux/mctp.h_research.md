# sources/distributed-fs/ceph-client/include/uapi/linux/mctp.h

Purpose: defines the Management Component Transport Protocol socket ABI, address types, tag flags, socket options, and tag allocation ioctls.

Important APIs and types: `mctp_eid_t`, `struct mctp_addr`, `struct sockaddr_mctp`, `struct sockaddr_mctp_ext`, and `struct mctp_fq_addr` encode endpoint IDs, network IDs, message type, tags, ifindex, and link-layer addresses. Constants include `MCTP_NET_ANY`, `MCTP_ADDR_NULL`, `MCTP_ADDR_ANY`, `MCTP_TAG_MASK`, `MCTP_TAG_OWNER`, `MCTP_TAG_PREALLOC`, and `MCTP_OPT_ADDR_EXT`. Ioctls include deprecated tag controls and network-aware `SIOCMCTPALLOCTAG2`/`SIOCMCTPDROPTAG2` using `struct mctp_ioc_tag_ctl2`.

Control flow: userspace creates AF_MCTP sockets, binds/connects/sends with MCTP sockaddr data, may request extended addressing, allocates preallocated tags for request/response flows, then drops tags when done.

State and persistence: runtime state includes socket bindings, route/network configuration, allocated tags, and link-layer neighbor state. No persistent state is defined by this header.

Dependencies and integration points: depends on `linux/types.h`, `linux/socket.h`, and `linux/netdevice.h`; integrates MCTP core networking, netdevice addressing, platform management protocols, and userspace management daemons.

Risks and test signals: risks include deprecated tag ioctl use on multi-network systems, tag owner/prealloc bit handling, local EID restrictions, extended sockaddr size, and ifindex/hardware-address validation. Test bind/send/recv, tag alloc/drop v1/v2, multi-network routing, extended address option, invalid tags, and concurrent tag allocation.
