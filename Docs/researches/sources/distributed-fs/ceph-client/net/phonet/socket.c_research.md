# sources/distributed-fs/ceph-client/net/phonet/socket.c

## Purpose
`socket.c` provides common PF_PHONET socket operations, global socket lookup tables, port allocation, resource binding, procfs sequence output, and shared datagram/stream `proto_ops`. It is the address/port/resource registry used by the datagram and PEP protocols.

## Important APIs, types, and functions
Core ops include `pn_socket_release()`, `pn_socket_bind()`, `pn_socket_autobind()`, `pn_socket_connect()`, `pn_socket_accept()`, `pn_socket_getname()`, `pn_socket_poll()`, `pn_socket_ioctl()`, `pn_socket_listen()`, and `pn_socket_sendmsg()`. Exported protocol ops are `phonet_dgram_ops` and `phonet_stream_ops`.

Socket hash functions are `pn_sock_init()`, `pn_hash_list()`, `pn_find_sock_by_sa()`, `pn_deliver_sock_broadcast()`, `pn_sock_hash()`, `pn_sock_unhash()`, and `pn_sock_get_port()`. Resource functions are `pn_find_sock_by_res()`, `pn_sock_bind_res()`, `pn_sock_unbind_res()`, and `pn_sock_unbind_all_res()`. Procfs seq operations are `pn_sock_seq_ops` and `pn_res_seq_ops`.

## Control flow and state
The global `pnsocks` hash table has 16 buckets protected by `pnsocks.lock` for mutation and RCU for lookup. Binding validates AF_PHONET address, checks local address availability, locks the socket, prevents rebinding, allocates a port under `port_mutex`, writes source object/resource, and hashes the socket. Autobind binds to an anonymous address/port; importantly, it only treats `-EINVAL` as "already bound" when the socket actually has a nonzero port, preventing false success after state-related bind failures.

Connect autobinds, validates destination sockaddr, checks socket state, stores destination object/resource, calls the protocol-specific connect callback, waits while `TCP_SYN_SENT` unless nonblocking or interrupted, and maps final protocol state to `SS_CONNECTED` or an errno. Listen autobinds and moves the socket to `TCP_LISTEN`. Accept delegates to the protocol accept callback and grafts the returned sock to the new socket.

`pn_socket_poll()` combines receive queue, PEP control request queue, close/hup state, send buffer, and PEP TX credits. `pn_socket_ioctl()` handles `SIOCPNGETOBJECT` by choosing a device and local source address, then delegates other commands to `sk_ioctl()`.

Resource binding is limited to init_net and `CAP_SYS_ADMIN`. The 256-entry `pnres` RCU table maps Phonet resource ids to sockets with held references. Unhash removes normal hash membership, unbinds all resources, and waits for RCU before final release.

## State and persistence behavior
Socket hash and resource tables are global in-memory state. Port allocation uses a static rotating `port_cur` and sysctl-provided local port range. Procfs exposes live socket and resource snapshots. No state persists across module unload.

## Dependencies and integration points
This file integrates with Phonet address lookup/device selection in `pn_dev.c`, PEP fields for stream poll behavior, datagram/PEP protocol callbacks, sysctl port range from `sysctl.c`, procfs registration from `pn_dev.c`, and generic socket helpers.

## Risks and edge cases
Risks include global hash namespace behavior, port collision races, RCU/refcount lifetime for resource sockets, bind/autobind state handling, and assumptions that stream sockets are PEP sockets in `pn_socket_poll()`. The fixed autobind behavior is a key test point because treating all `-EINVAL` binds as success can leave sockets without ports and later crash.

## Test signals
Test bind/autobind, port range exhaustion, explicit port conflict, local address validation, connect blocking/nonblocking/interrupted paths, listen/accept, broadcast delivery, resource bind/unbind in init_net and non-init namespaces, procfs socket/resource output, `SIOCPNGETOBJECT`, and the autobind `-EINVAL` regression case.
