## sources/distributed-fs/ceph-client/fs/smb/smbdirect/listen.c

Purpose: Implements SMBDirect listening sockets and conversion of RDMA connect requests into accepting sockets queued for the upper layer.

Important APIs and functions: `smbdirect_socket_listen()` is exported and starts RDMA listening on a bound socket. `smbdirect_listen_rdma_event_handler()` handles listener CM events. `smbdirect_listen_connect_request()` validates a new request, enforces backlog, creates an accepting socket, copies listener settings/logging, enqueues it as pending, and starts passive accept handling.

Control flow: A created socket enters `LISTENING`, installs the listen RDMA event handler, expects `RDMA_CM_EVENT_CONNECT_REQUEST`, and calls `rdma_listen()`. For connect requests, the handler detaches the new CM id from the listener context, installs a placeholder handler until accept code takes ownership, validates event/status, and calls `smbdirect_listen_connect_request()`. That function checks FRWR support and transport restrictions, counts pending/ready queues under the listener lock, creates a child socket, copies parameters and kernel settings, adds it to pending, and calls `smbdirect_accept_connect_request()`.

State and persistence: Uses `sc->listen.backlog`, pending and ready lists, listener lock/wait queue, `status`, `first_error`, and `rdma.expected_event`. Child sockets store `accept.listener` back-pointers while pending/ready. State is in-memory and destroyed through socket cleanup/release.

Dependencies and integration points: Depends on RDMA CM listen/connect-request events, `smbdirect_frwr_is_supported()`, socket creation and parameter APIs from `socket.c`, accept handling in `accept.c`, logging in `socket.h`, and global workqueues initialized by `main.c`.

Risks and edge cases: Backlog checks use `>` rather than `>=`, so the exact accepted queue depth should be reviewed against intended semantics. If child setup fails after `new_id` ownership transfer, the code clears child `cm_id`/`ib.dev` so the caller can destroy the CM id. Unexpected listener events schedule listener cleanup and may return an error so RDMA core destroys the new id. Concurrent accept/cleanup requires careful list locking and `list_del_init`.

Test signals: Test listen on bound/unbound created sockets, zero and negative backlog, RDMA connect request success, backlog full, unsupported FRWR, IB-only/iWARP-only restrictions, child parameter copy failure, listener shutdown while children are pending, and upper-layer accept wakeups.
