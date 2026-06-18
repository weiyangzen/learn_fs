# sources/distributed-fs/ceph-client/net/9p/trans_fd.c

Purpose: implements the 9P `tcp`, `unix`, and explicit `fd` transports by wrapping sockets or user-provided file descriptors in an asynchronous mux. It is the generic stream/file backend for v9fs clients when virtio-like shared-memory transports are not used.

Important APIs, types, and functions: `struct p9_trans_fd` holds read/write `struct file` references and an embedded `struct p9_conn`. `struct p9_conn` owns sent and unsent request lists, current read/write request references, poll wait entries, and read/write work items. `p9_fd_create_tcp`, `p9_fd_create_unix`, and `p9_fd_create` connect the transport; `p9_fd_request`, `p9_fd_cancel`, `p9_fd_cancelled`, and `p9_fd_close` implement the `p9_trans_module` contract. `p9_read_work`, `p9_write_work`, `p9_poll_mux`, and `p9_poll_workfn` are the event engine.

Control flow: create opens a TCP/Unix socket or duplicates supplied fds, forces nonblocking I/O, marks the client connected, and registers poll wait hooks. Requests are queued on `unsent_req_list`; write work moves one request to `req_list`, writes its 9P frame incrementally, and keeps a reference until the frame is fully written. Read work first reads the 9P header into `tmp_buf`, resolves the tag with `p9_tag_lookup`, switches to the request response buffer, then completes the request through `p9_client_cb`.

State and persistence: all state is per client except the global poll pending list and reserved port sysctl-style globals. Request state transitions use `REQ_STATUS_UNSENT`, `SENT`, `RCVD`, `FLSHD`, and `ERROR`; `m->err` makes cancellation one-shot. State is volatile kernel memory; no persistence survives unmount/module removal.

Dependencies and integration points: depends on vfs `kernel_read`/`kernel_write`, socket creation/connect, poll wait queues, workqueues, and the net/9p client tag table. It registers three transports with `v9fs_register_trans` and reports mount options with `seq_file`.

Risks: the transport mutates file flags with intentional `data_race()` to force `O_NONBLOCK`; incorrect sharing of fds can break mounts. Header parsing, tag lookup, request list removal, and work cancellation are concurrency-sensitive. Unexpected tags or overlarge responses disconnect the whole client. The TCP privileged-port bind loop can fail under port exhaustion.

Test signals: useful checks include mounting over `trans=tcp`, `trans=unix`, and `trans=fd`; exercising short reads/writes and `EAGAIN`; flush/cancel races; server disconnects; malformed tags/lengths; module unload after active requests; and KCSAN/lockdep around request lists and poll wait removal.
