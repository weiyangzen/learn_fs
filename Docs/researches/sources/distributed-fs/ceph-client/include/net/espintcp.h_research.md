# sources/distributed-fs/ceph-client/include/net/espintcp.h

Read `sources/distributed-fs/ceph-client/include/net/espintcp.h` completely for this pass (40 lines, 972 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/net/espintcp.h_research.md`.

Purpose: declares the ESP-in-TCP upper-layer protocol context and queueing APIs used to carry ESP/IKE traffic over TCP.

Important APIs/types/functions: initialization/API functions are `espintcp_init()`, `espintcp_push_skb()`, `espintcp_queue_out()`, and `tcp_is_ulp_esp()`. `struct espintcp_msg` tracks an skb, `sk_msg`, offset, and length for partial transmission. `struct espintcp_ctx` embeds a `strparser`, IKE and output skb queues, current partial message, saved socket callbacks (`data_ready`, `write_space`, `destruct`), work item, and `tx_running` flag. `espintcp_getctx()` retrieves the context from `inet_csk(sk)->icsk_ulp_data`.

Control flow: init registers the ULP. When a TCP socket uses ESP ULP, receive data is parsed by strparser and queued as IKE/ESP records; transmit paths queue skbs or partial sk_msgs and schedule work while preserving original socket callbacks for chaining/restoration. `tcp_is_ulp_esp()` lets callers detect sockets using this ULP.

State and persistence: per-socket `espintcp_ctx` persists while the ULP is attached. It owns receive/output queues, partial send progress, saved callbacks, and worker state. No durable state exists beyond socket lifetime.

Dependencies and integration points: depends on TCP inet connection sockets, strparser, skmsg, skbuff queues, workqueues, ESP/IPsec users, and diagnostic paths that may read `icsk_ulp_data` under RCU.

Risks: socket callback save/restore and ULP data lifetime are race-prone. Partial sk_msg progress must be resumed correctly after backpressure. Queue ordering between IKE and ESP data matters. `espintcp_getctx()` trusts the socket has the ESP ULP; callers must check. Comments note RCU is only needed for diag, so normal paths depend on socket locking/ownership.

Test signals: attach/detach ULP, IKE and ESP record receive parsing, transmit queueing under write-space backpressure, partial message resume, callback restoration on close, `tcp_is_ulp_esp()` detection, concurrent diag reads, and IPsec NAT/firewall traversal interop.
