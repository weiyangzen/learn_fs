# Group Research: group_1084_linux_stable_sources_os_linux_linux_stable_fs_smb_smbdirect_accept__c2142d131303

Scope: `Docs/research_subset_a.md` includes `sources/os/linux/linux-stable`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/accept.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/accept.c

## Purpose
Server-side SMBDirect accept and negotiation path. It converts an RDMA CM connect request into a `struct smbdirect_socket`, accepts the RDMA connection, receives the client's SMBDirect negotiate request, and sends the negotiate response only after the listener accepts the socket.

## Main Flow
- `smbdirect_accept_connect_request()` initializes server-side RDMA resources for an incoming request:
  - clamps `initiator_depth` to device capability
  - negotiates iWARP/IRD/ORD values through `smbdirect_connection_negotiate_rdma_resources()`
  - validates send SGE limits and initializes credits in `smbdirect_accept_init_params()`
  - creates QP and send/recv memory pools
  - posts one receive buffer for `SMBDIRECT_EXPECT_NEGOTIATE_REQ`
  - calls `rdma_accept()` with RC connection parameters
  - starts the negotiate timeout timer
- `smbdirect_accept_negotiate_recv_done()` handles the receive completion for the negotiate request, DMA-syncs it, appends valid request buffers to the reassembly queue, and schedules work.
- `smbdirect_accept_negotiate_recv_work()` validates the request:
  - version range must include `SMBDIRECT_V1`
  - `credits_requested` must be nonzero
  - peer receive and fragmented sizes must meet SMBDirect minima
  - local `max_recv_size`, fragmented receive size, send size, fragmented send size, and receive credit target are adjusted from peer values
- If the socket still has a listener, it is moved from listener `pending` to `ready` and the listener waitqueue is woken. A success response is deliberately deferred until `smbdirect_socket_accept()`.
- `smbdirect_socket_accept()` waits for a ready socket, detaches it from the listener, marks it connected for the caller, and then calls `smbdirect_accept_negotiate_finish(nsc, 0)` to grant credits and send the negotiate response.
- `smbdirect_accept_negotiate_finish()` posts receive buffers for data-transfer PDUs, grants receive credits, builds a negotiate response, maps it for DMA, and posts an RDMA SEND.
- `smbdirect_accept_negotiate_send_done()` frees the send buffer, decrements pending sends, disconnects on failed/non-success NT status, otherwise calls `smbdirect_connection_negotiation_done()`.

## RDMA Event Handling
- `smbdirect_accept_rdma_event_handler()` expects `RDMA_CM_EVENT_ESTABLISHED`.
- On established:
  - calls `smbdirect_connection_rdma_established()`
  - transitions to `SMBDIRECT_SOCKET_NEGOTIATE_NEEDED`
  - queues negotiation work if the receive completion already arrived
- Error, reject, device removal, or unexpected events schedule centralized cleanup.

## Important Semantics
- A passive connection can finish low-level RDMA establishment before the negotiate receive completion, or vice versa. The code explicitly handles both ordering possibilities.
- Successful negotiate response is withheld until upper layer accept, preventing credit grant to an unaccepted connection.
- Unsupported SMBDirect version sends a negotiate response with `STATUS_NOT_SUPPORTED`; malformed sizes/credits abort the transport.
- `accept.c` depends heavily on `connection.c` for QP, memory pools, receive refill, send posting, and final connected transition.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/accept.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/connect.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/connect.c

## Purpose
Client-side SMBDirect connection establishment. It drives RDMA address resolution, route resolution, RDMA connect, SMBDirect negotiate request/response exchange, and synchronous wait helper.

## Main Flow
- `smbdirect_connect()` validates a newly created socket, captures any bound source address, installs the connect RDMA event handler, and starts `rdma_resolve_addr()`.
- `smbdirect_connect_rdma_event_handler()` advances the state machine:
  - `ADDR_RESOLVED` -> `smbdirect_connect_resolve_route()`
  - `ROUTE_RESOLVED` -> `smbdirect_connect_rdma_connect()`
  - `ESTABLISHED` -> RDMA resource negotiation and SMBDirect negotiate start
- `smbdirect_connect_rdma_connect()`:
  - checks FRWR support
  - enforces optional IB-only or iWARP-only flags
  - selects MR type (`IB_MR_TYPE_SG_GAPS` when supported, otherwise `IB_MR_TYPE_MEM_REG`)
  - clamps `max_frmr_depth` and responder resources to device limits
  - creates QP
  - sends legacy IRD/ORD private data for iWARP
  - calls `rdma_connect_locked()`
  - starts a connect timeout timer
- `smbdirect_connect_negotiate_start()`:
  - creates send/recv memory pools
  - initializes batch/local send credits
  - posts one receive buffer for the negotiate response
  - allocates a send buffer containing `struct smbdirect_negotiate_req`
  - fills version, credit request, send size, receive size, and fragmented receive size
  - DMA maps and sends the request
  - starts negotiate timeout
- `smbdirect_connect_negotiate_recv_done()` handles the response receive completion, syncs DMA, stores valid responses in the reassembly queue, and schedules work.
- `smbdirect_connect_negotiate_recv_work()` validates response fields:
  - negotiated version must be `SMBDIRECT_V1`
  - NT status must be success
  - peer receive and fragmented sizes must meet SMBDirect minima
  - both requested and granted credits must be nonzero
  - peer preferred send size must fit local receive size
  - resulting max read/write size must be at least one page
- After validation it updates local negotiated parameters, creates the MR list, switches receive buffers to data-transfer completion handling, refills receive buffers, and calls `smbdirect_connection_negotiation_done()`.
- `smbdirect_connect_sync()` wraps `smbdirect_connect()` and `smbdirect_connection_wait_for_connected()`.

## iWARP Handling
- iWARP reports peer initiator/responder values from a different perspective than non-iWARP transports. The established event path swaps values before negotiation.
- Legacy iWARP private data is passed to shared resource negotiation.

## Error Handling
- Any unexpected RDMA event/status maps to transport errors such as `-ECONNREFUSED`, `-ENETDOWN`, or event status, then schedules cleanup.
- `-ENODEV` logging is downgraded to info in synchronous wait paths.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/connect.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/connection.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/connection.c

## Purpose
Core SMBDirect connection engine shared by client and server. It manages QP/CQ/PD lifecycle, negotiated connected transition, send/receive credits, SMBDirect data-transfer PDUs, keepalive, receive reassembly, send batching, and iterator-to-SGE DMA mapping.

## RDMA/QP Lifecycle
- `smbdirect_connection_qp_event_handler()` schedules cleanup on fatal QP/CQ events.
- `smbdirect_connection_rdma_event_handler()` is installed after RDMA establishment and expects `RDMA_CM_EVENT_DISCONNECTED`. It handles normal disconnect and device removal by forcing status toward `DISCONNECTED` and draining the QP.
- `smbdirect_connection_rdma_established()` logs local/remote endpoints, installs the steady-state event handler, and changes expected CM event to disconnect.
- `smbdirect_connection_negotiation_done()` transitions from negotiating to connected, initializes receive-refill and immediate-send work handlers, and wakes waiters.
- `smbdirect_connection_create_qp()` computes QP capacity from send credits, receive credits, responder resources, and RDMA RW context needs, validates device CQ/WR/SGE limits, allocates PD/CQs, and creates an RC QP.
- `smbdirect_connection_destroy_qp()` drains and destroys QP, CQs, and PD.

## Memory Pools
- `smbdirect_connection_create_mem_pools()` creates per-socket slab caches/mempools for:
  - send I/O objects sized to include a negotiate response-sized packet area
  - receive I/O objects sized to include `max_recv_size` user-exposable receive buffer
- It preallocates `recv_credit_max` receive buffers into the free list.
- `smbdirect_connection_destroy_mem_pools()` frees free-list receive buffers and destroys pools/caches.

## Receive Buffer Management
- `smbdirect_connection_get_recv_io()` pops from the free list unless the socket has an error.
- `smbdirect_connection_put_recv_io()` DMA-unmaps a posted receive buffer if needed, returns it to the free list, updates statistics, and queues refill work.
- `smbdirect_connection_post_recv_io()` DMA maps the receive packet area and posts one receive WR.
- `smbdirect_connection_recv_io_refill()` posts enough receive buffers to satisfy the peer's current requested target, records newly available credits, and returns the number of buffers posted.
- `smbdirect_connection_recv_io_refill_work()` can schedule an empty immediate send so newly available credits are advertised to the peer.

## Credit Handling
- `smbdirect_connection_grant_recv_credits()` moves posted receive availability into granted receive credits up to the current peer-requested target.
- Send path has three credit concepts:
  - batch credit: serializes a send batch
  - local credits: available local send WR capacity
  - remote send credits: peer-granted ability to send data-transfer PDUs
- `smbdirect_socket_wait_for_credits()` from `socket.c` underpins these waits.

## Send Path
- `smbdirect_connection_send_single_iter()` builds one SMBDirect data-transfer PDU:
  - validates connected state and iterator direction
  - waits for batch/local/remote send credits
  - optionally grants receive credits
  - allocates a send buffer
  - maps header and payload SGEs
  - sets `credits_requested`, `credits_granted`, flags, offsets, lengths, and remaining length
  - optionally sets `SMBDIRECT_FLAG_RESPONSE_REQUESTED` for keepalive
  - posts immediately or appends to a batch
- `smbdirect_connection_send_iter()` expects an RFC1002-style 4-byte length prefix, validates fragmented send size, sends fragments through a batch, flushes the batch, and waits for pending sends to drain.
- `smbdirect_connection_send_batch_flush()` chains WRs, optionally converts the first to `IB_WR_SEND_WITH_INV`, signals the last WR, and posts the chain.
- `smbdirect_connection_send_io_done()` frees sibling send buffers and the signaled buffer, restores local credits, wakes waiters, and schedules cleanup on failed completions.
- `smbdirect_connection_send_immediate_work()` sends an empty data-transfer PDU for keepalive/credit advertisement.

## Receive/Reassembly Path
- `smbdirect_connection_recv_io_done()` parses incoming data-transfer PDUs:
  - validates completion opcode/status
  - refreshes keepalive timer
  - validates minimal header length, data offset alignment, bounds, and fragmented receive size
  - updates peer requested credits and locally usable send credits from `credits_granted`
  - handles response-requested keepalive flag
  - tracks first segment and full-packet state
  - queues payload buffers on the reassembly list or returns empty buffers
- `smbdirect_connection_reassembly_append_recv_io()` appends buffers and updates `data_length` after a write barrier so lockless readers can observe consistent queue metadata.
- `smbdirect_connection_recvmsg()` copies reassembled payload to a destination `msghdr` iterator:
  - returns a synthetic RFC1002 length when upper layer asks for 4 bytes at the first segment
  - copies partial or full segments
  - returns consumed buffers to the free list
  - waits interruptibly for enough data when needed

## Keepalive
- `smbdirect_connection_idle_timer_work()` treats pending/sent keepalive as timeout, otherwise schedules a response-requested empty message.
- Incoming data resets keepalive state and reschedules the interval timer.
- Empty sends are also used to advertise receive credits without payload.

## Iterator Mapping
- `smbdirect_map_sges_from_iter()` supports `ITER_BVEC`, `ITER_KVEC`, and `ITER_FOLIOQ` sources.
- `smbdirect_map_sges_from_bvec()`, `_kvec()`, and `_folioq()` map pages into IB SGEs without pinning/refcounting; callers must ensure iterator backing lifetime.
- On mapping failure, newly mapped SGEs are unmapped before returning.

## Public Exports
Exports connected-state helpers, wait helper, batch flush/init, send helpers, recvmsg, and lower-level send-wait functions through GPL symbols where marked.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/connection.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/debug.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/debug.c

## Purpose
Legacy debug/proc reporting for SMBDirect connections.

## Main Function
- `smbdirect_connection_legacy_debug_proc_show()` writes connection state and counters into a `seq_file`.
- Reports:
  - protocol version and socket status
  - receive credit max, send credit target, max send/receive sizes
  - fragmented send/receive sizes
  - keepalive interval, max RDMA read/write size, caller-provided RDMA threshold
  - receive buffer get/put counters and empty-send counter
  - reassembly enqueue/dequeue counters and current queue state
  - current send/receive credits and pending sends
  - responder resources, FRMR depth, MR type
  - MR ready/used counts

## Notes
- Null socket input returns without output.
- It reads live atomics and counters without locking; this is diagnostic output, not a synchronization boundary.
- Exported as `smbdirect_connection_legacy_debug_proc_show`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/devices.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/devices.c

## Purpose
Tracks RDMA devices capable of SMBDirect and provides netdev-to-RDMA capability lookup for client/server upper layers.

## Device Registration
- `smbdirect_ib_device_rdma_capable_node_type()` accepts only devices with FRWR support and node type `RDMA_NODE_IB_CA` or `RDMA_NODE_RNIC`.
- `smbdirect_ib_client_add()` logs device capabilities, ignores unsupported devices, allocates `struct smbdirect_device`, stores `ib_dev` and a copy of its name, and inserts it into the global list.
- `smbdirect_ib_client_remove()` removes matching device entries and frees them.
- `smbdirect_ib_client_rename()` updates stored names for diagnostic consistency.
- `smbdirect_ib_client` is the RDMA core client with add/remove/rename callbacks.

## Netdev Lookup
- `smbdirect_netdev_find_rdma_capable_node_type()` scans registered devices and ports, comparing `ib_device_get_netdev()` output to the given netdev.
- If not found in the local list, it falls back to `ib_device_get_by_netdev()`.
- `smbdirect_netdev_rdma_capable_node_type()` additionally checks bridge/VLAN lower devices and treats IPoIB netdevs as `RDMA_NODE_IB_CA`.

## Init/Exit
- `smbdirect_devices_init()` initializes global rwlock/list and registers the IB client.
- `smbdirect_devices_exit()` clears tracked devices under lock, then unregisters the IB client.

## Concurrency
- Global device list uses `smbdirect_globals.devices.lock` as an rwlock.
- Netdev refs obtained from RDMA helpers are released with `dev_put()`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/devices.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/internal.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/internal.h

## Purpose
Private SMBDirect subsystem header. It defines module-global state, internal device tracking, cleanup scheduling macros, and cross-file prototypes.

## Key Types
- `struct smbdirect_module_state`
  - global mutex
  - workqueues: accept, connect, idle, refill, immediate, cleanup
  - RDMA device list protected by rwlock
- `struct smbdirect_device`
  - global-list node
  - `ib_device *`
  - cached IB device name for remove/rename logs

## Cleanup Macros
- `smbdirect_socket_schedule_cleanup()`
- `smbdirect_socket_schedule_cleanup_lvl()`
- `smbdirect_socket_schedule_cleanup_status()`

These wrap `__smbdirect_socket_schedule_cleanup()` with caller function/line, log level, error, and optional forced status.

## Internal Interfaces
Declares internal functions shared across implementation files:
- socket init/destroy/wait helpers
- RDMA established and negotiation completion
- QP and memory pool lifecycle
- send/recv I/O allocation and posting
- reassembly helpers
- RDMA resource negotiation
- idle timer and credit grant helpers
- MR list lifecycle
- accept-side connect request and negotiate finish
- device subsystem init/exit

## Notes
- Sets `DEFAULT_SYMBOL_NAMESPACE` to `SMBDIRECT`.
- Includes public `<linux/smbdirect.h>` and private `pdu.h`, then includes `socket.h` after globals are declared.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/listen.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/listen.c

## Purpose
Listening socket setup and RDMA CM connect-request admission for SMBDirect.

## Listen Setup
- `smbdirect_socket_listen()`:
  - validates backlog and socket state
  - defaults backlog 0 to 1
  - transitions `CREATED` -> `LISTENING`
  - sets expected event to `RDMA_CM_EVENT_CONNECT_REQUEST`
  - installs `smbdirect_listen_rdma_event_handler()`
  - calls `rdma_listen()`
  - records backlog only after successful listen

## RDMA Event Handling
- `smbdirect_listen_rdma_event_handler()` handles only expected connect requests.
- For connect request events, it detaches the new CM ID from the listener context and installs a placeholder handler until the accepting socket owns it.
- Unexpected events or statuses schedule cleanup on the listener; for a new CM ID, error is returned so RDMA CM destroys it.

## Connect Request Admission
- `smbdirect_listen_connect_request()`:
  - validates FRWR support on the selected device
  - enforces listener port-range flags for IB/RoCE or iWARP only
  - counts pending and ready accepted sockets against backlog
  - creates an accepting socket for the new RDMA CM ID
  - copies logging and initial parameters from listener
  - copies kernel settings from listener
  - links new socket into listener `pending` list
  - calls `smbdirect_accept_connect_request()`
- On failure after socket creation, it removes listener linkage, detaches RDMA ID ownership so caller can destroy it, and releases the socket.

## Concurrency
- Listener `pending` and `ready` lists are guarded by `lsc->listen.lock`.
- Connect request handler assumes RDMA CM callback context may sleep and warns if in interrupt.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/listen.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/main.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/main.c

## Purpose
SMBDirect module initialization and teardown.

## Initialization
- Defines global `smbdirect_globals` with initialized mutex.
- `smbdirect_module_init()` allocates subsystem workqueues:
  - `smbdirect-accept`
  - `smbdirect-connect`
  - `smbdirect-idle`
  - `smbdirect-refill`
  - `smbdirect-immediate`
  - `smbdirect-cleanup`
- Workqueues use `WQ_SYSFS`, `WQ_PERCPU`, `WQ_POWER_EFFICIENT`; refill/immediate/cleanup are high priority, and cleanup has `WQ_MEM_RECLAIM`.
- Calls `smbdirect_devices_init()` after workqueues are ready.
- On failure, unwinds already allocated workqueues in reverse order.

## Teardown
- `smbdirect_module_exit()` unregisters/cleans devices and destroys all workqueues under the global mutex.

## Module Metadata
- `module_init()` / `module_exit()`
- Description: `smbdirect subsystem`
- License: GPL
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/main.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/mr.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/mr.c

## Purpose
Memory registration lifecycle for SMBDirect RDMA read/write. This is primarily used by the SMB client side to expose local buffers to the peer via SMBDirect buffer descriptors.

## MR Pool Creation/Destruction
- `smbdirect_connection_create_mr_list()` requires nonzero negotiated responder resources and allocates `responder_resources * 2` MRs.
- Each `smbdirect_mr_io` gets:
  - kref and mutex
  - `ib_alloc_mr()` with negotiated MR type and `max_frmr_depth`
  - scatterlist array sized to `max_frmr_depth`
  - state `SMBDIRECT_MR_READY`
- `smbdirect_connection_destroy_mr_list()` splices the global MR list, disables each MR, detaches it from the socket, and drops the connection reference.
- `smbdirect_mr_io_disable_locked()` deregisters the MR, unmaps DMA SGs if present, frees the SGL, clears fields, and marks disabled.

## MR Acquisition
- `smbdirect_connection_get_mr_io()` waits for ready MR count while connected, scans the MR list for `SMBDIRECT_MR_READY`, marks it registered, takes a kref, decrements ready count, and increments used count.

## Registration
- `smbdirect_connection_register_mr_io()`:
  - checks iterator page count against `max_frmr_depth`
  - gets an MR
  - sets DMA direction based on SMBDirect operation
  - extracts iterator pages into the MR SG table via `extract_iter_to_sg()`
  - DMA maps SGs
  - maps SGs into the MR with `ib_map_mr_sg()`
  - updates rkey with `ib_update_fast_reg_key()`
  - posts `IB_WR_REG_MR`
- Registration completion only logs/schedules cleanup on failed CQ status; normal path relies on WR ordering before peer-visible I/O.

## Descriptor Export
- `smbdirect_mr_io_fill_buffer_descriptor()` fills `offset`, `token`, and `length` from the registered MR.
- If the MR is not registered, it fills sentinel max values.

## Deregistration
- `smbdirect_connection_deregister_mr_io()`:
  - disables immediately if socket is no longer connected
  - if `need_invalidate`, posts `IB_WR_LOCAL_INV` and waits for completion
  - otherwise marks remote-invalidated MR invalidated
  - unmaps DMA SGs
  - returns MR to ready state, wakes waiters, decrements used count, and drops caller kref
- Local invalidation completion marks state invalidated and completes `invalidate_done`.

## Error Handling
- Registration/deregistration posting failures schedule socket cleanup.
- Kref release is coordinated while holding the MR mutex to allow detached but still referenced MRs during connection teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/mr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/pdu.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/pdu.h

## Purpose
Private SMBDirect wire-format definitions for negotiation and data-transfer PDUs.

## Constants
- `SMBDIRECT_V1` is `0x0100`.
- Minimums from MS-SMBD:
  - `SMBDIRECT_MIN_RECEIVE_SIZE` = 128
  - `SMBDIRECT_MIN_FRAGMENTED_SIZE` = 131072
- Data PDU layout constants:
  - `SMBDIRECT_DATA_MIN_HDR_SIZE`
  - `SMBDIRECT_DATA_OFFSET`
- `SMBDIRECT_FLAG_RESPONSE_REQUESTED` requests an immediate response/keepalive.

## Wire Structures
- `struct smbdirect_negotiate_req`
  - min/max version
  - credits requested
  - preferred send size
  - max receive size
  - max fragmented size
- `struct smbdirect_negotiate_resp`
  - min/max/negotiated version
  - credits requested/granted
  - NT status
  - max read/write size
  - preferred send size
  - max receive size
  - max fragmented size
- `struct smbdirect_data_transfer`
  - credits requested/granted
  - flags
  - remaining data length
  - data offset and length
  - padding
  - flexible payload buffer

## Notes
- All PDU structures are packed and use little-endian fields.
- These structures are consumed by `accept.c`, `connect.c`, and `connection.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/pdu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/rw.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/rw.c

## Purpose
Server-side RDMA read/write execution against peer-provided SMBDirect buffer descriptors.

## Credit Accounting
- `smbdirect_connection_calc_rw_credits()` computes credits from local buffer page count and pages per RW credit.
- `smbdirect_connection_wait_for_rw_credits()` waits on RW credits while connected.

## SG Construction
- `smbdirect_connection_rdma_get_sg_list()` converts a kernel/vmalloc buffer into scatterlist entries using `vmalloc_to_page()` or `kmap_to_page()`.
- It validates nonzero size and enough entries for the page span.

## RDMA Execution
- `smbdirect_connection_rdma_xmit()`:
  - validates connected state and `max_read_write_size`
  - walks descriptor array, truncating final descriptor length to remaining buffer length when needed
  - calculates needed credits
  - waits for RW credits
  - allocates one `smbdirect_rw_io` per descriptor
  - allocates chained SG tables
  - builds SGs over local buffer spans
  - initializes `rdma_rw_ctx` with remote offset/token and direction
  - chains work requests in reverse order
  - posts the chain with `ib_post_send()`
  - waits for completion of the last message
  - destroys all RDMA RW contexts, frees SG tables, returns credits, and wakes waiters

## Completion Handling
- `smbdirect_connection_rdma_read_done()` and `_write_done()` call shared completion logic.
- Failed completions set `msg->error = -EIO`; non-flush failures schedule socket cleanup.
- Completion wakes the stack completion used by the synchronous transmit call.

## Notes
- `is_read` selects DMA direction:
  - true: local buffer receives data (`DMA_FROM_DEVICE`)
  - false: local buffer sends data (`DMA_TO_DEVICE`)
- Exported as `smbdirect_connection_rdma_xmit`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/rw.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/socket.c -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/socket.c

## Purpose
Socket object lifecycle, public construction/configuration APIs, central cleanup/disconnect/destroy handling, bind/shutdown/release, and generic credit wait helper.

## Creation and Configuration
- `smbdirect_frwr_is_supported()` requires `IB_DEVICE_MEM_MGT_EXTENSIONS` and nonzero `max_fast_reg_page_list_len`.
- `smbdirect_socket_init_new()` initializes a socket, creates an RDMA CM ID, enforces address-family-only behavior, and installs cleanup work.
- `smbdirect_socket_create_kern()` allocates a standalone kernel socket and initializes destroy refcount.
- `smbdirect_socket_init_accepting()` initializes a socket around an accepted RDMA CM ID, sets context/handler, and caches `ib.dev`.
- `smbdirect_socket_create_accepting()` allocates a standalone accepting socket.
- `smbdirect_socket_set_initial_parameters()` is only valid in `CREATED`, validates flags/depth/resource limits, optionally restricts RDMA node type, and copies parameters.
- `smbdirect_socket_set_kernel_settings()` is only valid in `CREATED` and sets CQ polling context plus GFP masks.
- `smbdirect_socket_set_logging()` installs upper-layer logging callbacks.

## Central Cleanup
- `__smbdirect_socket_schedule_cleanup()`:
  - records first error once
  - disables connect/refill/immediate/idle work without waiting
  - clears keepalive state
  - recursively schedules cleanup for listener pending/ready accepted sockets
  - maps current status to failed/disconnected/error state
  - applies optional forced status
  - wakes all waitqueues
  - queues `disconnect_work`
- `smbdirect_socket_cleanup_work()`:
  - ensures first error exists
  - disables work
  - propagates cleanup to accepted sockets for listeners
  - for connected/negotiating/error sockets, transitions to disconnecting and calls `rdma_disconnect()` under RDMA handler lock
  - for pre-established states, moves directly to disconnected
  - wakes all waiters

## Destruction
- `smbdirect_socket_destroy()` expects disconnected state, disables all work synchronously, locks RDMA handler, drains QP, releases listener child sockets, drains receive reassembly buffers, destroys MR list, QP, RDMA CM ID, and mempools, then marks `DESTROYED`.
- `smbdirect_socket_destroy_sync()` disables future disconnect work, schedules shutdown cleanup if needed, waits for disconnected state, then calls destroy.
- `smbdirect_socket_release()` drops the frontend disconnect reference and backend destroy reference; standalone sockets are freed when destroy ref reaches zero.

## Other APIs
- `smbdirect_socket_bind()` wraps `rdma_bind_addr()` for created sockets.
- `smbdirect_socket_shutdown()` schedules cleanup with `-ESHUTDOWN`.
- `smbdirect_socket_wait_for_credits()` atomically reserves credits or waits interruptibly until credits are available or socket status changes.

## Concurrency Model
- Waitqueues for status, listener accept, send credits, pending sends, receive reassembly, RW credits, and MR readiness are all woken on cleanup.
- RDMA handler lock coordinates disconnect/destroy ordering around `rdma_disconnect()`, `ib_drain_qp()`, and CM callbacks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/socket.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/socket.h -->
# File Research: sources/os/linux/linux-stable/fs/smb/smbdirect/socket.h

## Purpose
Private socket-state definitions for the SMBDirect implementation.

## Status Machine
`enum smbdirect_socket_status` covers:
- creation/listening
- address and route resolution states
- RDMA connect states
- negotiation states
- connected, error, disconnecting, disconnected, destroyed

`smbdirect_socket_status_string()` maps each enum to diagnostics.

## Main Socket Structure
`struct smbdirect_socket` contains:
- status waitqueue and first error
- per-socket workqueue pointers copied from globals
- cleanup/disconnect work
- separate krefs:
  - `disconnect` frontend lifetime
  - `destroy` backend memory lifetime
- RDMA CM state, expected event, and legacy iWARP flag
- IB resources: PD, send/recv CQs, QP, device, poll context
- negotiated `smbdirect_socket_parameters`
- connect work state
- idle keepalive/immediate/timer work
- listener state: pending/ready accepted socket lists, waitqueue, backlog
- accepting-socket backpointer/list node
- send state:
  - mempool/cache
  - batch credit
  - local send WR credits
  - peer-granted send credits
  - pending sends and zero waitqueue
- receive state:
  - expected PDU type
  - mempool/cache
  - free receive buffers
  - posted count/refill work
  - receive credit target/available/count
  - reassembly queue metadata
- MR state:
  - MR type
  - all MR list
  - ready and used counts
- server-side RDMA read/write credits
- debug counters
- logging callbacks

## Initialization Helper
`smbdirect_socket_init()` zeroes the structure and initializes all waitqueues, work items, refs, list heads, locks, defaults, counters, and disabled placeholder work/logging callbacks.

## Logging Helpers
- Fallback logging callbacks warn if used before upper layer installs real callbacks.
- Macros classify logs as outgoing, incoming, read, write, RDMA send/recv/event/MR/RW, keepalive, or negotiate.

## Status Check Macros
- `SMBDIRECT_CHECK_STATUS_WARN()` logs and warns on unexpected state.
- `SMBDIRECT_CHECK_STATUS_DISCONNECT()` also schedules cleanup for unexpected state.

## I/O Types
- `struct smbdirect_send_io`: send CQE, up to 6 SGEs, sibling-chain list, WR, flexible packet header.
- `struct smbdirect_send_batch`: list of sends, WR count, optional remote key invalidation, serialized batch credit.
- `struct smbdirect_recv_io`: receive CQE, single SGE, list node, first-segment marker, flexible packet buffer.
- `enum smbdirect_mr_state` and `struct smbdirect_mr_io`: MR state, refs, mutex, SG table, reg/inv WRs, invalidation completion.
- `struct smbdirect_rw_io`: RDMA read/write context, SG table, completion pointer.
- `smbdirect_get_buf_page_count()` computes page span for arbitrary buffer/length.

## Constants
- RDMA CM retry count: 6
- RNR retry count: 0 because SMBDirect manages credits.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/smb/smbdirect/socket.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/splice.c -->
# File Research: sources/os/linux/linux-stable/fs/splice.c

## Purpose
Linux VFS splice/vmsplice/tee implementation. It implements zero-copy or low-copy data movement through pipes, file-to-pipe, pipe-to-file, pipe-to-pipe, socket splice, direct splice for sendfile/copy_file_range, and vmsplice user-memory pipe integration.

## Pipe Buffer Operations
- `pipe_clear_nowait()` clears `FMODE_NOWAIT` from pipe files because splice does not support it.
- Page-cache pipe buffer ops:
  - `page_cache_pipe_buf_confirm()` verifies uptodate page-cache folios and handles truncated/unhashed folios as `-ENODATA`.
  - `page_cache_pipe_buf_try_steal()` tries to remove a folio from page cache after writeback/release checks.
  - `page_cache_pipe_buf_release()` drops page ref and clears LRU flag.
- User-page pipe buffer ops allow stealing only when `PIPE_BUF_FLAG_GIFT` is present.
- `default_pipe_buf_ops` and `nosteal_pipe_buf_ops` provide generic buffer behavior.

## Splice Into Pipe
- `splice_to_pipe()` installs pages from a `splice_pipe_desc` into a pipe until full or descriptor exhausted, handling no-readers with `SIGPIPE`/`-EPIPE`.
- `add_to_pipe()` inserts one prepared `pipe_buffer` or releases it on failure.
- `splice_grow_spd()` / `splice_shrink_spd()` manage dynamic descriptor arrays when pipe capacity exceeds default buffers.
- `copy_splice_read()` is fallback read-copy-to-pipe logic for O_DIRECT/DAX or read paths that cannot use page cache splicing.

## Splice From Pipe
- `splice_from_pipe_feed()` walks pipe buffers, confirms them, calls an actor, advances offsets/lengths, releases consumed buffers, and tracks wakeups.
- `splice_from_pipe_next()` waits for readable pipe data, respects `SPLICE_F_NONBLOCK`, signals, EOF, and empty buffers.
- `__splice_from_pipe()` is the generic loop over `next` and `feed`.
- `splice_from_pipe()` wraps it with pipe locking.
- `iter_file_splice_write()` builds bvec arrays from pipe buffers and writes through `->write_iter`, then consumes written pipe data.
- Under `CONFIG_NET`, `splice_to_socket()` sends pipe pages to sockets via `MSG_SPLICE_PAGES`, using `MSG_MORE` when appropriate.

## Direct Splice
- `do_splice_read()` validates readable input, caps reads by pipe space and `MAX_RW_COUNT`, uses `copy_splice_read()` for O_DIRECT/DAX, otherwise calls `->splice_read`.
- `vfs_splice_read()` wraps `rw_verify_area()` then `do_splice_read()`.
- `splice_direct_to_actor()` implements non-pipe to non-pipe transfer through a per-task cached pipe (`current->splice_pipe`), used by sendfile-like paths.
- It requires seekable input and drains the internal pipe through an actor to avoid stuck pipe data.
- `do_splice_direct()` uses a direct actor with `file_start_write()`/`file_end_write()`.
- `splice_file_range()` is the copy-file-range variant where the caller already holds write-start state.
- EOF notification is supported through `splice_eof`.

## Splice Syscall Routing
- `do_splice()` selects behavior:
  - pipe -> pipe: `splice_pipe_to_pipe()`
  - pipe -> file: validate write area, reject append, call `do_splice_from()`
  - file -> pipe: validate read area, call `splice_file_to_pipe()`
  - non-pipe -> non-pipe: invalid for `splice(2)`
- It updates offsets, honors pipe/nonblock flags, and emits fsnotify access/modify on success.
- `__do_splice()` handles userspace offsets and clears NOWAIT on pipe endpoints.
- `SYSCALL_DEFINE6(splice)` validates flags, fds, zero length, then calls `__do_splice()`.

## vmsplice
- `iter_to_pipe()` pins/gets pages from a source iterator with `iov_iter_get_pages2()` and inserts them as user-page pipe buffers.
- `vmsplice_to_pipe()` optionally marks buffers as gifts, waits for pipe space, inserts iterator pages, wakes readers, and sends modify notification.
- `vmsplice_to_user()` copies pipe pages to a destination user iterator via `__splice_from_pipe()` and `pipe_to_user()`.
- `SYSCALL_DEFINE4(vmsplice)` imports user iovecs, chooses source/destination mode from file permissions, and dispatches to pipe or user copy path.

## Pipe-to-Pipe and tee
- `ipipe_prep()` waits for readable input pipe data.
- `opipe_prep()` waits for writable output pipe space and handles no-reader `SIGPIPE`.
- `splice_pipe_to_pipe()` moves pipe buffers from input to output, partially copying buffer refs when only part of a buffer is requested. It uses `pipe_double_lock()` to avoid ABBA deadlocks.
- `link_pipe()` duplicates pipe buffer references into another pipe without consuming input; it clears gift and merge flags on output buffers.
- `do_tee()` validates pipe endpoints and uses `link_pipe()` for zero-copy duplication.
- `SYSCALL_DEFINE4(tee)` validates flags/fds/length and calls `do_tee()`.

## Important Semantics
- Pipe locking and wakeups are carefully separated between readers/writers and fasync notifications.
- `SPLICE_F_NONBLOCK` affects waiting on pipe readiness/space; direct splice deliberately clears nonblock for output drain.
- Gifted pages may be stolen only through user-page pipe ops and only once; cloned pipe buffers clear gift/merge flags.
- Page-cache splicing must coordinate with folio writeback and mapping removal to avoid filesystem corruption.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/splice.c -->