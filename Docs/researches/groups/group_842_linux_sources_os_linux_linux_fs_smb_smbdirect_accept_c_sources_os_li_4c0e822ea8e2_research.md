# Group Research: group_842_linux_sources_os_linux_linux_fs_smb_smbdirect_accept_c_sources_os_li_4c0e822ea8e2

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux`, which is included in subset A. Every listed file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/accept.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/accept.c

Implements the server-side SMB Direct accept path after `listen.c` has received an RDMA CM connect request and created an accepting child socket. It initializes responder parameters, creates the QP and memory pools, posts the first receive buffer for the SMB Direct negotiate request, calls `rdma_accept()`, handles `RDMA_CM_EVENT_ESTABLISHED`, validates the negotiate request, and sends the negotiate response.

Key entry points:
- `smbdirect_accept_connect_request()` transitions a child socket from `CREATED` to `RDMA_CONNECT_RUNNING`, negotiates RDMA initiator/responder resources from RDMA CM private data, sets server-side send/local/RDMA RW credits, creates QP/mempools, posts the negotiate receive, and starts the negotiate timeout.
- `smbdirect_accept_negotiate_recv_done()` is the CQ completion for the negotiate request. It validates CQ status/opcode, DMA-syncs the receive buffer, appends valid-sized requests to the reassembly queue, and defers protocol parsing to workqueue context.
- `smbdirect_accept_negotiate_recv_work()` parses `struct smbdirect_negotiate_req`, validates version, credits, receive size, and fragmented size, updates negotiated socket parameters, then either moves listener-owned children to the listener ready queue or calls `smbdirect_accept_negotiate_finish()` directly for non-listener accepted sockets.
- `smbdirect_accept_negotiate_finish()` prepares data-transfer receive buffers, grants receive credits, constructs `struct smbdirect_negotiate_resp`, DMA maps it, posts an `IB_WR_SEND`, and relies on send completion to finalize negotiation.
- `smbdirect_socket_accept()` waits for a ready child, removes it from the listener ready queue, marks it connected for the caller, then sends the deferred negotiate response that grants the client credits.

Important state and invariants:
- The server delays a successful negotiate response for listener children until userspace/kernel frontend calls `smbdirect_socket_accept()`. This prevents granting peer credits before the application accepts the socket.
- `sc->recv_io.expected` gates the receive completion path: negotiate request first, then data-transfer receives after successful negotiation.
- Some drivers can deliver the negotiate receive completion before `RDMA_CM_EVENT_ESTABLISHED`; the code handles this by initializing `sc->connect.work` in the receive completion and queueing it only once the status reaches `NEGOTIATE_NEEDED`.
- Invalid protocol version results in a negotiate response with `STATUS_NOT_SUPPORTED`; malformed sizes or zero credits trigger cleanup rather than a protocol-level negative response.
- `smbdirect_accept_negotiate_send_done()` frees the send buffer, decrements pending send count, disconnects on send failure, disconnects after non-success NT status, and calls `smbdirect_connection_negotiation_done()` on success.

Dependencies:
- Uses `connection.c` for QP/mempool creation, receive posting/refill, send WR posting, credit granting, reassembly queue helpers, RDMA established state, and negotiation completion.
- Uses `socket.c` cleanup/status machinery.
- Uses `pdu.h` SMB Direct negotiate PDU layouts and constants.
- Uses `../common/smb2status.h` for NT status values.

Maintenance notes:
- The code relies on careful ordering between RDMA CM callbacks, CQ callbacks, workqueue processing, and listener queue locking. Changes to statuses around `RDMA_CONNECT_RUNNING`, `NEGOTIATE_NEEDED`, and `NEGOTIATE_RUNNING` need to preserve the early-CQ-completion workaround.
- The accepted child temporarily remains on listener queues while negotiation parses; cleanup paths must continue to remove it and release listener ownership exactly once.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/accept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/connect.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/connect.c

Implements the client-side SMB Direct connection path. It drives RDMA address resolution, route resolution, QP creation, `rdma_connect_locked()`, SMB Direct negotiate request send, negotiate response receive, and final transition to connected state.

Key entry points:
- `smbdirect_connect()` validates that the socket is still `CREATED`, installs the connect RDMA CM handler, and starts address resolution against the destination.
- `smbdirect_connect_resolve_addr()` and `smbdirect_connect_resolve_route()` issue asynchronous RDMA CM resolution calls and set `expected_event`.
- `smbdirect_connect_rdma_connect()` validates FRWR support and optional IB/iWARP restrictions, selects MR type (`IB_MR_TYPE_MEM_REG` or `IB_MR_TYPE_SG_GAPS`), clamps responder resources and FRMR depth to device capabilities, creates the QP, prepares iWARP private data if needed, calls `rdma_connect_locked()`, and starts the RDMA-connect timeout.
- `smbdirect_connect_rdma_event_handler()` advances the RDMA CM state machine through `ADDR_RESOLVED`, `ROUTE_RESOLVED`, and `ESTABLISHED`; on establishment it normalizes peer initiator/responder resources for iWARP versus non-iWARP devices and starts SMB Direct negotiation.
- `smbdirect_connect_negotiate_start()` creates memory pools, initializes send batch/local credits, posts a receive for the negotiate response, sends `struct smbdirect_negotiate_req`, and starts the negotiate timeout.
- `smbdirect_connect_negotiate_recv_done()` queues response parsing in workqueue context after DMA-syncing the receive buffer.
- `smbdirect_connect_negotiate_recv_work()` validates `struct smbdirect_negotiate_resp`, applies negotiated send/receive/read-write limits, creates the client MR list, posts data-transfer receive buffers, and marks negotiation done.
- `smbdirect_connect_sync()` wraps async connect plus `smbdirect_connection_wait_for_connected()`.

Important state and invariants:
- Client status sequence is `CREATED -> RESOLVE_ADDR_NEEDED/RUNNING -> RESOLVE_ROUTE_NEEDED/RUNNING -> RDMA_CONNECT_NEEDED/RUNNING -> NEGOTIATE_NEEDED/RUNNING -> CONNECTED`.
- RDMA CM errors are converted to connection errno values, with device removal mapped to `-ENETDOWN` and rejected events to `-ECONNREFUSED`.
- iWARP reports peer RDMA depths from a different perspective than RoCE/IB in this path; the handler swaps fields before shared resource negotiation.
- The negotiate response must grant nonzero send credits and request nonzero receive credits; size fields must meet SMB Direct minimums and fit the local advertised limits.
- Client-side RDMA read/write registration resources are created only after a successful negotiate response, because `max_read_write_size`, `max_frmr_depth`, and responder resources are negotiated there.

Dependencies:
- Uses `connection.c` for RDMA established handling, QP/mempools, receive posting/refill, send WR posting, MR list creation, and connected wait.
- Uses `socket.c` status/cleanup helpers.
- Uses `pdu.h` negotiate PDU definitions and `../common/smb2status.h` for success status validation.

Maintenance notes:
- Error paths after posting receives intentionally do not free posted receive buffers directly; cleanup relies on QP drain and completion handlers.
- The code assumes the first SMB payload seen after RDMA establishment is a negotiate response. If future versions add pre-negotiation messages, `recv_io.expected` and validation logic must be extended.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/connect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/connection.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/connection.c

Provides the core SMB Direct connected-session machinery: RDMA CM disconnect handling, QP/CQ/PD allocation, send and receive memory pools, credit accounting, keepalive handling, send batching, receive reassembly, and iterator-to-SGE DMA mapping.

Major areas:
- RDMA/QP lifecycle:
  - `smbdirect_connection_rdma_established()` switches the RDMA CM handler to the connected disconnect handler and expects `RDMA_CM_EVENT_DISCONNECTED`.
  - `smbdirect_connection_rdma_event_handler()` handles disconnect/device-removal events, schedules cleanup, and drains the QP.
  - `smbdirect_connection_create_qp()` validates device CQE/QP WR/SGE limits, allocates PD/CQs, accounts for RDMA RW work requests, and creates an RC QP.
  - `smbdirect_connection_destroy_qp()` drains and destroys QP, CQs, and PD.
- Memory pools:
  - `smbdirect_connection_create_mem_pools()` creates per-socket slab/mempool caches for send and receive IO objects and preallocates all receive buffers.
  - `smbdirect_connection_destroy_mem_pools()` returns free receive buffers and destroys pools/caches.
- Receive path:
  - `smbdirect_connection_post_recv_io()` DMA maps a receive buffer and posts an `ib_recv_wr`.
  - `smbdirect_connection_recv_io_done()` validates SMB Direct data-transfer headers, updates keepalive timer, adjusts receive/send credit accounting, handles response-requested keepalives, appends payload buffers to the reassembly queue, and schedules refills.
  - `smbdirect_connection_recv_io_refill()` posts missing receive buffers up to the peer-requested target and records newly available credits to grant.
  - `smbdirect_connection_recvmsg()` copies reassembled SMB payload data into a destination iterator and synthesizes an RFC1002 length header for first-segment 4-byte reads expected by upper layers.
- Send path:
  - `smbdirect_connection_send_single_iter()` waits for batch, local, and peer send credits; grants newly posted receive credits; builds a data-transfer PDU; maps payload iterator segments to SGEs; and posts or batches the send.
  - `smbdirect_connection_send_iter()` consumes the RFC1002 length header from the source iterator, enforces negotiated fragmented send size, sends fragments, flushes the batch, and waits for all pending sends.
  - `smbdirect_connection_send_batch_flush()` chains WRs, optionally turns the first WR into `IB_WR_SEND_WITH_INV`, signals the final WR, and releases the single batch credit.
  - `smbdirect_connection_send_io_done()` frees a signaled send and any sibling send IOs, restores local send credits, decrements pending count, and wakes waiters.
- Keepalive:
  - `smbdirect_connection_idle_timer_work()` converts idle interval expiry into an empty message request and treats pending/sent keepalive timeout as fatal.
  - `smbdirect_connection_send_immediate_work()` sends an empty data-transfer message for keepalive or credit-grant purposes.
- Iterator mapping:
  - `smbdirect_map_sges_from_iter()` supports `ITER_BVEC`, `ITER_KVEC`, and `ITER_FOLIOQ` source iterators, DMA maps page fragments into `ib_sge` entries, advances the iterator, and unmaps partial mappings on failure.

Important state and invariants:
- Receive credits represent posted receive buffers granted to the peer; send credits represent peer-granted permission to send data-transfer PDUs.
- There is exactly one send batch credit, serializing batch construction.
- Local send credits (`lcredits`) limit outstanding `IB_WR_SEND` WRs; they are returned by send completions.
- Reassembly queue updates use barriers: append updates list/queue length before data length; receive-side reads data length before queue metadata.
- `recvmsg()` assumes a single reader consumes from the front of reassembly while completions append at the back.
- Empty data-transfer messages are used both for keepalives and for granting receive credits.
- Iterator-to-SGE mapping does not pin pages; callers must provide iterator types whose backing pages are stable for the RDMA send lifetime.

Dependencies:
- Uses RDMA core verbs, RDMA CM, `rdma_rw_*` helpers, Linux pipe-like iterator primitives, and `folio_queue`.
- Shared structs and status/logging helpers come from `socket.h`/`internal.h`.
- PDU layouts come from `pdu.h`.

Maintenance notes:
- `smbdirect_connection_recvmsg()` contains subtle lockless/front-of-queue assumptions; any move toward multiple concurrent readers would require redesign.
- Send error unwinding restores credits manually; future changes to the credit model must audit all `goto` labels in `smbdirect_connection_send_single_iter()`.
- `ITER_FOLIOQ` mapping maps from `folio_page(folio, 0)` with an offset; changes to large-folio assumptions should be checked carefully.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/connection.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/debug.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/debug.c

Provides a legacy proc/debug reporting helper for SMB Direct connection state.

Key entry point:
- `smbdirect_connection_legacy_debug_proc_show()` emits human-readable state into a `seq_file`.

Reported data:
- SMB Direct protocol version and transport status.
- Negotiated receive credit max, send credit target, max send/receive sizes, fragmented send/receive sizes.
- Keepalive interval, max RDMA read/write size, and caller-supplied RDMA read/write threshold.
- Receive buffer get/put counters, empty-send counter, reassembly enqueue/dequeue counters, reassembly data length and queue length.
- Current send and receive credits, receive credit target, pending send count.
- MR responder resources, FRMR depth, MR type, ready MR count, and used MR count.

Dependencies:
- Reads `struct smbdirect_socket` fields defined in `socket.h`.
- Uses `seq_file` output and is exported with `EXPORT_SYMBOL_GPL`.

Maintenance notes:
- This is observational only and does not lock around counters/queue lengths; values are snapshots suitable for diagnostics, not strict consistency checks.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/devices.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/devices.c

Tracks RDMA-capable IB devices usable for SMB Direct and provides netdev-to-RDMA-capability discovery.

Key functions:
- `smbdirect_ib_device_rdma_capable_node_type()` accepts only devices with FRWR support and node type `RDMA_NODE_IB_CA` or `RDMA_NODE_RNIC`.
- `smbdirect_ib_client_add()` logs device capabilities, logs per-port protocol support, allocates a `smbdirect_device`, copies the IB device name, and adds it to the global device list.
- `smbdirect_ib_client_remove()` removes matching tracked devices and frees their records.
- `smbdirect_ib_client_rename()` updates the cached device name for diagnostic logging.
- `smbdirect_netdev_find_rdma_capable_node_type()` searches tracked devices and ports for a matching netdev via `ib_device_get_netdev()`, then falls back to `ib_device_get_by_netdev()`.
- `smbdirect_netdev_rdma_capable_node_type()` checks the given netdev, bridge/VLAN lower devices, and IPoIB type to return `RDMA_NODE_RNIC`, `RDMA_NODE_IB_CA`, or `RDMA_NODE_UNSPECIFIED`.
- `smbdirect_devices_init()` initializes the global device list lock and registers the IB client.
- `smbdirect_devices_exit()` frees tracked device records and unregisters the IB client.

Important state:
- Uses `smbdirect_globals.devices.list` protected by `rwlock_t`.
- Device records keep both `ib_dev` and a cached `ib_name` so removals/renames can log stable names.

Dependencies:
- Requires `smbdirect_frwr_is_supported()` from `socket.c`.
- Uses RDMA device, port, and netdev lookup APIs.
- Exported capability lookup is `smbdirect_netdev_rdma_capable_node_type()`.

Maintenance notes:
- Netdev lookup correctly drops references from `ib_device_get_netdev()` with `dev_put()`.
- Exit deliberately clears the list before `ib_unregister_client()` so normal remove callbacks do not produce removal logs during module unload.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/devices.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/internal.h -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/internal.h

Internal umbrella header for the SMB Direct subsystem. It sets the default symbol namespace, logging prefix, global module state, internal device record type, and cross-file function prototypes.

Contents:
- Defines `DEFAULT_SYMBOL_NAMESPACE "SMBDIRECT"` and `pr_fmt`.
- Includes public `<linux/smbdirect.h>` and local `pdu.h`, then includes `socket.h` after declaring global state.
- Defines `struct smbdirect_module_state` with a mutex, six workqueues (`accept`, `connect`, `idle`, `refill`, `immediate`, `cleanup`), and the global RDMA device list.
- Declares `extern struct smbdirect_module_state smbdirect_globals`.
- Defines `struct smbdirect_device` for tracked IB devices.
- Declares internal socket initialization, cleanup scheduling, QP/mempool, send/recv, reassembly, negotiation, MR-list, accept, and device init/exit functions.
- Provides cleanup scheduling macros:
  - `smbdirect_socket_schedule_cleanup()`
  - `smbdirect_socket_schedule_cleanup_lvl()`
  - `smbdirect_socket_schedule_cleanup_status()`

Important role:
- This header is the dependency hub for all `fs/smb/smbdirect/*.c` files. It keeps implementation-private lifecycle APIs out of the public SMB Direct header while making them available across subsystem compilation units.

Maintenance notes:
- Because `socket.h` depends on `smbdirect_globals`, the include order in this file is intentional.
- Cleanup scheduling macros capture caller function and line; preserving that behavior is useful for debugging asynchronous disconnects.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/listen.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/listen.c

Implements the listener-side RDMA CM accept front-end. It binds an SMB Direct socket into listening mode, receives RDMA connect requests, validates device/protocol/backlog constraints, creates accepting child sockets, and hands them to `accept.c` for RDMA accept and SMB Direct negotiation.

Key entry points:
- `smbdirect_socket_listen()` validates backlog and socket state, switches status to `LISTENING`, installs `smbdirect_listen_rdma_event_handler()`, sets expected event to `RDMA_CM_EVENT_CONNECT_REQUEST`, and calls `rdma_listen()`.
- `smbdirect_listen_rdma_event_handler()` handles RDMA CM events for the listening CM ID. On connect requests it detaches the new CM ID from the listener context before processing and delegates to `smbdirect_listen_connect_request()`.
- `smbdirect_listen_connect_request()` validates FRWR support and optional IB/iWARP restrictions, checks pending plus ready child counts against backlog, creates an accepting socket around the new RDMA CM ID, copies listener logging/parameters/kernel settings, adds the child to the listener pending queue, and calls `smbdirect_accept_connect_request()`.

Important state and invariants:
- `listen.backlog == -1` means the socket was never a listener; valid listener backlog is always positive.
- Listener child sockets move from `listen.pending` to `listen.ready` in `accept.c` after SMB Direct negotiate request parsing succeeds.
- Backlog accounting considers both pending and ready children.
- On failure before ownership transfer is complete, the new RDMA CM ID is left for the caller/RDMA core to destroy; the child socket clears `ib.dev` and `rdma.cm_id` before release in that path.
- The temporary `smbdirect_new_rdma_event_handler()` is a guard that should never perform real work; it catches unexpected events before the accepting socket installs its handler.

Dependencies:
- Uses `socket.c` creation/configuration/release helpers.
- Uses `accept.c` for server-side connection acceptance and negotiation.
- Uses `devices/socket.c` FRWR and protocol checks.

Maintenance notes:
- The listener RDMA handler runs under the RDMA CM handler mutex and assumes it may sleep; this matters because child socket setup can allocate memory.
- The backlog check currently uses `>` rather than `>=`, allowing exactly backlog plus possibly one depending on combined counts; preserve or revisit deliberately if changing accept queue semantics.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/listen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/main.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/main.c

Module initialization and teardown for the SMB Direct subsystem.

Key behavior:
- Defines global `smbdirect_globals` with an initialized mutex.
- `smbdirect_module_init()` allocates six named workqueues:
  - `smbdirect-accept`
  - `smbdirect-connect`
  - `smbdirect-idle`
  - `smbdirect-refill`
  - `smbdirect-immediate`
  - `smbdirect-cleanup`
- The refill and immediate queues are high priority; cleanup is high priority and `WQ_MEM_RECLAIM`.
- After workqueues are allocated, it calls `smbdirect_devices_init()` to register the RDMA IB client.
- Failure unwinds already-created workqueues in reverse order and returns the allocation/init error.
- `smbdirect_module_exit()` unregisters devices and destroys all workqueues.

Dependencies:
- Device registration lives in `devices.c`.
- Workqueue pointers are copied into each socket during `smbdirect_socket_init()` in `socket.h`.

Maintenance notes:
- The global mutex serializes module init/exit workqueue and device-list setup.
- Any new per-socket async path should either reuse one of these workqueues or be added here with matching reverse-order failure cleanup.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/mr.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/mr.c

Implements client-side memory registration objects used for SMB Direct RDMA read/write buffer descriptors.

Key functions:
- `smbdirect_connection_create_mr_list()` allocates `responder_resources * 2` MR objects, each with an `ib_mr` and scatterlist sized to `max_frmr_depth`, marks them ready, and increments the ready count.
- `smbdirect_connection_destroy_mr_list()` detaches all MRs from the socket list, disables each MR, clears socket ownership, and drops references safely under each MR mutex.
- `smbdirect_connection_get_mr_io()` waits for a ready MR while connected, marks it registered, takes a reference, decrements ready count, and increments used count.
- `smbdirect_connection_register_mr_io()` validates iterator page count, extracts iterator pages into an SG table, DMA maps the SG list, maps it into the MR, updates the rkey, posts `IB_WR_REG_MR`, and returns the MR to the caller for descriptor publication.
- `smbdirect_mr_io_fill_buffer_descriptor()` fills an SMB Direct buffer descriptor with MR iova/rkey/length when registered, or sentinel invalid values otherwise.
- `smbdirect_connection_deregister_mr_io()` locally invalidates when required, waits for invalidation completion, DMA-unmaps the SG list, returns the MR to ready state, wakes waiters, decrements used count, and drops the caller reference.

Important state and invariants:
- MR states are `READY`, `REGISTERED`, `INVALIDATED`, `ERROR`, and `DISABLED`.
- Each MR has a mutex plus kref. The connection owns one reference; active registrations take another.
- Destruction can detach an MR from the connection while a registration user still holds a reference; final free occurs only after disable and kref release.
- Local invalidation uses `IB_WR_LOCAL_INV`; remote invalidation paths can set the MR invalidated without posting local invalidation.
- `register_mr_io()` posts the registration WR but does not wait for its completion; ordering is relied on before later sends that expose the descriptor.

Dependencies:
- Uses iterator-to-SG extraction, RDMA MR APIs, DMA SG mapping, and `smbdirect_socket_schedule_cleanup()` for fatal registration/invalidation failures.
- Buffer descriptor type comes from public SMB Direct definitions.

Maintenance notes:
- Error handling must preserve kref/mutex discipline; `smbdirect_mr_io_free_locked()` expects the mutex held and may unlock/free the MR.
- `smbdirect_iter_to_sgt()` depends on `extract_iter_to_sg()` to hold or pin pages appropriately for the iterator type supplied by upper layers.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/mr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/pdu.h -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/pdu.h

Defines local SMB Direct protocol constants and packed wire-format PDUs used by the SMB Direct implementation.

Contents:
- `SMBDIRECT_V1` protocol version constant.
- Minimum receive and fragmented sizes from MS-SMBD:
  - `SMBDIRECT_MIN_RECEIVE_SIZE`
  - `SMBDIRECT_MIN_FRAGMENTED_SIZE`
- Packed negotiate request:
  - `struct smbdirect_negotiate_req`
  - fields for min/max version, credits requested, preferred send size, max receive size, and max fragmented size.
- Packed negotiate response:
  - `struct smbdirect_negotiate_resp`
  - fields for version range, negotiated version, credits requested/granted, NT status, max read/write size, preferred send size, max receive size, and max fragmented size.
- Data-transfer constants:
  - `SMBDIRECT_DATA_MIN_HDR_SIZE`
  - `SMBDIRECT_DATA_OFFSET`
  - `SMBDIRECT_FLAG_RESPONSE_REQUESTED`
- Packed data-transfer PDU:
  - `struct smbdirect_data_transfer`
  - fields for credits, flags, remaining data length, data offset, data length, padding, and variable payload.

Usage:
- `accept.c` and `connect.c` use negotiate PDUs.
- `connection.c` uses data-transfer PDUs for send/receive, fragmentation, credit grants, and keepalive response requests.

Maintenance notes:
- All multibyte fields are little-endian wire fields and are converted at use sites.
- Structs are `__packed`; any protocol extension should preserve explicit endian types and avoid implicit padding.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/rw.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/rw.c

Implements server-side RDMA read/write transfer execution against peer-provided SMB Direct buffer descriptors.

Key functions:
- `smbdirect_connection_wait_for_rw_credits()` consumes RDMA RW credits using the generic socket credit waiter.
- `smbdirect_connection_calc_rw_credits()` computes required RW credits from local buffer page count and negotiated pages-per-credit.
- `smbdirect_connection_rdma_get_sg_list()` converts a kernel/vmalloc buffer into a scatterlist by walking pages.
- `smbdirect_connection_rw_io_free()` destroys the `rdma_rw_ctx`, frees chained SG tables, and frees the flexible IO object.
- `smbdirect_connection_rdma_xmit()` is the exported main operation. It validates connected state and max read/write size, walks buffer descriptors, clamps descriptor lengths to remaining buffer length, computes credits, waits for credits, builds one `smbdirect_rw_io` and `rdma_rw_ctx` per descriptor, chains WRs in reverse order, posts them, waits for completion, frees all contexts, restores credits, and returns completion error status.

Direction semantics:
- `is_read == true` uses `DMA_FROM_DEVICE` and RDMA read completion callback.
- `is_read == false` uses `DMA_TO_DEVICE` and RDMA write completion callback.
- Completion errors set `msg->error = -EIO`; non-flush failures schedule socket cleanup.

Important state:
- `rw_io.credits.count` limits concurrent RDMA RW contexts.
- Credits are always returned after the operation’s cleanup path.
- The function mutates descriptor lengths if a descriptor extends beyond the remaining requested buffer length.

Dependencies:
- Uses RDMA core `rdma_rw_ctx_*` helpers.
- Uses public `struct smbdirect_buffer_descriptor_v1`.
- Uses `smbdirect_get_buf_page_count()` from `socket.h`.

Maintenance notes:
- The log message after descriptor walking prints `buf_len` after it has been consumed down, which may be zero rather than original length.
- The implementation waits for one stack completion after posting the chained WR list and then reads the last message error; changes to multiple completion behavior should verify all contexts complete before free.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/rw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/socket.c -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/socket.c

Owns SMB Direct socket creation, initial parameter validation, logging setup, cleanup scheduling, synchronous destruction, bind/shutdown/release, and a generic credit wait helper.

Key functions:
- `smbdirect_frwr_is_supported()` checks RDMA device FRWR capability by requiring memory management extensions and nonzero fast-registration page-list length.
- `smbdirect_socket_init_new()` initializes a new active socket and creates an RDMA CM ID.
- `smbdirect_socket_create_kern()` allocates and initializes a standalone socket with normal destroy kref.
- `smbdirect_socket_init_accepting()` initializes a socket around an accepted RDMA CM ID and sets device/context fields.
- `smbdirect_socket_create_accepting()` allocates such an accepting socket.
- `smbdirect_socket_set_initial_parameters()` validates flags, depth/resource values, optional IB/iWARP restrictions, and copies caller parameters.
- `smbdirect_socket_set_kernel_settings()` sets IB poll context and GFP masks for send/recv/RW allocations.
- `smbdirect_socket_set_logging()` installs frontend logging callbacks.
- `__smbdirect_socket_schedule_cleanup()` records the first error, disables non-cleanup work, recursively schedules cleanup for listener children, maps current status to the appropriate failure/disconnect status, wakes all wait queues, and queues cleanup work.
- `smbdirect_socket_cleanup_work()` performs asynchronous disconnect state progression and calls `rdma_disconnect()` when needed.
- `smbdirect_socket_destroy()` performs final teardown: disables work, drains QP, releases pending listener children, drains receive reassembly queue, destroys MR list, QP, RDMA CM ID, and memory pools, then marks destroyed.
- `smbdirect_socket_destroy_sync()` forces cleanup, waits for disconnected state if needed, and calls final destroy.
- `smbdirect_socket_bind()`, `smbdirect_socket_shutdown()`, and `smbdirect_socket_release()` provide exported lifecycle operations.
- `smbdirect_socket_wait_for_credits()` atomically consumes credits or sleeps until credits/status changes.

Important state and invariants:
- `first_error` is sticky and drives wakeups and later API failures.
- Cleanup wakes every wait queue: status, listener accept, send credits, pending sends, receive reassembly, RW credits, and MR readiness.
- There are two krefs:
  - `disconnect` represents frontend ownership and triggers synchronous disconnect/destroy at zero.
  - `destroy` represents backend memory lifetime and may be `REFCOUNT_MAX` for embedded sockets.
- `smbdirect_socket_release()` expects exactly one disconnect reference; violating that is treated as a bug.
- RDMA CM handler locking coordinates `rdma_disconnect()`, QP drain, and RDMA event callbacks.

Dependencies:
- Uses all other SMB Direct teardown helpers from `connection.c` and `mr.c`.
- Exports public socket setup/lifecycle symbols.

Maintenance notes:
- Cleanup and destroy paths are intentionally conservative and wake waiters repeatedly. New wait queues or async work items must be added to both wake/disable paths.
- `smbdirect_socket_wait_for_credits()` subtracts optimistically then adds back before sleeping; callers must restore any higher-level credits on later failures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/socket.h -->
# File Research: sources/os/linux/linux/fs/smb/smbdirect/socket.h

Defines the central SMB Direct socket state object, status enums, logging macros, IO object structs, initialization helper, and small utility functions.

Major contents:
- `enum smbdirect_socket_status` covers lifecycle from `CREATED` through address/route/connect/negotiate states, `CONNECTED`, error/disconnecting/disconnected, and `DESTROYED`.
- `smbdirect_socket_status_string()` converts statuses to diagnostics.
- `SMBDIRECT_DEBUG_ERR_PTR()` safely formats errno values including zero.
- `enum smbdirect_keepalive_status` tracks none/pending/sent keepalive state.
- `struct smbdirect_socket` contains:
  - status and first error.
  - global workqueue pointers and disconnect work.
  - disconnect/destroy krefs.
  - RDMA CM state and expected event.
  - IB PD/CQ/QP/device state.
  - negotiated parameters.
  - connect work/lock.
  - idle keepalive work and timer.
  - listener pending/ready queues and accept-child linkage.
  - send IO pools and batch/local/remote/pending credit counters.
  - receive IO pools, expected PDU type, free list, posted count, receive credits, and reassembly queue.
  - MR lists and ready/used counts.
  - server-side RDMA RW credit state.
  - debug counters and logging callbacks.
- Disabled default work/logging callbacks warn if invoked before proper setup.
- Logging macros route categories such as outgoing, incoming, read, write, RDMA send/recv/event/MR/RW, keepalive, and negotiate through frontend-provided callbacks.
- `smbdirect_socket_init()` zeroes the socket, initializes wait queues/locks/lists/krefs/work items, copies global workqueue pointers, sets default RDMA expected event and poll context, initializes credit counters, and installs disabled logging callbacks.
- Status-check macros centralize expected-state validation and optional cleanup scheduling.
- IO structs:
  - `struct smbdirect_send_io`
  - `struct smbdirect_send_batch`
  - `struct smbdirect_recv_io`
  - `struct smbdirect_mr_io`
  - `struct smbdirect_rw_io`
- `smbdirect_get_buf_page_count()` computes the number of pages spanned by an arbitrary buffer.

Important invariants:
- `SMBDIRECT_SOCKET_CREATED` must remain zero because `smbdirect_socket_init()` relies on `memset()`.
- Work items are initialized to disabled warning callbacks until the appropriate path installs real handlers.
- Send IO supports up to six SGEs: one protocol header plus mapped payload fragments.
- Receive IO currently uses a single SGE covering one large receive buffer.
- The MR kref model allows up to two references: connection ownership and active registration ownership.

Dependencies:
- Includes RDMA RW headers and public SMB Direct parameter/log definitions via `internal.h`.

Maintenance notes:
- This header encodes most subsystem ownership rules. Adding fields usually requires updates in `smbdirect_socket_init()`, cleanup wakeups, destroy paths, and debug reporting.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/smb/smbdirect/socket.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/splice.c -->
# File Research: sources/os/linux/linux/fs/splice.c

Implements Linux VFS splice, vmsplice, tee, direct splice, and pipe-buffer helper machinery. It moves data between files, pipes, sockets, and user iterators using pipe buffers as the central transport abstraction, with zero-copy where possible and fallback copying where required.

Major areas:
- Pipe buffer operations:
  - `page_cache_pipe_buf_ops` supports page-cache buffers with confirm, release, steal, and get operations.
  - `page_cache_pipe_buf_try_steal()` locks the folio, waits for writeback, releases filesystem-private state, removes the folio from mapping, and marks it LRU when stealing succeeds.
  - `page_cache_pipe_buf_confirm()` validates page-cache data is uptodate and handles truncated/unhashed folios with `-ENODATA`.
  - `user_page_pipe_buf_ops` allows stealing only gifted user pages.
  - `default_pipe_buf_ops` and `nosteal_pipe_buf_ops` cover generic and socket-like buffers.
- Filling pipes:
  - `splice_to_pipe()` inserts a `splice_pipe_desc` page array into a pipe and releases unused pages.
  - `add_to_pipe()` appends one `pipe_buffer` or releases it on `EPIPE`/`EAGAIN`.
  - `splice_grow_spd()` and `splice_shrink_spd()` size temporary page/partial arrays to pipe capacity.
  - `copy_splice_read()` allocates pages, reads through `->read_iter()`, and inserts copied pages into a pipe; used for O_DIRECT and DAX sources.
- Draining pipes:
  - `splice_from_pipe_feed()`, `splice_from_pipe_next()`, `splice_from_pipe_begin()`, and `splice_from_pipe_end()` implement the generic pipe-to-actor loop with signal, nonblock, EOF, wakeup, and buffer-release handling.
  - `__splice_from_pipe()` exports the unlocked generic loop.
  - `splice_from_pipe()` wraps it with pipe locking.
  - `iter_file_splice_write()` writes pipe buffers to files through `->write_iter()` using bvec iterators.
  - `splice_to_socket()` sends pipe pages to sockets with `MSG_SPLICE_PAGES` when `CONFIG_NET` is enabled.
- File and direct splice:
  - `do_splice_read()` validates read mode, clamps length to pipe space and `MAX_RW_COUNT`, selects `copy_splice_read()` for O_DIRECT/DAX, otherwise calls file `->splice_read`.
  - `vfs_splice_read()` performs `rw_verify_area()` then `do_splice_read()`.
  - `splice_direct_to_actor()` implements sendfile/direct copy through a per-task cached internal pipe.
  - `do_splice_direct()` supports sendfile-style file-to-file transfer and wraps output writes in `file_start_write()`.
  - `splice_file_range()` provides the copy-file-range helper variant where the caller already started the write.
- `splice(2)` syscall:
  - `do_splice()` dispatches pipe-to-pipe, pipe-to-file, file-to-pipe, or invalid non-pipe/non-pipe cases; handles offsets, `FMODE_PREAD/PWRITE`, append rejection, `rw_verify_area()`, nonblock propagation, write accounting, f_pos updates, and fsnotify events.
  - `__do_splice()` copies user offsets in/out, rejects offsets on pipe ends, clears `FMODE_NOWAIT` on pipe files, and calls `do_splice()`.
  - `SYSCALL_DEFINE6(splice)` validates flags, fds, zero length, and delegates to `__do_splice()`.
- `vmsplice(2)`:
  - `iter_to_pipe()` pins/imports user iterator pages in chunks, creates user-page pipe buffers, and supports `SPLICE_F_GIFT`.
  - `vmsplice_to_pipe()` waits for pipe space, maps user pages into the pipe, wakes readers, and sends modify notification.
  - `vmsplice_to_user()` copies pipe data to a user iterator via `pipe_to_user()`; reverse vmsplice is implemented as copying rather than VM remapping.
  - `SYSCALL_DEFINE4(vmsplice)` imports user iovecs as source or destination depending on file mode and dispatches accordingly.
- Pipe-to-pipe and tee:
  - `ipipe_prep()` and `opipe_prep()` wait for readable input and writable output with signal/nonblock handling.
  - `splice_pipe_to_pipe()` moves or partially copies pipe buffers between two pipes, avoiding ABBA deadlock with `pipe_double_lock()`, clearing gifted/merge flags for partial references, and waking readers/writers.
  - `link_pipe()` duplicates pipe buffer references without consuming input, used by tee.
  - `do_tee()` validates pipe endpoints and duplicates pipe contents with fsnotify events.
  - `SYSCALL_DEFINE4(tee)` validates flags/fds/length and calls `do_tee()`.

Important invariants:
- Pipe locks protect head/tail manipulation; pipe-to-pipe paths use address-ordered double locking to avoid deadlocks.
- `splice_direct_to_actor()` must drain its internal pipe before returning; output side is forced blocking even if input nonblock is requested.
- Offsets are invalid for pipe ends and require seek-capable file modes for regular files.
- `O_APPEND` outputs are rejected for splice-to-file/direct splice because explicit offsets and append semantics conflict.
- `pipe_clear_nowait()` strips `FMODE_NOWAIT` from pipe file modes because splice itself does not support NOWAIT semantics.
- Partial pipe-buffer duplication clears `PIPE_BUF_FLAG_GIFT` and `PIPE_BUF_FLAG_CAN_MERGE` to avoid multiple steals or unsafe merging.
- `-ENODATA` from confirming a truncated page-cache buffer is treated as zero-byte progress/EOF-like behavior in splice feed paths.

Exported symbols include:
- `splice_to_pipe()`
- `add_to_pipe()`
- `copy_splice_read()`
- `default_pipe_buf_ops`
- `nosteal_pipe_buf_ops`
- `__splice_from_pipe()`
- `iter_file_splice_write()`
- `vfs_splice_read()`
- `splice_direct_to_actor()`
- `do_splice_direct()`
- `splice_file_range()`

Maintenance notes:
- This file is central VFS code with many subtle user-visible errno, blocking, signal, and notification semantics. Changes should be checked against splice/vmsplice/tee syscall behavior, pipe wakeups, and file position update rules.
- Page stealing is filesystem-sensitive; the writeback wait and `filemap_release_folio()`/`remove_mapping()` sequence protects against corruption when removing page-cache folios.
- `copy_splice_read()` maps `-EFAULT` from `read_iter()` to `-EAGAIN` to satisfy splice caller expectations when no pipe data could be produced.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/splice.c -->