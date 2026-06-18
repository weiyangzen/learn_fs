# sources/distributed-fs/ceph-client/include/rdma/ib_addr.h

Purpose: defines RDMA address-resolution data structures and helpers for translating IP/network-device addresses into RDMA link-layer, GID, P_Key, VLAN, multicast, and MTU information.

Important APIs and types: `struct rdma_dev_addr` stores source/destination/broadcast hardware addresses, device type, bound ifindex, transport, net namespace, selected SGID attribute, RDMA network type, and hop limit. Core APIs are `rdma_translate_ip()`, asynchronous `rdma_resolve_ip()`, `rdma_addr_cancel()`, and sockaddr size helpers. Inline helpers get/set IB P_Key and MGID from encoded broadcast data, compute GID offsets for InfiniBand vs Ethernet-like devices, map VLAN devices, convert IP to/from GIDs, get/set SGID/DGID, derive IBoE MTU, detect link-local and multicast addresses, derive link-local or multicast MACs, extract VLAN ID from a GID, and return real VLAN devices.

Control flow: callers initialize `rdma_dev_addr.net`, optionally provide a source address, and request synchronous translation or asynchronous resolution. Completion invokes the callback with resolved source address and device address or error; cancellation targets a pending resolution. Later connection setup uses the resolved GIDs, MACs, VLAN, P_Key, hoplimit, MTU, and selected SGID attribute.

State and persistence: `rdma_dev_addr` is caller-owned transient state that must remain valid until the resolution callback completes. `sgid_attr` is a referenced RDMA cache object whose lifetime rules come from the cache layer. No persistent state is stored here.

Dependencies and integration points: depends on Linux netdevice/VLAN/IP/IPv6/net namespace headers, `ib_verbs.h`, packet header sizes from `ib_pack.h`, GID attributes, and ARP hardware types. It connects RDMA CM/SA/QP setup to kernel networking address resolution for IB, RoCE, and iWARP transports.

Risks and test signals: risks include callback after caller storage is freed, net namespace or bound ifindex mismatch, incorrect GID offset for ARPHRD_INFINIBAND, VLAN ID sentinel confusion, MTU underflow after encapsulation overhead, multicast MAC derivation errors, and SGID attribute lifetime leaks. Test IPv4/IPv6/v4-mapped conversion, RoCE VLAN and non-VLAN devices, link-local address MAC generation, multicast joins, timeout/cancel races, netns isolation, and smallest-MTU edge cases.
