# sources/distributed-fs/ceph-client/fs/ocfs2/cluster/tcp.c

## Purpose

`tcp.c` implements the OCFS2 O2CB cluster network transport (`o2net`) over kernel TCP sockets. It provides synchronous message send APIs for higher layers such as DLM, handler registration for inbound message types keyed by domain key, connection establishment/teardown tied to heartbeat state, protocol handshaking, keepalive/idle timeout handling, and quorum notification when a peer becomes unreachable or suspicious.

The file deliberately presents a simple blocking RPC-like contract to callers: send a message to a target node, wait for a status response from the remote handler, and translate network/system failure into Linux errno values. Internally, it is event-driven through socket callbacks, an ordered workqueue, per-node status waiters, and per-socket framing state.

## Important APIs, Types, and Functions

Exported APIs are `o2net_send_message()`, `o2net_send_message_vec()`, `o2net_register_handler()`, `o2net_unregister_handler_list()`, `o2net_fill_node_map()`, `o2net_register_hb_callbacks()`, `o2net_unregister_hb_callbacks()`, `o2net_start_listening()`, `o2net_stop_listening()`, `o2net_disconnect_node()`, `o2net_num_connected_peers()`, `o2net_init()`, and `o2net_exit()`.

Global state includes the handler red-black tree protected by `o2net_handler_lock`, `o2net_nodes[O2NM_MAX_NODES]`, the listening socket, ordered workqueue `o2net_wq`, heartbeat callbacks, static handshake and keepalive message buffers, and the connected peer count. Per-node runtime state is manipulated through `o2net_set_nn_state()`, which owns the connection pointer, validity bit, persistent transmit error, status waiter completion, reconnect scheduling, and quorum notifications.

Message waiting is built around `struct o2net_status_wait`. `o2net_prep_nsw()` allocates a per-node ID with `idr_alloc()`, links it onto `nn_status_list`, and gives the outgoing `msg_num` its waiter. `o2net_complete_nsw()` and `o2net_complete_nodes_nsw()` wake waiters for status responses or node shutdown.

Connection state is represented by `struct o2net_sock_container`. `sc_alloc()`, `sc_get()`, `sc_put()`, and `sc_kref_release()` manage the socket, node dependency, receive page, work items, idle timer, keepalive work, debugfs hooks, and refcounted lifetime. Socket callbacks are installed and removed by `o2net_register_callbacks()` and `o2net_unregister_callbacks()`.

## Control Flow

Initialization starts in `o2net_init()`: quorum/debugfs are initialized, one zeroed folio is carved into `o2net_hand`, `o2net_keep_req`, and `o2net_keep_resp`, protocol magic fields are filled, and every `o2net_node` is initialized with locks, wait queues, status IDR/list, delayed work, and initial `-ENOTCONN` persistent error.

Listening is started by node manager via `o2net_start_listening()`, which allocates the ordered `o2net` workqueue, opens a listening socket with `o2net_open_listening_sock()`, replaces the listen socket data-ready callback, and reports the local connection up to quorum. Accepted connections are drained by `o2net_accept_many()`. `o2net_accept_one()` validates remote IP, enforces the node-number direction rule, requires heartbeat to already be visible, rejects duplicate connections, allocates an `sc`, attaches it to the node, registers callbacks, queues receive work, and sends the local handshake.

Outbound connection attempts are driven by heartbeat and loss events through `o2net_start_connect()`. Only the higher-numbered node initiates. The worker gets local and remote node config, avoids attempts when an existing socket or non-retryable persistent error exists, creates/binds a TCP socket, sets no-delay and TCP user timeout, registers callbacks, attaches the `sc`, and issues a nonblocking connect. Completion of either an accepted or connected socket queues `o2net_sc_connect_completed()`, which sends the current handshake.

Receive framing is handled by `o2net_rx_until_empty()` and `o2net_advance_rx()`. The receive page first accumulates `struct o2net_handshake`; `o2net_check_handshake()` validates protocol version, idle timeout, keepalive delay, and heartbeat timeout, then marks the socket valid and starts idle/keepalive. After handshake, the same page accumulates an `o2net_msg` header and payload. Oversized payloads, bad magic, EOF, and protocol failures close the connection.

Sending flows through `o2net_send_message_vec()`. It validates payload size and target, waits for `o2net_tx_can_proceed()` to yield either a valid socket or persistent error, allocates a header and combined kvec array, prepares an `o2net_status_wait`, sets `msg_num`, serializes the send under `sc_send_lock`, then blocks until the waiter completes. Remote handler status is delivered by `O2NET_MSG_STATUS_MAGIC`; transport/system errors use `O2NET_ERR_*` translation and do not overwrite caller status.

Inbound messages are processed by `o2net_process_message()`. Status frames wake local waiters, keepalive requests send keepalive responses, keepalive responses only refresh idle state, and normal messages look up a registered handler by type/key. Payload length is checked against the handler's `nh_max_len`; the handler is called with the receive buffer; a status frame is sent back; and optional post-handler callbacks run after the response.

## State and Persistence Behavior

There is no disk persistence in this file. Long-lived kernel state consists of per-node connection state, status waiter IDRs, delayed reconnect/expiry/quorum work, the handler tree, and the shared static protocol buffers. Runtime status is intentionally reset by heartbeat transitions: node down forces `-ENOTCONN`, cancels reconnect and quorum work, completes pending status waiters, and prevents reconnect until heartbeat returns.

Connection validity is separated from socket existence. A socket may be present while handshaking (`nn_sc` set, `nn_sc_valid` false), and transmitters only proceed when valid or when a persistent error wakes them. Idle timeout does not immediately close the socket; it marks `nn_timeout`, reports a quorum connection error, queues delayed still-up handling, and resets the timer. Any later received data clears the timeout/quorum suspicion in `o2net_sc_postpone_idle()`.

## Dependencies and Integration Points

`tcp.c` depends on Linux kernel sockets, TCP helpers, workqueues, timers, krefs, IDR, wait queues, spin/rw locks, folios/pages, NOFS allocation guards, tracepoints, debugfs hooks, and optional stats. OCFS2-specific integration is with heartbeat (`o2hb_*`), node manager (`o2nm_*`), quorum (`o2quo_*`), masklog, and the public/private transport headers.

The most important consumer is OCFS2 DLM, whose message handlers register with `o2net_register_handler()` and whose remote operations rely on the synchronous status response. Node manager owns listening lifecycle, while heartbeat callbacks drive connect/disconnect policy.

## Risks and Edge Cases

Ordering and lifetime are the main risks. Socket callbacks queue work while teardown unregisters callbacks and flushes work; missed refs or callback races can become use-after-free. `o2net_set_nn_state()` has many side effects and must be called under `nn_lock`; incorrect callers can desynchronize connected peer counts, waiter completion, reconnect work, and quorum state.

Handshake mismatches are treated as persistent enough to stop reconnect for that peer, because mismatched protocol/timeouts can corrupt cluster assumptions. Payload max-length protection is per-handler; handler registration mistakes can reject valid traffic or allow oversized handler input. `o2net_sendpage()` loops on `-EAGAIN` with `cond_resched()` and shuts down on other short sends, so TCP behavior under memory pressure or partial sends is important.

Node-number direction is integral: higher-numbered nodes connect, lower-numbered nodes accept. Split-brain or duplicate socket attempts are rejected, but testing must cover races where heartbeat visibility and inbound connect ordering differ across nodes.

## Test Signals

Useful signals include multi-node O2CB mount/unmount, heartbeat up/down cycles, higher-to-lower connection establishment, accept rejection from unknown IPs or wrong node-number direction, duplicate connection attempts, protocol version/timeout mismatch logs, keepalive timeout and recovery, DLM message round trips, pending sender wakeup on disconnect, and clean `o2net_stop_listening()` teardown under traffic.

Fault injection should cover allocation failures in `sc_alloc()` and send path, `idr_alloc()` failure, partial/short sends, EOF while receiving header/payload, payload overflow, missing handler, handler status propagation, and delayed reconnect expiry.
