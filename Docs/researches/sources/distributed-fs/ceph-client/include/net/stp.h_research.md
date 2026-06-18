<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/stp.h -->
# sources/distributed-fs/ceph-client/include/net/stp.h

Purpose: Provides the small kernel registration contract for Spanning Tree Protocol handlers keyed by Ethernet group address.

Important APIs/types/functions: `struct stp_proto` carries a `group_address`, receive callback `rcv(const struct stp_proto *, struct sk_buff *, struct net_device *)`, and opaque `data`. `stp_proto_register()` and `stp_proto_unregister()` install or remove protocol handlers.

Control flow: A bridge or STP implementation registers a protocol descriptor. The Ethernet receive path can match destination group address and invoke the `rcv` callback with the skb and ingress device. Unregistration removes the callback association.

State and persistence behavior: The header declares no storage; registered protocols live in networking core state. The `data` pointer is caller-owned and must outlive registration.

Dependencies/integration points: Depends on Ethernet address definitions and skb/net_device types. Integrates with bridge/STP receive handling and any module implementing STP-like link-local protocols.

Risks: Callback lifetime and module unload ordering are the main risks. Bad group address registration can steal or drop bridge control traffic.

Test signals: Module register/unregister tests, STP BPDU receive tests on bridge ports, unload with active traffic, and duplicate address registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/stp.h -->
