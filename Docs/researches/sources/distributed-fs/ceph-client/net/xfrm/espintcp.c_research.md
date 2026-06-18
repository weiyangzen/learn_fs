# sources/distributed-fs/ceph-client/net/xfrm/espintcp.c

Purpose: `espintcp.c` implements the TCP ULP named `espintcp`, allowing ESP packets and non-ESP/IKE traffic to be multiplexed over a framed TCP stream. It is used by ESP code through `espintcp_queue_out()` and `espintcp_push_skb()` and is initialized from core XFRM policy init when `CONFIG_XFRM_ESPINTCP` is enabled.

Important APIs and types: The file uses `struct espintcp_ctx` and `struct espintcp_msg` from `include/net/espintcp.h`, `strparser` for two-byte length-framed input, saved TCP protocol/proto_ops clones, and an `ike_queue` for non-ESP messages. Exported APIs are `espintcp_queue_out()`, `espintcp_push_skb()`, and `tcp_is_ulp_esp()`. `espintcp_init()` registers `tcp_ulp_ops`.

Control flow: Receive path starts in `espintcp_data_ready()`, which drives `strp_data_ready()`. `espintcp_parse()` reads the 16-bit length, rejects lengths below two, and returns the full framed size. `espintcp_rcv()` removes the length field, drops one-byte `0xff` keepalives, distinguishes non-ESP marker zero from ESP SPI, queues non-ESP data for userspace `recvmsg()`, or passes ESP into `xfrm4_rcv_encap()`/`xfrm6_rcv_encap()` with `TCP_ENCAP_ESPINTCP`. Send path stores either skb output from ESP or userspace sk_msg data in `ctx->partial`, pushes with `skb_send_sock_locked()` or `tcp_sendmsg_locked()`, and preserves partial state across `-EAGAIN`.

State and persistence: Per-socket ULP state stores parser state, saved callbacks, work item, IKE/out queues, and a partial transmit. It is attached through `icsk_ulp_data`, freed in the socket destructor, and purged on close.

Dependencies and integration: It depends on TCP internals, strparser, XFRM IPv4/IPv6 receive encapsulation, ESP output, socket memory accounting, and `net_hotdata.max_backlog`. It rejects sockmap use by checking `sk_user_data`.

Risks: Framing and partial-send accounting are security-sensitive. Bugs can misclassify IKE vs ESP, leak skb/sk_msg pages, deadlock callback replacement, or lose data under TCP backpressure. IPv6 proto cloning is protected by `tcpv6_prot_mutex`; races here affect all sockets using the ULP.

Test signals: Exercise TCP ULP attach, IKE marker delivery through `recvmsg()`, ESP delivery to XFRM, keepalive drop, large send rejection above `MAX_ESPINTCP_MSG`, nonblocking `EAGAIN`, socket close with pending partials, and IPv4/IPv6 ESP-in-TCP interop.
