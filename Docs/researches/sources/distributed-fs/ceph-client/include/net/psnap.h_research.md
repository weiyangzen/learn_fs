# sources/distributed-fs/ceph-client/include/net/psnap.h

Purpose: declares SNAP protocol client registration for datalink protocol demultiplexing.

Important APIs and types: `register_snap_client()` registers a SNAP descriptor and receive callback returning a `datalink_proto`; `unregister_snap_client()` removes it. Forward declarations cover skb, packet_type, net_device, and datalink protocol objects.

Control flow: protocol modules register a SNAP OUI/descriptor and receive callback; packet receive dispatch calls the registered function with skb/device/original-device context.

State and persistence: registration tables live in the SNAP implementation, not here, and are runtime only.

Dependencies and integration points: integrates datalink/SNAP handling with packet receive paths and netdevices.

Risks and test signals: risks include unregister while packets are in flight, descriptor collisions, and skb ownership mistakes in callbacks. Test register/unregister, receive dispatch, duplicate clients, module unload, and malformed SNAP frames.
