# sources/distributed-fs/ceph-client/net/appletalk/ddp.c

Purpose: implements the AppleTalk Datagram Delivery Protocol socket family, interface/routing ioctls, packet receive/routing/send paths, and module lifecycle for the Linux AppleTalk stack.

Important APIs, types, and functions: global state includes `atalk_sockets`, `atalk_routes`, `atalk_interfaces`, and `atrtr_default` with rwlocks. Exports are `atrtr_get_dev` and `atalk_find_dev_addr`. Important internals include `atalk_create`, `atalk_bind`, `atalk_connect`, `atalk_sendmsg`, `atalk_recvmsg`, `atalk_rcv`, `ltalk_rcv`, `atif_ioctl`, `atrtr_create`, `atrtr_delete`, `atalk_route_packet`, and `atalk_init`/`atalk_exit`.

Control flow: module init registers the DDP proto and PF_APPLETALK family, registers SNAP DDP, LocalTalk, and PPP packet handlers, installs a device notifier, initializes AARP, procfs, and sysctl. Interface ioctls add AppleTalk addresses, probe via AARP, create direct routes, and join multicast. Sendmsg autobinds if needed, looks up routes, builds DDP headers/checksums, handles broadcast loopback, and delegates link-layer delivery to `aarp_send_ddp`. Receive validates length and checksum, finds a local interface/socket, queues to the socket, or routes the packet onward with hop-count enforcement.

State and persistence: all sockets, interfaces, routes, and default router are runtime global init-net state. Device references are held for interfaces/routes. Socket lifecycle removes from global hlist and defers destruction until allocations drain.

Dependencies and integration points: depends on LLC/SNAP datalink, AARP, netdevice notifier, socket core, rtnl for interface ioctls, proc/sysctl optional helpers, and packet handlers for LocalTalk/PPP encapsulations.

Risks: namespace support is intentionally absent for non-init_net sockets and packets. Routing/interface state uses linked lists and global locks, so scaling is limited. Route creation must maintain device refs correctly. Legacy ioctls and compat conversions are broad attack surface. Packet routing mutates shared skb data and has comments noting limitations around `skb->cb`.

Test signals: PF_APPLETALK socket creation/bind/connect/send/recv, raw socket permission checks, interface add/delete with AARP probe success/failure, route add/delete, LocalTalk short-header expansion, checksum failures, broadcast loopback, packet forwarding hop limit, compat ioctls, device-down cleanup, and full init failure unwind.
