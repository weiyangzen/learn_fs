# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_node.c

## Purpose
`efc_node.c` implements core remote-node allocation, reference management, event posting, generic node shutdown, pending-frame handling, and receive-frame-to-event decoding.

## Important APIs, Types, And Functions
Key APIs are `efc_remote_node_cb`, `efc_node_find`, `efc_node_alloc`, `efc_node_free`, `efc_node_attach`, `efc_node_post_event`, `efc_node_transition`, `efc_node_recv_els_frame`, `efc_node_recv_ct_frame`, `efc_node_recv_fcp_cmd`, `efc_process_node_pending`, SCSI completion hooks, WWN helpers, pause support, and generic shutdown states.

## Control Flow And State
Allocation uses the node mempool and DMA pool, reserves an RPI, stores the node in the nport xarray by FC_ID, initializes pending-frame and ELS lists, and takes an nport reference. Event posting increments `evtdepth`, invokes the current state, processes held frames when safe, and frees the node if `req_free` is set at outermost depth. Shutdown disables or waits for ELS I/O, detaches hardware if needed, waits for active I/O empty, purges pending frames for default shutdown, and frees resources/xarray entries. ELS receive decoding maps protocol opcodes to `EFC_EVT_*`; CT defaults to reject; FCP commands become `EFC_EVT_FCP_CMD_RCVD`.

## Dependencies And Integration Points
The file integrates command helpers, ELS send/reject helpers, domain frame dispatch, backend SCSI completion callbacks, Linux xarray/list/spinlock/timer primitives, and FC protocol headers.

## Risks And Test Signals
Risks include event-depth lifetime bugs, freeing a node while callbacks still hold implicit references, duplicate or stale pending frames, counter underflow in shutdown states, and `efc_node_check_els_req`/`efc_node_check_ns_req` currently returning 0 without validation. Test signals include allocation failure cleanup, xarray lookup/refcount behavior, nested event transitions, pending-frame hold/replay, unsupported ELS rejection, CT reject, SCSI completion event posting, and shutdown with active ELS/I/O.
