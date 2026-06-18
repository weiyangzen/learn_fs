# sources/distributed-fs/ceph-client/net/phonet/datagram.c

## Purpose
`datagram.c` implements the ISI datagram transport for PF_PHONET `SOCK_DGRAM` sockets. It provides send/receive/ioctl/close behavior and registers the `PN_PROTO_PHONET` protocol with the Phonet core.

## Important APIs, types, and functions
The protocol object is `pn_proto`, with callbacks `pn_sock_close()`, `pn_ioctl()`, `pn_init()`, `pn_sendmsg()`, `pn_recvmsg()`, `pn_backlog_rcv()`, `pn_sock_hash()`, `pn_sock_unhash()`, and `pn_sock_get_port()`. `pn_dgram_proto` binds `pn_proto` to `phonet_dgram_ops` and `SOCK_DGRAM`. Module-facing registration is through `isi_register()` and `isi_unregister()`.

## Control flow and state
`pn_sendmsg()` validates message flags and `sockaddr_pn`, allocates an skb with `MAX_PHONET_HEADER` headroom, copies the user payload, and delegates header/device routing to `pn_skb_send()`. `pn_recvmsg()` receives a datagram with `skb_recv_datagram()`, extracts the source Phonet sockaddr, copies data with truncation support, fills `msg_name`, and frees the skb. `pn_backlog_rcv()` queues received skbs to the socket receive queue or drops them on failure.

`pn_ioctl()` supports `SIOCINQ` and resource bind/unbind ioctls (`SIOCPNADDRESOURCE`, `SIOCPNDELRESOURCE`), delegating resource table updates to `socket.c`.

## State and persistence behavior
The file itself stores no global runtime state. Per-socket state lives in `struct pn_sock` and socket queues. `pn_destruct()` purges the receive queue when the final socket reference is gone.

## Dependencies and integration points
It depends on the Phonet core send path (`pn_skb_send()`), common socket hash/port/resource helpers in `socket.c`, generic datagram receive helpers, and PF_PHONET protocol registration in `af_phonet.c`.

## Risks and edge cases
The main risks are user payload copy errors, flag compatibility, datagram truncation semantics, resource ioctl authorization through delegated helpers, and ensuring skb ownership/drop paths are correct when `pn_skb_send()` fails. Since send requires an explicit destination, callers get `-EDESTADDRREQ` when `msg_name` is absent.

## Test signals
Exercise datagram send/receive between local Phonet sockets, invalid flags, short or wrong-family sockaddr, truncation and `MSG_TRUNC`, `SIOCINQ`, resource add/delete, receive queue pressure, and module registration/unregistration of `PN_PROTO_PHONET`.
