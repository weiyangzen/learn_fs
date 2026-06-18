# sources/distributed-fs/lustre-release/lnet/klnds/o2iblnd/o2iblnd_cb.c

## Purpose
`o2iblnd_cb.c` implements the o2iblnd callback and hot-path logic: LNet send/receive translation, RDMA memory mapping for message payloads, TX/RX completion handling, credit accounting, active/passive RDMA CM negotiation, connection timeout/reconnect processing, CQ scheduling, and failover thread execution.

## Important APIs, types, and functions
- TX completion and allocation: `kiblnd_tx_done()`, `kiblnd_txlist_done()`, `kiblnd_get_idle_tx()`, `kiblnd_unmap_tx()`.
- RX posting and handling: `kiblnd_post_rx()`, `kiblnd_drop_rx()`, `kiblnd_handle_rx()`, `kiblnd_rx_complete()`, `kiblnd_recv()`.
- Message and RDMA setup: `kiblnd_init_tx_msg_payload()`, `kiblnd_init_tx_sge()`, `kiblnd_setup_rd_kiov()`, `kiblnd_map_tx()`, `kiblnd_fmr_map_tx()`, `kiblnd_init_rdma()`.
- Send queueing: `kiblnd_queue_tx_locked()`, `kiblnd_queue_tx()`, `kiblnd_post_tx_locked()`, `kiblnd_check_sends_locked()`, `kiblnd_launch_tx()`, `kiblnd_send()`.
- Completion protocol: `kiblnd_find_waiting_tx_locked()`, `kiblnd_handle_completion()`, `kiblnd_send_completion()`, `kiblnd_reply()`.
- Connection management: privileged port address resolution, `kiblnd_connect_peer()`, `kiblnd_reconnect_peer()`, `kiblnd_close_conn_locked()`, `kiblnd_finalise_conn()`, `kiblnd_connreq_done()`, `kiblnd_passive_connect()`, `kiblnd_active_connect()`, `kiblnd_rejected()`, `kiblnd_check_connreply()`.
- Callback threads/events: `kiblnd_cm_callback()`, `kiblnd_connd()`, `kiblnd_qp_event()`, `kiblnd_cq_completion()`, `kiblnd_scheduler()`, and `kiblnd_failover_thread()`.

## Control flow
For sends, `kiblnd_send()` allocates a TX descriptor, inspects the LNet message type, and chooses immediate send, PUT RDMA, or GET RDMA. Small non-GPU payloads are copied into the message buffer. Large or GPU-backed payloads are converted into scatterlists, DMA mapped, registered through FMR/FastReg, and described in wire RDMA descriptors. `kiblnd_launch_tx()` finds or creates a peer, queues while connection attempts are in progress, or queues on an established connection. `kiblnd_check_sends_locked()` drains nocredit, NOOP, reserved, and normal queues according to credits, concurrent send limits, and keepalive/credit-return needs. `kiblnd_post_tx_locked()` packs final headers, posts IB send WR chains, and handles rollback on post failure.

For receives, CQ completions call `kiblnd_rx_complete()`, which unpacks the message, rejects stale NID/incarnation stamps, records peer liveness, defers early receives until establishment, and then dispatches `kiblnd_handle_rx()`. Immediate messages are passed to `lnet_parse()`. PUT requests cause `kiblnd_recv()` to register a local sink and send `PUT_ACK`; the sender then performs RDMA write and sends `PUT_DONE`. GET requests cause `kiblnd_reply()` to register a source, perform RDMA write, and send `GET_DONE`. Completion messages match waiting TX cookies and finalize LNet messages.

For connection setup, active connects resolve address/route, create a conn, send `CONNREQ`, and validate `CONNACK`. Passive connects validate private data, destination NI, protocol version, queue depth, max fragments, message size, privileged port policy, stale incarnations, and connection races before accepting with `CONNACK`. Rejections can trigger reconnect with downgraded protocol, reduced queue depth, or reduced max fragments.

For background processing, `kiblnd_connd()` destroys zombie conns, disconnects closing conns, schedules reconnects, and periodically checks peer buckets for waiting TX, connection request, and active RDMA timeouts. CQ callbacks schedule connections onto per-CPT scheduler queues; scheduler threads poll CQs, re-arm notifications, dispatch RX/TX/MR/RDMA completion types, and drop refs. The failover thread drains failed-device requests, calls `kiblnd_dev_failover()`, and periodically probes active devices.

## State and persistence behavior
This file mutates only runtime kernel state. It owns TX descriptor transitions, RX repost/drop decisions, peer liveness timestamps, peer connection attempt counters, connection state transitions after CM events, health status propagation into LNet messages, timeout deadlines, reconnect queues, CQ scheduling flags, and failover retry timestamps. LNet messages are finalized exactly when o2iblnd knows local copy/RDMA/control completion status, and health status is preserved through `tx_hstatus`.

## Dependencies and integration points
The file depends on shared definitions from `o2iblnd.h`, LNet message parsing/finalization/reply creation, LNet error simulation, LNet GPU MD detection, RDMA CM, IB verbs CQ/QP/send/recv APIs, Linux credentials for privileged source port binding, and failover/device functions implemented in `o2iblnd.c`. It is the implementation target for many callbacks registered from the LNet driver and RDMA CM listener.

## Risks and edge cases
- Credit accounting is complex: peer credits, reserved credits, outstanding credits, NOOP credits, OOB v2 behavior, and v1 last-credit reservation must remain balanced.
- TX descriptors can be simultaneously affected by send completion, remote completion, timeout, and connection close; the `tx_sending`, `tx_waiting`, and `tx_queued` state machine is delicate.
- FastReg local invalidate/reg WR chains must be posted in the right order and returned to pools exactly once.
- Failure to receive expected IB completions can leave stale connections; the code comments call out this risk during abort handling.
- Passive/active connection races are resolved by NID hash and a race counter, so regressions can cause repeated rejection or duplicate connections.
- Privileged port override temporarily changes credentials; error paths must revert credentials and destroy CM IDs.
- CQ scheduling uses extra connection refs; missed drops or scheduling after refcount zero would be severe.

## Test signals
High-value tests include immediate ACK/PUT/REPLY traffic, RDMA PUT and GET with large and fragmented payloads, GPU-backed MD sends, v1/v2 interoperability, concurrent sends at credit limits, keepalive/NOOP generation, connect race simulations, stale incarnation rejection, CM rejection downgrade paths, privileged source port binding, RDMA timeouts, CQ poll error/fail completions, device fatal/port events, failover retry, and LNet health status assertions for local, remote, network, and timeout failures.
