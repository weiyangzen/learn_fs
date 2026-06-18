# sources/distributed-fs/ceph-client/include/net/phonet/phonet.h

Purpose: declares the kernel Phonet socket core: protocol socket base layout, lookup/hash/resource APIs, send helper, address extraction helpers, protocol registration, sysctl/init hooks, and ioctl dispatch.

Important APIs and types: `struct pn_sock` embeds `struct sock` first and stores source/destination Phonet objects plus resource. `struct phonet_protocol` registers socket type, proto, and proto_ops. Helpers cast sockets, access Phonet headers/messages in skbs, populate source/destination `sockaddr_pn`, register/unregister protocols, bind/unbind resources, send skbs, and process resource ioctls.

Control flow: socket creation uses registered Phonet protocols; bind/hash/resource tables locate sockets; receive paths extract source/destination addresses from skb headers; send paths use `pn_skb_send()` to target Phonet addresses.

State and persistence: per-socket object/resource fields and namespace hash/resource bindings are runtime-only. Sysctl values may tune behavior but are not stored here.

Dependencies and integration points: depends on Linux Phonet UAPI, socket core, skbuffs, net namespaces, proc/sysctl, and ISI/PEP protocols.

Risks and test signals: risks include assuming `pn_sock` is first in protocol structs, resource binding collisions, ioctl user-copy errors, skb header offset assumptions, and broadcast delivery fanout. Test datagram/stream sockets, bind/unbind resource, port allocation, broadcasts, ioctl add/delete resource, and protocol register/unregister.
