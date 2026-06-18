# sources/distributed-fs/ceph-client/net/9p/trans_rdma.c

Purpose: provides a 9P transport over reliable connected RDMA. It maps each request and expected reply into RDMA send/receive work requests and integrates with RDMA CM for address resolution, route resolution, and connection management.

Important APIs, types, and functions: `struct p9_trans_rdma` tracks RDMA CM state, CM ID, PD, QP, CQ, queue depths, semaphores, `excess_rc`, and connection completion. `struct p9_rdma_context` wraps an `ib_cqe`, DMA address, and either a request or receive fcall. Core functions are `p9_cm_event_handler`, `post_recv`, `rdma_request`, `recv_done`, `send_done`, `rdma_create_trans`, `rdma_close`, `rdma_cancelled`, and `p9_rdma_bind_privport`.

Control flow: creation allocates transport state, creates an RDMA CM ID, optionally binds a privileged local port, resolves IPv4 address and route, allocates CQ and PD, creates the QP, connects, then marks the client connected. Each request usually posts a receive buffer first, clears `req->rc.sdata` so ownership belongs to the receive context, maps and posts the send buffer, and marks the request sent before `ib_post_send` to avoid a fast-reply race. Completion callbacks unmap DMA, release queue semaphores, parse tags, attach response buffers, and call `p9_client_cb`.

State and persistence: state is in RDMA objects and per-client memory. `sq_sem` and `rq_sem` bound outstanding work. `excess_rc` records receive buffers that remain posted after a flush or a send-side failure, so later requests can skip posting another receive. No persistent on-disk state exists.

Dependencies and integration points: depends on `rdma_cm`, `ib_verbs`, `net/9p`, semaphores, completions, and socket address parsing. It registers `p9_rdma_trans`, advertises `pooled_rbuffers = true`, and does not support vmalloc request buffers because DMA mapping needs suitable memory.

Risks: receive-before-send is necessary but creates hard-to-test `excess_rc` paths. Error handling changes RDMA and client state to flushing/disconnected but does not cancel every outstanding request locally. CM event handler uses strict `BUG_ON` assumptions for event order. DMA mapping, buffer ownership, and duplicate reply detection are critical.

Test signals: RDMA mount/connect success, address/route/connection failure paths, queue-depth exhaustion, interruptible waits, flushes without replies, send errors after receive posting, duplicate or malformed replies, device removal events, and module unload should all be tested under RDMA-capable CI or emulation.
