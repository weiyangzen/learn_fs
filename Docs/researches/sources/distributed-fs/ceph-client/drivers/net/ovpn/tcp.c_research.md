# sources/distributed-fs/ceph-client/drivers/net/ovpn/tcp.c

Purpose: Implements OpenVPN-over-TCP socket integration, including stream framing, userspace control packet delivery, kernel data packet receive, TCP send buffering, callback replacement, and transport-error peer deletion.

Important APIs, types, and functions: `ovpn_tcp_init()` builds cloned IPv4/IPv6 proto/proto_ops tables. `ovpn_tcp_socket_attach()`, `ovpn_tcp_socket_detach()`, and `ovpn_tcp_socket_wait_finish()` own socket callback lifetime. RX framing uses `ovpn_tcp_parse()` and `ovpn_tcp_rcv()` with `strparser`. Userspace I/O is `ovpn_tcp_recvmsg()` and `ovpn_tcp_sendmsg()`. Kernel TX uses `ovpn_tcp_send_skb()`, `ovpn_tcp_tx_work()`, and `ovpn_tcp_release()`. Close/poll/write callbacks are `ovpn_tcp_close()`, `ovpn_tcp_poll()`, `ovpn_tcp_data_ready()`, and `ovpn_tcp_write_space()`.

Control flow: Attach requires an established, unowned TCP socket, installs `sk_user_data`, initializes strparser, saves original callbacks/proto/ops, then replaces them with ovpn variants. Incoming stream data is parsed by a 16-bit length prefix. `DATA_V2` frames are handed to `ovpn_recv()` with a peer reference; other non-`DATA_V1` frames are re-prefixed and queued for userspace `recvmsg()`. Outgoing packets are prefixed with length and either sent immediately under socket lock, queued while userspace owns the socket, or retried by write-space/TX work.

State and persistence behavior: TCP peer state includes strparser, userspace queue, deferred out queue, current partially sent skb and offset/length, callback backups, and a deferred-delete work item. This state lasts for the peer/socket lifetime and is purged on detach.

Dependencies and integration points: It depends on TCP internals, `strparser`, cloned proto tables, socket callbacks, `ovpn_recv()`, `ovpn_peer_del()`, and netdev dynamic stats. It is selected by `socket.c` for `IPPROTO_TCP`.

Risks and edge cases: TCP is a stream, so malformed length fields or too-small frames require peer deletion. Partial sends must not duplicate or lose bytes. Callback replacement must be restored even if close races detach. `release_cb` and nested socket locks need the custom lockdep subclass. Userspace `sendmsg()` supports only `MSG_DONTWAIT` and `MSG_NOSIGNAL`. Transport errors intentionally kill the peer because the stream cannot be resynchronized.

Test signals: Test established-state requirement, length framing across fragmented TCP receives, control packet forwarding to userspace, DATA_V1 rejection, partial send and `EAGAIN` retry, out_queue backlog limit, close/disconnect behavior, poll over user_queue, IPv6 build path, callback restoration on detach, and race tests for close/write_space/release_cb/delete.
