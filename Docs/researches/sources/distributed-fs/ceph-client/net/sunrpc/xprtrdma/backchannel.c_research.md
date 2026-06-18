<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/backchannel.c -->
# sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/backchannel.c

Purpose: Implements reverse-direction RPC callback support over RPC/RDMA for client transports, including backchannel setup, maximum payload/slot reporting, reply marshalling/sending, preallocated request recycling, and incoming callback Call delivery to the upper-layer callback service.

Important APIs/types/functions: `xprt_rdma_bc_setup()` records available backchannel server credits. `xprt_rdma_bc_maxpayload()` and `xprt_rdma_bc_max_slots()` report inline payload and slot limits. `xprt_rdma_bc_send_reply()` marshals and sends a backchannel reply through `rpcrdma_bc_marshal_reply()` and `frwr_send()`. `xprt_rdma_bc_destroy()` releases preallocated backchannel requests. `xprt_rdma_bc_free_rqst()` returns a request to the pool after ULP processing. `rpcrdma_bc_receive_call()` wraps an incoming RDMA receive buffer as an RPC request and enqueues it with `xprt_enqueue_bc_request()`.

Control flow: Setup currently sets `rb_bc_srv_max_requests` to half of `RPCRDMA_BACKWARD_WRS`. Reply sending checks connection state, obtains congestion credit, encodes a minimal RPC/RDMA header into the request header buffer, prepares send SGEs for inline data, and posts via FRWR; failures close the RDMA xprt and return `-ENOTCONN` unless marshalling failed permanently. Incoming calls borrow a request from `bc_pa_list` or allocate/setup a new one up to `RPCRDMA_BACKWARD_WRS`, point its receive `xdr_buf` at the RDMA receive buffer, attach the `rpcrdma_rep` to the request to keep the buffer alive, and enqueue the callback. Overflow logs a warning and forces disconnect.

State and persistence behavior: State lives in `rpc_xprt` backchannel fields (`bc_pa_list`, `bc_pa_lock`, `bc_alloc_count`) and in `rpcrdma_req`/`rpcrdma_rep` ownership links. Receive buffers are held by `req->rl_reply` until `xprt_rdma_bc_free_rqst()` returns the rep and request to their pools. No durable persistence.

Dependencies and integration points: Integrates SUNRPC backchannel APIs, RPC/RDMA request/reply buffers, XDR stream encoding, FRWR send, congestion helpers from `xprt.c`, and callback queueing in `bc_xprt`. It is conditionally built by the xprtrdma Makefile.

Risks: Backchannel receive buffer lifetime depends on the request holding `rep`; premature repost/free would corrupt callback decoding. Allocation is capped to prevent remote resource exhaustion, but overflow disconnects the whole transport. Reply marshalling supports inline backchannel replies only and depends on negotiated inline sizes. Congestion credit failures return `-EBADSLT`, which upper layers must treat correctly. The credit model explicitly ignores remote backchannel credits, relying on ULP replay/session behavior.

Test signals: Exercise setup credit reporting, max payload with different inline send/recv sizes, reply send success and disconnected/error paths, congestion failure, callback Call enqueue and XID propagation, request pool reuse, dynamic allocation cap/overflow disconnect, receive buffer hold/repost after free, and module builds with backchannel enabled/disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/sunrpc/xprtrdma/backchannel.c -->
