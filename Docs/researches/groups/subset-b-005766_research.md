# subset-b-005766 research

Grouped research for SMBDirect transport files and `fs/splice.c`. Each section is source-tree aligned and bounded for the reconciliation splitter.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/accept.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/accept.c

Purpose: Implements the passive SMBDirect connection path after a listener receives an RDMA connect request. It accepts the CM connection, posts the initial receive buffer for the client negotiate request, validates the SMBDirect negotiate PDU, optionally waits until userspace/upper SMB layer accepts the socket, and sends the negotiate response that grants initial receive credits.

Important APIs and functions: `smbdirect_accept_connect_request()` is the entry point from `listen.c` for a newly created accepting socket. `smbdirect_accept_init_params()` initializes send batch/local credits, server-side RDMA read/write credit geometry, and the first receive-credit target. `smbdirect_accept_negotiate_recv_done()` is the receive CQ completion for the negotiate request and defers sleeping validation to `smbdirect_accept_negotiate_recv_work()`. `smbdirect_accept_negotiate_finish()` posts the negotiate response and transitions successful sockets through `smbdirect_connection_negotiation_done()`. `smbdirect_socket_accept()` exposes ready accepted sockets to the upper layer and deliberately sends the successful negotiate response only after the socket is accepted.

Control flow: The listener constructs an accepting socket, copies listener parameters, adds it to the listener pending queue, and calls `smbdirect_accept_connect_request()`. That function negotiates RDMA initiator/responder resources, creates QP and memory pools, posts one receive for `SMBDIRECT_EXPECT_NEGOTIATE_REQ`, sets the RDMA CM handler, calls `rdma_accept()`, and starts a negotiate timeout. The RDMA established event calls `smbdirect_connection_rdma_established()`, moves status to `NEGOTIATE_NEEDED`, and queues negotiate work if the receive completion already arrived. The negotiate receive work parses `smbdirect_negotiate_req`, rejects unsupported versions or invalid credit/size fields, clamps negotiated sizes and credit targets, then either moves a listener-owned socket from pending to ready or sends a response immediately for direct accept use.

State and persistence: State is in `struct smbdirect_socket`, especially `status`, `first_error`, `rdma.expected_event`, `accept.listener`, listener pending/ready lists, `recv_io.expected`, receive reassembly, credit counters, and idle timer fields. There is no persistent storage; all state is in-memory kernel transport state tied to the socket, RDMA CM id, QP, workqueues, and mempools.

Dependencies and integration points: Depends on RDMA CM/IB verbs, `connection.c` for QP, mempool, credit, receive refill, and connected-state helpers, `pdu.h` for negotiate PDU layout, `socket.c` for cleanup, and SMB2 NT status constants from `../common/smb2status.h`. It integrates with `listen.c` through pending/ready accept queues and with upper SMB server code through exported `smbdirect_socket_accept()`.

Risks and edge cases: Receive completions can race with `RDMA_CM_EVENT_ESTABLISHED`, so queueing is guarded by `connect.lock` and status checks. Invalid negotiate fields must disconnect without leaking posted receive buffers. The listener backlog check occurs earlier in `listen.c`, while this file must still handle a listener disappearing through cleanup. `smbdirect_socket_accept()` sets `CONNECTED` before the negotiate response is sent, so failures in `smbdirect_accept_negotiate_finish()` can produce a socket that immediately schedules cleanup. Credit grant correctness depends on `recv_io_refill()` posting buffers before the response advertises credits.

Test signals: Exercise IB/RoCE and iWARP passive connects, including legacy iWARP private data, clients that send negotiate before established, unsupported SMBDirect version, zero `credits_requested`, too-small receive/fragment sizes, backlog pressure, accept timeout/nonblocking accept, disconnect during pending negotiation, and CQ send/recv flush paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/accept.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/connect.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/connect.c

Purpose: Implements the active/client SMBDirect connection path: address resolution, route resolution, RDMA connect, RDMA resource negotiation, SMBDirect negotiate request/response exchange, memory registration setup, and synchronous connect waiting.

Important APIs and functions: `smbdirect_connect()` starts asynchronous connection setup and is exported. `smbdirect_connect_sync()` wraps it with `smbdirect_connection_wait_for_connected()`. Internal stages are `smbdirect_connect_setup_connection()`, `smbdirect_connect_resolve_addr()`, `smbdirect_connect_resolve_route()`, `smbdirect_connect_rdma_connect()`, `smbdirect_connect_rdma_event_handler()`, `smbdirect_connect_negotiate_start()`, `smbdirect_connect_negotiate_send_done()`, `smbdirect_connect_negotiate_recv_done()`, and `smbdirect_connect_negotiate_recv_work()`.

Control flow: `smbdirect_connect()` requires a created socket and installed RDMA CM id, then switches the event handler and starts `rdma_resolve_addr()`. RDMA CM events advance `RESOLVE_ADDR_RUNNING -> RESOLVE_ROUTE_NEEDED -> RDMA_CONNECT_NEEDED -> NEGOTIATE_NEEDED`. The RDMA connect stage validates FRWR support and requested IB/iWARP transport restrictions, clamps MR depth and responder resources to device limits, creates the QP, provides iWARP IRD/ORD private data when needed, calls `rdma_connect_locked()`, and arms a timeout. On established, it normalizes peer RDMA resource values for iWARP versus non-iWARP, calls `smbdirect_connection_negotiate_rdma_resources()`, posts one receive for the negotiate response, sends a negotiate request, and arms the negotiate timeout.

State and persistence: The active path mutates `sc->status`, `rdma.expected_event`, `ib.dev`, `mr_io.type`, `parameters` negotiated limits, send local/batch credits, receive expected PDU type, send credits granted by peer, receive credit target requested by peer, MR list state, and idle keepalive timer. It uses the socket receive reassembly list as temporary storage for the negotiate response. No state is persisted beyond in-memory socket lifetime.

Dependencies and integration points: Uses RDMA CM (`rdma_resolve_addr`, `rdma_resolve_route`, `rdma_connect_locked`), IB device attributes, QP/mempool/MR helpers from `connection.c` and `mr.c`, PDU definitions from `pdu.h`, status constants from `smb2status.h`, and cleanup/status helpers from `socket.c`/`socket.h`. Upper SMB client code enters through exported connect APIs and then uses send/receive/RDMA APIs after `CONNECTED`.

Risks and edge cases: Event order is strict and unexpected CM events schedule cleanup. Device removal maps to lower-noise logging for `-ENODEV`/`-ENETDOWN`. Negotiation rejects unsupported version, non-success NT status, zero credits, undersized receive/fragment values, peer preferred-send larger than local receive capacity, and max read/write below one page. The code notes a TODO where peer-lowered receive size may require receive-buffer count adjustment. A posted receive remains owned by RDMA after post failure boundaries, so error paths intentionally avoid freeing some resources directly.

Test signals: Cover success on RoCE/IB and iWARP, route/address failure, FRWR-unsupported devices, port-range restrictions, RDMA reject/device-removal, connect timeout, malformed negotiate responses, small max read/write, zero credits, MR allocation failure, and `smbdirect_connect_sync()` interruption/timeout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/connect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/connection.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/connection.c

Purpose: Provides the shared SMBDirect connected data path: RDMA CM connected/disconnected handling, QP/CQ/PD lifecycle, send and receive mempools, receive-credit grant/refill logic, keepalive, SMBDirect data-transfer send/receive, reassembly into upper-layer SMB messages, and DMA SGE mapping from kernel iterators.

Important APIs and functions: Connection lifecycle functions include `smbdirect_connection_rdma_established()`, `smbdirect_connection_negotiation_done()`, `smbdirect_connection_create_qp()`, `smbdirect_connection_destroy_qp()`, `smbdirect_connection_create_mem_pools()`, and `smbdirect_connection_destroy_mem_pools()`. Buffer helpers include `smbdirect_connection_alloc_send_io()`, `smbdirect_connection_free_send_io()`, `smbdirect_connection_get_recv_io()`, `smbdirect_connection_put_recv_io()`, and reassembly helpers. Data APIs include exported `smbdirect_connection_send_single_iter()`, `smbdirect_connection_send_iter()`, `smbdirect_connection_send_batch_flush()`, `smbdirect_connection_recvmsg()`, `smbdirect_connection_send_wait_zero_pending()`, and status wait helpers.

Control flow: After accept/connect negotiation calls `smbdirect_connection_negotiation_done()`, refill and immediate-send work handlers are enabled and status waiters are woken. Send operations wait for one batch credit, one local send WR credit, and one peer send credit, possibly flush a batch, grant newly posted receive credits, map header/payload SGEs, fill `smbdirect_data_transfer`, and post an IB send. Send completions free sibling batches, restore local credits, decrement pending counts, and wake waiters. Receive completions validate `smbdirect_data_transfer`, update keepalive, consume posted/receive credits, apply peer credit grants, append payload buffers to the reassembly queue, and schedule refill or immediate response work. `recvmsg()` waits until enough reassembled data exists and copies into an ITER_DEST, synthesizing an RFC1002 length header for first-segment length reads.

State and persistence: Key volatile state includes socket status/error, RDMA expected disconnect event, QP/CQ/PD pointers, mempool pointers, send batch/local/remote/pending credit atomics, receive free/posted/available/granted credit counters, reassembly queue length/data/offset/full-packet flags, idle keepalive state/timer, and debug statistics. No durable persistence exists; teardown drains QP and frees all in-memory resources.

Dependencies and integration points: Uses RDMA CM, IB verbs, `rdma_rw` QP sizing helpers, Linux mempools/slab, wait queues, workqueues, folio queue/iov iterator APIs, SMBDirect PDU structs, and socket cleanup macros. It is the shared backend for `accept.c`, `connect.c`, `mr.c`, `rw.c`, and upper SMB transport operations.

Risks and edge cases: QP sizing must avoid CQE/QP WR overruns, especially when RDMA RW contexts add hidden WRs. Credit accounting spans multiple atomics and wait queues; missed wakeups can deadlock sends or refills. Reassembly uses lockless front reads plus memory barriers, so queue length/data ordering is subtle. Iterator mapping supports BVEC, KVEC, and FOLIOQ only; unsupported iterator types fail. `send_io_done()` has special handling for unsignaled sibling completions during errors to avoid use-after-free. Receive validation must reject misaligned offsets, short packets, and fragmented sizes beyond negotiated limits.

Test signals: Validate large fragmented SMB sends/receives, RFC1002 header reads, zero-payload keepalives, peer response-requested flags, credit starvation/regrant, concurrent send batching, disconnect while waiters block, QP/CQ capacity failure, unsupported iterator types, FOLIOQ/KVEC/BVEC mapping, malformed data-transfer headers, and workqueue behavior under CQ flush.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/connection.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/debug.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/debug.c

Purpose: Emits legacy proc/seq-file diagnostics for an SMBDirect socket so upper SMB code can expose transport status, negotiated parameters, counters, credits, and memory-registration state.

Important APIs and functions: `smbdirect_connection_legacy_debug_proc_show()` is exported and takes a socket, the caller's RDMA read/write threshold, and a `seq_file`. It reads `struct smbdirect_socket_parameters`, socket status, statistics, atomic credit counters, and MR counters.

Control flow: The function returns immediately for a NULL socket. Otherwise it prints multiple newline-separated groups: protocol/status, receive/send credits and sizes, fragmented sizes, keepalive and read/write limits, receive-buffer counters, reassembly counters, current credit counts, pending sends, and MR resource state.

State and persistence: It is read-only diagnostic code. It observes live in-memory socket fields without taking locks, so output is a best-effort snapshot and may race with connection teardown or data-path updates. It persists nothing.

Dependencies and integration points: Depends on `seq_file`, `internal.h`, `SMBDIRECT_V1`, `smbdirect_socket_status_string()`, and the socket layout in `socket.h`. It is exported for external SMB client/server diagnostic plumbing that still expects the older debug layout.

Risks and edge cases: Because values are read locklessly, counters and related fields can be internally inconsistent under concurrent traffic. A non-NULL socket being destroyed concurrently would require external lifetime protection by the caller. Keepalive interval is printed in microsecond-looking units by multiplying milliseconds by 1000, so consumers must know the legacy display convention.

Test signals: Proc/debug output should be checked for NULL sockets, connected sockets with active send/receive traffic, MR use, disconnecting sockets, and stable formatting expected by legacy consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/devices.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/devices.c

Purpose: Tracks RDMA devices usable for SMBDirect and provides net-device capability lookup so higher layers can decide whether a network interface can support SMBDirect over IB/RoCE or iWARP.

Important APIs and functions: `smbdirect_devices_init()` registers an `ib_client`; `smbdirect_devices_exit()` unregisters it and clears the tracked device list. `smbdirect_netdev_rdma_capable_node_type()` is exported for netdev capability lookup. Internal callbacks `smbdirect_ib_client_add()`, `smbdirect_ib_client_remove()`, and `smbdirect_ib_client_rename()` maintain `smbdirect_globals.devices.list`. `smbdirect_ib_device_rdma_capable_node_type()` filters devices by FRWR support and RDMA node type.

Control flow: On module init, the IB client add callback logs device capabilities, ignores devices lacking FRWR or supported node type, allocates a `smbdirect_device`, stores the `ib_device` and name copy, and adds it under a write lock. Remove/rename callbacks update the same list. Capability lookup first scans tracked IB devices and their ports for a matching netdev, then falls back to `ib_device_get_by_netdev()`. It also checks lower devices for bridge/VLAN netdevs and treats IPoIB ARPHRD_INFINIBAND as IB-capable.

State and persistence: Maintains an in-memory global list protected by `rwlock_t`. Each entry stores an `ib_device *` and a stable name copy used for remove/rename logging. No persistent state exists; the list is rebuilt by IB client registration.

Dependencies and integration points: Depends on RDMA core device/client APIs, netdevice APIs for lower-device traversal, `smbdirect_frwr_is_supported()` from `socket.c`, and global module state from `internal.h`. It integrates with module init/exit in `main.c` and callers that need `RDMA_NODE_*` answers for interfaces.

Risks and edge cases: Netdev-to-IB mapping can race with device removal, so reference handling through `ib_device_get_netdev()`/`dev_put()` and `ib_device_get_by_netdev()`/`ib_device_put()` is important. Bridge/VLAN lookup returns the first capable lower device and may not represent all paths. Device add logs substantial capability data, which is useful for diagnosis but can be noisy on systems with many RDMA devices.

Test signals: Test add/remove/rename callbacks, FRWR-unsupported devices, RoCE/IB/iWARP node types, bridge and VLAN lower devices, IPoIB fallback, no-device netdevs, and module unload after devices have been tracked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/devices.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/internal.h -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/internal.h

Purpose: Defines SMBDirect module-internal declarations and global state shared across implementation files. It establishes the module symbol namespace, logging prefix, global workqueue/device container, internal device wrapper, cleanup scheduling macros, and prototypes for non-exported cross-file helpers.

Important APIs and types: `struct smbdirect_module_state` holds the global mutex, six workqueue pointers (`accept`, `connect`, `idle`, `refill`, `immediate`, `cleanup`), and the RDMA device list protected by an rwlock. `struct smbdirect_device` links an `ib_device` into the global list with a copied device name. Cleanup macros wrap `__smbdirect_socket_schedule_cleanup()` with call-site function/line and optional forced status. Prototypes cover socket initialization/destruction, connection QP/mempool/send/recv/MR helpers, accept negotiation, and device init/exit.

Control flow: This header has no runtime control flow, but it shapes cross-file control by allowing accept/connect/listen/device/main code to call shared connection and socket internals while keeping public API declarations in external headers.

State and persistence: Declares the global `smbdirect_globals`, whose storage is in `main.c`. State remains volatile module memory: workqueues, device list, locks, and socket resources. No persistent state is introduced.

Dependencies and integration points: Includes `<linux/smbdirect.h>`, `pdu.h`, mutex support, and finally `socket.h` so all internal code sees the full socket layout. It integrates the SMBDirect module with Linux RDMA/IB types and the rest of fs/smb transport code.

Risks and edge cases: Since this header exposes the full internal socket helper surface to every implementation file, changes to prototypes or global state have wide compile-time and behavioral impact. Cleanup macros capture local `__func__`/`__LINE__`; misuse outside a real socket error path could force unwanted disconnect. Include ordering matters because `socket.h` depends on definitions and PDU types.

Test signals: Build coverage is the main signal: all SMBDirect implementation files must compile after prototype or struct changes. Runtime smoke tests should verify that all workqueue pointers are initialized before any socket is initialized and that cleanup macros produce correct status transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/listen.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/listen.c

Purpose: Implements SMBDirect listening sockets and conversion of RDMA connect requests into accepting sockets queued for the upper layer.

Important APIs and functions: `smbdirect_socket_listen()` is exported and starts RDMA listening on a bound socket. `smbdirect_listen_rdma_event_handler()` handles listener CM events. `smbdirect_listen_connect_request()` validates a new request, enforces backlog, creates an accepting socket, copies listener settings/logging, enqueues it as pending, and starts passive accept handling.

Control flow: A created socket enters `LISTENING`, installs the listen RDMA event handler, expects `RDMA_CM_EVENT_CONNECT_REQUEST`, and calls `rdma_listen()`. For connect requests, the handler detaches the new CM id from the listener context, installs a placeholder handler until accept code takes ownership, validates event/status, and calls `smbdirect_listen_connect_request()`. That function checks FRWR support and transport restrictions, counts pending/ready queues under the listener lock, creates a child socket, copies parameters and kernel settings, adds it to pending, and calls `smbdirect_accept_connect_request()`.

State and persistence: Uses `sc->listen.backlog`, pending and ready lists, listener lock/wait queue, `status`, `first_error`, and `rdma.expected_event`. Child sockets store `accept.listener` back-pointers while pending/ready. State is in-memory and destroyed through socket cleanup/release.

Dependencies and integration points: Depends on RDMA CM listen/connect-request events, `smbdirect_frwr_is_supported()`, socket creation and parameter APIs from `socket.c`, accept handling in `accept.c`, logging in `socket.h`, and global workqueues initialized by `main.c`.

Risks and edge cases: Backlog checks use `>` rather than `>=`, so the exact accepted queue depth should be reviewed against intended semantics. If child setup fails after `new_id` ownership transfer, the code clears child `cm_id`/`ib.dev` so the caller can destroy the CM id. Unexpected listener events schedule listener cleanup and may return an error so RDMA core destroys the new id. Concurrent accept/cleanup requires careful list locking and `list_del_init`.

Test signals: Test listen on bound/unbound created sockets, zero and negative backlog, RDMA connect request success, backlog full, unsupported FRWR, IB-only/iWARP-only restrictions, child parameter copy failure, listener shutdown while children are pending, and upper-layer accept wakeups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/listen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/main.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/main.c

Purpose: Owns SMBDirect module-global state, module initialization, workqueue allocation, RDMA device registration, and teardown.

Important APIs and functions: Defines `struct smbdirect_module_state smbdirect_globals`. `smbdirect_module_init()` allocates the accept, connect, idle, refill, immediate, and cleanup workqueues and calls `smbdirect_devices_init()`. `smbdirect_module_exit()` calls `smbdirect_devices_exit()` and destroys all workqueues. `module_init()`/`module_exit()` register the lifecycle hooks.

Control flow: Init locks the global mutex, allocates workqueues in dependency order, initializes devices, unlocks, and reports loaded. Any allocation/device failure jumps through reverse cleanup labels and logs a critical failure. Exit locks, unregisters devices, destroys workqueues, unlocks, and reports unloaded.

State and persistence: Global state is an in-memory module singleton. Workqueues are stored in `smbdirect_globals.workqueues` and copied into each socket during `smbdirect_socket_init()`. Device list state is initialized by `devices.c`. No persistent state exists.

Dependencies and integration points: Depends on Linux module and workqueue APIs, `internal.h`, and `devices.c`. All socket code assumes this initialization has run before sockets are created.

Risks and edge cases: Workqueue allocation failures must unwind in exact reverse order; null destroy safety is not relied on for the failed allocation itself. The cleanup workqueue uses `WQ_MEM_RECLAIM | WQ_HIGHPRI`, indicating disconnect/destroy paths may run under memory pressure. Any future socket initialization before module init would copy NULL workqueue pointers and fail later.

Test signals: Build/module load-unload smoke tests, forced workqueue allocation failure paths if injectable, RDMA device init failure unwinding, repeated load/unload with device add/remove callbacks, and ensuring all workqueues disappear on unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/mr.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/mr.c

Purpose: Manages Fast Registration Memory Region (FRMR/MR) objects used by SMBDirect RDMA read/write buffer descriptors. It allocates MR pools, registers iterator memory for remote access, fills SMBDirect buffer descriptors, invalidates/deregisters MRs, and recycles them.

Important APIs and functions: `smbdirect_connection_create_mr_list()` allocates `responder_resources * 2` MR objects and scatterlists. `smbdirect_connection_destroy_mr_list()` detaches and disables all MRs. `smbdirect_connection_register_mr_io()` extracts an iterator to SG, DMA maps it, maps the MR, updates rkey, and posts `IB_WR_REG_MR`. `smbdirect_mr_io_fill_buffer_descriptor()` writes offset/token/length into `smbdirect_buffer_descriptor_v1`. `smbdirect_connection_deregister_mr_io()` performs local invalidation when needed or recycles remotely invalidated MRs.

Control flow: MR creation requires nonzero negotiated responder resources and allocates all MRs in READY state on `sc->mr_io.all.list`, incrementing ready count. Registration waits for a ready MR, marks it REGISTERED, takes a kref, extracts pages from the iterator, DMA maps SG entries, maps the MR, increments rkey, posts a signaled register WR, and returns the MR to the caller. Deregistration locks the MR, disables immediately if socket is disconnected, optionally posts and waits for `IB_WR_LOCAL_INV`, unmaps DMA SG entries, returns state to READY, wakes ready waiters, decrements used count, and drops the kref.

State and persistence: MR state is in `struct smbdirect_mr_io`: kref, mutex, list node, state enum, `ib_mr`, SG table, DMA direction, register/invalidate WR storage, `need_invalidate`, and completion. Socket-level state tracks all MRs, ready count wait queue, and used count. All state is volatile and destroyed during socket teardown.

Dependencies and integration points: Depends on IB MR APIs (`ib_alloc_mr`, `ib_map_mr_sg`, `ib_update_fast_reg_key`, `ib_post_send`, `ib_dereg_mr`), DMA SG mapping, iov iterator SG extraction, SMBDirect buffer descriptor types from public headers, QP/PD state from `connection.c`, and cleanup scheduling from `socket.c`.

Risks and edge cases: Reference/lifetime rules are subtle because destroy can detach MRs while callers still hold registration references. Register completion does not wake callers because hardware ordering is relied on before later send I/O. Local invalidation waits while temporarily dropping the mutex, so state is rechecked. Error paths set MR ERROR or DISABLED and schedule socket cleanup. `extract_iter_to_sg()` and `iov_iter_npages()` must agree with `max_frmr_depth`; over-depth iterators fail early.

Test signals: Test MR pool creation with zero and nonzero responder resources, max_frmr_depth boundaries, registration for read and write directions, local invalidation path, remote invalidation path, socket disconnect during deregistration, register WR failure, DMA map failure, descriptor fill for REGISTERED versus invalid states, and concurrent MR acquisition under exhaustion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/mr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/pdu.h -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/pdu.h

Purpose: Defines SMBDirect wire-format constants and packed PDU structures used for protocol negotiation and data transfer.

Important APIs and types: `SMBDIRECT_V1` is the supported protocol version. `SMBDIRECT_MIN_RECEIVE_SIZE` and `SMBDIRECT_MIN_FRAGMENTED_SIZE` encode minimum negotiated values from MS-SMBD. `struct smbdirect_negotiate_req` and `struct smbdirect_negotiate_resp` describe little-endian negotiation PDUs. `struct smbdirect_data_transfer` describes the data PDU header plus flexible payload. `SMBDIRECT_DATA_MIN_HDR_SIZE`, `SMBDIRECT_DATA_OFFSET`, and `SMBDIRECT_FLAG_RESPONSE_REQUESTED` are used by send/receive logic.

Control flow: This header has no runtime control flow. Its fields are populated in `connect.c`/`accept.c` for negotiate exchange and in `connection.c` for data transfer send/receive.

State and persistence: PDU structs represent on-wire state, not stored state. They are packed and use explicit little-endian integer types to preserve protocol layout across architectures.

Dependencies and integration points: Included by `internal.h`, which makes these definitions available across SMBDirect implementation files. Values integrate with MS-SMBD negotiation validation, credit exchange, keepalive response requests, and upper SMB message fragmentation.

Risks and edge cases: Any layout change would break wire compatibility. Callers must use endian conversion on all multi-byte fields. `data_offset` alignment and minimum header sizes are validated in receive code, so constants must remain consistent with struct layout and protocol expectations.

Test signals: Compile-time layout awareness, negotiation interop with SMBDirect peers, endian correctness on non-little-endian builds, malformed PDU validation, and data-transfer offset/length boundary tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/pdu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/rw.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/rw.c

Purpose: Implements server-side SMBDirect RDMA read/write transfer execution against remote SMBDirect buffer descriptors, using Linux `rdma_rw_ctx` helpers and the socket's negotiated RDMA RW credits.

Important APIs and functions: `smbdirect_connection_rdma_xmit()` is exported and performs RDMA READ when `is_read` is true or RDMA WRITE otherwise. Internal helpers calculate and wait for RW credits, convert a kernel buffer to scatterlist entries, free RDMA IO contexts, and handle read/write completions.

Control flow: The API validates connected state and max read/write size, walks buffer descriptors to clamp descriptor lengths to local buffer length and calculate needed credits, waits for RW credits, allocates one `smbdirect_rw_io` per descriptor, builds a chained SG table over the local buffer, initializes an `rdma_rw_ctx` with remote offset/token and direction, concatenates WRs in reverse descriptor order, posts the first WR, waits for a completion, frees all contexts, restores credits, and wakes credit waiters.

State and persistence: Uses transient `smbdirect_rw_io` objects containing completion pointer, error, RDMA context, SG table, and inline SG storage. Persistent socket-level state is only the atomic RW credit count and negotiated `rw_io.credits.max/num_pages`. No durable persistence exists.

Dependencies and integration points: Depends on `rdma_rw_ctx_init`, `rdma_rw_ctx_wrs`, `rdma_rw_ctx_destroy`, IB send posting, scatterlist helpers, virtual/kmap page conversion, SMBDirect buffer descriptor layout, and credit helpers in `socket.c`/`connection.c`. It is called by upper SMB server logic after clients provide RDMA descriptors.

Risks and edge cases: The debug log prints remaining `buf_len` after descriptor walking, which may be zero and not the original length. Completion waits on a single stack completion shared by all descriptor contexts and then reads the last message error; multi-WR error attribution deserves scrutiny. `smbdirect_connection_rdma_get_sg_list()` uses `kmap_to_page()` for non-vmalloc buffers and requires valid kernel mappings. Descriptor length zero fails, overlarge total transfer fails, and credit restoration must occur on all allocation/posting error paths.

Test signals: RDMA READ and WRITE with one and multiple descriptors, descriptor length clamping, zero descriptor length, transfer larger than negotiated maximum, vmalloc and direct-mapped buffers, credit exhaustion/interruption, post-send failure, CQ error/flush, and disconnect while waiting for RW credits or completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/rw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/socket.c -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/socket.c

Purpose: Owns SMBDirect socket creation, initialization, parameter/logging setup, bind/shutdown/release, central cleanup scheduling, synchronous destruction, and generic credit waiting.

Important APIs and functions: Exported APIs include `smbdirect_frwr_is_supported()`, `smbdirect_socket_create_kern()`, `smbdirect_socket_create_accepting()`, `smbdirect_socket_set_initial_parameters()`, `smbdirect_socket_get_current_parameters()`, `smbdirect_socket_set_kernel_settings()`, `smbdirect_socket_set_logging()`, `smbdirect_socket_bind()`, `smbdirect_socket_shutdown()`, and `smbdirect_socket_release()`. Internal lifecycle functions include `smbdirect_socket_init_new()`, `smbdirect_socket_init_accepting()`, `__smbdirect_socket_schedule_cleanup()`, `smbdirect_socket_cleanup_work()`, `smbdirect_socket_destroy()`, and `smbdirect_socket_destroy_sync()`.

Control flow: New sockets are zero-initialized through `smbdirect_socket_init()`, assigned module workqueues, wait queues, locks, disabled work items, krefs, default logging callbacks, and RDMA CM ids. Parameter setters are only valid in `CREATED`. Cleanup scheduling records `first_error`, disables async work, recursively schedules pending accepted sockets, maps the current status to an error/disconnect status, wakes all wait queues, and queues cleanup work. Cleanup work performs RDMA disconnect when appropriate or marks pre-established sockets disconnected. Destroy sync disables cleanup work, schedules shutdown if needed, waits for disconnected status, then destroys QP, CM id, mempools, MR list, reassembly buffers, and pending listener children.

State and persistence: Manages the full in-memory socket lifecycle: status, first error, krefs, RDMA CM id, work items, listener queues, reassembly buffers, QP resources, mempools, MR list, wait queues, and logging hooks. No persistent state exists.

Dependencies and integration points: Depends on RDMA CM id creation/bind/destroy/disconnect, socket layout and helpers from `socket.h`, connection teardown helpers in `connection.c`/`mr.c`, global workqueues from `main.c`, and upper SMB code that owns create/set/connect/listen/release sequencing.

Risks and edge cases: Cleanup can be invoked from many paths and must be idempotent enough to avoid double destruction while still waking all waiters. `refs.destroy` may be `REFCOUNT_MAX` when sockets are embedded, so release behavior differs by allocation model. Destroy holds `rdma_lock_handler()` while draining QP and destroying RDMA objects to coordinate CM callbacks. Recursive listener child cleanup can amplify errors across pending/ready children. `smbdirect_socket_wait_for_credits()` subtracts optimistically and restores on failure; misuse with negative needed values is guarded.

Test signals: Socket create/destroy, accepting socket creation, parameter validation and invalid status setters, bind before/after state changes, shutdown before connect/listen/connected, repeated cleanup calls, listener with pending children, disconnect during waits on each wait queue, FRWR capability filter, and release behavior for allocated versus embedded sockets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/socket.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/socket.h -->
## sources/distributed-fs/ceph-client/fs/smb/smbdirect/socket.h

Purpose: Defines the central SMBDirect socket state machine, in-memory transport structures, logging helpers, send/receive/MR/RW IO objects, initialization routine, status-check macros, and constants shared by the SMBDirect implementation.

Important APIs and types: `enum smbdirect_socket_status` covers created, listening, active connect phases, negotiate, connected, error, disconnecting, disconnected, and destroyed. `smbdirect_socket_status_string()` maps status to diagnostics. `struct smbdirect_socket` contains status/error, workqueues, krefs, RDMA CM and IB resources, negotiated parameters, connect/listen/accept state, send/receive credit and buffer state, MR and RW credit state, statistics, and logging callbacks. It also defines `struct smbdirect_send_io`, `struct smbdirect_send_batch`, `struct smbdirect_recv_io`, `struct smbdirect_mr_io`, `struct smbdirect_rw_io`, MR state enum, logging macros, `smbdirect_socket_init()`, status-check macros, page-count helper, and RDMA CM retry constants.

Control flow: The inline `smbdirect_socket_init()` establishes initial state for every socket: zeroes memory, initializes wait queues/locks/lists, copies global workqueues, disables work items until real handlers are installed, initializes krefs, marks RDMA expected event internal, sets default poll context and GFP masks, initializes credit counters and logging stubs. Status-check macros centralize warnings and optional disconnect scheduling when code observes an unexpected state.

State and persistence: This header defines all volatile socket state but does not persist anything. The state machine is enforced cooperatively by accept/connect/listen/connection/socket code. Atomic counters and wait queues represent flow-control state; spinlocks protect lists; krefs protect lifetime; work items drive async progress.

Dependencies and integration points: Includes wait queues, workqueues, krefs, mempool, spinlock, mutex, completion, and `rdma/rw.h`. It is included through `internal.h` by all SMBDirect implementation files and aligns with public `linux/smbdirect.h` types embedded in parameters and descriptors.

Risks and edge cases: Because `struct smbdirect_socket` is large and shared across all files, field layout and locking rules are easy to violate. Disabled placeholder work functions intentionally warn if queued before initialization. Logging callbacks are mandatory for logging macros; default stubs warn if callers forget to install real logging but code logs anyway. Status ordering is used by cleanup force-status comparisons, so enum reordering has behavioral consequences.

Test signals: Compile coverage for all users, initialization assertions, logging callback installation, status string coverage for every enum, status-check macro behavior, refcounted release paths, and runtime tests that exercise all status transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/smb/smbdirect/socket.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/splice.c -->
## sources/distributed-fs/ceph-client/fs/splice.c

Purpose: Implements Linux VFS splice/vmsplice/tee infrastructure: moving or referencing pages between files, pipes, sockets, and user iterators with minimal copying where possible. It provides pipe buffer operations, generic splice helpers, direct file-to-file splicing through a task-private pipe, socket splicing, vmsplice, and syscall entry points.

Important APIs and functions: Exported helpers include `splice_to_pipe()`, `add_to_pipe()`, `splice_grow_spd()`, `splice_shrink_spd()`, `copy_splice_read()`, `__splice_from_pipe()`, `iter_file_splice_write()`, `vfs_splice_read()`, `splice_direct_to_actor()`, `do_splice_direct()`, and `splice_file_range()`. Syscalls are `splice`, `vmsplice`, and `tee`. Important internal helpers include page-cache/user pipe buffer ops, `splice_from_pipe_next/feed/begin/end`, `splice_to_socket()`, `do_splice()`, `iter_to_pipe()`, `vmsplice_to_pipe()`, `vmsplice_to_user()`, `splice_pipe_to_pipe()`, and `link_pipe()`.

Control flow: File-to-pipe splicing locks the output pipe, waits for space, verifies read access, and calls file `splice_read` or `copy_splice_read()` for O_DIRECT/DAX. Pipe-to-file splicing verifies write access, rejects append/invalid offsets, starts write accounting, and invokes the file `splice_write`. Pipe-to-pipe splice moves or splits pipe buffers under double pipe locks. `tee` duplicates pipe buffer references without consuming input. Direct file-to-file splice allocates/reuses `current->splice_pipe`, splices input into it, calls an actor to drain it to output, handles partial/EOF cases, and releases leftover pipe buffers. `vmsplice` imports user iovecs, then either pins/maps user pages into a pipe or copies pipe pages back to userspace.

State and persistence: State is mostly transient pipe ring state (`head`, `tail`, `pipe_buffer` entries, readers/writers, wait queues), task-local `current->splice_pipe`, file offsets, and iterator progress. It does not persist durable metadata, but it can alter file positions and produces fsnotify access/modify events. Pipe buffers carry page refs, offsets, lengths, flags, private fields, and operation tables controlling release/steal/confirm behavior.

Dependencies and integration points: Integrates with VFS file operations (`splice_read`, `splice_write`, `read_iter`, `write_iter`, `splice_eof`), pipe internals, page cache/folio writeback and removal, socket sendmsg with `MSG_SPLICE_PAGES`, iov iter import/copy/page extraction, security/rw verification, fsnotify, signals, fasync, and memory allocation/page ref helpers.

Risks and edge cases: Pipe locking and wakeups are central; pipe-to-pipe operations avoid ABBA deadlock with ordered double locks. Nonblocking flags must be propagated from file flags and `FMODE_NOWAIT` is cleared on pipes because splice can block. Page stealing must wait for writeback and remove mapping safely to avoid filesystem corruption. Partial transfers require precise offset/tail/head updates and release of unconsumed buffers. User-page gifts must avoid double stealing by clearing gift/merge flags when buffers are duplicated. Direct splicing must not leave data in the private pipe on nonblocking output. Offset pointer rules reject pipe offsets and append writes.

Test signals: Cover splice file-to-pipe, pipe-to-file, pipe-to-pipe, pipe-to-socket, direct sendfile-style file-to-file, copy_file_range fallback, vmsplice in/out, tee duplication, O_NONBLOCK/SPLICE_F_NONBLOCK, signals while waiting, no readers/writers causing `EPIPE`/EOF, O_APPEND rejection, O_DIRECT/DAX copy path, short reads/writes, page-cache truncation/ENODATA, pipe full/empty races, and fsnotify/access position updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/splice.c -->
