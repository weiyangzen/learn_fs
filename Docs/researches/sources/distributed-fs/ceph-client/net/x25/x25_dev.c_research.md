# sources/distributed-fs/ceph-client/net/x25/x25_dev.c

Purpose: bridges X.25 Packet Layer Protocol frames to and from X.25 netdevices and LAPB-style interface messages.

Important APIs/functions: `x25_lapb_receive_frame()` is the packet-type receive hook. Helpers `x25_receive_data()`, `x25_establish_link()`, and `x25_send_frame()` dispatch PLP frames, request lower-layer connection, and transmit frames with the one-byte X.25 interface prefix.

Control flow: receive copies the incoming skb, rejects non-init_net devices, locates an `x25_neigh`, strips interface type, and routes `DATA`, `CONNECT`, and `DISCONNECT` indications. PLP data with LCI 0 goes to link control; known LCI frames go to the socket state machine or backlog; call requests go to `x25_rx_call_request()`; otherwise forwarding is attempted and clear confirmations tear down forwarding entries.

State and persistence: this file owns no durable state; it mutates skb ownership and consumes or forwards frames. Neighbour state is updated through `x25_link_established()` and `x25_link_terminated()`.

Dependencies and integration: depends on packet type registration in `af_x25.c`, neighbour lookup in `x25_link.c`, socket lookup/state processing, forwarding, and netdevice transmit via `dev_queue_xmit()`.

Risks and test signals: skb ownership is subtle because successful socket processing keeps the skb while failures must free it. Tests should cover unknown devices, short frames, link connect/disconnect indications, LCI 0 restart/diagnostic frames, incoming call requests, forwarding paths, and malformed frame drops without leaks.
