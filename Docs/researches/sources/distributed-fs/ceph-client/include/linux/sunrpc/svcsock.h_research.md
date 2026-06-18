# sources/distributed-fs/ceph-client/include/linux/sunrpc/svcsock.h

Purpose: declares the socket-based SUNRPC server transport and helpers for receiving, sending, and creating service sockets.

Important APIs and types: `struct svc_sock` embeds `svc_xprt`, stores `socket`/`sock`, saved socket callbacks, send `bio_vec`, TCP record marker/length accounting, page fragment cache, handshake completion, max pages, and flexible page array. Inline helpers `svc_sock_reclen()` and `svc_sock_final_rec()` decode the RPC stream fragment header. APIs include `svc_recv()`, `svc_send()`, `svc_addsock()`, `svc_init_xprt_sock()`, and `svc_cleanup_xprt_sock()`. Socket creation flags include anonymous and temporary.

Control flow: socket callbacks mark transports ready, service threads receive request records/fragments into pages, process RPCs, and send replies. TCP receive state tracks record marker, received bytes, and data length across fragments.

State and persistence: socket transport state is per-connection runtime state: callbacks, fragment progress, page cache, handshake completion, and page arrays.

Dependencies and integration points: integrates with `svc.h`, `svc_xprt.h`, Berkeley sockets, INET sockets, bio vectors, and RPC record marking from `msg_prot.h`.

Risks and test signals: risks include fragment length parsing bugs, callback restoration races, send vector lifetime, handshake stalls, and page accounting errors. Test TCP fragmented RPCs, UDP service sockets, TLS handshake paths, temporary sockets, and service shutdown under traffic.
