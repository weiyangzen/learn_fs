# sources/distributed-fs/ceph-client/fs/dlm/lowcomms.c

## Purpose
`lowcomms.c` is the DLM transport layer. It maps cluster node ids to configured socket addresses, owns TCP/SCTP listening and outgoing sockets, queues outbound bytes into page-backed write queue entries, receives raw byte streams from peers, validates complete DLM packet boundaries through midcomms, and hands full buffers to a DLM processing workqueue. It deliberately keeps callers from doing socket I/O directly so lock paths do not block under load.

## Important APIs, Types, And Functions
Key internal types are `struct connection`, `struct listen_connection`, `struct writequeue_entry`, `struct dlm_msg`, `struct processqueue_entry`, and `struct dlm_proto_ops`. Connections are hashed by `nodeid_hash()` under `connection_hash[]`, protected by SRCU plus `connections_lock`; socket lifetime is serialized by `sock_lock`.

The exported API includes `dlm_lowcomms_start()`, `dlm_lowcomms_shutdown()`, `dlm_lowcomms_stop()`, `dlm_lowcomms_init()`, `dlm_lowcomms_exit()`, `dlm_lowcomms_addr()`, `dlm_lowcomms_connect_node()`, `dlm_lowcomms_close()`, `dlm_lowcomms_new_msg()`, `dlm_lowcomms_commit_msg()`, `dlm_lowcomms_put_msg()`, and `dlm_lowcomms_resend_msg()`. Cache constructors `dlm_lowcomms_writequeue_cache_create()` and `dlm_lowcomms_msg_cache_create()` are consumed by `memory.c`.

Important workers and callbacks are `process_send_sockets()`, `process_recv_sockets()`, `process_listen_recv_socket()`, `lowcomms_data_ready()`, `lowcomms_write_space()`, `lowcomms_error_report()`, `receive_from_sock()`, `send_to_sock()`, `accept_from_sock()`, and `dlm_connect()`.

## Control Flow
Startup runs `init_local()` to load local cluster addresses from configfs, chooses TCP or SCTP `dlm_proto_ops`, creates `dlm_io` and `dlm_process` workqueues, creates a kernel socket, installs listen callbacks, binds/listens on the configured DLM port, and stores the listen socket in `listen_con`.

Outbound flow starts when midcomms calls `dlm_lowcomms_new_msg()`. The function finds the per-node connection, allocates or reuses a page-backed `writequeue_entry`, returns a writable pointer, and keeps a SRCU read-side lock until `dlm_lowcomms_commit_msg()`. Commit links a `dlm_msg` to the entry, marks the entry sendable when all users are done filling it, and queues send work. `process_send_sockets()` connects if no socket exists, then repeatedly calls `send_to_sock()` until the socket blocks, the queue drains, or an error causes reconnection.

Inbound flow starts from socket callbacks. Data-ready schedules `rwork`; `receive_from_sock()` merges previous leftovers with a nonblocking `kernel_recvmsg()`, calls `dlm_validate_incoming_buffer()` to find complete DLM messages, saves incomplete tail bytes in `rx_leftover_buf`, and queues a `processqueue_entry`. `process_dlm_messages()` calls `dlm_process_incoming_buffer()` outside the socket worker, so parsing and lock handling are separated from socket receive.

Accepted inbound sockets are matched back to cluster nodes with `addr_to_nodeid()`. If an outgoing socket already exists, the accepted socket is placed in `othercon` to support historical crossed-connect behavior. Connection close, shutdown, and node removal stop callbacks, cancel work, optionally perform socket shutdown handshakes, clean partial writes, and release connections through SRCU callbacks.

## State And Persistence
All state is in kernel memory: connection hash entries, socket pointers, per-node address arrays, write queues, process queues, leftover receive bytes, transport protocol selection, and workqueues. It persists for the lifetime of the DLM module or a live node membership entry, not across reboot. Write queue entries use krefs because a page, the queued entry, and one or more `dlm_msg` handles can share lifetime. Partial dirty entries are discarded after reconnect to avoid delivering half a message.

## Dependencies And Integration Points
This file integrates with configfs via `dlm_our_addr()`, `dlm_config`, `dlm_comm_seq`, and protocol settings; with midcomms through `dlm_validate_incoming_buffer()`, `dlm_process_incoming_buffer()`, and `dlm_midcomms_unack_msg_resend()`; with memory cache setup through `memory.c`; with Linux sockets, TCP, SCTP, workqueues, SRCU, RCU, krefs, and tracepoints.

## Risks
The largest risks are races around socket callback replacement, `othercon` handling, SRCU connection removal, and writequeue lifetime. A protocol mismatch, bad configured addresses, or missing local address blocks startup. The code retries outbound connect forever, so cluster-manager fencing or upper-layer failure detection must handle unreachable peers. Receive-side buffering can grow pressure under bursts; `DLM_MAX_PROCESS_BUFFERS` backpressure waits for the processing queue to drain.

## Test Signals
Useful signals include successful TCP/SCTP module startup, connection establishment and reconnect under node restart, retransmission after socket error, no use-after-free under simultaneous accept/connect/close, correct handling of packet fragmentation across receives, and tracepoints `trace_dlm_send`/`trace_dlm_recv`. Fault injection for allocation failures, malformed lengths, and write-space/app-limited transitions is especially valuable.
