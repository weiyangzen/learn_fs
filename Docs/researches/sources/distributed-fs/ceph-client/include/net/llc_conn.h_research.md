# Research: sources/distributed-fs/ceph-client/include/net/llc_conn.h

Purpose: `llc_conn.h` declares the AF_LLC connection socket state (`struct llc_sock`) and connection-level operations for allocation, teardown, state-machine processing, PDU send/return/resend, ACK removal, established-socket lookup, SAP socket membership, and data-acceptance checks.

Important APIs/types/functions: `struct llc_timer` wraps a kernel timer and expiration value. `struct llc_sock` embeds `struct sock` first, then bound address, state, SAP pointer, local/remote LLC addresses, net device and tracker, sequence counters, retry/window parameters, four LLC2 timers, P/F/S/data/remote-busy/cause flags, unacknowledged PDU queue, link metadata, temporary state, cmsg flags, and hash node. Helpers include `llc_sk()`, `llc_set_backlog_type()`, and `llc_backlog_type()`. Functions include `llc_sk_alloc()`, `llc_sk_stop_all_timers()`, `llc_sk_free()`, `llc_sk_reset()`, `llc_conn_state_process()`, `llc_conn_send_pdu()`, `llc_conn_rtn_pdu()`, I-PDU resend helpers, `llc_conn_remove_acked_pdus()`, `llc_lookup_established()`, SAP socket add/remove, and `llc_build_offset_table()`.

Control flow: sockets are allocated as `llc_sock`, attached to a SAP and optionally a device, then process backlog packets or generated events through `llc_conn_state_process()`. Connection actions send PDUs, append unacknowledged I PDUs, arm timers, and remove acknowledged frames. Backlog type markers differentiate packet and event entries in `skb->cb`. Established lookup resolves incoming connection traffic by SAP, local/remote address pair, and network namespace.

State and persistence behavior: connection state persists for the lifetime of the socket. Timers continue across event processing until stopped during state transitions or socket teardown. Queued unacknowledged PDUs hold retransmission state. Device lifetime is tracked by `netdevice_tracker`; SAP references connect sockets to SAP lifetime.

Dependencies and integration points: it depends on timer APIs, AF_LLC UAPI address definitions, `net/sock.h`, `llc_if.h`, netdevice tracking, sk_buff queues, and LLC SAP hashing. It is consumed by LLC actions, events, socket operations, and packet receive dispatch.

Risks: `struct sock` must remain first for casting. Timer teardown must be synchronized correctly to avoid callbacks after free. `skb->cb` backlog marking shares space with event metadata. Sequence/window variables are small modulo fields and prone to wrap bugs. Device and SAP references must be released in all teardown paths.

Test signals: verify socket allocation/free under refcount debugging, all timer callbacks during close/reset, established lookup with namespace/device/address variants, backlog packet versus event handling, ACK removal across sequence wrap, device unregister while sockets exist, and retransmission queue cleanup.
