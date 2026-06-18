# sources/distributed-fs/ceph-client/net/nfc/llcp_sock.c

Purpose: Exposes LLCP as an NFC socket protocol supporting stream/seqpacket connected sockets, datagram UI sockets, and privileged raw LLCP sockets.

Important APIs and functions: Implements socket ops for bind, raw bind, listen, accept, connect, getname, poll, release, sendmsg, recvmsg, getsockopt, and setsockopt. Shared helpers include `sock_wait_state`, `nfc_llcp_accept_unlink`, `nfc_llcp_accept_enqueue`, `nfc_llcp_accept_dequeue`, `nfc_llcp_sock_alloc`, `nfc_llcp_sock_free`, `nfc_llcp_sock_init`, and `nfc_llcp_sock_exit`.

Control flow: Bind resolves the NFC device and local LLCP object, reserves a service SAP, stores service name/protocol, and links the socket. Listen changes bound stream/seqpacket sockets to `LLCP_LISTEN`. Connect reserves a local SAP, links the socket in `connecting_sockets`, sends CONNECT, and waits for `LLCP_CONNECTED` unless nonblocking. Sendmsg routes datagrams to UI frames and connected sockets to I-frames. Recvmsg dequeues skbs and fills datagram peer SAPs when needed.

State and persistence: Per-socket state lives in `struct nfc_llcp_sock`: service name allocation, SAPs, reserved SAP, local/device refs, queues, sequence numbers, remote params, parent and accept queue. Release sends DISC for connected sockets, disconnects accepted children, unlinks from local socket lists, releases SAPs, orphans the sock, and drops references.

Dependencies and integration points: Registered with `nfc_proto_register` as `NFC_SOCKPROTO_LLCP`. Uses LLCP core SAP/list helpers, command builders, NFC device refs, socket wait queues, Linux poll, and raw socket capabilities.

Risks: Bind rejects DSAP but allows zero-length service-name allocation paths that should be checked. Connect cleanup must unwind local refs, device refs, SAP reservation, connecting-list link, and service-name allocation correctly for each failure point. Release uses `llcp_sock->ssap` rather than `reserved_ssap` when freeing, so reserved SAP semantics should be tested. Recvmsg requeues partially read skbs for stream, datagram, and raw types, which is unusual for datagrams.

Test signals: Socket API tests should cover bind/listen/accept/connect success and failure, nonblocking connect, service-name and DSAP addressing, SAP exhaustion, accepted child cleanup, raw socket permission checks, poll masks, option bounds, datagram send/recv names, partial recv behavior, and release during active link teardown.
