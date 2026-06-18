# sources/distributed-fs/ceph-client/include/net/netns/packet.h

Purpose: Defines per-network-namespace AF_PACKET state.

Important APIs/types/functions: `struct netns_packet` stores the packet socket list and associated synchronization state.

Control flow: AF_PACKET socket create/destroy updates the namespace list; packet delivery enumerates matching packet sockets.

State and persistence: Runtime per-net socket list, protected by packet socket locking/RCU in implementation code.

Dependencies/integration: Depends on AF_PACKET, netdevice receive path, socket lifecycle, and namespace teardown.

Risks/test signals: Test packet socket creation/destruction under traffic, namespace isolation, device unregister cleanup, fanout interactions, and teardown with open sockets.
