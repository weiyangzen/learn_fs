# sources/distributed-fs/ceph-client/net/xdp/xsk_diag.c

Purpose: implements SOCK_DIAG dumping for PF_XDP sockets so monitoring tools can inspect AF_XDP socket, ring, UMEM, memory, and statistics state.

Important APIs/functions: `xsk_diag_init()` registers the AF_XDP diag handler; `xsk_diag_exit()` unregisters it. `xsk_diag_handler_dump()`, `xsk_diag_dump()`, and `xsk_diag_fill()` serve dump requests, while helpers put info, ring config, UMEM, and stats attributes.

Control flow: a netlink dump request must be `NLM_F_DUMP` and at least `struct xdp_diag_req`. The dump walks `net->xdp.list` under lock, resumes from callback state, and fills each socket if it fits. Per socket, the code locks the xsk mutex, skips unbound sockets, conditionally emits requested attributes, ends the message, or cancels on size failure.

State and persistence: no persistent state is owned. Output snapshots socket state, queue entry counts, UMEM id/geometry/refcount/zero-copy flag, pool queue/device, sock memory info, and descriptor/stat counters.

Dependencies and integration: depends on PF_XDP per-net socket list from `xsk.c`, queue counter helpers, Linux sock_diag/netlink APIs, and module aliasing for AF_XDP diagnostics.

Risks and test signals: diagnostic dumps must avoid racing socket teardown and must handle absent queues/pools. Tests should cover all `xdiag_show` masks, small skb/EMSGSIZE resume, unbound socket skip, namespace filtering, module load/unload, and `ss` output for copy/zero-copy/shared UMEM sockets.
