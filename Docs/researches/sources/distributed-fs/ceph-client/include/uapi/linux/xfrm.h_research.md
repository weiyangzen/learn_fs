<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xfrm.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/xfrm.h

Purpose: defines the IPsec/XFRM netlink ABI for security associations, policies, algorithms, lifetimes, replay state, offload, migration, defaults, multicast groups, and IPTFS attributes.

Important APIs and types: address, ID, selector, lifetime, replay, algorithm, stats, SA, policy, acquire/expire, migration, mapping, offload, and default-policy structs form the fixed netlink payloads. Message types cover new/delete/get/update/flush SA and policy, allocate SPI, acquire/expire, AE events, report, migrate, SAD/SPD info, mapping, and default policy. Attributes include algorithms, templates, security context, replay ESN, marks, offload dev, IF ID, SA direction, NAT keepalive, per-CPU SA, and IPTFS options.

Control flow, state, and persistence: key managers configure SAs and policies over netlink; kernel XFRM applies them to packet paths and emits acquire/expire/events. State persists in XFRM SAD/SPD tables until expired, flushed, or deleted.

Dependencies and integration points: integrates netlink, IPsec transforms, LSM security contexts, crypto algorithms, route lookup, hardware offload, NAT traversal, and IKE daemons.

Risks and test signals: high-risk areas are fixed struct size ABI, flexible-array bounds for keys/replay/security contexts, endian address/SPI fields, policy direction, replay ESN, offload flags, and compatibility aliases. Test SA/policy CRUD, IPv4/IPv6, AE events, migration, offload, marks/if_id, replay windows, IPTFS attrs, and strongSwan/libreswan interop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/xfrm.h -->
