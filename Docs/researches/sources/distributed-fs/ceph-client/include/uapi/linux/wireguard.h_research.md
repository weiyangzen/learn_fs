<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wireguard.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/wireguard.h

Purpose: defines the generic netlink UAPI for configuring and dumping WireGuard devices, peers, and allowed IPs.

Important APIs and types: `WG_GENL_NAME`, version, and `WG_KEY_LEN` identify the family and key size. Device flags include peer replacement. Peer flags remove, replace allowed IPs, or update only. Allowed-IP flags remove entries. Attribute enums cover device ifindex/name, private/public keys, listen port, fwmark, peer nesting, peer endpoint, keepalive, handshake time, byte counters, allowed IP nesting, and protocol version. Commands are get and set device.

Control flow, state, and persistence: userspace sends netlink set/get messages with nested peers and allowed IPs; kernel updates device configuration and counters. Configuration persists in kernel netdevice state until changed or device removal.

Dependencies and integration points: auto-generated from YNL spec; integrates generic netlink, WireGuard netdevice, routing, and key management tools.

Risks and test signals: risks include nested attribute validation, accidental private-key exposure in dumps, replacement semantics, and counter width handling. Test get/set, peer replace/remove/update-only, allowed IP replace/remove, endpoint changes, and netns/device lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/wireguard.h -->
